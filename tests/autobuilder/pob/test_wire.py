"""S12: inf, -inf, NaN and missing values cross from Lua to Python as themselves, and every reply is an envelope whose
error kind becomes the matching PobError. The Lua side is rpc.lua in a bare state (lua/dispatcher.lua) and real PoB."""

import math
from typing import Any

import pytest

from autobuilder.errors import BuildLoadFailed, NoBuildLoaded, PobError, UnknownEndpoint
from autobuilder.pob import wire
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.lua_host import LuaHost
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob


def ask(host: LuaHost, name: str, payload: dict[str, Any] | None = None) -> Any:
    return wire.decode_reply(host.call(name, wire.encode_request(payload)))


def test_non_finite_numbers_arrive_as_floats(probe_rpc: LuaHost) -> None:
    value = ask(probe_rpc, "probe.numbers")
    assert value["inf"] == math.inf and value["ninf"] == -math.inf and math.isnan(value["nan"])
    assert (value["plain"], value["negative"], value["list"][1]) == (7.5757, -3, math.inf)
    assert value["nested"]["deeper"]["value"] == -math.inf


def test_finite_numbers_arrive_as_the_same_double(probe_rpc: LuaHost) -> None:
    """dkjson alone keeps 14 digits (dkjson.lua:201-203): 3.9999999999999996 would arrive as 4 and floor to 4."""
    value = ask(probe_rpc, "probe.numbers")
    assert (value["almostFour"], value["long"], value["sum"]) == (3.9999999999999996, 7176019.123456789, 0.1 + 0.2)
    assert (value["tiny"], value["level"], math.floor(value["almostFour"])) == (5e-324, 98, 3)


def test_a_missing_value_is_a_missing_key(probe_rpc: LuaHost) -> None:
    assert ask(probe_rpc, "probe.echo", {"keep": 1, "gone": None}) == {"keep": 1}
    assert ask(probe_rpc, "probe.nothing") is None


@pytest.mark.parametrize(
    ("kind", "error"), [("NoBuild", NoBuildLoaded), ("BuildNotLoaded", BuildLoadFailed), ("Other", PobError)]
)
def test_an_error_kind_becomes_its_error_class(probe_rpc: LuaHost, kind: str, error: type[PobError]) -> None:
    with pytest.raises(error, match=r"^why$") as caught:
        ask(probe_rpc, "probe.fail", {"kind": kind, "message": "why"})
    assert type(caught.value) is error


def test_unknown_names_bad_requests_and_crashes_are_errors(probe_rpc: LuaHost) -> None:
    with pytest.raises(UnknownEndpoint, match=r"no endpoint named probe.none"):
        ask(probe_rpc, "probe.none")
    with pytest.raises(PobError, match="not a JSON object"):
        wire.decode_reply(probe_rpc.call("probe.echo", b"[1, 2"))
    with pytest.raises(PobError, match=r"dispatcher.lua:.*: kaput") as caught:
        ask(probe_rpc, "probe.crash", {"message": "kaput"})
    assert caught.value.traceback is not None and "stack traceback" in caught.value.traceback
    with pytest.raises(PobError, match=r"^table: "):
        ask(probe_rpc, "probe.crash_table")
    with pytest.raises(PobError, match="table inside itself"):
        ask(probe_rpc, "probe.cycle")
    with pytest.raises(PobError, match="type 'function' is not supported by JSON"):
        ask(probe_rpc, "probe.function")
    with pytest.raises(PobError, match=r"registered twice: probe.echo"):
        ask(probe_rpc, "probe.register_twice")


def test_a_request_with_a_non_finite_number_is_a_bug() -> None:
    with pytest.raises(ValueError, match="Out of range float"):
        wire.encode_request({"x": math.inf})


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (b"\xff", "not JSON"),
        (b"{", "not JSON"),
        (b"[]", "not an {ok, value, error} envelope"),
        (b'{"ok": 1}', "not an {ok, value, error} envelope"),
        (b'{"ok": false}', "failed without saying why"),
        (b'{"ok": false, "error": {"kind": "X"}}', r"PoB failed \(X\)"),
    ],
)
def test_a_reply_that_is_not_an_envelope_is_an_error(raw: bytes, message: str) -> None:
    with pytest.raises(PobError, match=message):
        wire.decode_reply(raw)


def test_typed_values_check_their_type() -> None:
    assert (wire.number(None), wire.number(3), wire.text(None), wire.table([])) == (None, 3.0, None, {})
    for bad, read in ((True, wire.number), ("1", wire.number), (1, wire.text), ([1], wire.table)):
        with pytest.raises(PobError, match="expected"):
            read(bad)


# Measured 2026-10-27 on PoB 2.67.2: the only non-finite numbers in the two builds' main output. dkjson alone would
# send each as null; MaximumHitTaken is m_huge when the hit cannot kill (CalcDefence.lua:3271-3272).
NON_FINITE = {
    "Worb": {"EHPSurvivalTime": math.inf, "enemySkillTime": math.inf},
    "CoC EK Assa": {"ChaosDotEHP": math.inf, "ChaosMaximumHitTaken": math.inf},
}


@pytest.mark.parametrize("name", NON_FINITE)
def test_real_pob_output_keeps_its_non_finite_numbers(
    pob_session: PobSession, reference_xml: dict[str, str], name: str
) -> None:
    pob_session.load_build(reference_xml[name], name)
    output = pob_session.call(Endpoint.BUILD_STATE)["output"]
    assert all(isinstance(value, float | int) and not isinstance(value, bool) for value in output.values())
    assert {key: value for key, value in output.items() if not math.isfinite(value)} == NON_FINITE[name]

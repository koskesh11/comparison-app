"""What every request must show (app/security.py): host, origin, token, body caps (ported from the first app's
tests/test_server_security.py cases)."""

import pytest

from comparison_app.app.security import (
    MAX_BODY_BYTES,
    MAX_CODE_BODY_BYTES,
    Refused,
    body_limit,
    check_request,
    new_token,
)

PORT, TOKEN = 8765, "secret-token"
GOOD = {"Host": "127.0.0.1:8765", "Origin": "http://127.0.0.1:8765", "X-Api-Token": TOKEN}


def refusal(headers: dict[str, str], *, api: bool = True) -> tuple[int, str]:
    with pytest.raises(Refused) as caught:
        check_request(headers, port=PORT, token=TOKEN, api=api)
    return caught.value.status, caught.value.reason


def test_the_page_and_its_api_calls_pass() -> None:
    check_request(GOOD, port=PORT, token=TOKEN, api=True)
    check_request({"Host": "localhost:8765"}, port=PORT, token=TOKEN, api=False)  # a plain browser load, no origin


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({**GOOD, "Host": "evil.example:8765"}, (403, "bad_host")),  # DNS rebinding
        ({**GOOD, "Origin": "http://evil.example"}, (403, "bad_origin")),
        ({key: value for key, value in GOOD.items() if key != "X-Api-Token"}, (401, "missing_token")),
        ({**GOOD, "X-Api-Token": "guess"}, (401, "bad_token")),
    ],
)
def test_a_request_without_its_credentials_is_refused(headers: dict[str, str], expected: tuple[int, str]) -> None:
    assert refusal(headers) == expected


def test_an_empty_server_token_refuses_every_api_call() -> None:
    with pytest.raises(Refused):
        check_request({**GOOD, "X-Api-Token": ""}, port=PORT, token="", api=True)


def test_bodies_are_capped_and_tokens_are_long() -> None:
    assert (body_limit(False), body_limit(True)) == (MAX_BODY_BYTES, MAX_CODE_BODY_BYTES) == (65536, 307200)
    assert len(new_token()) >= 40 and new_token() != new_token()

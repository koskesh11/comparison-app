"""pobb.in links and the one request per link (ported from tests/test_pobbin.py). No network: a fake opener answers."""

import urllib.error
import urllib.request
from email.message import Message
from typing import Any, cast

import pytest

from comparison_app.errors import BadLink, FetchFailed, TooLarge
from comparison_app.intake import pobbin

ID = "F8CiRC9KVADl"


@pytest.mark.parametrize(
    "text",
    [
        f"pobb.in/{ID}", f"https://pobb.in/{ID}", f"http://pobb.in/{ID}", f"https://pobb.in/pob/{ID}",
        f"https://pobb.in/{ID}/raw", f"  https://pobb.in/{ID}  ", f"https://www.pobb.in/{ID}",
    ],
)  # fmt: skip
def test_accepted_link_forms(text: str) -> None:
    assert pobbin.parse_link(text) == ID


@pytest.mark.parametrize(
    "text",
    [
        "", ID, f"https://evil.example/{ID}", "https://pobb.in.evil.example/abcd", "https://pobb.in/abc",
        "https://pobb.in/" + "a" * 33, "https://pobb.in/ab cd/efgh", "https://pobb.in/../etc",
        f"https://user@pobb.in/{ID}", f"ftp://pobb.in/{ID}", f"https://pobb.in/{ID}?x=1", f"https://pobb.in/{ID}/other",
        "https://pobb.in/raw", "https://pobb.in/pob",
    ],
)  # fmt: skip
def test_rejected_link_forms(text: str) -> None:
    with pytest.raises(BadLink, match=r"not a pobb.in build link"):
        pobbin.parse_link(text)


def test_only_text_with_a_dot_or_slash_counts_as_a_link() -> None:
    assert pobbin.looks_like_link("pobb.in/x") and pobbin.looks_like_link("https://example/x")
    assert not pobbin.looks_like_link("eNrtfW1v20aW_n_-AGUT")


def test_one_request_to_the_address_pob_uses(opener: Any) -> None:
    fake = opener(b"  abcd\n")
    assert pobbin.fetch(ID, fake) == "abcd"
    assert fake.requests == [(f"https://pobb.in/pob/{ID}", pobbin.READ_SECONDS)]


@pytest.mark.parametrize(
    ("failure", "text"),
    [
        (urllib.error.HTTPError("u", 404, "nf", Message(), None), "answered 404"),
        (urllib.error.URLError("offline"), "no connection"),
        (TimeoutError(), "no connection"),
        (OSError("reset"), "no connection"),
        (503, "answered 503"),
    ],
)
def test_failures_become_fetch_failed(opener: Any, failure: Any, text: str) -> None:
    fake = opener(b"x", status=failure) if isinstance(failure, int) else opener(error=failure)
    with pytest.raises(FetchFailed, match=text):
        pobbin.fetch(ID, fake)


def test_a_body_is_read_in_chunks_up_to_the_limit(opener: Any) -> None:
    body = b"b" * (pobbin.CHUNK_BYTES * 2 + 5)
    assert pobbin.fetch(ID, opener(body)) == body.decode()
    with pytest.raises(TooLarge):
        pobbin.fetch(ID, opener(b"c" * (pobbin.MAX_CODE_BYTES + 10)))


def test_a_trickling_server_is_cut_off_by_the_total_deadline(opener: Any) -> None:
    ticks = iter(range(0, 1000, 20))  # every clock reading is 20 s later
    with pytest.raises(FetchFailed, match="too slow"):
        pobbin.fetch(ID, opener(b"a" * 100), clock=lambda: next(ticks))


def redirect(target: str) -> urllib.request.Request | None:
    request = urllib.request.Request(f"https://pobb.in/pob/{ID}")
    return pobbin.SameHostRedirect().redirect_request(request, cast(Any, None), 301, "moved", cast(Any, {}), target)


@pytest.mark.parametrize(
    "target",
    [
        f"http://pobb.in/pob/{ID}", "https://pobb.in:8080/x", "ftp://pobb.in/x", "https://user@pobb.in/x",
        "https://user:pass@pobb.in/x", "https://evil.example/x", "https://pobb.in:abc/", "https://pobb.in:99999999/x",
        "https://[bad/x",
    ],
)  # fmt: skip
def test_a_redirect_off_https_pobb_in_443_is_refused(target: str) -> None:
    with pytest.raises(urllib.error.URLError):
        redirect(target)


def test_a_redirect_within_pobb_in_is_followed() -> None:
    assert redirect(f"https://pobb.in/pob/{ID}") is not None
    assert redirect("https://www.pobb.in:443/x") is not None


def test_the_real_opener_only_opens_pobb_in_over_https() -> None:
    with pytest.raises(ValueError, match=r"only https://pobb.in/"):
        pobbin.open_https("file:///C:/Windows/win.ini", 1)

"""Fixtures for the intake tests: the recorded pobb.in code, a PoB code maker, and a fake opener that answers
with a canned response (or raises) and records each request instead of sending it. No test here uses the network."""

import base64
import io
import zlib
from collections.abc import Callable
from pathlib import Path

import pytest

RECORDED_CODE = Path(__file__).parents[1] / "fixtures" / "codes" / "pobb_F8CiRC9KVADl.code.txt"


def make_code(xml: str) -> str:
    return base64.urlsafe_b64encode(zlib.compress(xml.encode("utf-8"))).decode("ascii")


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int = 200) -> None:
        super().__init__(body)
        self.status = status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class FakeOpener:
    """Answers every request with `response` (or raises it) and keeps the (url, timeout) of each."""

    def __init__(self, response: FakeResponse | BaseException) -> None:
        self.response = response
        self.requests: list[tuple[str, float]] = []

    def __call__(self, url: str, timeout: float) -> FakeResponse:
        self.requests.append((url, timeout))
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


@pytest.fixture
def recorded_code() -> str:
    return RECORDED_CODE.read_text(encoding="ascii")


@pytest.fixture
def code_of() -> Callable[[str], str]:
    return make_code


@pytest.fixture
def opener() -> Callable[..., FakeOpener]:
    """opener(body, status=200), or opener(error=...) for a failure."""

    def make(body: bytes = b"", status: int = 200, error: BaseException | None = None) -> FakeOpener:
        return FakeOpener(error if error is not None else FakeResponse(body, status))

    return make

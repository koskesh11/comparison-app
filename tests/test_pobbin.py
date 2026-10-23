"""pobb.in link parsing, fetch limits and decoding (task 010, T2). Network is stubbed; the fixture is a recorded code."""

import base64
import io
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
import zlib
from pathlib import Path
from unittest import mock

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import pobbin  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pobb_F8CiRC9KVADl.code.txt"
SMALL_XML = "<PathOfBuilding><Build level=\"1\"/></PathOfBuilding>"


def make_code(xml: str) -> str:
    return base64.urlsafe_b64encode(zlib.compress(xml.encode("utf-8"))).decode("ascii")


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int = 200):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ParseLinkTests(unittest.TestCase):
    def test_accepted_forms(self):
        for text in ("pobb.in/F8CiRC9KVADl", "https://pobb.in/F8CiRC9KVADl", "http://pobb.in/F8CiRC9KVADl",
                     "https://pobb.in/pob/F8CiRC9KVADl", "https://pobb.in/F8CiRC9KVADl/raw",
                     "  https://pobb.in/F8CiRC9KVADl  ", "https://www.pobb.in/F8CiRC9KVADl"):
            with self.subTest(text=text):
                self.assertEqual(pobbin.parse_link(text), "F8CiRC9KVADl")

    def test_rejected_forms(self):
        for text in ("", "F8CiRC9KVADl", "https://evil.example/F8CiRC9KVADl", "https://pobb.in.evil.example/abcd",
                     "https://pobb.in/abc", "https://pobb.in/" + "a" * 33, "https://pobb.in/ab cd/efgh",
                     "https://pobb.in/../etc", "https://user@pobb.in/F8CiRC9KVADl", "ftp://pobb.in/F8CiRC9KVADl",
                     "https://pobb.in/F8CiRC9KVADl?x=1", "https://pobb.in/F8CiRC9KVADl/other", None, 5):
            with self.subTest(text=text):
                with self.assertRaises(pobbin.BadLink):
                    pobbin.parse_link(text)


class DecodeTests(unittest.TestCase):
    def test_recorded_fixture_decodes_to_a_pob_build(self):
        xml = pobbin.decode(FIXTURE.read_text())
        self.assertIn("<PathOfBuilding>", xml[:200])
        self.assertIn("<Build", xml)

    def test_small_roundtrip(self):
        self.assertEqual(pobbin.decode(make_code(SMALL_XML)), SMALL_XML)

    def test_bad_base64_and_bad_zlib_are_unreadable(self):
        for code in ("!!!not base64!!!", base64.urlsafe_b64encode(b"plain text, not zlib").decode(),
                     make_code("<html><body>hello</body></html>")):
            with self.subTest(code=code[:20]):
                with self.assertRaises(pobbin.Unreadable):
                    pobbin.decode(code)

    def test_10_mb_bomb_is_rejected_before_lua(self):
        bomb = make_code("<PathOfBuilding>" + "a" * (10 * 1024 * 1024) + "</PathOfBuilding>")
        self.assertLess(len(bomb), pobbin.MAX_CODE_BYTES)  # tiny on the wire, huge once inflated
        with self.assertRaises(pobbin.TooLarge):
            pobbin.decode(bomb)

    def test_oversized_code_is_rejected(self):
        with self.assertRaises(pobbin.TooLarge):
            pobbin.decode("A" * (pobbin.MAX_CODE_BYTES + 1))

    def test_entities_and_doctype_are_refused(self):
        for xml in ('<!DOCTYPE x [<!ENTITY a "b">]><PathOfBuilding/>', "<PathOfBuilding><!ENTITY a 'b'></PathOfBuilding>"):
            with self.subTest(xml=xml[:30]):
                with self.assertRaises(pobbin.Unreadable):
                    pobbin.decode(make_code(xml))


class FetchTests(unittest.TestCase):
    def fetch_with(self, side_effect):
        with mock.patch.object(pobbin, "_open", side_effect=side_effect) as opened:
            return opened, pobbin.fetch("F8CiRC9KVADl")

    def test_fetch_uses_fixed_host_and_raw_path(self):
        opened, code = self.fetch_with(lambda url, timeout: FakeResponse(b"abcd"))
        self.assertEqual(code, "abcd")
        self.assertEqual(opened.call_args.args[0], "https://pobb.in/F8CiRC9KVADl/raw")
        self.assertEqual(opened.call_args.kwargs["timeout"], pobbin.TIMEOUT_S)

    def test_failures_become_fetch_failed_with_status(self):
        cases = [(urllib.error.HTTPError("u", 404, "nf", {}, None), "404"),
                 (urllib.error.URLError("offline"), "no connection"),
                 (TimeoutError(), "no connection"), (OSError("reset"), "no connection")]
        for error, text in cases:
            with self.subTest(text=text):
                with mock.patch.object(pobbin, "_open", side_effect=error):
                    with self.assertRaises(pobbin.FetchFailed) as caught:
                        pobbin.fetch("F8CiRC9KVADl")
                self.assertIn(text, str(caught.exception))
                self.assertEqual(caught.exception.status, 502)

    def test_non_200_is_fetch_failed(self):
        with mock.patch.object(pobbin, "_open", return_value=FakeResponse(b"x", status=503)):
            with self.assertRaises(pobbin.FetchFailed) as caught:
                pobbin.fetch("F8CiRC9KVADl")
        self.assertIn("503", str(caught.exception))

    def test_oversized_body_is_too_large(self):
        body = b"a" * (pobbin.MAX_CODE_BYTES + 5)
        with mock.patch.object(pobbin, "_open", return_value=FakeResponse(body)):
            with self.assertRaises(pobbin.TooLarge):
                pobbin.fetch("F8CiRC9KVADl")

    def test_redirect_to_another_host_is_refused(self):
        handler = pobbin._SameHostRedirect()
        with self.assertRaises(urllib.error.URLError):
            handler.redirect_request(mock.Mock(), None, 302, "Found", {}, "https://evil.example/x")


class ImportTests(unittest.TestCase):
    def test_import_link_returns_xml_and_saves_only_under_imports(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(pobbin, "_open", return_value=FakeResponse(FIXTURE.read_bytes())):
            result = pobbin.import_link("https://pobb.in/F8CiRC9KVADl", Path(tmp))
            saved = Path(result["path"])
            self.assertEqual(saved.parent, Path(tmp) / "imports")
            self.assertEqual(saved.name, "pobb-F8CiRC9KVADl.xml")
            self.assertEqual(saved.read_bytes().decode("utf-8"), result["xml"])
            self.assertEqual(result["id"], "F8CiRC9KVADl")
            self.assertGreater(result["xmlBytes"], 1000)
            self.assertEqual(sorted(p.name for p in Path(tmp).rglob("*") if p.is_file()), [saved.name])

    def test_bad_link_does_no_network_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(pobbin, "_open") as opened:
            with self.assertRaises(pobbin.BadLink):
                pobbin.import_link("https://evil.example/abcd", Path(tmp))
            opened.assert_not_called()
            self.assertEqual(list(Path(tmp).rglob("*")), [])

    def test_errors_carry_the_player_strings_and_statuses(self):
        self.assertEqual(pobbin.BadLink.status, 400)
        self.assertEqual(pobbin.Unreadable.status, 400)
        self.assertEqual(pobbin.TooLarge.status, 400)
        self.assertEqual(pobbin.FetchFailed.status, 502)


class SlowAndRedirectTests(unittest.TestCase):
    """GATE 2 M9 and L1: a slow server is cut off in total; a redirect must stay on https://pobb.in:443."""

    def test_trickling_server_is_cut_off_by_the_total_deadline(self):
        ticks = iter(range(0, 1000, 20))  # every clock reading is 20 s later
        slow = FakeResponse(b"a" * 100)
        with mock.patch.object(pobbin, "_open", return_value=slow):
            with self.assertRaises(pobbin.FetchFailed) as caught:
                pobbin.fetch("F8CiRC9KVADl", clock=lambda: next(ticks))
        self.assertIn("too slow", str(caught.exception))

    def test_fast_server_is_read_in_chunks_up_to_the_limit(self):
        body = b"b" * (pobbin.CHUNK_BYTES * 2 + 5)
        with mock.patch.object(pobbin, "_open", return_value=FakeResponse(body)):
            self.assertEqual(body.decode(), pobbin.fetch("F8CiRC9KVADl"))
        big = b"c" * (pobbin.MAX_CODE_BYTES + 10)
        with mock.patch.object(pobbin, "_open", return_value=FakeResponse(big)):
            with self.assertRaises(pobbin.TooLarge):
                pobbin.fetch("F8CiRC9KVADl")

    def test_redirects_off_https_443_or_with_a_login_are_refused(self):
        handler = pobbin._SameHostRedirect()
        request = urllib.request.Request("https://pobb.in/F8CiRC9KVADl/raw")
        for target in ("http://pobb.in/F8CiRC9KVADl/raw", "https://pobb.in:8080/x", "ftp://pobb.in/x",
                       "https://user@pobb.in/x", "https://user:pass@pobb.in/x", "https://evil.example/x"):
            with self.subTest(target=target):
                with self.assertRaises(urllib.error.URLError):
                    handler.redirect_request(request, None, 301, "moved", {}, target)
        for target in ("https://pobb.in/F8CiRC9KVADl/raw", "https://www.pobb.in:443/x"):
            with self.subTest(target=target):
                self.assertIsNotNone(handler.redirect_request(request, None, 301, "moved", {}, target))


if __name__ == "__main__":
    unittest.main()

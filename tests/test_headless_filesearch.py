import glob
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "engine"))

from pobhost import POB_DIR, PobEngine, _lua_str


class HeadlessFileSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp_dir.name)
        files = {
            "alpha.txt": b"alpha",
            "beta.txt": b"b" * 1234,
            "ünïcode.txt": b"utf8",
            "delta.txtx": b"not txt",
            "gamma.log": b"log",
            "data.zip.part0": b"part zero",
            "data.zip.part1": b"part one",
        }
        for name, content in files.items():
            (cls.root / name).write_bytes(content)
        (cls.root / "sub").mkdir()
        (cls.root / "sub" / "inner.txt").write_bytes(b"inner")

        cls.engine = PobEngine()
        cls.engine.run(
            """
            function fileSearchJSON(spec, dirs)
                local h = NewFileSearch(spec, dirs)
                if not h then return require("dkjson").encode(nil) end
                local entries = {}
                repeat
                    table.insert(entries, {
                        name = h:GetFileName(),
                        size = h:GetFileSize(),
                        mtime = h:GetFileModifiedTime(),
                    })
                until not h:NextFile()
                return require("dkjson").encode({
                    entries = entries,
                    exhausted = not h:NextFile(),
                })
            end
            """
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def search(self, spec, dirs=False):
        raw = self.engine.run(
            f"return fileSearchJSON({_lua_str(str(spec))}, {'true' if dirs else 'false'})"
        )
        return json.loads(raw)

    def test_no_match_and_missing_folder_return_nil(self):
        self.assertIsNone(self.search(self.root / "*.xyz"))
        self.assertIsNone(self.search(self.root / "nope" / "*.txt"))

    def test_exact_file_reports_name_size_and_modified_time(self):
        path = self.root / "beta.txt"
        result = self.search(path)
        self.assertEqual(len(result["entries"]), 1)
        entry = result["entries"][0]
        self.assertEqual(entry["name"], "beta.txt")
        self.assertEqual(entry["size"], path.stat().st_size)
        self.assertIsInstance(entry["size"], int)
        self.assertLessEqual(abs(entry["mtime"] - path.stat().st_mtime), 2)

    def test_txt_glob_uses_long_utf8_names_without_short_name_false_positives(self):
        result = self.search(self.root / "*.txt")
        actual = sorted(entry["name"] for entry in result["entries"])
        expected = sorted(Path(path).name for path in glob.glob(str(self.root / "*.txt")))
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(expected))
        self.assertNotIn("delta.txtx", actual)
        self.assertIn("ünïcode.txt", actual)

    def test_prefix_wildcard_matches_both_parts(self):
        result = self.search(self.root / "data.zip.part*")
        names = sorted(entry["name"] for entry in result["entries"])
        self.assertEqual(names, ["data.zip.part0", "data.zip.part1"])

    def test_directory_flag_filters_files_and_directories(self):
        directories = self.search(self.root / "*", dirs=True)
        self.assertEqual([entry["name"] for entry in directories["entries"]], ["sub"])
        files = self.search(self.root / "*")
        names = [entry["name"] for entry in files["entries"]]
        self.assertNotIn("sub", names)
        self.assertEqual(len(names), 7)

    def test_next_file_stays_false_after_all_entries(self):
        result = self.search(self.root / "*.txt")
        self.assertGreater(len(result["entries"]), 1)
        self.assertTrue(result["exhausted"])

    def test_backslash_spec_matches_forward_slash_spec(self):
        backslash_names = sorted(
            entry["name"] for entry in self.search(str(self.root / "*.txt"))["entries"]
        )
        forward_spec = self.root.as_posix() + "/*.txt"
        forward_names = sorted(
            entry["name"] for entry in self.search(forward_spec)["entries"]
        )
        self.assertEqual(backslash_names, forward_names)

    def test_exact_directory_respects_directory_flag(self):
        result = self.search(self.root / "sub", dirs=True)
        self.assertEqual([entry["name"] for entry in result["entries"]], ["sub"])
        self.assertIsNone(self.search(self.root / "sub"))

    def test_real_install_file_is_readable_by_absolute_and_relative_spec(self):
        path = POB_DIR / "Data" / "TimelessJewelData" / "MilitantFaith.zip"
        absolute = self.search(path)
        relative = self.search("Data/TimelessJewelData/MilitantFaith.zip")
        for result in (absolute, relative):
            self.assertEqual(len(result["entries"]), 1)
            self.assertEqual(result["entries"][0]["name"], "MilitantFaith.zip")
            self.assertEqual(result["entries"][0]["size"], os.stat(path).st_size)


if __name__ == "__main__":
    unittest.main()

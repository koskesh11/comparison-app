"""Python write guard for the PoB install folder (task 037).

PobEngine.__init__ chdirs into the PoB install, so a relative-path write from any Python code in the same
process would land there. pobhost installs one process-wide audit hook that refuses Python writes into every
guarded folder. A temp folder stands in for the install; one test uses the real engine."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "engine"))

import pobhost  # noqa: E402
from pobhost import POB_DIR, PobEngine, guard_pob_dir, unguard_pob_dir  # noqa: E402

REFUSED = "refused: write into the Path of Building install; use an absolute path outside it"
NO_SUCH = "__write_guard_probe_no_such_dir__"


class GuardTestCase(unittest.TestCase):
    def assertRefused(self, action, *args, **kwargs):
        with self.assertRaises(PermissionError) as caught:
            action(*args, **kwargs)
        self.assertEqual(str(caught.exception), REFUSED)


class TempDirGuardTests(GuardTestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.existing = self.root / "existing.txt"
        self.existing.write_text("hello", encoding="utf-8")
        self.other = tempfile.TemporaryDirectory()
        guard_pob_dir(self.root)

    def tearDown(self):
        unguard_pob_dir(self.root)   # before cleanup, or the cleanup itself is refused
        os.chdir(self.cwd)
        self.temp.cleanup()
        self.other.cleanup()

    def test_relative_write_after_chdir_is_refused(self):
        os.chdir(self.root)
        self.assertRefused(open, "relative.txt", "w")
        self.assertFalse((self.root / "relative.txt").exists())

    def test_absolute_write_inside_is_refused(self):
        self.assertRefused(open, self.root / "absolute.txt", "w")
        self.assertRefused(open, str(self.root / "absolute.txt").upper(), "a")   # case-insensitive
        self.assertRefused(open, os.fsencode(self.root / "absolute.txt"), "xb")
        self.assertRefused(open, self.existing, "r+")
        self.assertRefused((self.root / "absolute.txt").write_text, "x")
        self.assertFalse((self.root / "absolute.txt").exists())

    def test_os_level_writes_inside_are_refused(self):
        target = str(self.root / "low.txt")
        self.assertRefused(os.open, target, os.O_WRONLY | os.O_CREAT)
        self.assertRefused(os.open, str(self.existing), os.O_RDWR)
        self.assertRefused(os.remove, self.existing)
        self.assertRefused(os.mkdir, self.root / "sub")
        self.assertRefused(os.rename, self.existing, self.root / "moved.txt")
        self.assertRefused(os.replace, self.existing, self.root / "moved.txt")
        self.assertRefused(os.rename, self.existing, Path(self.other.name) / "moved.txt")
        self.assertTrue(self.existing.exists())
        self.assertFalse((self.root / "sub").exists())

    def test_rmdir_inside_is_refused(self):
        unguard_pob_dir(self.root)
        (self.root / "empty").mkdir()
        guard_pob_dir(self.root)
        self.assertRefused(os.rmdir, self.root / "empty")
        self.assertTrue((self.root / "empty").is_dir())

    def test_read_inside_is_allowed(self):
        self.assertEqual(self.existing.read_text(encoding="utf-8"), "hello")
        os.chdir(self.root)
        with open("existing.txt", "rb") as handle:
            self.assertEqual(handle.read(), b"hello")
        fd = os.open("existing.txt", os.O_RDONLY)
        os.close(fd)

    def test_write_to_another_folder_is_allowed(self):
        os.chdir(self.root)
        target = Path(self.other.name) / "out.txt"
        target.write_text("ok", encoding="utf-8")
        os.mkdir(Path(self.other.name) / "sub")
        os.replace(target, Path(self.other.name) / "sub" / "out.txt")
        os.remove(Path(self.other.name) / "sub" / "out.txt")
        os.rmdir(Path(self.other.name) / "sub")
        self.assertEqual(os.listdir(self.other.name), [])

    def test_sibling_with_common_prefix_is_not_guarded(self):
        sibling = Path(str(self.root) + "-sibling")
        sibling.mkdir()
        try:
            (sibling / "x.txt").write_text("ok", encoding="utf-8")
        finally:
            (sibling / "x.txt").unlink()
            sibling.rmdir()

    def test_fd_open_is_ignored(self):
        fd = os.open(Path(self.other.name) / "fd.txt", os.O_WRONLY | os.O_CREAT)
        with open(fd, "w") as handle:
            handle.write("ok")

    def test_hook_installs_once(self):
        guard_pob_dir(self.root)
        guard_pob_dir(self.root)
        self.assertTrue(pobhost._guard_installed)


@unittest.skipUnless((POB_DIR / "Launch.lua").is_file(), "Path of Building is not installed")
class RealEngineGuardTests(GuardTestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self):
        os.chdir(self.cwd)
        self.temp.cleanup()

    def test_relative_write_after_engine_init_is_refused(self):
        temp = Path(self.temp.name)
        with PobEngine(userdata_dir=temp / "userdata", autobuilder_dir=temp / "AutoBuilder"):
            self.assertEqual(os.path.normcase(os.getcwd()), os.path.normcase(str(POB_DIR)))
            # a folder that does not exist: a broken guard fails with FileNotFoundError, not a stray file
            self.assertRefused(open, f"{NO_SUCH}/x.txt", "w")
            self.assertFalse((POB_DIR / NO_SUCH).exists())
            with open("Launch.lua", "rb") as handle:
                self.assertTrue(handle.read(1))


if __name__ == "__main__":
    unittest.main()

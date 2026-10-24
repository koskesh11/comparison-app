"""Write sandbox of the headless PoB Lua state (task 025): refused vs allowed writes, on a real engine.

Refusal probes use paths in a folder that does not exist, so a broken sandbox fails the test with an OS
error instead of writing into the PoB install or the user builds."""
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "engine"))

import api_errors
import optimize
from pobhost import AUTOBUILDER_DIR, POB_DIR, LuaError, PobEngine, _lua_str

NO_SUCH = "__sandbox_probe_no_such_dir__"
BUILDS_DIR = Path.home() / "Documents" / "Path of Building" / "Builds"


def lua_path(path: Path) -> str:
    return _lua_str(path.as_posix())


class WriteSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.autobuilder = Path(cls.temp.name) / "Builds" / "AutoBuilder"
        cls.autobuilder.mkdir(parents=True)
        cls.engine = PobEngine(userdata_dir=Path(cls.temp.name) / "userdata", autobuilder_dir=cls.autobuilder)

    @classmethod
    def tearDownClass(cls):
        cls.engine.close()
        cls.temp.cleanup()

    def refused(self, code: str) -> str:
        with self.assertRaises(LuaError) as caught:
            self.engine.run(code)
        message = str(caught.exception)
        self.assertIn("write refused", message)
        self.assertIn("write sandbox (task 025)", message)
        return message

    def open_for_write(self, path: Path, mode: str = "w") -> str:
        return f"return io.open({lua_path(path)}, '{mode}')"

    def allowed(self, path: str) -> str:
        return self.engine.run(f"return tostring(WriteSandbox.allowed({_lua_str(path)}))")

    def test_write_into_pob_install_is_refused_and_names_the_path(self):
        target = POB_DIR / NO_SUCH / "x.txt"
        for mode in ("w", "wb", "a", "r+", "w+b"):
            message = self.refused(self.open_for_write(target, mode))
            self.assertIn(target.as_posix(), message)

    def test_relative_write_resolves_against_the_pob_dir(self):
        self.refused(f"return io.open('{NO_SUCH}/x.txt', 'w')")
        self.refused("return io.open('Data/ModCache.lua', 'w')")

    def test_write_into_user_builds_is_refused(self):
        self.refused(self.open_for_write(BUILDS_DIR / "3.29" / NO_SUCH / "x.xml"))
        self.refused(self.open_for_write(BUILDS_DIR / NO_SUCH / "x.xml"))

    def test_path_traversal_out_of_autobuilder_is_refused(self):
        self.refused(self.open_for_write(self.autobuilder / ".." / NO_SUCH / "x.xml"))
        base = _lua_str(self.autobuilder.as_posix())
        self.refused(f"return io.open({base} .. '\\\\..\\\\{NO_SUCH}\\\\x', 'w')")
        self.refused(self.open_for_write(self.autobuilder / "sub" / ".." / ".." / NO_SUCH / "x.xml"))

    def test_prefix_and_lookalike_paths_are_refused(self):
        base = self.autobuilder.as_posix()
        self.refused(self.open_for_write(self.autobuilder.parent / "AutoBuilder2" / NO_SUCH / "x.xml"))
        self.refused(f"return io.open({_lua_str(base + '.')} .. '/{NO_SUCH}/x', 'w')")
        self.refused(f"return io.open({_lua_str(base)} .. ' /{NO_SUCH}/x', 'w')")
        self.refused(f"return io.open({_lua_str(base)} .. '/x.xml:stream', 'w')")
        self.refused("return io.open('C:foo', 'w')")
        self.refused("return io.open('//server/share/x', 'w')")

    def test_autobuilder_save_is_allowed_case_insensitive_and_readable_back(self):
        target = self.autobuilder / "saved build.xml"
        self.engine.run(f"local f = assert(io.open({lua_path(target)}, 'wb')); "
                        "f:write('<PathOfBuilding/>'); f:close()")
        self.assertEqual(target.read_text(), "<PathOfBuilding/>")
        shouting = str(target).upper().replace("\\", "\\\\")
        self.engine.run(f"local f = assert(io.open('{shouting}', 'ab')); f:write('!'); f:close()")
        self.assertEqual(target.read_text(), "<PathOfBuilding/>!")
        base = _lua_str(self.autobuilder.as_posix())
        self.engine.run(f"assert(io.open({base} .. '/./sub/../again.xml', 'w')):close()")
        self.assertTrue((self.autobuilder / "again.xml").is_file())

    def test_reads_stay_unrestricted(self):
        launch = POB_DIR / "Launch.lua"
        size = self.engine.run(f"local f = assert(io.open({lua_path(launch)}, 'rb')); "
                               "local n = #f:read('*a'); f:close(); return tostring(n)")
        self.assertGreater(int(size), 100)
        self.engine.run(f"for _ in io.lines({lua_path(launch)}) do break end")

    def test_timeless_cache_allows_only_flat_bin_files(self):
        timeless = (POB_DIR / "Data" / "TimelessJewelData").as_posix()
        self.assertEqual(self.allowed(f"{timeless}/GloriousVanity.bin"), "true")
        self.assertEqual(self.allowed(f"{timeless}/glorioUSvanity.BIN"), "true")
        self.assertEqual(self.allowed("Data/TimelessJewelData/Elegant Hubris.bin"), "true")  # relative to PoB dir
        for bad in (f"{timeless}/GloriousVanity.zip", f"{timeless}/NodeIndexMapping.lua", f"{timeless}/.bin",
                    f"{timeless}/sub/x.bin", f"{timeless}/../x.bin", f"{timeless}x/x.bin",
                    f"{timeless}/x.bin.exe", timeless):
            self.assertEqual(self.allowed(bad), "false", bad)

    def test_timeless_cache_non_bin_open_for_write_is_refused(self):
        # The allowed .bin case is checked through WriteSandbox.allowed above: a real open would create a file in
        # the PoB install. Only the refusal side goes through io.open.
        self.refused("return io.open('Data/TimelessJewelData/x.zip', 'wb')")
        self.refused("return io.open('Data/TimelessJewelData/sub/x.bin', 'wb')")

    def test_remove_rename_and_helpers_are_refused(self):
        self.refused(f"return os.remove({lua_path(POB_DIR / NO_SUCH / 'x')})")
        self.refused(f"return os.remove({lua_path(BUILDS_DIR / NO_SUCH / 'x.xml')})")
        inside = self.autobuilder / "inside.xml"
        inside.write_text("x")
        self.refused(f"return os.rename({lua_path(inside)}, {lua_path(POB_DIR / NO_SUCH / 'y')})")
        self.refused(f"return os.rename({lua_path(BUILDS_DIR / NO_SUCH / 'a')}, {lua_path(inside)})")
        self.assertTrue(inside.is_file())
        self.refused(f"io.output({lua_path(POB_DIR / NO_SUCH / 'out.txt')})")
        self.refused(f"RemoveDir({lua_path(POB_DIR / 'TreeData')}, true)")
        self.refused(f"MakeDir({lua_path(POB_DIR / NO_SUCH)})")
        self.refused("return io.popen('cmd /c echo hi > x.txt')")
        self.refused("return os.execute('cmd /c echo hi > x.txt')")

    def test_remove_and_rename_inside_autobuilder_work(self):
        source = self.autobuilder / "old.xml"
        source.write_text("x")
        renamed = self.autobuilder / "new.xml"
        self.engine.run(f"assert(os.rename({lua_path(source)}, {lua_path(renamed)}))")
        self.assertTrue(renamed.is_file())
        self.engine.run(f"assert(os.remove({lua_path(renamed)}))")
        self.assertFalse(renamed.exists())

    def test_makedir_of_an_existing_pob_folder_is_a_noop(self):
        self.engine.run("MakeDir('TreeData')")  # PoB calls this on every tree load; the folder exists

    def test_error_reaches_the_user_as_a_sanitized_engine_error(self):
        with self.assertRaises(LuaError) as caught:
            self.engine.run(self.open_for_write(POB_DIR / NO_SUCH / "x.txt"))
        status, body = api_errors.classify(caught.exception)
        self.assertEqual((status, body["kind"]), (500, "EngineError"))
        self.assertTrue(body["error"].startswith("engine error: write refused: io.open(w)"), body["error"])
        self.assertNotIn("traceback", body["error"])
        self.assertNotIn("\n", body["error"])

    def test_default_autobuilder_dir_is_the_documents_folder(self):
        self.assertEqual(AUTOBUILDER_DIR, BUILDS_DIR / "AutoBuilder")
        self.assertEqual(optimize.DEFAULT_OUT_DIR, AUTOBUILDER_DIR)


if __name__ == "__main__":
    unittest.main()

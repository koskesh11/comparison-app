"""Lifecycle and reuse tests for Path of Building engines."""

import ctypes
import hashlib
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

from audit import Auditor  # noqa: E402
from engine_pool import EnginePool  # noqa: E402
from optimize import StaleAudit, check_source_fresh  # noqa: E402
from pobhost import ENGINE_DIR, LuaError, PobEngine  # noqa: E402

GOLDEN = json.loads(gc.GOLDEN_PATH.read_text(encoding="utf-8"))
TOLERANCES = GOLDEN["tolerances"]
_install_before: dict = {}


def setUpModule():
    _install_before.update(gc.install_snapshot())


def tearDownModule():
    changes = gc.install_diff(_install_before, gc.install_snapshot())
    if changes:
        raise AssertionError("PoB install changed:\n  " + "\n  ".join(changes))


def _working_set() -> int | None:
    if sys.platform != "win32":
        return None

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = ctypes.c_void_p
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), ctypes.c_ulong]
    get_process_memory_info.restype = ctypes.c_int
    process = get_current_process()
    ok = get_process_memory_info(process, ctypes.byref(counters), counters.cb)
    if not ok:
        raise ctypes.WinError()
    return counters.WorkingSetSize


class FakeEngine:
    def __init__(self, slot: int):
        self.slot = slot
        self.closed = False

    def close(self):
        self.closed = True


class EnginePoolUnitTests(unittest.TestCase):
    def test_lease_returns_same_engine_after_success(self):
        made = []

        def factory(slot):
            engine = FakeEngine(slot)
            made.append(engine)
            return engine

        pool = EnginePool(size=1, factory=factory)
        self.addCleanup(pool.close)
        with pool.lease() as first:
            self.assertEqual(first.slot, 0)
        with pool.lease() as second:
            self.assertIs(second, first)
        self.assertEqual(made, [first])

    def test_body_exception_closes_and_replaces_engine(self):
        made = []

        def factory(slot):
            engine = FakeEngine(slot)
            made.append(engine)
            return engine

        pool = EnginePool(size=1, factory=factory)
        self.addCleanup(pool.close)
        with self.assertRaisesRegex(RuntimeError, "body failed"):
            with pool.lease() as old:
                raise RuntimeError("body failed")
        self.assertTrue(old.closed)
        with pool.lease() as replacement:
            self.assertIsNot(replacement, old)
            self.assertFalse(replacement.closed)

    def test_failed_replacement_leaves_retryable_slot(self):
        calls = 0

        def factory(slot):
            nonlocal calls
            calls += 1
            if calls in (2, 3):
                raise LookupError(f"factory failed {calls}")
            return FakeEngine(slot)

        pool = EnginePool(size=1, factory=factory)
        self.addCleanup(pool.close)
        with self.assertRaisesRegex(RuntimeError, "original"):
            with pool.lease():
                raise RuntimeError("original")
        with self.assertRaisesRegex(LookupError, "factory failed 3"):
            with pool.lease():
                pass
        with pool.lease() as recovered:
            self.assertFalse(recovered.closed)
        self.assertEqual(calls, 4)

    def test_close_with_checked_out_engine_closes_it_on_return(self):
        pool = EnginePool(size=1, factory=FakeEngine)
        with pool.lease() as engine:
            pool.close()
            self.assertFalse(engine.closed)
        self.assertTrue(engine.closed)
        pool.close()
        with self.assertRaisesRegex(RuntimeError, "engine pool is closed"):
            with pool.lease():
                pass

    def test_exception_after_close_does_not_create_replacement(self):
        made = []

        def factory(slot):
            engine = FakeEngine(slot)
            made.append(engine)
            return engine

        pool = EnginePool(size=1, factory=factory)
        with self.assertRaisesRegex(RuntimeError, "body failed"):
            with pool.lease():
                pool.close()
                raise RuntimeError("body failed")
        self.assertEqual(len(made), 1)
        self.assertTrue(made[0].closed)

    def test_four_threads_share_two_engines(self):
        pool = EnginePool(size=2, factory=FakeEngine)
        self.addCleanup(pool.close)
        barrier = threading.Barrier(4)
        active = 0
        peak = 0
        completed = []
        lock = threading.Lock()

        def worker(index):
            nonlocal active, peak
            barrier.wait()
            with pool.lease():
                with lock:
                    active += 1
                    peak = max(peak, active)
                threading.Event().wait(0.05)
                with lock:
                    active -= 1
                    completed.append(index)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(sorted(completed), list(range(4)))
        self.assertEqual(peak, 2)


class EngineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.saved_cwd = os.getcwd()
        self.addCleanup(os.chdir, self.saved_cwd)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def factory(self, made):
        root = Path(self.temp_dir.name)

        def create(slot):
            engine = PobEngine(userdata_dir=root / f"engine-{slot}")
            made.append(engine)
            return engine

        return create

    def assert_golden(self, expected, actual):
        differences = gc.diff(expected, actual, TOLERANCES)
        self.assertFalse(differences, "\n  ".join(differences))

    def test_engine_pool_reuse_and_close(self):
        made = []
        with gc.pob_cwd():
            pool = EnginePool(size=2, factory=self.factory(made))
            self.addCleanup(pool.close)
            with pool.lease() as engine:
                lua_kb = []
                working_sets = []
                build = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
                for _ in range(20):
                    engine.load_build(build)
                    engine.run("collectgarbage(); collectgarbage()")
                    lua_kb.append(float(engine.run("return collectgarbage('count')")))
                    working_sets.append(_working_set())

            lua_limit = lua_kb[2] * 1.10
            message = f"Lua KiB load 3={lua_kb[2]:.1f}, load 20={lua_kb[-1]:.1f}, limit={lua_limit:.1f}"
            self.assertLessEqual(lua_kb[-1], lua_limit, message)
            if working_sets[-1] is not None:
                ws_limit = working_sets[2] * 1.25
                message += (f"; working set load 3={working_sets[2] / 1024 / 1024:.1f} MiB, "
                            f"load 20={working_sets[-1] / 1024 / 1024:.1f} MiB, "
                            f"limit={ws_limit / 1024 / 1024:.1f} MiB")
                self.assertLessEqual(working_sets[-1], ws_limit, message)

            pool.close()
            self.assertTrue(all(engine.closed for engine in made))
            with self.assertRaisesRegex(LuaError, "engine is closed"):
                made[0].run("return 1")
            pool.close()
            with self.assertRaisesRegex(RuntimeError, "engine pool is closed"):
                with pool.lease():
                    pass
        print(message)

    def test_engine_reload_after_error(self):
        made = []
        with gc.pob_cwd():
            pool = EnginePool(size=2, factory=self.factory(made))
            self.addCleanup(pool.close)
            with self.assertRaises(LuaError) as caught:
                with pool.lease() as old:
                    old.run("error('boom')")
            self.assertIn("boom", str(caught.exception))
            self.assertIn("stack traceback", str(caught.exception))
            self.assertTrue(old.closed)

            leased = []
            with pool.lease() as first:
                leased.append(first)
                with pool.lease() as second:
                    leased.append(second)
            self.assertNotIn(old, leased)
            self.assertTrue(all(not engine.closed for engine in leased))
            summary = leased[0].load_build(gc.build_path(gc.AUDIT_BUILDS["EK"]["file"]))
            self.assert_golden(GOLDEN["audit"]["EK"]["snapshot"]["summary"], summary)

            with self.assertRaisesRegex(RuntimeError, "non-Lua"):
                with pool.lease() as before_runtime:
                    raise RuntimeError("non-Lua")
            self.assertTrue(before_runtime.closed)
            with pool.lease() as after_runtime:
                self.assertIsNot(after_runtime, before_runtime)

    def test_reused_engine_matches_golden(self):
        made = []
        with gc.pob_cwd():
            pool = EnginePool(size=1, factory=self.factory(made))
            self.addCleanup(pool.close)
            with pool.lease() as engine:
                for key in ("EK", "Worb", "EK"):
                    settings = gc.AUDIT_BUILDS[key]
                    auditor = gc.offline_auditor(gc.build_path(settings["file"]), settings, engine=engine)
                    auditor.engine.run(gc.LUA_HELPERS)
                    self.assert_golden(GOLDEN["audit"][key]["snapshot"], gc.audit_snapshot(auditor))
                    self.assertFalse(engine.closed)

    def test_default_userdata_engine_still_works(self):
        build = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
        with gc.pob_cwd():
            with PobEngine() as engine:
                self.assertEqual(engine.run("return GetUserPath()"), (ENGINE_DIR / "userdata").as_posix())
                self.assert_golden(GOLDEN["audit"]["EK"]["snapshot"]["summary"], engine.load_build(build))
                engine.run("debug = nil")
                with self.assertRaises(LuaError) as caught:
                    engine.run("error('still traced')")
                self.assertIn("still traced", str(caught.exception))
                self.assertIn("stack traceback", str(caught.exception))
                self.assertEqual(engine.run("return 9"), "9")
            self.assertTrue(engine.closed)

            custom = Path(self.temp_dir.name) / "custom-userdata"
            with PobEngine(userdata_dir=custom) as engine:
                self.assertEqual(engine.run("return GetUserPath()"), custom.as_posix())
            self.assertTrue(engine.closed)


class SourceFreshnessTests(unittest.TestCase):
    def test_check_source_fresh(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "build.xml"
            path.write_bytes(b"original")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            check_source_fresh(path, digest)

            path.write_bytes(b"changed")
            with self.assertRaisesRegex(StaleAudit, "re-run the audit"):
                check_source_fresh(path, digest)

            path.unlink()
            with self.assertRaisesRegex(StaleAudit, "re-run the audit"):
                check_source_fresh(path, digest)


if __name__ == "__main__":
    unittest.main()

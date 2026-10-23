"""Tests for the read-only PreToolUse guard (tools/hooks/guard_readonly.py)."""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

GUARD_PATH = Path(__file__).resolve().parent.parent / "tools" / "hooks" / "guard_readonly.py"
spec = importlib.util.spec_from_file_location("guard_readonly", GUARD_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

INSTALL = str(guard.POB_INSTALL)
BUILDS = str(guard.BUILDS)
AUTOBUILDER = str(guard.ALLOWED)


def write(path: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path, "content": "x"}}


def bash(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


class FileToolTests(unittest.TestCase):
    def test_blocks_write_into_install(self):
        self.assertIsNotNone(guard.decide(write(INSTALL + r"\Data\x.lua")))

    def test_blocks_edit_of_user_build(self):
        payload = {"tool_name": "Edit", "tool_input": {"file_path": BUILDS + r"\3.29\Worb.xml"}}
        self.assertIsNotNone(guard.decide(payload))

    def test_allows_autobuilder_output(self):
        self.assertIsNone(guard.decide(write(AUTOBUILDER + r"\New build.xml")))

    def test_allows_project_files(self):
        self.assertIsNone(guard.decide(write(str(GUARD_PATH.parent / "other.py"))))

    def test_git_bash_style_path_is_recognised(self):
        path = "/" + INSTALL[0].lower() + INSTALL[2:].replace("\\", "/") + "/Launch.lua"
        self.assertIsNotNone(guard.decide(write(path)))


class ShellToolTests(unittest.TestCase):
    def test_blocks_redirect_into_install(self):
        self.assertIsNotNone(guard.decide(bash('echo hi > "$APPDATA/Path of Building Community/x.txt"')))

    def test_blocks_copy_into_builds(self):
        self.assertIsNotNone(guard.decide(bash(f'cp a.xml "{BUILDS}/3.29/a.xml"')))

    def test_blocks_powershell_set_content(self):
        payload = {"tool_name": "PowerShell",
                   "tool_input": {"command": 'Set-Content "$env:APPDATA\\Path of Building Community\\a.txt" x'}}
        self.assertIsNotNone(guard.decide(payload))

    def test_allows_reading_install(self):
        self.assertIsNone(guard.decide(bash('grep -n Inner "$APPDATA/Path of Building Community/Data/x.lua"')))

    def test_allows_fd_duplication_without_write(self):
        self.assertIsNone(guard.decide(bash('ls "$APPDATA/Path of Building Community" 2>&1 | head')))

    def test_allows_writing_autobuilder(self):
        self.assertIsNone(guard.decide(bash(f'cp out.xml "{AUTOBUILDER}/out.xml"')))

    def test_allows_unrelated_writes(self):
        self.assertIsNone(guard.decide(bash("echo hi > /tmp/x.txt")))


class ProcessTests(unittest.TestCase):
    def run_hook(self, payload: dict) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(GUARD_PATH)], input=json.dumps(payload),
                              capture_output=True, text=True, timeout=30)

    def test_exit_2_with_reason_when_blocked(self):
        result = self.run_hook(write(INSTALL + r"\x.txt"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Blocked", result.stderr)

    def test_exit_0_when_allowed(self):
        self.assertEqual(self.run_hook(bash("ls")).returncode, 0)

    def test_unreadable_input_does_not_block(self):
        result = subprocess.run([sys.executable, str(GUARD_PATH)], input="not json",
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

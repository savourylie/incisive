"""Regression tests for install.sh. Every run uses a throwaway HOME.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "install.sh"
SKILL_SRC = REPO / "skills" / "incisive"


class InstallTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)

    def install(self, *args):
        env = dict(os.environ, HOME=str(self.home))
        return subprocess.run(["bash", str(INSTALL), *args], capture_output=True, text=True, env=env)

    def dest(self, root=".claude"):
        return self.home / root / "skills" / "incisive"

    def test_default_target_is_claude_symlink(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.dest().is_symlink())
        self.assertEqual(self.dest().resolve(), SKILL_SRC.resolve())

    def test_copy_flag_alone_copies_to_default_target(self):
        result = self.install("--copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.dest().is_symlink())
        self.assertTrue((self.dest() / "SKILL.md").is_file())

    def test_copy_flag_may_precede_the_target(self):
        result = self.install("--copy", "cursor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.dest(".cursor") / "SKILL.md").is_file())
        self.assertFalse(self.dest(".cursor").is_symlink())

    def test_unknown_argument_prints_usage_and_fails(self):
        result = self.install("claud")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage", result.stdout + result.stderr)
        self.assertFalse((self.home / ".claude").exists())

    def test_unrelated_existing_directory_is_not_deleted(self):
        self.dest().mkdir(parents=True)
        keep = self.dest() / "notes.txt"
        keep.write_text("mine")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(keep.read_text(), "mine")

    def test_force_replaces_unrelated_existing_directory(self):
        self.dest().mkdir(parents=True)
        (self.dest() / "notes.txt").write_text("mine")
        result = self.install("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.dest().is_symlink())

    def test_previous_copy_install_is_replaced_without_force(self):
        self.assertEqual(self.install("--copy").returncode, 0)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.dest().is_symlink())

    def test_previous_symlink_install_is_replaced_without_force(self):
        self.assertEqual(self.install().returncode, 0)
        result = self.install("--copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.dest().is_symlink())
        self.assertTrue((SKILL_SRC / "SKILL.md").is_file(), "replacing a symlink must not touch the repo")

    def test_all_skips_tools_that_are_not_installed(self):
        (self.home / ".claude").mkdir()
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.dest().is_symlink())
        self.assertFalse((self.home / ".cursor").exists())
        self.assertFalse((self.home / ".codex").exists())


if __name__ == "__main__":
    unittest.main()

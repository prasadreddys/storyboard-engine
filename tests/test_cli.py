import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples")


def run_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "storyboard", *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )


class TestCliE2E(unittest.TestCase):
    def test_build_then_check_matches_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(
                "build",
                "--script", os.path.join(EXAMPLES, "script.md"),
                "--character", os.path.join(EXAMPLES, "character.json"),
                "--out", tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("4 scenes, 24.0 seconds total", result.stdout)
            with open(os.path.join(tmp, "storyboard.json"), encoding="utf-8") as handle:
                board = json.load(handle)
            with open(
                os.path.join(EXAMPLES, "expected-storyboard.json"), encoding="utf-8"
            ) as handle:
                expected = json.load(handle)
            board.pop("character_traits", None)
            self.assertEqual(board, expected)
            md_path = os.path.join(tmp, "storyboard.md")
            self.assertTrue(os.path.exists(md_path))
            with open(md_path, encoding="utf-8") as handle:
                md = handle.read()
            self.assertIn("Scene 3: The Chase", md)
            self.assertIn("close-up", md)

            check = run_cli("check", "--storyboard", os.path.join(tmp, "storyboard.json"))
            self.assertEqual(check.returncode, 0, check.stdout)
            self.assertIn("overall: PASS", check.stdout)

    def test_check_fails_on_tampered_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(
                "build",
                "--script", os.path.join(EXAMPLES, "script.md"),
                "--character", os.path.join(EXAMPLES, "character.json"),
                "--out", tmp,
            )
            path = os.path.join(tmp, "storyboard.json")
            with open(path, encoding="utf-8") as handle:
                board = json.load(handle)
            board["scenes"][1]["visual_prompt"] = board["scenes"][1][
                "visual_prompt"
            ].replace("a teal cloak with gold stitching", "a red cloak")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(board, handle, indent=2)
            check = run_cli("check", "--storyboard", path)
            self.assertEqual(check.returncode, 1)
            self.assertIn("overall: FAIL", check.stdout)

    def test_build_rejects_bad_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.md")
            with open(bad, "w", encoding="utf-8") as handle:
                handle.write("## Scene 1: Silent\nVisual: Nothing.\n")
            result = run_cli(
                "build",
                "--script", bad,
                "--character", os.path.join(EXAMPLES, "character.json"),
                "--out", tmp,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("no Narration", result.stderr)

    def test_init_writes_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("init", "--dir", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(os.path.exists(os.path.join(tmp, "script.md")))
            with open(os.path.join(tmp, "character.json"), encoding="utf-8") as handle:
                character = json.load(handle)
            self.assertTrue(character["traits"])


if __name__ == "__main__":
    unittest.main()

import unittest

from storyboard.script import ScriptError, parse_script


class TestParseScript(unittest.TestCase):
    def test_two_scenes_parsed(self):
        scenes = parse_script(
            "## Scene 1: Opening\nNarration: Hello world.\nVisual: A door.\n\n"
            "## Scene 2: Second\nNarration: More words here.\n"
        )
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0].number, 1)
        self.assertEqual(scenes[0].title, "Opening")
        self.assertEqual(scenes[0].narration, "Hello world.")
        self.assertEqual(scenes[0].visual, "A door.")
        self.assertEqual(scenes[1].title, "Second")

    def test_explicit_duration_parsed(self):
        scenes = parse_script(
            "## Scene 1: Timed\nNarration: Some words.\nDuration: 7.5\n"
        )
        self.assertEqual(scenes[0].duration, 7.5)

    def test_no_duration_is_none(self):
        scenes = parse_script("## Scene 1: Free\nNarration: Some words.\n")
        self.assertIsNone(scenes[0].duration)

    def test_plain_line_continues_narration(self):
        scenes = parse_script(
            "## Scene 1: Long\nNarration: First part.\nSecond part here.\n"
        )
        self.assertEqual(scenes[0].narration, "First part. Second part here.")

    def test_missing_narration_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script("## Scene 1: Silent\nVisual: Nothing said.\n")

    def test_empty_script_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script("")

    def test_no_headings_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script("Narration: Words with no scene.\n")

    def test_content_before_first_heading_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script("Some intro text.\n## Scene 1: Start\nNarration: Go.\n")

    def test_bad_duration_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script(
                "## Scene 1: Bad\nNarration: Words.\nDuration: soon\n"
            )

    def test_zero_duration_rejected(self):
        with self.assertRaises(ScriptError):
            parse_script(
                "## Scene 1: Zero\nNarration: Words.\nDuration: 0\n"
            )


if __name__ == "__main__":
    unittest.main()

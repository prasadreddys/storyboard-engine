import copy
import unittest

from storyboard.character import validate_character
from storyboard.script import Scene, parse_script
from storyboard.storyboard import (
    assign_shot_type,
    build_storyboard,
    build_visual_prompt,
    check_storyboard,
)

CHARACTER = validate_character({
    "name": "Mara",
    "traits": ["curly red hair", "a brass compass"],
    "palette": ["#0F766E"],
    "style": "flat vector",
    "voice": "calm narrator",
})


def scene(number, narration, title="T"):
    return Scene(number, title, narration=narration)


class TestShotType(unittest.TestCase):
    def test_first_scene_is_wide(self):
        self.assertEqual(assign_shot_type(scene(1, "She runs fast."), 0), "wide")

    def test_action_verb_is_close_up(self):
        self.assertEqual(
            assign_shot_type(scene(2, "She runs through the market."), 1),
            "close-up",
        )

    def test_dialogue_is_medium(self):
        self.assertEqual(
            assign_shot_type(scene(2, "Is this the real map?"), 1), "medium"
        )

    def test_plain_narration_is_medium(self):
        self.assertEqual(
            assign_shot_type(scene(2, "She looks at the map quietly."), 1),
            "medium",
        )


class TestBuild(unittest.TestCase):
    def test_every_prompt_contains_every_trait_verbatim(self):
        scenes = parse_script(
            "## Scene 1: A\nNarration: She looks at the map.\n\n"
            "## Scene 2: B\nNarration: She runs away.\n"
        )
        board = build_storyboard(scenes, CHARACTER)
        for shot in board["scenes"]:
            for trait in CHARACTER["traits"]:
                self.assertIn(trait, shot["visual_prompt"])
            self.assertTrue(shot["continuity_ok"])

    def test_prompt_includes_palette_and_style(self):
        prompt = build_visual_prompt(CHARACTER, scene(1, "Words."))
        self.assertIn("#0F766E", prompt)
        self.assertIn("flat vector", prompt)
        self.assertIn("Mara", prompt)

    def test_totals(self):
        scenes = parse_script(
            "## Scene 1: A\nNarration: " + " ".join(["word"] * 15) + "\n\n"
            "## Scene 2: B\nNarration: " + " ".join(["word"] * 13) + "\n"
            "Duration: 8\n"
        )
        board = build_storyboard(scenes, CHARACTER)
        self.assertEqual(board["scene_count"], 2)
        self.assertEqual(board["total_narration_seconds"], 11.2)
        self.assertEqual(board["total_seconds"], 14.0)

    def test_first_scene_wide_others_by_rule(self):
        scenes = parse_script(
            "## Scene 1: A\nNarration: She runs fast.\n\n"
            "## Scene 2: B\nNarration: She runs fast.\n\n"
            "## Scene 3: C\nNarration: She looks quietly.\n"
        )
        board = build_storyboard(scenes, CHARACTER)
        self.assertEqual(
            [s["shot_type"] for s in board["scenes"]],
            ["wide", "close-up", "medium"],
        )


class TestCheck(unittest.TestCase):
    def _good_board(self):
        scenes = parse_script(
            "## Scene 1: A\nNarration: She looks at the map.\n"
        )
        board = build_storyboard(scenes, CHARACTER)
        board["character_traits"] = CHARACTER["traits"]
        return board

    def test_check_passes_on_good_board(self):
        passed, checks = check_storyboard(self._good_board())
        self.assertTrue(passed)
        self.assertTrue(all(c["passed"] for c in checks))

    def test_check_fails_when_trait_removed(self):
        board = self._good_board()
        board["scenes"][0]["visual_prompt"] = board["scenes"][0][
            "visual_prompt"
        ].replace("curly red hair", "short hair")
        passed, checks = check_storyboard(board)
        self.assertFalse(passed)
        failed = [c for c in checks if not c["passed"]]
        self.assertEqual(failed[0]["check"], "traits_verbatim")

    def test_check_fails_on_bad_timing(self):
        board = self._good_board()
        board["scenes"][0]["narration_seconds"] = 99.9
        passed, _ = check_storyboard(board)
        self.assertFalse(passed)

    def test_check_fails_on_bad_total(self):
        board = self._good_board()
        board["total_seconds"] = 99.9
        passed, _ = check_storyboard(board)
        self.assertFalse(passed)

    def test_check_with_character_arg(self):
        passed, _ = check_storyboard(self._good_board(), CHARACTER)
        self.assertTrue(passed)


if __name__ == "__main__":
    unittest.main()

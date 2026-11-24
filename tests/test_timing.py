import unittest

from storyboard.script import Scene
from storyboard.timing import (
    MIN_SCENE_SECONDS,
    count_words,
    narration_seconds,
    scene_duration,
)


class TestTiming(unittest.TestCase):
    def test_count_words(self):
        self.assertEqual(count_words("one two three"), 3)
        self.assertEqual(count_words("  spaced   out  "), 2)
        self.assertEqual(count_words(""), 0)

    def test_narration_seconds_150_wpm(self):
        # 15 words at 150 wpm = 15 * 0.4 = 6.0s
        self.assertEqual(narration_seconds(" ".join(["word"] * 15)), 6.0)

    def test_narration_seconds_14_words(self):
        # 14 words * 0.4 = 5.6s (example scene 1)
        self.assertEqual(narration_seconds(" ".join(["word"] * 14)), 5.6)

    def test_narration_seconds_13_words(self):
        # 13 words * 0.4 = 5.2s (example scenes 2-4)
        self.assertEqual(narration_seconds(" ".join(["word"] * 13)), 5.2)

    def test_narration_seconds_rounded_1dp(self):
        # 7 words * 0.4 = 2.8s
        self.assertEqual(narration_seconds(" ".join(["word"] * 7)), 2.8)

    def test_min_duration_floor(self):
        # 1 word = 0.4s, floored to 2.0s
        scene = Scene(1, "Tiny", narration="Go.")
        self.assertEqual(scene_duration(scene), MIN_SCENE_SECONDS)

    def test_explicit_duration_wins(self):
        scene = Scene(1, "Timed", narration=" ".join(["word"] * 13), duration=8.0)
        self.assertEqual(scene_duration(scene), 8.0)

    def test_duration_defaults_to_narration(self):
        scene = Scene(1, "Free", narration=" ".join(["word"] * 15))
        self.assertEqual(scene_duration(scene), 6.0)


if __name__ == "__main__":
    unittest.main()

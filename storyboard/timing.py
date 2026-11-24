"""Voiceover timing math.

Narration is timed at 150 words per minute, the standard voiceover
pace used by this tool:

    narration_seconds = words / 150 * 60 = words * 0.4

rounded to 1 decimal place. A scene's duration is its explicit
``Duration:`` value when given, otherwise its narration seconds, with
a floor of 2.0 seconds (a shot shorter than that is unreadable).
"""

WORDS_PER_MINUTE = 150
MIN_SCENE_SECONDS = 2.0


def count_words(text):
    """Count whitespace-separated words in text."""
    return len(text.split())


def narration_seconds(text):
    """Seconds of voiceover for narration text, rounded to 1 decimal."""
    return round(count_words(text) / WORDS_PER_MINUTE * 60, 1)


def scene_duration(scene):
    """A scene's duration: explicit Duration, else narration time, min 2.0s."""
    seconds = scene.duration if scene.duration is not None else narration_seconds(scene.narration)
    return max(MIN_SCENE_SECONDS, round(seconds, 1))

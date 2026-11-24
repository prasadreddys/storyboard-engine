"""Parse storyboard scripts (markdown) into scenes.

Script format (documented in README.md)::

    ## Scene 1: Mara Finds the Map
    Narration: Mara has searched the old library for years.
    Visual: Dusty shelves, one glowing map.
    Duration: 6

Scenes are separated by ``## Scene N: <title>`` headings. Each scene
requires a ``Narration:`` line; ``Visual:`` and ``Duration:`` are
optional. A plain non-empty line inside a scene continues the narration.
"""

import re

SCENE_HEADING_RE = re.compile(r"^##\s+Scene\s+(\d+)\s*:\s*(.+?)\s*$")


class ScriptError(ValueError):
    """Raised when a script file is malformed."""


class Scene:
    """One parsed scene from a script."""

    def __init__(self, number, title, narration="", visual="", duration=None):
        self.number = number
        self.title = title
        self.narration = narration
        self.visual = visual
        self.duration = duration

    def to_dict(self):
        return {
            "number": self.number,
            "title": self.title,
            "narration": self.narration,
            "visual": self.visual,
            "duration": self.duration,
        }


def parse_script(text):
    """Parse script markdown text into a list of Scene objects.

    Raises ScriptError on an empty script, content before the first
    scene heading, a scene without narration, or a bad Duration value.
    """
    scenes = []
    current = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SCENE_HEADING_RE.match(line)
        if match:
            current = Scene(number=int(match.group(1)), title=match.group(2))
            scenes.append(current)
            continue
        if current is None:
            raise ScriptError(
                "content before first scene heading: %r" % line
            )
        lowered = line.lower()
        if lowered.startswith("narration:"):
            value = line[len("Narration:"):].strip()
            current.narration = (
                (current.narration + " " + value).strip()
                if current.narration
                else value
            )
        elif lowered.startswith("visual:"):
            value = line[len("Visual:"):].strip()
            current.visual = (
                (current.visual + " " + value).strip()
                if current.visual
                else value
            )
        elif lowered.startswith("duration:"):
            value = line[len("Duration:"):].strip()
            try:
                seconds = float(value)
            except ValueError:
                raise ScriptError(
                    "scene %d: Duration must be a number, got %r"
                    % (current.number, value)
                )
            if seconds <= 0:
                raise ScriptError(
                    "scene %d: Duration must be > 0, got %s"
                    % (current.number, value)
                )
            current.duration = seconds
        else:
            # A plain line continues the narration.
            current.narration = (
                (current.narration + " " + line).strip()
                if current.narration
                else line
            )
    if not scenes:
        raise ScriptError("script has no scenes (no '## Scene N: ...' headings)")
    for scene in scenes:
        if not scene.narration:
            raise ScriptError(
                "scene %d (%s) has no Narration line"
                % (scene.number, scene.title)
            )
    return scenes


def load_script(path):
    """Read a script file and parse it into scenes."""
    with open(path, "r", encoding="utf-8") as handle:
        return parse_script(handle.read())

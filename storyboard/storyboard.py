"""Build and check storyboards.

Shot-type rule (documented in README.md), applied in order:
  1. The first scene is always a wide establishing shot.
  2. A scene whose narration contains an action verb is a close-up.
  3. Everything else is a medium shot (dialogue-heavy scenes included).

Every shot's visual_prompt repeats the character's name, ALL traits
verbatim, the palette, and the style, plus the scene's visual note —
so the same character description is handed to the image generator
for every shot, keeping the character consistent.
"""

import re

ACTION_VERBS = {
    "run", "runs", "running", "jump", "jumps", "jumping",
    "fight", "fights", "fighting", "grab", "grabs", "grabbing",
    "chase", "chases", "chasing", "climb", "climbs", "climbing",
    "fall", "falls", "falling", "push", "pushes", "pushing",
    "pull", "pulls", "pulling", "hit", "hits", "hitting",
    "open", "opens", "opening", "close", "closes", "closing",
    "leap", "leaps", "leaping", "dive", "dives", "diving",
    "sprint", "sprints", "sprinting", "escape", "escapes", "escaping",
}

FRAMING = {
    "wide": "wide establishing shot",
    "medium": "medium shot",
    "close-up": "close-up shot",
}

_WORD_RE = re.compile(r"[A-Za-z']+")


def assign_shot_type(scene, index):
    """Assign a shot type to a scene by the documented rule."""
    if index == 0:
        return "wide"
    words = {w.lower() for w in _WORD_RE.findall(scene.narration)}
    if words & ACTION_VERBS:
        return "close-up"
    return "medium"


def build_visual_prompt(character, scene):
    """Build the shot prompt: name + every trait verbatim + palette + style."""
    parts = [character["name"]]
    parts.extend(character["traits"])
    if character["palette"]:
        parts.append("palette " + ", ".join(character["palette"]))
    if character["style"]:
        parts.append("style: " + character["style"])
    note = scene.visual or scene.title
    parts.append("scene: " + note)
    return ", ".join(parts)


def build_storyboard(scenes, character):
    """Build the storyboard dict from parsed scenes and a character sheet."""
    from .timing import narration_seconds, scene_duration

    built_scenes = []
    total_seconds = 0.0
    total_narration = 0.0
    for index, scene in enumerate(scenes):
        shot_type = assign_shot_type(scene, index)
        n_seconds = narration_seconds(scene.narration)
        duration = scene_duration(scene)
        prompt = build_visual_prompt(character, scene)
        total_seconds += duration
        total_narration += n_seconds
        built_scenes.append({
            "scene": scene.number,
            "title": scene.title,
            "shot_type": shot_type,
            "framing": FRAMING[shot_type],
            "narration": scene.narration,
            "narration_seconds": n_seconds,
            "duration_seconds": duration,
            "visual_note": scene.visual,
            "visual_prompt": prompt,
            "continuity_ok": all(t in prompt for t in character["traits"]),
        })
    return {
        "format_version": 1,
        "character": character["name"],
        "voice": character["voice"],
        "scene_count": len(built_scenes),
        "total_seconds": round(total_seconds, 1),
        "total_narration_seconds": round(total_narration, 1),
        "scenes": built_scenes,
    }


def check_storyboard(data, character=None):
    """Verify a storyboard dict.

    Checks per scene: every character trait appears verbatim in the
    visual_prompt, duration > 0, narration_seconds matches the word-count
    math. Also checks the reported total equals the sum of durations.
    Returns (all_passed, checks) where checks is a list of dicts with
    scene/check/passed/detail.
    """
    from .timing import narration_seconds

    checks = []
    traits = None
    if character is not None:
        traits = character["traits"]
    elif isinstance(data.get("character_traits"), list):
        traits = data["character_traits"]

    scenes = data.get("scenes", [])
    for scene in scenes:
        number = scene.get("scene")
        if traits:
            missing = [t for t in traits if t not in scene.get("visual_prompt", "")]
            checks.append({
                "scene": number,
                "check": "traits_verbatim",
                "passed": not missing,
                "detail": "all traits present" if not missing
                          else "missing traits: " + "; ".join(missing),
            })
        duration = scene.get("duration_seconds")
        checks.append({
            "scene": number,
            "check": "duration_positive",
            "passed": isinstance(duration, (int, float)) and duration > 0,
            "detail": "duration_seconds = %s" % (duration,),
        })
        expected = narration_seconds(scene.get("narration", ""))
        actual = scene.get("narration_seconds")
        checks.append({
            "scene": number,
            "check": "narration_timing",
            "passed": actual == expected,
            "detail": "narration_seconds %s, expected %s (words/150*60)"
                      % (actual, expected),
        })
    total = data.get("total_seconds")
    summed = round(sum(s.get("duration_seconds", 0) for s in scenes), 1)
    checks.append({
        "scene": None,
        "check": "total_duration",
        "passed": total == summed,
        "detail": "total_seconds %s, sum of durations %s" % (total, summed),
    })
    return all(c["passed"] for c in checks), checks


def render_markdown(board):
    """Render a human-readable shot list with timings from a storyboard dict."""
    lines = [
        "# Storyboard — %s" % board["character"],
        "",
        "- Scenes: %d" % board["scene_count"],
        "- Total duration: %s s (narration %s s)" % (
            board["total_seconds"], board["total_narration_seconds"]),
    ]
    if board.get("voice"):
        lines.append("- Voice: %s" % board["voice"])
    lines.append("")
    for scene in board["scenes"]:
        lines.extend([
            "## Scene %s: %s" % (scene["scene"], scene["title"]),
            "",
            "- Shot: %s (%s)" % (scene["shot_type"], scene["framing"]),
            "- Duration: %s s (narration %s s)" % (
                scene["duration_seconds"], scene["narration_seconds"]),
            "- Narration: %s" % scene["narration"],
        ])
        if scene.get("visual_note"):
            lines.append("- Visual: %s" % scene["visual_note"])
        lines.extend([
            "- Visual prompt: %s" % scene["visual_prompt"],
            "- Continuity: %s" % ("OK" if scene["continuity_ok"] else "FAIL"),
            "",
        ])
    return "\n".join(lines) + "\n"

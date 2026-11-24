"""Storyboard Engine CLI.

Usage:
    python3 -m storyboard build --script script.md --character character.json --out DIR
    python3 -m storyboard check --storyboard storyboard.json [--character character.json]
    python3 -m storyboard init --dir PATH
"""

import argparse
import json
import os
import sys

from .character import load_character
from .script import load_script
from .storyboard import build_storyboard, check_storyboard, render_markdown

SAMPLE_SCRIPT = """## Scene 1: Mara Finds the Map
Narration: Mara has searched the old library for years, and tonight the map finally answers.
Visual: Dusty shelves, one glowing map.

## Scene 2: The Question
Narration: Is this the real map, or just another copy meant to mislead her?
Visual: Mara holds the map up to the lamplight.
"""

SAMPLE_CHARACTER = {
    "name": "Mara",
    "traits": [
        "a young cartographer with curly red hair",
        "a brass compass on a leather cord",
        "a teal cloak with gold stitching",
    ],
    "palette": ["#0F766E", "#D97706"],
    "style": "flat vector illustration, warm evening light",
    "voice": "calm female narrator",
}


def _cmd_build(args):
    scenes = load_script(args.script)
    character = load_character(args.character)
    board = build_storyboard(scenes, character)
    # Keep the traits in the file so `check` can verify continuity
    # without a separate character sheet.
    board["character_traits"] = character["traits"]
    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "storyboard.json")
    md_path = os.path.join(args.out, "storyboard.md")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(board, handle, indent=2)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(render_markdown(board))
    print("%d scenes, %s seconds total" % (board["scene_count"], board["total_seconds"]))
    print("wrote %s" % json_path)
    print("wrote %s" % md_path)
    return 0


def _cmd_check(args):
    with open(args.storyboard, "r", encoding="utf-8") as handle:
        board = json.load(handle)
    character = load_character(args.character) if args.character else None
    passed, checks = check_storyboard(board, character)
    for check in checks:
        scene = check["scene"] if check["scene"] is not None else "-"
        status = "PASS" if check["passed"] else "FAIL"
        print("[%s] scene %s %s: %s" % (status, scene, check["check"], check["detail"]))
    print("overall: %s" % ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


def _cmd_init(args):
    os.makedirs(args.dir, exist_ok=True)
    script_path = os.path.join(args.dir, "script.md")
    char_path = os.path.join(args.dir, "character.json")
    with open(script_path, "w", encoding="utf-8") as handle:
        handle.write(SAMPLE_SCRIPT)
    with open(char_path, "w", encoding="utf-8") as handle:
        json.dump(SAMPLE_CHARACTER, handle, indent=2)
    print("wrote %s" % script_path)
    print("wrote %s" % char_path)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="storyboard",
        description="Script to consistent-character storyboard for faceless video.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build a storyboard from a script + character sheet")
    build.add_argument("--script", required=True)
    build.add_argument("--character", required=True)
    build.add_argument("--out", required=True)
    build.set_defaults(func=_cmd_build)

    check = sub.add_parser("check", help="verify continuity and timing of a storyboard")
    check.add_argument("--storyboard", required=True)
    check.add_argument("--character", default=None)
    check.set_defaults(func=_cmd_check)

    init = sub.add_parser("init", help="write sample script.md + character.json templates")
    init.add_argument("--dir", required=True)
    init.set_defaults(func=_cmd_init)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

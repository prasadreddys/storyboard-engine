"""Character sheets: load and validate the JSON character definition.

Character sheet format (documented in README.md)::

    {
      "name": "Mara",
      "traits": ["curly red hair", "a brass compass"],
      "palette": ["#0F766E", "#D97706"],
      "style": "flat vector illustration",
      "voice": "calm female narrator"
    }

``traits`` are the exact phrases that must appear verbatim in every
shot prompt. ``palette`` entries must be ``#RRGGBB`` hex colours.
"""

import json
import re

HEX_COLOUR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class CharacterError(ValueError):
    """Raised when a character sheet is malformed."""


def validate_character(data):
    """Validate a parsed character-sheet dict and return a normalised copy.

    Raises CharacterError on any problem. ``style`` and ``voice`` are
    optional and default to "".
    """
    if not isinstance(data, dict):
        raise CharacterError("character sheet must be a JSON object")
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise CharacterError("character sheet needs a non-empty 'name'")
    traits = data.get("traits")
    if not isinstance(traits, list) or not traits:
        raise CharacterError("character sheet needs a non-empty 'traits' list")
    for trait in traits:
        if not isinstance(trait, str) or not trait.strip():
            raise CharacterError("every trait must be a non-empty string")
    palette = data.get("palette", [])
    if not isinstance(palette, list):
        raise CharacterError("'palette' must be a list of hex colours")
    for colour in palette:
        if not isinstance(colour, str) or not HEX_COLOUR_RE.match(colour):
            raise CharacterError(
                "bad palette colour %r (expected #RRGGBB)" % (colour,)
            )
    style = data.get("style", "")
    voice = data.get("voice", "")
    if not isinstance(style, str) or not isinstance(voice, str):
        raise CharacterError("'style' and 'voice' must be strings")
    return {
        "name": name.strip(),
        "traits": [t.strip() for t in traits],
        "palette": list(palette),
        "style": style.strip(),
        "voice": voice.strip(),
    }


def load_character(path):
    """Read a character-sheet JSON file and return the validated dict."""
    with open(path, "r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise CharacterError("character sheet is not valid JSON: %s" % exc)
    return validate_character(data)

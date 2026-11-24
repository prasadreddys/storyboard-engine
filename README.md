# Storyboard Engine v1

Script to consistent-character storyboard, shot list, and voiceover
timing for faceless video.

Faceless creators lose viewers when a character changes face, clothes,
or style between shots. Storyboard Engine takes a script + a character
sheet and produces a storyboard where every shot prompt repeats the
character's exact visual traits verbatim, so the character stays
consistent from shot to shot.

**Free / $0. No network. No paid APIs. Stdlib-only Python 3.12 — no
dependencies to install.**

## Quick start

```bash
python3 -m unittest discover -s tests -v   # unit suite
./run_tests.sh                              # unit suite + demo e2e

# 1. Write your script and character sheet (or start from templates):
python3 -m storyboard init --dir ./my-video

# 2. Build the storyboard:
python3 -m storyboard build --script script.md --character character.json --out ./board

# 3. Verify continuity before you generate any images:
python3 -m storyboard check --storyboard ./board/storyboard.json
```

## Script format (`script.md`)

Markdown. Scenes are separated by `## Scene N: <title>` headings.
Each scene has a `Narration:` line and optional `Visual:` and
`Duration:` lines. A plain non-empty line inside a scene continues
the narration.

```markdown
## Scene 1: Mara Finds the Map
Narration: Mara has searched the old library for years.
Visual: Dusty shelves, one glowing map.

## Scene 2: The Chase
Narration: She runs through the market as the guards chase her.
Visual: Crowded stalls, guards pushing through.
Duration: 8
```

Rules: a script with no scenes is rejected; a scene with no
`Narration:` line is rejected; `Duration:` must be a number > 0;
content before the first scene heading is rejected.

## Character sheet format (`character.json`)

```json
{
  "name": "Mara",
  "traits": [
    "a young cartographer with curly red hair",
    "a brass compass on a leather cord",
    "a teal cloak with gold stitching"
  ],
  "palette": ["#0F766E", "#D97706"],
  "style": "flat vector illustration, warm evening light",
  "voice": "calm female narrator"
}
```

- `name` — non-empty string.
- `traits` — non-empty list of non-empty strings. These exact phrases
  must appear verbatim in every shot prompt.
- `palette` — list of `#RRGGBB` hex colours (bad hex is rejected).
- `style`, `voice` — optional strings, default "".

## Timing math

Narration is timed at **150 words per minute**:

```
narration_seconds = words / 150 * 60 = words * 0.4   (rounded to 1 decimal)
```

A scene's duration is its explicit `Duration:` when given, otherwise
its narration seconds, with a floor of **2.0 seconds** (a shorter shot
is unreadable). Example: 14 words → 5.6 s; 13 words → 5.2 s.

## Shot-type rule (applied in order)

1. The first scene is always a **wide** establishing shot.
2. A scene whose narration contains an action verb (run, jump, fight,
   grab, chase, climb, fall, push, pull, hit, open, close, leap, dive,
   sprint, escape, and their -s/-ing forms) is a **close-up**.
3. Everything else is a **medium** shot (dialogue-heavy scenes included).

Framing: wide → "wide establishing shot", medium → "medium shot",
close-up → "close-up shot".

## Visual prompts (the consistency mechanism)

Every shot's `visual_prompt` is built the same way:

```
<name>, <trait 1>, <trait 2>, ..., palette <colours>, style: <style>, scene: <visual note or title>
```

Because every trait is repeated verbatim in every prompt, the image
generator gets the same character description for every shot. `check`
verifies this: it fails if any trait is missing from any prompt.

## Outputs (`--out`)

- `storyboard.json` — scenes with shot type, framing, narration,
  narration_seconds, duration_seconds, visual prompt, continuity_ok;
  plus scene_count, total_seconds, total_narration_seconds, voice,
  and `character_traits` (so `check` works without the character file).
- `storyboard.md` — human-readable shot list with timings.

## `check` output

Per scene: `traits_verbatim`, `duration_positive`,
`narration_timing` (recomputed from the word count), plus a
`total_duration` check that total_seconds equals the sum of durations.
Exit 0 only if every check passes.

## Layout

```
storyboard-engine/
  storyboard/   __init__.py __main__.py cli.py script.py character.py storyboard.py timing.py
  tests/        stdlib unittest only
  examples/     script.md / character.json / expected-storyboard.json
  run_tests.sh
```

## Limitations (honest)

- The tool writes prompts, it does not generate images — whether an
  image model actually keeps the character consistent depends on the
  model; the prompts give it the best chance, they cannot guarantee it.
- Shot types come from a fixed rule (first = wide, action verb =
  close-up, else medium), not from understanding the scene — review
  the shot list before generating.
- Timing assumes 150 wpm for every narrator; a faster or slower voice
  shifts the real durations.
- Word counting is whitespace-based; hyphenated words and numbers count
  as one word each.

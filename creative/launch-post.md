# Storyboard Engine launch post — DRAFT, not published

Status: draft for the user's approval. Nothing posted yet. Repo not created, nothing pushed.

Rules for this post: only measured numbers, no user/sales/revenue claims, no invented quotes.

## X / Threads version

Your faceless video's hero changes face in every shot. Viewers notice.

Storyboard Engine takes your script + one character sheet and builds a storyboard where every shot prompt repeats the character's exact traits verbatim — same face, same clothes, same style, every scene — with voiceover timing built in.

Free, open source, stdlib-only Python, local files only, no sign-up.

## Longer version (README / Product Hunt style)

Faceless creators lose viewers when a character drifts between shots. Storyboard Engine is the continuity layer: write the script in markdown, define the character once (traits, palette, style), and get a shot list where every visual prompt carries the full character description, plus narration timing at 150 wpm and a `check` command that proves every trait is present in every prompt.

- Demo ("Mara", 4 scenes): wide / medium / close-up / medium, 24.0s total (21.2s narration), all 13 continuity checks PASS
- Shot types follow one documented rule; durations are explicit or derived from the words, floored at 2.0s
- It writes prompts, it does not generate images — whether a model keeps the character consistent is up to the model

Measured, not estimated: 44 unit tests, all passing. No network, no keys, no paid API.

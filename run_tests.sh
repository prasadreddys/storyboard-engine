#!/bin/bash
# Storyboard Engine — unit suite + demo e2e. Exits non-zero on any failure.
set -e
cd "$(dirname "$0")"

echo "=== unit tests ==="
python3 -m unittest discover -s tests -v

echo ""
echo "=== demo e2e: build examples ==="
rm -rf /tmp/storyboard-demo
python3 -m storyboard build \
  --script examples/script.md \
  --character examples/character.json \
  --out /tmp/storyboard-demo

echo ""
echo "=== demo e2e: check ==="
python3 -m storyboard check --storyboard /tmp/storyboard-demo/storyboard.json

echo ""
echo "=== demo e2e: totals vs hand-checked expected values ==="
python3 - <<'EOF'
import json
with open("/tmp/storyboard-demo/storyboard.json") as f:
    board = json.load(f)
with open("examples/expected-storyboard.json") as f:
    expected = json.load(f)
board.pop("character_traits", None)
assert board == expected, "demo storyboard does not match expected-storyboard.json"
print("demo storyboard matches hand-checked expected values:")
print("  scenes: %d, total: %s s (narration %s s)" % (
    board["scene_count"], board["total_seconds"], board["total_narration_seconds"]))
print("  shot types: %s" % [s["shot_type"] for s in board["scenes"]])
EOF
echo "demo done."

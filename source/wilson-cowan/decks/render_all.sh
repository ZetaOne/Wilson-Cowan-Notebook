#!/usr/bin/env bash
# Render every chapter deck (ManimGX -> Manim Slides HTML via sciviz) and copy it next to the book:
#   rendered-anims/wc-chNN/wc-chNN_deck.html  ->  rendered-anims/wilson-cowan/book/decks/chNN/
# Usage: scripts/wilson-cowan/decks/render_all.sh [ch01 ch02 ...]     (default: all that exist)
# Set CPU=1 to force the CPU renderer (lavapipe) if the GPU runs out of memory.
set -u
cd "$(dirname "$0")/../../.."
ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
  for f in scripts/wilson-cowan/decks/ch[0-9][0-9].py; do ids+=("$(basename "$f" .py)"); done
fi
[ "${CPU:-0}" = "1" ] && export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json
for id in "${ids[@]}"; do
  n=${id#ch}
  name="wc-$id"
  echo "=== $id"
  rm -f "rendered-anims/$name"/[0-9][0-9]_*.mp4
  ok=0
  for try in 1 2 3; do
    if .venv/bin/python -m sciviz render "$name" "scripts/wilson-cowan/decks/$id.py" "Deck$n"; then ok=1; break; fi
    echo "render failed (try $try); retrying on the CPU renderer"
    export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json
  done
  [ $ok = 1 ] || { echo "GIVING UP on $id"; continue; }
  rm -rf "rendered-anims/$name/${name}_deck_assets"   # convert keeps stale files otherwise
  .venv/bin/python -m sciviz deck "$name" --offline || { echo "deck failed for $id"; continue; }
  dst="rendered-anims/wilson-cowan/book/decks/$id"
  rm -rf "$dst"; mkdir -p "$dst"
  cp -r "rendered-anims/$name/$name"_deck.html "rendered-anims/$name/$name"_deck_assets "$dst"/ 2>/dev/null || \
    cp -r "rendered-anims/$name/$name"_deck* "$dst"/
  [ "${CPU:-0}" = "1" ] || unset VK_ICD_FILENAMES
done

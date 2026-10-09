#!/usr/bin/env bash
# One command: episode folder (script.json + episode.json) -> final.mp4 + preview-720p.mp4 + thumbnail.jpg
#   produce.sh <episode-dir> [--stills-only]
# Steps (each skipped when its output is newer than its input, so reruns resume):
#   photos -> voice + timeline -> lip-sync cues (if presenter) -> data.js -> stills sheet -> render -> music mix -> mux -> thumbnail
set -euo pipefail
SK=$(cd "$(dirname "$0")/.." && pwd); SKILLS=$(cd "$SK/.." && pwd)
EP=$(cd "$1" && pwd); MODE=${2:-}
source "$SK/scripts/setup.sh" >/dev/null
cfg() { python3 -c "import json,sys;d=json.load(open('$EP/episode.json'));v=d.get('$1','$2');print(str(v).lower() if isinstance(v,bool) else v)"; }
VOICE=$(cfg voice af_heart); SPEED=$(cfg speed 0.93); MUSIC=$(cfg music ""); PRESENTER=$(cfg presenter false); BED=$(cfg music_db -20)
WD=$EP/.render; mkdir -p "$WD"
newer() { [ -e "$1" ] && [ "$1" -nt "$2" ]; }

echo "== 1/8 photos"; python3 "$SK/scripts/fetch_photos.py" "$EP"
echo "== 2/8 voice"
if ! newer "$EP/timeline.json" "$EP/script.json"; then "$YT_TOOLS/tts/bin/python" "$SK/scripts/make_vo.py" "$YT_TOOLS" "$EP" "$VOICE" "$SPEED" 2>&1 | grep -v Warn | tail -1; fi
TOTAL=$(python3 -c "import json;print(json.load(open('$EP/timeline.json'))['total'])")
if [ "$PRESENTER" = "true" ]; then
  echo "== 3/8 lip-sync"; cp "$SKILLS/cartoon-presenter/scripts/character.js" "$EP/"
  newer "$EP/cues.json" "$EP/voiceover.wav" || RHUBARB_DIR="$YT_TOOLS/rhubarb" "$SKILLS/cartoon-presenter/scripts/lipsync.sh" "$EP/voiceover.wav" "$EP/cues.json"
else rm -f "$EP/cues.json"; fi
echo "== 4/8 data.js"; cp "$SK/templates/engine.html" "$EP/video.html"; python3 "$SK/scripts/build_data.py" "$EP"
echo "== 5/8 stills"; mkdir -p "$WD/stills"; rm -f "$WD/stills"/*.jpg
node "$SK/scripts/stills.cjs" "$EP/video.html" "$WD/stills"
"$YT_TOOLS/tts/bin/python" - "$WD/stills" "$EP/stills-sheet.jpg" <<'PY'
import sys, glob
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + "/b*.jpg")); W, H, cols = 384, 216, 6
sh = Image.new("RGB", (cols * W, ((len(fs) + cols - 1) // cols) * H))
for i, f in enumerate(fs): sh.paste(Image.open(f).resize((W, H)), ((i % cols) * W, (i // cols) * H))
sh.save(sys.argv[2], quality=70); print(f"stills sheet: {len(fs)} scenes")
PY
[ "$MODE" = "--stills-only" ] && { echo "stills only: check $EP/stills-sheet.jpg"; exit 0; }
echo "== 6/8 music"
AUDIO="$EP/voiceover.wav"
if [ -n "$MUSIC" ]; then
  M="$MUSIC"; [ -f "$M" ] || M="$(git -C "$SK" rev-parse --show-toplevel)/youtube/music/$MUSIC"
  newer "$EP/mix.m4a" "$EP/voiceover.wav" || "$SKILLS/background-music/scripts/mix_music.sh" "$EP/voiceover.wav" "$M" "$EP/mix.m4a" "$BED"
  AUDIO="$EP/mix.m4a"
fi
echo "== 7/8 render (~9 s of compute per second of video; resumable)"
"$SK/scripts/render_chunks.sh" "$EP" "$TOTAL" "$WD/parts" 8 4 "$AUDIO" "$EP/final.mp4"
echo "== 8/8 thumbnail"
if [ -f "$EP/thumbnail.json" ]; then python3 "$SKILLS/yt-thumbnail/scripts/thumb.py" "$EP/thumbnail.json" "$EP/thumbnail.jpg"; fi
ls -la "$EP"/final.mp4 "$EP"/preview-720p.mp4 2>/dev/null

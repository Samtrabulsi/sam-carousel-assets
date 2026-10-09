#!/usr/bin/env bash
# Resumable parallel render: render_chunks.sh <episode-dir> <total-seconds> <workdir> [chunks=8] [parallel=4]
# Each chunk is rendered with record.mjs --from; finished chunks are kept, so a rerun only redoes missing ones.
set -e
EP=$(cd "$1" && pwd); TOTAL=$2; WD=$3; N=${4:-8}; P=${5:-4}
R=$(cd "$(dirname "$0")/../../.claude/skills/code-motion-video/scripts" && pwd)/record.mjs
mkdir -p "$WD"; cd "$EP"
LEN=$(python3 -c "import math;print(math.ceil($TOTAL/$N*30)/30)")
: > "$WD/list.txt"
for i in $(seq 0 $((N-1))); do
  f="$WD/part$i.mp4"; echo "file '$f'" >> "$WD/list.txt"
  if ffprobe -v error "$f" >/dev/null 2>&1 && [ -s "$f" ]; then echo "part$i done"; continue; fi
  rm -f "$f"
  while [ "$(jobs -rp | wc -l)" -ge "$P" ]; do wait -n; done
  ( node "$R" video.html "$f.tmp.mp4" --w 1920 --h 1080 --fps 30 --sec "$LEN" --from "$(python3 -c "print($i*$LEN)")" > "$WD/part$i.log" 2>&1 && mv "$f.tmp.mp4" "$f" && echo "part$i rendered" ) &
done
wait
ffmpeg -y -loglevel error -f concat -safe 0 -i "$WD/list.txt" -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart 5-problems-ai-fixes.mp4
ffmpeg -y -loglevel error -i 5-problems-ai-fixes.mp4 -vf scale=1280:720 -c:v libx264 -preset slow -crf 30 -c:a aac -b:a 96k -movflags +faststart preview-720p.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 5-problems-ai-fixes.mp4

#!/usr/bin/env bash
# Resumable parallel render: render_chunks.sh <episode-dir> <total-seconds> <workdir> [chunks=8] [parallel=4] [audio=voiceover.wav] [out=final.mp4]
# Each chunk is rendered with record.mjs --from; finished chunks are kept, so a rerun only redoes missing ones.
set -e
EP=$(cd "$1" && pwd); TOTAL=$2; WD=$3; N=${4:-8}; P=${5:-4}; AUDIO=${6:-voiceover.wav}; OUT=${7:-final.mp4}
R=$(cd "$(dirname "$0")/../../code-motion-video/scripts" && pwd)/record.mjs
mkdir -p "$WD"; cd "$EP"
LEN=$(python3 -c "import math;print(math.ceil($TOTAL/$N*30)/30)")
: > "$WD/list.txt"
for i in $(seq 0 $((N-1))); do
  f="$WD/part$i.mp4"; echo "file '$f'" >> "$WD/list.txt"
  if ffprobe -v error "$f" >/dev/null 2>&1 && [ -s "$f" ]; then echo "part$i done"; continue; fi
  rm -f "$f"
  while [ "$(jobs -rp | wc -l)" -ge "$P" ]; do wait -n; done
  ( node "$R" "$EP/video.html" "$f.tmp.mp4" --w 1920 --h 1080 --fps 30 --sec "$LEN" --from "$(python3 -c "print($i*$LEN)")" > "$WD/part$i.log" 2>&1 && mv "$f.tmp.mp4" "$f" && echo "part$i rendered" ) &
done
wait
ffmpeg -y -loglevel error -f concat -safe 0 -i "$WD/list.txt" -i "$AUDIO" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
ffmpeg -y -loglevel error -i "$OUT" -vf scale=1280:720 -c:v libx264 -preset slow -crf 30 -c:a aac -b:a 96k -movflags +faststart preview-720p.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"

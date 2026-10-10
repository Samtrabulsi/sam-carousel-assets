#!/usr/bin/env bash
# One-time (per container) setup for the YouTube pipeline. Safe to re-run; skips what exists.
#   source .claude/skills/yt-produce/scripts/setup.sh   ->  exports YT_TOOLS
set -e
export YT_TOOLS=${YT_TOOLS:-$HOME/.cache/yt-tools}
mkdir -p "$YT_TOOLS"
python3 -m yt_dlp --version >/dev/null 2>&1 || python3 -m pip install -q --user yt-dlp
if [ ! -x "$YT_TOOLS/tts/bin/python" ]; then python3 -m venv "$YT_TOOLS/tts"; "$YT_TOOLS/tts/bin/pip" install -q kokoro-onnx soundfile pillow; fi
mkdir -p "$YT_TOOLS/kokoro"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$YT_TOOLS/kokoro/$f" ] || curl -sSfL -o "$YT_TOOLS/kokoro/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
node -e "require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright')" 2>/dev/null || echo "WARN: global playwright not found (needed by record.mjs)"
echo "yt tools ready in $YT_TOOLS"

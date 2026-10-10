#!/usr/bin/env bash
# Voice audio -> mouth-shape timeline (Rhubarb Lip Sync, MIT). Downloads Rhubarb on first use.
#   lipsync.sh voice.wav cues.json [dialog.txt]
# Output: {"mouthCues":[{"start":0.0,"end":0.12,"value":"X"},...]}  values A–H, X (see SKILL.md)
set -euo pipefail
IN=$1; OUT=$2; DIALOG=${3:-}
DIR=${RHUBARB_DIR:-$HOME/.cache/rhubarb}; BIN="$DIR/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb"
if [ ! -x "$BIN" ]; then
  mkdir -p "$DIR"
  curl -sSfL -o "$DIR/rh.zip" https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip
  (cd "$DIR" && unzip -q -o rh.zip)
fi
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
ffmpeg -y -loglevel error -i "$IN" -ac 1 -ar 16000 "$TMP/v.wav"          # Rhubarb wants WAV/OGG
ARGS=(-f json -r phonetic --extendedShapes GHX -q)                       # phonetic = fast, any language
[ -n "$DIALOG" ] && ARGS+=(-d "$DIALOG")
"$BIN" "${ARGS[@]}" -o "$OUT" "$TMP/v.wav"
python3 -c "import json;d=json.load(open('$OUT'));print(len(d['mouthCues']),'cues ->','$OUT')"

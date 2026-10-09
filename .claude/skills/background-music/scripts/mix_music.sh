#!/usr/bin/env bash
# Lay a music bed under a narration track: loop the music to the narration length with
# crossfades, duck it under the voice (sidechain), fade in/out, normalise to YouTube loudness.
#
#   mix_music.sh voice.wav music.mp3 out.m4a [bed_db=-20] [xfade_s=4]
#
# Then mux into a rendered video:  ffmpeg -i video.mp4 -i out.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest final.mp4
set -euo pipefail
VOICE=$1; MUSIC=$2; OUT=$3; BED=${4:--20}; XF=${5:-4}
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
VD=$(dur "$VOICE"); MD=$(dur "$MUSIC")

# 1. Loop the track with crossfades until it covers the narration (+2 s).
ffmpeg -y -loglevel error -i "$MUSIC" -ar 44100 -ac 2 "$TMP/loop0.wav"
cp "$TMP/loop0.wav" "$TMP/bed.wav"
while python3 -c "import sys; sys.exit(0 if $(dur "$TMP/bed.wav") < $VD + 2 else 1)"; do
  ffmpeg -y -loglevel error -i "$TMP/bed.wav" -i "$TMP/loop0.wav" -filter_complex "acrossfade=d=$XF:c1=tri:c2=tri" "$TMP/bed2.wav"
  mv "$TMP/bed2.wav" "$TMP/bed.wav"
done

# 2. Trim, set bed level, fade in/out, duck under the voice, mix, normalise to -14 LUFS.
FO=$(python3 -c "print(max(0, $VD - 3))")
ffmpeg -y -loglevel error -i "$VOICE" -i "$TMP/bed.wav" -filter_complex "
  [0:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[v][vkey];
  [1:a]atrim=0:$VD,asetpts=N/SR/TB,volume=${BED}dB,afade=t=in:d=2,afade=t=out:st=$FO:d=3[m];
  [m][vkey]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=600:makeup=1[duck];
  [v][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]" \
  -map "[out]" -c:a aac -b:a 192k "$OUT"
echo "wrote $OUT ($(dur "$OUT")s; voice ${VD}s, music ${MD}s looped, bed ${BED} dB)"

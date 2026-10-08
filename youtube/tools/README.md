# YouTube pipeline tools

- `make_vo.py`: script.json → voiceover.wav + timeline.json with Kokoro TTS (free, runs locally).
  Setup once: `python3 -m venv tts && tts/bin/pip install kokoro-onnx soundfile`, then download
  `kokoro-v1.0.onnx` and `voices-v1.0.bin` from github.com/thewh1teagle/kokoro-onnx releases (model-files-v1.0) into `<dir>/kokoro/`.
  Run: `tts/bin/python make_vo.py <dir> <episode-folder> am_michael 1.0`
- `stills.cjs`: one preview still per beat (`node stills.cjs video.html outdir`). Check these before a full render.
- Render: `.claude/skills/code-motion-video/scripts/record.mjs` with `--from` to split long videos into parallel chunks.

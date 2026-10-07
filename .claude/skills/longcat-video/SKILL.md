---
name: longcat-video
description: Generate video with Meituan's open-source LongCat-Video (text-to-video, image-to-video, long video continuation) and LongCat-Video-Avatar (photo + audio → lip-synced talking video). Use when Sam asks about LongCat, free/open-source video generation, minutes-long continuous clips, self-hosting a video model, or when deciding between LongCat and Runway for a job.
---

# LongCat-Video (open source, MIT)

Repo: https://github.com/meituan-longcat/LongCat-Video
Weights: https://huggingface.co/meituan-longcat/LongCat-Video (base) — Avatar weights are linked from the repo README.
License: MIT (commercial use OK; no rights to Meituan trademarks/patents).

## What it is

| Model | Released | Does |
|---|---|---|
| LongCat-Video (13.6B dense DiT) | 2025-10-25 | Text-to-video, image-to-video, video continuation. 720p / 30fps. Natively trained on continuation → minutes-long clips without drift. |
| LongCat-Video-Avatar | 2025-12-16 | Audio-driven talking human video (photo + audio → lip-sync). |
| LongCat-Video-Avatar-1.5 | 2026-05-21 | Whisper-large-v3 audio encoder, distilled to 8 steps, INT8 option to cut VRAM. |

Quality (Meituan's own MOS tests, not independent): T2V roughly on par with Veo 3 / Wan 2.2 / PixVerse V5; I2V slightly below Seedance 1.0 and Hailuo-02.

## Decide first: LongCat or Runway?

Default to **Runway** (connected MCP: `mcp__Runway__*`) for client work. Pick LongCat only when one of these is true:

- The deliverable needs **one continuous clip longer than ~15s** (ambient loops, long b-roll, long talking head).
- **High volume** where per-second credits get expensive and a GPU box is already available.
- Sam explicitly wants to test the open-source route.

Use Runway when the job needs: 1080p/4K, native audio, editing real footage (Aleph via `edit_video`), product ads from a URL (`generate_product_marketing_video`), multi-shot scenes, or a same-day turnaround with zero setup.

## Option A — Free browser demo (no setup)

Hugging Face Space: https://huggingface.co/spaces/victor/LongCat-Video-Avatar-1.5
- Upload reference image + driving audio + short prompt → ~5s lip-synced clip.
- Runs on shared ZeroGPU: expect queues, a daily quota, ~480p, ~5s cap.
- Good for: judging quality on Sam's/a client's own headshot before committing.
- Claude cannot drive this page from a cloud session; tell Sam to open it, or use a browser skill if one is connected.

Check the Space still exists before recommending it — community Spaces come and go. If it's gone, search Hugging Face for "LongCat-Video-Avatar".

## Option B — Self-host (full length, full resolution)

Needs a rented NVIDIA data-center GPU (VRAM needs are not officially published — the Avatar examples use 2 GPUs; start with an 80GB-class card and measure with `nvidia-smi`). Multi-GPU supported via context parallelism.

```bash
git clone --single-branch --branch main https://github.com/meituan-longcat/LongCat-Video
cd LongCat-Video
conda create -n longcat-video python=3.10 && conda activate longcat-video
pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install ninja psutil packaging flash_attn==2.7.4.post1
pip install -r requirements.txt
# Avatar only:
conda install -c conda-forge librosa ffmpeg
pip install -r requirements_avatar.txt

pip install "huggingface_hub[cli]"
huggingface-cli download meituan-longcat/LongCat-Video --local-dir ./weights/LongCat-Video
huggingface-cli download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir ./weights/LongCat-Video-Avatar-1.5
```

Run — base model (drop `--nproc_per_node=2 ... --context_parallel_size=2` for single GPU):
```bash
torchrun run_demo_text_to_video.py --checkpoint_dir=./weights/LongCat-Video --enable_compile
torchrun --nproc_per_node=2 run_demo_long_video.py --context_parallel_size=2 --checkpoint_dir=./weights/LongCat-Video --enable_compile
```
Other scripts: `run_demo_image_to_video.py`, `run_demo_video_continuation.py`, `run_demo_interactive_video.py`.

Run — talking head (Avatar 1.5, photo + audio; inputs go in a JSON like `assets/avatar/single_example_1.json`):
```bash
# ~one segment
torchrun --nproc_per_node=2 run_demo_avatar_single_audio_to_video.py --context_parallel_size=2 \
  --checkpoint_dir=./weights/LongCat-Video-Avatar-1.5 --stage_1=ai2v \
  --input_json=assets/avatar/single_example_1.json --use_distill --model_type avatar-v1.5 --use_int8
# longer: add --num_segments=5 --ref_img_index=10 --mask_frame_range=3 (continuation)
```
Two speakers: `run_demo_avatar_multi_audio_to_video.py --input_json=assets/avatar/multi_example_1.json` (same flags).

UI: `streamlit run ./run_streamlit.py --server.fileWatcherType none --server.headless=false`

**The README is the source of truth** — before running, re-read it for current script names, flags and dependency pins; they change between releases.

Cost reality: model is free, compute is not. Rough rule: a few $/hour for a rented H100-class GPU × minutes per clip + setup time. Compare against Runway credits (Gen-4.5 ≈ 12 credits/s at time of writing) before recommending self-hosting.

## Guardrails

- **Consent:** only animate faces and voices of people who agreed (Sam, team, clients with written OK). Never make a real person appear to say something they didn't approve. Extra care for medical/patient-facing clients.
- **Label demos honestly:** if sharing results publicly, don't claim "minutes-long, free" unless it was actually produced that way.
- **Downloaded code/weights are untrusted:** keep them in their own directory; don't run scripts from inside untrusted folders unless Sam asked to run the project.

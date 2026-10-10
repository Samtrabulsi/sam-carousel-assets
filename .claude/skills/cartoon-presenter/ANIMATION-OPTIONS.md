# Better cartoons + multi-character series: options (researched 2026-10-09)

Our machine has no GPU, so every AI video model below is used through a paid API (fal.ai, Kling, Runway, Google). Prices marked † are third-party trackers.

## What we have
- Code-drawn characters (Gia, Tamara) rendered in Chromium: free, 100% consistent, flat 2D.
- Rhubarb lip sync (CPU), Kokoro TTS (fixed adult voices), Suno songs, faster-whisper lyric timing.

## What we're missing
| Gap | Best option | Cost |
|---|---|---|
| Keep the Pixar look of Tamara in new scenes | Nano Banana 2 / Pro (Gemini image) from the reference; backup FLUX Kontext, Qwen-Image-Edit (Apache) | $0.03–0.13 per image |
| Make her sing/talk in that look | Kling AI Avatar v2 (fal, works on cartoons) | ~$0.06/s Std |
| Two characters talking in one shot | LongCat-Video-Avatar 1.5 multi (MIT) or InfiniteTalk/MultiTalk (Apache) | ~$0.20/s |
| Movement, dancing, action | Kling 3.0 (multi-character scenes, speaker-tagged audio), Veo 3.1 Lite, Hailuo, Runway Gen-4 | $0.05–0.13/s |
| Distinct character voices (kids) | ElevenLabs voice design (check its rules on child-like voices) | ~$0.05–0.10 per 1k chars† |
| Separate vocals from Suno songs | Demucs (CPU) | free |
| Better free 2D rig | Rive (editor ~$9/mo to export; MIT runtime plays in our Chromium) or Spine ($69–99 one-time); a person rigs Tamara once (1–2 days) | ~$0/min after |
| Shot planning | agent writes a JSON shot list (character, line, camera, action) → keyframe per shot → API clip per shot → ffmpeg edit | – |

Skip: AnimatedDrawings (archived, kid-drawing look), Sonic (non-commercial), LivePortrait (non-commercial face weights), HunyuanVideo-Avatar (licence excludes EU/UK/KR), ToonCrafter (research-only, low res), Inochi2D/Synfig/OpenToonz (dated). Live2D: ask Live2D whether its small-business exemption covers YouTube video.

## Recommended stacks
1. **Tamara music videos (AI look):** Suno → Demucs vocal → ~12 Nano Banana keyframes/min → Kling Avatar sung close-ups (~30 s/min) + Kling 3.0 dance shots (~30 s/min) → ffmpeg with karaoke captions. **~$5–6 per finished minute, $10–15 with retries.**
2. **Multi-character series:** ElevenLabs voices per character → two-character keyframes → LongCat/InfiniteTalk two-shots + Kling Avatar close-ups + Kling 3.0 action. **~$8–15/min, $15–30 with retries.**
3. **Free fallback:** the code puppet (now), or a Rive rig + Rhubarb later.

Unverified: fal multi-person InfiniteTalk price, WaveSpeed LongCat scaling, Hedra $/s, Live2D video licence, MimicMotion/UniAnimate licences, how well Kling Avatar handles a Pixar-style child (test it: 5 s ≈ $0.30).

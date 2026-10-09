# Episode 1 (v2): 5 Problems AI Fixes for Small Businesses

9:31 long-form explainer. Opens straight on the 5 problems; 30 of 49 scenes use CC0 photos (see `photos/CREDITS.md`) with slow zooms, slide transitions and chapter light-sweeps. Each problem shows the real cost, the fix, specific tools, setup steps, a worked example, and the mistake to avoid.

**Files**
- `5-problems-ai-fixes.mp4`: final video, 1920x1080, 30fps, burned-in captions
- `thumbnail.jpg`: 1280x720, main thumbnail (problem list). `thumbnail-combo.jpg`: problem list + contractor face (`thumbnail-combo.html`). `thumbnail-face.jpg`: full-face vidIQ version. Test them with YouTube Test & Compare
- `script.json`: the script as 51 "beats" (narration line + visual spec). Edit this to change the video.
- `timeline.json`: start time and length of each beat, measured from the voiceover
- `video.html` + `data.js`: the animation engine (15 visual templates)
- `voiceover.wav`: Kokoro TTS (open-source, Apache 2.0), voice `af_heart` (female), speed 0.93, generated locally for free

## Rebuild after editing script.json
```bash
S=<dir with the kokoro venv + model, see ../tools/README.md>
$S/tts/bin/python ../tools/make_vo.py $S $PWD af_heart 0.93          # voiceover.wav + timeline.json
python3 -c "import json;open('data.js','w').write('const BEATS='+json.dumps(json.load(open('script.json')),ensure_ascii=False)+';\nconst TL='+open('timeline.json').read()+';\n')"
# render 4 chunks in parallel with record.mjs --from, then concat + mux voiceover.wav
```

## Upload copy

**Title:** 5 Expensive Problems AI Fixes for Small Businesses (Step by Step)

**Description:**
Most small businesses lose money every week to five problems AI can now fix: missed leads, slow follow-ups, forgotten meeting promises, late invoices, and no time for content. For each one you'll see the real cost, the exact tools, the setup steps, and the mistake to avoid.

00:00 Intro: 5 problems AI fixes
00:23 Problem 1: Missed leads & repeat questions
02:25 Problem 2: Slow follow-ups
04:27 Problem 3: Forgotten meeting promises
05:58 Problem 4: Late invoices
07:20 Problem 5: No time for content
08:40 Where to start

Tools mentioned: Tidio, Intercom Fin, Chatbase, ManyChat, HubSpot CRM, Zapier, Make, Claude, ChatGPT, Fathom, Fireflies, Otter, QuickBooks, Xero, FreshBooks, Stripe, Descript, Opus Clip, Canva, Metricool, Buffer. Not sponsored.

Lead response stat: Lead Response Management Study (Dr. James Oldroyd, MIT / InsideSales.com).

**Tags:** ai automation for small business, ai for small business, ai tools for small business, business automation, ai automation for business, small business tips, ai for business owners, zapier automation, ai chatbot for website

**Upload settings:** AI voice, so answer "yes" to altered/synthetic content if asked. Add the chapters above so YouTube shows them.

Niche research for this channel is in `../2026-10-08-5-tasks-to-automate/README.md`.

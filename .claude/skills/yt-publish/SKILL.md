---
name: yt-publish
description: Upload and schedule a finished episode to YouTube through the free official YouTube Data API — title, description with auto-generated chapters and sources, tags, thumbnail, playlist, scheduled publish time. Includes the one-time Google Cloud + OAuth setup per channel. Use for "upload the video", "schedule it", "publish", or the Publisher routine.
---

# yt-publish

```bash
python3 .claude/skills/yt-publish/scripts/publish.py <episode-dir> --channel <slug> --publish-at 2026-10-20T15:00:00Z
python3 .claude/skills/yt-publish/scripts/publish.py <episode-dir> --channel <slug> --dry-run   # check metadata first
```

**Inputs** (in the episode folder):
- `final.mp4`, `thumbnail.jpg`
- `upload.json`: `{"title", "description", "tags": [], "category": "27", "playlist_id"?, "synthetic": false}`
- `script.json` + `timeline.json`: chapters are generated automatically from the chapter scenes
- `sources.md`: links are appended as a Sources section

**Output:** `upload-result.json` (video id and URL). Copy the URL to the episode's Notion card.

## Description template (write it in upload.json)
1. 2 lines that restate the hook with the main search phrase (from the scout report's autocomplete list).
2. 2–3 sentences on what the video covers.
3. A disclaimer where needed: "Educational content, not financial advice."
4. The script adds Chapters and Sources itself.

Use 5–15 tags, mostly search phrases.

**`synthetic`:** set it to true only if the video shows realistic AI-made people, places or events that could be mistaken for real. Animated graphics, stock photos and an AI narrator don't need it. Never depict real people with AI.

## One-time setup per Google account (about 10 minutes, done by Sam or the assistant)
1. Go to **console.cloud.google.com** and create a project, e.g. "yt-automation".
2. **APIs & Services → Library**: enable **YouTube Data API v3** and **YouTube Analytics API**.
3. **APIs & Services → OAuth consent screen**: External. App name "yt-automation". Add your email as a test user. Then publish the app to "In production"; otherwise the sign-in expires every 7 days.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID → Desktop app**, then download `client_secret.json`.
5. Also **Create credentials → API key**. Restrict it to YouTube Data API v3. This is `YT_API_KEY`, used by yt-scout and yt-analytics.
6. On a computer with a browser:
   ```bash
   pip install google-auth-oauthlib
   python3 yt_auth.py client_secret.json <channel-slug>
   ```
   Sign in, pick the **channel** (brand account), and copy the printed JSON.
7. Add the secrets in the Claude Code environment settings: `YT_OAUTH_<CHANNEL_SLUG>` (the JSON) and `YT_API_KEY`. Never commit them.
8. **Request the API audit** (Google "YouTube API Services – Audit and Quota Extension" form). Until it's approved, every API upload is forced **private**. The assistant then sets visibility or the schedule in Studio (10 seconds per video).

## Limits
- An upload costs about 1,600 of the 10,000 free daily quota units, so about **6 uploads a day per Cloud project**. The audit form can also raise the quota.
- One Cloud project can serve several channels, each with its own OAuth secret.
- Fallback when the API is unavailable: the assistant uploads in YouTube Studio using `upload.json` and `final.mp4`, or uses vidIQ `vidiq_video_upload` if that channel is connected there.

## Before publishing: checklist (the Publisher routine refuses if any is missing)
- [ ] `FACTCHECK.md` all ticked by a human
- [ ] Preview watched and approved (Notion status "Approved")
- [ ] Thumbnail checked at phone size
- [ ] Title under 70 characters, no misleading claims
- [ ] Music source recorded in the episode README

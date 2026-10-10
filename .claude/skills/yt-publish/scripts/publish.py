#!/usr/bin/env python3
"""Upload a finished episode to YouTube (official Data API) and set its thumbnail.

  python3 publish.py <episode-dir> --channel <slug> [--privacy private|unlisted|public] [--publish-at 2026-10-20T15:00:00Z] [--dry-run]
  python3 publish.py <episode-dir> --channel <slug> --schedule-existing --publish-at 2026-10-20T15:00:00Z
      (after review: re-uses the video id in upload-result.json and only changes visibility / schedule)

Reads <episode>/upload.json: {"title", "description", "tags": [], "category": "27", "playlist_id"?, "synthetic": false}
Appends YouTube chapters (from chapter scenes + timeline.json) and a Sources section (sources.md links) to the description.
Uses final.mp4 and thumbnail.jpg. Writes upload-result.json with the video id/URL.

Quota: an upload costs ~1,600 of the free 10,000 daily units, so about 6 uploads/day per Google Cloud project.
NOTE: until the Cloud project passes YouTube's API compliance audit, API uploads are locked to PRIVATE.
Request the audit early (free); meanwhile the assistant flips each video to Public/Scheduled in Studio.
"""
import argparse, json, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("ep"); ap.add_argument("--channel", required=True)
ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
ap.add_argument("--publish-at", help="UTC ISO time; implies private until then")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--schedule-existing", action="store_true", help="update privacy/publishAt of the already-uploaded private video")
a = ap.parse_args()
ep = a.ep
meta = json.load(open(os.path.join(ep, "upload.json")))

if a.schedule_existing:
    sys.path.insert(0, os.path.dirname(__file__))
    from ytapi import youtube
    res = json.load(open(os.path.join(ep, "upload-result.json")))
    status = {"privacyStatus": "private" if a.publish_at else a.privacy, "selfDeclaredMadeForKids": bool(meta.get("made_for_kids", False))}
    if a.publish_at:
        status["publishAt"] = a.publish_at
    if a.dry_run:
        print(json.dumps({"id": res["video_id"], "status": status})); sys.exit(0)
    youtube(a.channel).videos().update(part="status", body={"id": res["video_id"], "status": status}).execute()
    res.update(privacy=status["privacyStatus"], publish_at=a.publish_at); json.dump(res, open(os.path.join(ep, "upload-result.json"), "w"), indent=1)
    print(json.dumps(res)); sys.exit(0)


def ts(sec):
    sec = int(sec); return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"


# chapters: YouTube needs the first at 00:00, >=3 chapters, each >=10 s
# song videos (yt-kids-song) have no script.json/timeline.json, so no chapters
has_tl = os.path.exists(os.path.join(ep, "script.json")) and os.path.exists(os.path.join(ep, "timeline.json"))
beats = json.load(open(os.path.join(ep, "script.json"))) if has_tl else []
tl = json.load(open(os.path.join(ep, "timeline.json")))["beats"] if has_tl else []
chap = [("00:00", meta.get("intro_chapter", "Intro"))]
for b, t in zip(beats, tl):
    if b["v"].get("t") == "chapter":
        chap.append((ts(t["start"]), b["v"]["title"]))
    if b["v"].get("outro") and len(chap) > 1:
        chap.append((ts(t["start"]), "Wrap-up"))
desc = meta["description"].rstrip()
if len(chap) >= 3:
    desc += "\n\nChapters\n" + "\n".join(f"{c} {n}" for c, n in chap)
src = os.path.join(ep, "sources.md")
if os.path.exists(src):
    links = re.findall(r"https?://\S+", open(src).read())
    if links:
        desc += "\n\nSources\n" + "\n".join(dict.fromkeys(l.rstrip(").,") for l in links))
body = {
    "snippet": {"title": meta["title"][:100], "description": desc[:5000], "tags": meta.get("tags", [])[:30], "categoryId": str(meta.get("category", "27"))},
    "status": {"privacyStatus": "private" if a.publish_at else a.privacy, "selfDeclaredMadeForKids": bool(meta.get("made_for_kids", False)),
               "containsSyntheticMedia": bool(meta.get("synthetic", False))},
}
if a.publish_at:
    body["status"]["publishAt"] = a.publish_at
video = os.path.join(ep, "final.mp4"); thumb = os.path.join(ep, "thumbnail.jpg")
print(json.dumps(body, indent=1, ensure_ascii=False))
missing = [p for p in (video, thumb) if not os.path.exists(p)]
if missing:
    print("missing:", missing, file=sys.stderr)
if a.dry_run:
    print("dry run: nothing uploaded"); sys.exit(0)
if missing:
    sys.exit(1)

sys.path.insert(0, os.path.dirname(__file__))
from ytapi import youtube
from googleapiclient.http import MediaFileUpload
yt = youtube(a.channel)
req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video, chunksize=8 * 1024 * 1024, resumable=True))
resp = None
while resp is None:
    status, resp = req.next_chunk()
    if status:
        print(f"uploaded {int(status.progress() * 100)}%")
vid = resp["id"]
yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb)).execute()
if meta.get("playlist_id"):
    yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": meta["playlist_id"], "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
res = {"video_id": vid, "url": f"https://youtu.be/{vid}", "privacy": body["status"]["privacyStatus"], "publish_at": a.publish_at}
json.dump(res, open(os.path.join(ep, "upload-result.json"), "w"), indent=1)
print(json.dumps(res))

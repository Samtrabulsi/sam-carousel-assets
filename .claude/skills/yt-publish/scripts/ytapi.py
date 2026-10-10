"""Shared: build authorised YouTube clients for a channel from the YT_OAUTH_<SLUG> secret (see yt_auth.py)."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def creds_for(slug):
    name = "YT_OAUTH_" + slug.upper().replace("-", "_")
    raw = os.environ.get(name)
    if not raw:
        path = os.path.expanduser(f"~/.config/yt-tools/{slug}.json")
        raw = open(path).read() if os.path.exists(path) else None
    if not raw:
        raise SystemExit(f"No credentials: set secret {name} (run yt_auth.py once on a computer with a browser)")
    d = json.loads(raw)
    return Credentials(None, refresh_token=d["refresh_token"], client_id=d["client_id"], client_secret=d["client_secret"],
                       token_uri=d.get("token_uri", "https://oauth2.googleapis.com/token"))


def youtube(slug):
    return build("youtube", "v3", credentials=creds_for(slug), cache_discovery=False)


def analytics(slug):
    return build("youtubeAnalytics", "v2", credentials=creds_for(slug), cache_discovery=False)

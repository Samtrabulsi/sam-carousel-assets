#!/usr/bin/env python3
"""ONE-TIME, on a computer with a browser: authorise a YouTube channel for uploads + analytics.

  pip install google-auth-oauthlib
  python3 yt_auth.py client_secret.json <channel-slug>

Sign in as the channel owner and pick the channel (brand account) when Google asks.
Prints a JSON token. Store it as a secret named YT_OAUTH_<CHANNEL_SLUG> (upper-case, '-' -> '_')
in the Claude Code environment settings (never commit it). It contains a refresh token: treat it like a password."""
import json, sys
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
name = "YT_OAUTH_" + sys.argv[2].upper().replace("-", "_")
print(f"\nSave this as the secret {name}:\n")
print(json.dumps({"refresh_token": creds.refresh_token, "client_id": creds.client_id, "client_secret": creds.client_secret, "token_uri": creds.token_uri}))

"""Publisher CLI: setup, publish, verify.

  setup     --client SLUG --token PIT       Discover location/accounts/user, write clients/SLUG.toml
  publish   --client SLUG --html PATH ...   Schedule a single-image or carousel post
  verify    --client SLUG [--post-id ID]    Confirm a scheduled post (or list a window)

Tokens never go in code or TOML — they live in .env as GHL_PIT_<SLUG>.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from . import config as cfg
from .ghl_client import GHLClient, GHLError, SocialAccount
from .render import DEFAULT_PRESET, PRESETS, render, render_many


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def parse_schedule(s: str, default_tz: str) -> str:
    """Accept '2026-05-21 10:00 Europe/Athens' or full ISO. Return ISO UTC string."""
    s = s.strip()
    # Try full ISO first
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(default_tz))
    except ValueError:
        # Pattern: "YYYY-MM-DD HH:MM [TZ]"
        parts = s.rsplit(" ", 1)
        if len(parts) == 2 and ("/" in parts[1] or parts[1].upper() == "UTC"):
            stamp, tz = parts
            tz = "UTC" if tz.upper() == "UTC" else tz
        else:
            stamp, tz = s, default_tz
        dt = datetime.strptime(stamp, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(tz))
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def read_caption(path: Optional[str], inline: Optional[str]) -> str:
    if inline:
        return inline
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    raise SystemExit("Either --caption-file or --caption is required.")


def mime_for(p: Path) -> str:
    ext = p.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
    }.get(ext, "application/octet-stream")


# ----------------------------------------------------------------------------
# setup
# ----------------------------------------------------------------------------


def cmd_setup(args) -> int:
    slug = args.client
    token = args.token
    loc_id = args.location_id

    # 1. Sanity ping with /locations/<id> to confirm token + location pairing
    client = GHLClient(token=token, location_id=loc_id, user_id="setup-tmp")
    try:
        location = client.get_location()
    except GHLError as e:
        print(f"ERROR fetching /locations/{loc_id}: {e}", file=sys.stderr)
        print("Common causes: token wrong, location_id wrong, or token lacks 'locations.readonly' scope.")
        return 2

    loc_obj = location.get("location", location)
    loc_name = loc_obj.get("name", "(unnamed)")
    loc_tz = loc_obj.get("timezone", "UTC")
    print(f"OK  location: {loc_name}  ({loc_id}, {loc_tz})")

    # 2. Discover users to pick author user_id
    user_id = args.user_id
    if not user_id:
        try:
            users = client.list_users()
            if not users:
                print("WARN /users returned empty. Pass --user-id explicitly.")
            elif len(users) == 1:
                user_id = users[0].get("id") or users[0].get("_id") or ""
                print(f"OK  user_id auto-picked: {user_id} ({users[0].get('email', '?')})")
            else:
                print("Multiple users found in this location. Pick one:")
                for u in users:
                    print(f"  - {u.get('id') or u.get('_id')}   {u.get('email', '?')}   {u.get('firstName', '')} {u.get('lastName', '')}")
                print("Re-run with --user-id <id>")
                return 3
        except GHLError as e:
            print(f"WARN listing users failed ({e}). Pass --user-id explicitly.")

    if not user_id:
        return 3

    # 3. Discover social accounts
    try:
        accounts = client.list_accounts()
    except GHLError as e:
        print(f"ERROR listing social accounts: {e}", file=sys.stderr)
        print("Token likely missing 'socialplanner.account.readonly' scope.")
        return 4

    if not accounts:
        print("WARN no social accounts connected to this location.")

    print(f"OK  social accounts: {len(accounts)}")
    by_platform: dict[str, SocialAccount] = {}
    notes: dict[str, str] = {}
    for a in accounts:
        marker = "EXPIRED" if a.is_expired else "ok"
        print(f"     - {a.platform:10s}  {marker:7s}  {a.name}   {a.id}")
        if a.is_expired:
            notes[a.platform] = "OAuth expired — reconnect in GHL UI before scheduling"
            continue
        # Keep first valid per platform
        if a.platform not in by_platform:
            by_platform[a.platform] = a

    accounts_map = {p: acc.id for p, acc in by_platform.items()}

    # 4. Write the TOML
    data = {
        "location": {
            "id": loc_id,
            "user_id": user_id,
            "default_timezone": loc_tz,
            "name": loc_name,
        },
        "accounts": accounts_map,
        "account_notes": notes,
        "brand": {
            "primary": "#000000",
            "handle": "@" + slug.replace("-", ""),
            "domain": "",
        },
        "notes": {
            "discovered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
    path = cfg.write_client_toml(slug, data)
    print(f"\nWrote: {path}")
    print(f"\nNext: add your token to .env as {cfg.slug_to_env_var(slug)}=<your-PIT>")
    print(f"Then:  python -m publisher.cli verify --client {slug}")
    return 0


# ----------------------------------------------------------------------------
# publish
# ----------------------------------------------------------------------------


def cmd_publish(args) -> int:
    client_cfg = cfg.load_client(args.client)
    token = load_token_or_dry(args.client, args.dry_run)

    platforms: list[str] = args.platforms
    if not platforms:
        platforms = list(client_cfg.accounts.keys())
    account_ids = client_cfg.account_ids_for(platforms)
    print(f"OK  client={args.client}  platforms={platforms}  accounts={len(account_ids)}")

    # Resolve schedule
    schedule_iso = parse_schedule(args.schedule, client_cfg.default_timezone)
    print(f"OK  schedule: {args.schedule}  ->  {schedule_iso}")

    # Render media (HTML -> PNG)
    out_dir = Path(args.out_dir or "publisher/.render_cache")
    html_paths = [Path(h) for h in args.html]
    for hp in html_paths:
        if not hp.exists():
            print(f"ERROR html not found: {hp}", file=sys.stderr)
            return 5
    rendered = render_many(html_paths, out_dir, preset=args.size)
    print(f"OK  rendered {len(rendered)} image(s) at preset={args.size}:")
    for r in rendered:
        print(f"     - {r}  ({r.stat().st_size // 1024} KB)")

    if args.dry_run:
        print("\n--dry-run: stopping before upload/schedule. Render artifacts above are real.")
        return 0

    # Live: upload + schedule
    api = GHLClient(token=token, location_id=client_cfg.location_id, user_id=client_cfg.user_id)
    media = []
    for r in rendered:
        up = api.upload_media(r)
        media.append({"url": up.url, "type": mime_for(r), "caption": ""})
        print(f"OK  uploaded -> fileId={up.file_id}  url={up.url}")

    caption = read_caption(args.caption_file, args.caption)
    try:
        resp = api.create_post(
            account_ids=account_ids,
            caption=caption,
            media=media,
            schedule_iso=schedule_iso,
            post_type=args.post_type,
            status="scheduled",
        )
    except GHLError as e:
        print(f"ERROR create_post: {e}", file=sys.stderr)
        return 6

    print("\nOK  scheduled.")
    print(json.dumps(resp, indent=2))
    pid = (resp or {}).get("postId") or (resp or {}).get("id")
    if pid:
        print(f"\nVerify:  python -m publisher.cli verify --client {args.client} --post-id {pid}")
    return 0


# ----------------------------------------------------------------------------
# verify
# ----------------------------------------------------------------------------


def cmd_verify(args) -> int:
    client_cfg = cfg.load_client(args.client)
    token = load_token_or_dry(args.client, dry=False)
    api = GHLClient(token=token, location_id=client_cfg.location_id, user_id=client_cfg.user_id)

    if args.post_id:
        try:
            post = api.get_post(args.post_id)
        except GHLError as e:
            print(f"ERROR get_post({args.post_id}): {e}", file=sys.stderr)
            return 7
        print(json.dumps(post, indent=2))
        return 0

    # List by window
    from_iso = args.from_date or datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")
    to_iso = args.to_date or (
        datetime.now(timezone.utc).replace(day=1)
        .replace(month=(datetime.now(timezone.utc).month % 12) + 1)
        .strftime("%Y-%m-%dT00:00:00.000Z")
    )
    try:
        posts = api.list_posts(from_iso=from_iso, to_iso=to_iso, status_filter=args.status)
    except GHLError as e:
        print(f"ERROR list_posts: {e}", file=sys.stderr)
        return 7
    print(f"Found {len(posts)} post(s) from {from_iso} to {to_iso} (status={args.status}):")
    for p in posts:
        pid = p.get("_id") or p.get("id")
        when = p.get("scheduleDate", "?")
        summary = (p.get("summary") or "")[:80].replace("\n", " ")
        st = p.get("status", "?")
        print(f"  - {pid}  {when}  [{st}]  {summary}")
    return 0


# ----------------------------------------------------------------------------
# token + dry-run helper
# ----------------------------------------------------------------------------


def load_token_or_dry(slug: str, dry: bool) -> str:
    if dry:
        return "dry-run-no-token"
    return cfg.load_token(slug)


# ----------------------------------------------------------------------------
# argparse
# ----------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="publisher",
        description="GHL Social Planner publisher (Private Integration Token, no MCP).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # setup
    sp = sub.add_parser("setup", help="Discover location/accounts/user from a PIT; write clients/<slug>.toml")
    sp.add_argument("--client", required=True, help="Slug (filename in clients/<slug>.toml)")
    sp.add_argument("--token", required=True, help="Private Integration Token (not stored — written to .env separately)")
    sp.add_argument("--location-id", required=True, help="GHL sub-account location ID")
    sp.add_argument("--user-id", help="Author user_id (auto-discovered if location has one user)")
    sp.set_defaults(func=cmd_setup)

    # publish
    pub = sub.add_parser("publish", help="Render HTML, upload to GHL media, schedule a post")
    pub.add_argument("--client", required=True)
    pub.add_argument("--html", required=True, nargs="+", help="HTML file(s). Multiple = carousel.")
    pub.add_argument("--caption", help="Inline caption text")
    pub.add_argument("--caption-file", help="Path to a .txt file with the caption")
    pub.add_argument("--schedule", required=True, help='ISO or "YYYY-MM-DD HH:MM Europe/Athens"')
    pub.add_argument("--platforms", nargs="+", default=None, help="facebook instagram linkedin twitter tiktok. Omit = all configured.")
    pub.add_argument("--size", default=DEFAULT_PRESET, choices=list(PRESETS.keys()), help="Image preset")
    pub.add_argument("--post-type", default="post", choices=["post", "story", "reel"])
    pub.add_argument("--out-dir", default=None, help="Where to drop rendered PNGs (default publisher/.render_cache)")
    pub.add_argument("--dry-run", action="store_true", help="Render only — skip upload+schedule")
    pub.set_defaults(func=cmd_publish)

    # verify
    v = sub.add_parser("verify", help="Get a single post by ID, or list posts in a window")
    v.add_argument("--client", required=True)
    v.add_argument("--post-id", help="Specific post to fetch")
    v.add_argument("--from-date", help="ISO start of listing window")
    v.add_argument("--to-date", help="ISO end of listing window")
    v.add_argument("--status", default="scheduled", choices=["all", "scheduled", "draft", "published", "failed", "in_review"])
    v.set_defaults(func=cmd_verify)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

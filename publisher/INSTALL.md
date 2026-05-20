# INSTALL — onboarding a new client

This is the doc to hand to a client (or run yourself) the first time you set up the publisher for a GHL sub-account.

## What the client needs to do (once)

### 1. Create a Private Integration Token in GHL

1. Log into GHL → switch to the correct sub-account
2. Go to **Settings → Private Integrations**
3. Click **Create New Integration**
4. Name it something like `Claude Publisher`
5. **Select these scopes:**
   - `locations.readonly`
   - `users.readonly`
   - `socialplanner/account.readonly`
   - `socialplanner/post.readonly`
   - `socialplanner/post.write`
   - `socialplanner/oauth.readonly`
   - `medias.readonly`
   - `medias.write`
6. Click **Create** — the token is shown **only once**. Copy it immediately.
7. Find your **Location ID** (in the URL of any sub-account page: `https://app.gohighlevel.com/v2/location/<LOCATION_ID>/...`)
8. Send the token + location ID to whoever runs the publisher.

### 2. Make sure social accounts are connected

In the same sub-account: **Marketing → Social Planner → Socials**.

Each platform must show a green "connected" indicator. If any are expired or disconnected, reconnect them (each one is ~30 seconds and requires logging into that platform).

Once accounts are reconnected, the publisher's `setup` command will pick them up automatically.

## What you (the operator) do — once per client

### 1. Add the token to `.env`

```bash
# In /path/to/carousel-system/.env (NOT committed to git)
GHL_PIT_<SLUG>=pit-xxxxxxxxxxxxxxxxxxxx
```

Replace `<SLUG>` with an uppercase identifier with underscores instead of hyphens. Example: client `acme-co` → variable `GHL_PIT_ACME_CO`.

### 2. Run `setup`

```bash
cd /path/to/carousel-system
python -m publisher.cli setup \
  --client acme-co \
  --token pit-xxxxxxxxxxxxxxxxxxxx \
  --location-id <LOCATION_ID>
```

This will:
- Verify the token works (hits `/locations/<id>`)
- Auto-pick the user_id (if there's one user in the location) or list users for you to choose
- List connected social accounts, flagging any with expired OAuth tokens
- Write `publisher/clients/acme-co.toml` with everything discovered

### 3. Verify it works

```bash
python -m publisher.cli verify --client acme-co --status scheduled
```

If the call returns successfully (even with `Found 0 posts`), the token + scopes are wired correctly.

### 4. Schedule a first test post

```bash
python -m publisher.cli publish \
  --client acme-co \
  --html test.html \
  --caption "Testing the publisher pipeline." \
  --schedule "2026-12-31 10:00 UTC" \
  --platforms facebook instagram \
  --size ig_portrait \
  --dry-run
```

The `--dry-run` flag renders the image and prints what it would do, without uploading or scheduling. Drop the flag when ready.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `GHL 401 ... invalid_token` on `setup` | PIT wrong or expired | Recreate in GHL UI |
| `GHL 403 ... scope missing` | Token lacks required scope | Add the scope (see step 1 above) and recreate token |
| `Token likely missing 'socialplanner.account.readonly' scope` | Same | Same |
| `setup` shows EXPIRED next to a platform | OAuth on that platform lapsed | Reconnect in GHL UI → Social Planner → Socials, then re-run `setup` |
| `userId must be a string` from `create_post` | `user_id` empty in TOML | Re-run `setup` with `--user-id <correct-user-id>` |
| Image renders blank or wrong fonts | Webfonts didn't load before screenshot | Increase `wait_extra_ms` in `render.py` |
| `verify` returns `[]` but posts exist in UI | Read endpoint differs by GHL build | Check the network tab in the GHL UI and adjust `GHLClient.list_posts` |

## Rotating a token

1. Create a new PIT in GHL with the same scopes
2. Update `.env`: replace the value of `GHL_PIT_<SLUG>` with the new token
3. Delete the old PIT in GHL UI

No code changes needed.

## Removing a client

```bash
# Delete the per-client config + the env var
rm publisher/clients/<slug>.toml
# Then remove the GHL_PIT_<SLUG>= line from .env
```

Plus revoke the PIT in GHL UI to be safe.

---
name: gsc-mcp
description: Set up and use the Google Search Console MCP (AminForou/mcp-gsc) so Claude can read a site's real Google search data - clicks, impressions, queries, positions, indexing and sitemaps. Use when Sam asks to connect Search Console / GSC, for SEO data on his or a client's site, "which keywords bring traffic", indexing problems, sitemap submission, or before any gsc-* skill when its tools are missing.
---

# Google Search Console MCP

Repo: https://github.com/AminForou/mcp-gsc (MIT, single maintainer; also sells a hosted version, which isn't needed). PyPI package: `mcp-search-console`.

Companion skills (installed): `gsc-seo-weekly-report`, `gsc-content-opportunities`, `gsc-indexing-audit`, `gsc-cannibalization-check`.

## Status

**Not connected yet.** It needs a Google credential from Sam. Don't put the tool in `.mcp.json` until the credential exists, or every session will start with a failing server.

## One-time setup (Sam, ~10 minutes)

Cloud sessions can't open a browser login, so use a **service account** (copied from the README, Option B):

1. Google Cloud Console: create or select a project.
2. Enable the **Search Console API**.
3. Credentials → Create Credentials → **Service Account**.
4. Keys tab → Add Key → Create new key → **JSON** → download.
5. In Search Console, for each property (samtrabulsi.com, client sites): Settings → Users and permissions → Add user → paste the service-account email → **Full** (or Restricted for read-only).
6. Store the JSON **as an environment secret, never in this repo**. Read the `environment.secrets` page of the cloud docs (`read_documentation`) for where Sam adds it, e.g. a secret named `GSC_SA_JSON` holding the whole file.

## Activate (Claude, after the secret exists)

```bash
mkdir -p ~/.config/gsc && printf '%s' "$GSC_SA_JSON" > ~/.config/gsc/service_account.json && chmod 600 ~/.config/gsc/service_account.json
```
Then add to `.mcp.json` (keep any other servers) and restart the session:
```json
"mcp-search-console": {
  "command": "uvx",
  "args": ["mcp-search-console"],
  "env": {
    "GSC_CREDENTIALS_PATH": "/root/.config/gsc/service_account.json",
    "GSC_SKIP_OAUTH": "true",
    "GSC_DATA_STATE": "all"
  }
}
```
The secret-to-file step must run each session (a SessionStart hook can do it, via the `session-start-hook` skill). If startup fails with `No module named 'mcp.server.fastmcp'`, add `"--with", "mcp<2"` before `"mcp-search-console"` in `args`. This repo's GEO server needed the same fix on 2026-10-10.

## Tools

`get_capabilities` (call first), `list_properties`, `get_search_analytics`, `get_performance_overview`, `compare_search_periods`, `get_search_by_page_query`, `get_advanced_search_analytics`, `inspect_url_enhanced`, `batch_url_inspection`, `check_indexing_issues`, `get_sitemaps`, `list_sitemaps_enhanced`, `manage_sitemaps`. Destructive tools (`add_site`, `delete_site`, `delete_sitemap`) stay off unless `GSC_ALLOW_DESTRUCTIVE=true`. Leave them off.

## Use

- Monthly client SEO report: `gsc-seo-weekly-report` (adapt to monthly), then `openseo-seo-report` or an artifact page.
- After a hack cleanup (growsuccessonline.com, 2026-10): check Search Console → Security issues, then run `gsc-indexing-audit` on top pages.
- Never share one client's data with another; one property per report.

---
name: claude-seo-cloud
description: How to run the Claude SEO plugin (AgriciDaniel/claude-seo, 26 seo-* skills + 19 agents) inside Sam's cloud sessions - one-time runtime setup, and the workaround for its proxy block on live page fetches. Read this before using any seo-* skill or /seo command in a cloud session, or when a Claude SEO script says "runtime is not ready" or "Refusing configured HTTP proxy".
---

# Claude SEO in cloud sessions

The plugin is enabled at project scope in `.claude/settings.json` (`claude-seo@agricidaniel-claude-seo`, marketplace `AgriciDaniel/claude-seo`, MIT). Cloud sessions install it at startup; its launcher lives at
`~/.claude/plugins/cache/agricidaniel-claude-seo/claude-seo/<version>/scripts/claude-seo` (skills call it as `${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo`).

## 1. Setup (once per new cloud session, about 1-2 minutes)

```bash
P=$(ls -d ~/.claude/plugins/cache/agricidaniel-claude-seo/claude-seo/*/scripts/claude-seo | tail -1)
"$P" doctor || "$P" setup        # isolated Python venv + Chromium; "Runtime: ready" when done
```

## 2. Live fetches are blocked here; use saved HTML

Its URL-safety guard refuses the session's local HTTP proxy (`Refusing configured HTTP proxy '127.0.0.1'`), so scripts that fetch URLs themselves (fetch_page, crawls, PageSpeed/Lighthouse runs) fail in the cloud. **Never unset the proxy.** Instead fetch with curl and pass the file:

```bash
curl -sSL -A 'Mozilla/5.0' --max-time 30 https://site.com/ -o page.html
"$P" run parse_html.py --url https://site.com/ --json page.html     # title, meta, headings, schema, OG, word count
```
Work from saved HTML (plus robots.txt / sitemap.xml fetched with curl) for audits. On Sam's own computer the live commands work normally.

## 3. Which SEO tool for what

| Need | Use |
|---|---|
| AI-search visibility score + llms.txt / schema fixes, hacked-site spam scan | `geo-optimizer` (works fully in the cloud) |
| Deep on-page / technical / schema / E-E-A-T / local SEO review, content briefs, SEO plans | Claude SEO `seo-*` skills (with the saved-HTML workaround) |
| Real Google search data (clicks, queries, indexing) | `gsc-mcp` + `gsc-*` (needs Sam's credential) |
| Keyword volumes, competitors, backlinks | `openseo-*` (needs account; paid data) |

Notes: the plugin adds about 4.5k tokens of skill descriptions to every session; full `/seo audit` runs many sub-agents and is token-heavy, so prefer a single leaf skill (e.g. `seo-page`, `seo-schema`, `seo-local`). Its PostToolUse hook validates JSON-LD in files Claude edits and reports schema errors; that's expected. Don't use its curl-to-bash uninstall line; disable with `claude plugin disable claude-seo@agricidaniel-claude-seo --scope project`.

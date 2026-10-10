---
name: openseo
description: Set up and use OpenSEO (every-app/open-seo), the pay-as-you-go open-source alternative to Semrush/Ahrefs, through its MCP, for keyword research, rank tracking, competitor and backlink analysis, site audits, local SEO and AI-visibility tracking. Use when Sam asks for keyword research, competitors' keywords, backlinks, rank tracking, local/Google Maps SEO, or a Semrush/Ahrefs-style analysis, or before any openseo-* skill when its tools are missing.
---

# OpenSEO

Repo: https://github.com/every-app/open-seo (MIT). Site: https://openseo.so. Data comes from **DataForSEO**, paid per request.

Companion skills (installed, from the repo): `openseo-seo-coach` (start here), `openseo-seo-project-setup`, `openseo-keyword-research`, `openseo-keyword-clustering`, `openseo-competitor-analysis`, `openseo-competitive-landscape`, `openseo-link-prospecting`, `openseo-local-seo`, `openseo-seo-audit`, `openseo-ai-visibility-audit`, `openseo-ai-prompt-research`, `openseo-seo-report`.

## Status

**Not connected yet.** It needs an OpenSEO account (hosted) or a DataForSEO key (self-hosted). Sam decides which.

## Options

| Route | Cost | Setup |
|---|---|---|
| **Hosted** (app.openseo.so) | Free account to try; $10/mo subscription supports the project; data billed at DataForSEO cost **+28%** | Sign up, then add the MCP below and approve the login |
| **Self-hosted** (Docker or Cloudflare free plan) | DataForSEO cost only | Follow the repo's `docs/SELF_HOSTING_CLOUDFLARE.md` and `docs/DATAFORSEO_API_KEY.md`; a developer job |

Hosted MCP entry for `.mcp.json` (from the repo's plugin config). Add it only once Sam has an account:
```json
"openseo": { "type": "http", "url": "https://app.openseo.so/mcp" }
```

## Rules

- **Every call costs money.** State the scope (domains, keyword count, locations) and ask before big pulls: full backlink exports, many locations, long keyword lists.
- **Use the free tools first:** `geo-optimizer` for AI visibility and technical checks, and `gsc-mcp` for a site's own real search data. OpenSEO is for market data: competitors, keyword volumes, backlinks.
- Arabic keyword research: set the right location and language (e.g. Lebanon, UAE, Saudi Arabia) per DataForSEO; don't assume English/US.

/* Brand Victory Operations Dashboard — local server (zero dependencies).
 *
 * Serves the static pages and exposes two API routes:
 *   POST /api/instagram/refresh  → Apify Instagram profile scrape (token from .env)
 *   POST /api/script/generate    → draft script in Sam's voice (Claude)
 *
 * Hard rule: secrets are read from .env on the server only. They never reach
 * the browser, the page source, or the chat. Run with:  node server.js
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const PORT = process.env.PORT || 4000;
const IG_USERNAME = 'samtrabulsi';
const APIFY_ACTOR = 'apify~instagram-profile-scraper';
const ANTHROPIC_MODEL = 'claude-sonnet-4-6';

// ---- Load .env (simple KEY=VALUE parser; never logged) ----
function loadEnv() {
  const file = path.join(ROOT, '.env');
  if (!fs.existsSync(file)) return {};
  const env = {};
  for (const raw of fs.readFileSync(file, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    env[line.slice(0, eq).trim()] = val;
  }
  return env;
}
const ENV = { ...loadEnv(), ...process.env };

// Brand voice reference, read fresh each request so edits to brand-voice.md
// take effect without a server restart.
function loadBrandVoice() {
  const file = path.join(ROOT, 'brand-voice.md');
  try { return fs.readFileSync(file, 'utf8'); } catch { return ''; }
}

// ---- Static file serving ----
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

function sendJson(res, status, obj) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(obj));
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/' || urlPath === '') urlPath = '/dashboard.html';
  // prevent path traversal
  const safe = path.normalize(urlPath).replace(/^(\.\.[/\\])+/, '');
  const filePath = path.join(ROOT, safe);
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end('Forbidden'); return; }
  // never serve dotfiles (.env, .gitignore, etc.) — keeps secrets off the wire
  if (safe.split(/[/\\]/).some((seg) => seg.startsWith('.') && seg.length > 1)) {
    res.writeHead(403); res.end('Forbidden'); return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end('<h1 style="font-family:sans-serif;color:#fff;background:#0A0A0F;padding:40px">404 — not found. <a style="color:#5B79F0" href="/dashboard.html">Back to Command Center</a></h1>');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
    res.end(data);
  });
}

function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', (c) => { body += c; if (body.length > 1e6) req.destroy(); });
    req.on('end', () => { try { resolve(body ? JSON.parse(body) : {}); } catch { resolve({}); } });
  });
}

// ---- Apify: shared actor runner ----
async function runActor(input) {
  const token = ENV.APIFY_TOKEN;
  if (!token) {
    throw new Error('No Apify token found. Add APIFY_TOKEN to dashboard/.env (see .env.example), then restart the server.');
  }
  const url = `https://api.apify.com/v2/acts/${APIFY_ACTOR}/run-sync-get-dataset-items?token=${encodeURIComponent(token)}`;
  let res;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
  } catch (e) {
    throw new Error('Network error reaching Apify: ' + e.message);
  }
  if (res.status === 401 || res.status === 403) {
    throw new Error('Apify rejected the token (auth error). Check APIFY_TOKEN in dashboard/.env.');
  }
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Apify run failed (${res.status}). ${txt.slice(0, 200)}`);
  }
  return res.json();
}

function profileEngagement(profile) {
  const latest = profile.latestPosts || profile.posts || [];
  const eng = (Array.isArray(latest) ? latest : []).slice(0, 12).map((p) => (p.likesCount ?? p.likes ?? 0) + (p.commentsCount ?? p.comments ?? 0));
  const followers = profile.followersCount ?? profile.followers ?? null;
  const total = eng.reduce((a, b) => a + b, 0);
  const avg = eng.length ? total / eng.length : 0;
  return {
    followers,
    posts: profile.postsCount ?? profile.posts ?? (Array.isArray(latest) ? latest.length : 0),
    avgEngagement: Math.round(avg),
    engagementRate: followers ? +((avg / followers) * 100).toFixed(2) : null,
  };
}

// ---- Instagram profile scrape (own account, full detail) ----
async function refreshInstagram() {
  const items = await runActor({ usernames: [IG_USERNAME], resultsLimit: 12 });
  const profile = Array.isArray(items) ? items.find((x) => x && (x.username || x.followersCount != null)) || items[0] : items;
  if (!profile) {
    throw new Error('Apify returned no data for @' + IG_USERNAME + '. The username or actor input may need adjusting.');
  }

  const latest = profile.latestPosts || profile.posts || [];
  const normalizeType = (t) => {
    const s = String(t || '').toLowerCase();
    if (s.includes('video') || s.includes('reel') || s.includes('clip')) return 'Reel';
    if (s.includes('sidecar') || s.includes('carousel')) return 'Carousel';
    if (s.includes('image') || s.includes('photo')) return 'Image';
    return 'Other';
  };
  const recentPosts = (Array.isArray(latest) ? latest : []).slice(0, 12).map((p) => ({
    caption: (p.caption || '').replace(/\s+/g, ' ').slice(0, 90),
    likes: p.likesCount ?? p.likes ?? 0,
    comments: p.commentsCount ?? p.comments ?? 0,
    type: normalizeType(p.type || p.productType || p.__typename),
    timestamp: p.timestamp || p.takenAtTimestamp || null,
    url: p.url || (p.shortCode ? `https://www.instagram.com/p/${p.shortCode}/` : ''),
  }));

  const recentEngagement = recentPosts.map((p) => (p.likes || 0) + (p.comments || 0));
  const reach = recentEngagement.reduce((a, b) => a + b, 0);
  const followers = profile.followersCount ?? profile.followers ?? null;
  const avgEng = recentEngagement.length ? reach / recentEngagement.length : 0;
  const engagementRate = followers ? +((avgEng / followers) * 100).toFixed(2) : null;

  return {
    username: profile.username || IG_USERNAME,
    followers,
    posts: profile.postsCount ?? profile.posts ?? recentPosts.length,
    reach,
    engagementRate,
    recentEngagement,
    recentPosts,
  };
}

// ---- Competitor benchmarking (public profile-level metrics only) ----
// User-authorized: tracks public follower/engagement numbers for a named list
// of profiles. Does NOT harvest followers or audience data of anyone.
async function refreshCompetitors(body) {
  const list = Array.isArray(body.usernames) ? body.usernames : [];
  const clean = [...new Set(list.map((u) => String(u).trim().replace(/^@/, '').toLowerCase()).filter(Boolean))].slice(0, 10);
  if (!clean.length) throw new Error('Add at least one competitor username first.');

  const items = await runActor({ usernames: clean, resultsLimit: 12 });
  const arr = Array.isArray(items) ? items : [items];
  const byUser = {};
  for (const p of arr) {
    if (p && p.username) byUser[String(p.username).toLowerCase()] = p;
  }
  const results = clean.map((u) => {
    const p = byUser[u];
    if (!p) return { username: u, error: 'No public data returned (private or not found).' };
    return { username: p.username || u, ...profileEngagement(p) };
  });
  return { competitors: results, fetchedAt: Date.now() };
}

// ---- Script generation ----
function buildPrompt({ title, note, platform, contentType }) {
  const voice = loadBrandVoice();
  const typeLine = contentType && contentType !== 'auto'
    ? `\nLEAN INTO THIS CONTENT TYPE: ${contentType} post (per Sam's three content types).`
    : '';
  return `You are Sam Trabulsi's ghostwriter, drafting a short-form ${platform || 'Instagram'} video script in his exact voice.

${voice ? `Here is Sam's brand voice and frameworks — follow them precisely:\n\n${voice}\n\n---\n` : ''}
TOPIC: ${title}${note ? `\nCONTEXT/ANGLE: ${note}` : ''}${typeLine}

Write the script now. Structure it as:
HOOK: one punchy, contrarian opening line that stops the scroll (a reframe is ideal).
BODY: teach ONE clear thing — name the wrong assumption, reveal the real cause, give one concrete shift. Short lines.
CTA: one specific action in Sam's style.

Output ONLY the script with the HOOK / BODY / CTA labels. No intro, no explanation, no sign-off, no emojis.`;
}

async function generateViaApi(prompt) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ENV.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: ENV.ANTHROPIC_MODEL || ANTHROPIC_MODEL,
      max_tokens: 800,
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    if (res.status === 401) throw new Error('Anthropic rejected the API key. Check ANTHROPIC_API_KEY in dashboard/.env.');
    throw new Error(`Claude API error (${res.status}). ${txt.slice(0, 200)}`);
  }
  const data = await res.json();
  const text = (data.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('\n').trim();
  if (!text) throw new Error('Claude returned an empty script.');
  return text;
}

function generateViaCli(prompt) {
  // Fallback: shell out to the `claude` CLI if it is installed and no API key is set.
  return new Promise((resolve, reject) => {
    const child = spawn('claude', ['-p', prompt], { timeout: 120000 });
    let out = '', err = '';
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (err += d));
    child.on('error', () => reject(new Error('No ANTHROPIC_API_KEY in .env and the `claude` CLI is not available. Add ANTHROPIC_API_KEY to dashboard/.env to enable script generation.')));
    child.on('close', (code) => {
      if (code === 0 && out.trim()) resolve(out.trim());
      else reject(new Error('Script generation via the claude CLI failed. ' + err.slice(0, 200)));
    });
  });
}

async function generateScript(body) {
  if (!body.title || !body.title.trim()) throw new Error('Missing a topic/title to write about.');
  const prompt = buildPrompt(body);
  if (ENV.ANTHROPIC_API_KEY) return { script: await generateViaApi(prompt) };
  return { script: await generateViaCli(prompt) };
}

// ---- Router ----
const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];

  if (req.method === 'POST' && url === '/api/instagram/refresh') {
    try { sendJson(res, 200, await refreshInstagram()); }
    catch (e) { sendJson(res, 502, { error: e.message }); }
    return;
  }

  if (req.method === 'POST' && url === '/api/competitors/refresh') {
    try { sendJson(res, 200, await refreshCompetitors(await readBody(req))); }
    catch (e) { sendJson(res, 502, { error: e.message }); }
    return;
  }

  if (req.method === 'POST' && url === '/api/script/generate') {
    try { sendJson(res, 200, await generateScript(await readBody(req))); }
    catch (e) { sendJson(res, 502, { error: e.message }); }
    return;
  }

  if (req.method === 'GET') { serveStatic(req, res); return; }

  res.writeHead(405); res.end('Method Not Allowed');
});

server.listen(PORT, () => {
  const hasApify = !!ENV.APIFY_TOKEN;
  const hasClaude = !!ENV.ANTHROPIC_API_KEY;
  console.log(`\n  Brand Victory Dashboard running →  http://localhost:${PORT}\n`);
  console.log(`  Apify token:     ${hasApify ? 'loaded ✓' : 'missing (add APIFY_TOKEN to .env for live Instagram data)'}`);
  console.log(`  Anthropic key:   ${hasClaude ? 'loaded ✓' : 'missing (add ANTHROPIC_API_KEY to .env, or rely on the claude CLI, for script generation)'}`);
  console.log(`\n  Press Ctrl+C to stop.\n`);
});

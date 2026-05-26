/* Brand Victory Operations Dashboard — shared front-end logic.
   Renders the sidebar nav on every page and provides localStorage helpers. */

(function () {
  // ---- Navigation (single source of truth, reused on every page) ----
  const NAV = [
    { href: 'dashboard.html',   label: 'Command Center',   ico: '◆' },
    { href: 'pipeline.html',    label: 'Content Pipeline', ico: '▦' },
    { href: 'research.html',    label: 'Content Research', ico: '✦' },
    { href: 'performance.html', label: 'Performance',      ico: '📈' },
    { href: 'competitors.html', label: 'Competitors',      ico: '⚔' },
    { href: 'sops.html',        label: 'SOP Library',      ico: '❏' },
    { href: 'tasks.html',       label: 'Tasks',            ico: '✓' },
  ];

  function currentFile() {
    const path = location.pathname.split('/').pop();
    return path === '' ? 'dashboard.html' : path;
  }

  function renderNav() {
    const root = document.getElementById('nav-root');
    if (!root) return;
    const here = currentFile();
    root.innerHTML = `
      <aside class="sidebar">
        <div class="brand">
          <div class="mark">B</div>
          <div>
            <div class="name">Brand Victory</div>
            <div class="sub">Ops Dashboard</div>
          </div>
        </div>
        <nav class="nav">
          ${NAV.map(n => `
            <a href="${n.href}" class="${n.href === here ? 'active' : ''}">
              <span class="ico">${n.ico}</span><span>${n.label}</span>
            </a>`).join('')}
        </nav>
        <div class="foot"><span class="dot"></span>Instagram • @samtrabulsi<br>Local build · v1</div>
      </aside>`;
  }

  // ---- localStorage store ----
  const PREFIX = 'bv:';
  const Store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(PREFIX + key);
        return raw == null ? fallback : JSON.parse(raw);
      } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch {}
    },
    remove(key) { localStorage.removeItem(PREFIX + key); },
  };

  // ---- Toast ----
  let toastEl, toastTimer;
  function toast(msg, isError) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.className = 'toast show' + (isError ? ' error' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastEl.className = 'toast'; }, 2600);
  }

  // ---- Trend history: append one dated metrics snapshot per day ----
  function recordHistory(metrics) {
    if (!metrics || metrics.followers == null) return;
    const hist = Store.get('history', []);
    const today = new Date(metrics.fetchedAt || Date.now()).toISOString().slice(0, 10);
    const point = {
      date: today,
      followers: metrics.followers,
      posts: metrics.posts,
      reach: metrics.reach,
      engagementRate: metrics.engagementRate,
    };
    const last = hist[hist.length - 1];
    if (last && last.date === today) hist[hist.length - 1] = point; // overwrite same-day
    else hist.push(point);
    Store.set('history', hist.slice(-120)); // keep ~4 months of daily points
  }

  // ---- Export / import all dashboard data ----
  const DATA_KEYS = ['metrics', 'history', 'pipeline', 'research', 'sops', 'tasks', 'competitors', 'competitorList'];
  function exportData() {
    const bundle = { _app: 'brand-victory-dashboard', _exportedAt: new Date().toISOString() };
    DATA_KEYS.forEach((k) => { bundle[k] = Store.get(k, null); });
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `brand-victory-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
  function importData(file, done) {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result);
        if (data._app !== 'brand-victory-dashboard') throw new Error('Not a dashboard backup file.');
        DATA_KEYS.forEach((k) => { if (data[k] != null) Store.set(k, data[k]); });
        done(null);
      } catch (e) { done(e); }
    };
    reader.onerror = () => done(new Error('Could not read file.'));
    reader.readAsText(file);
  }

  // ---- Helpers ----
  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

  function fmt(n) {
    if (n == null || isNaN(n)) return '—';
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
    return String(n);
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // POST JSON to a local API route; throws on non-OK with a readable message.
  async function api(path, body) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    let data = null;
    try { data = await res.json(); } catch {}
    if (!res.ok) {
      const msg = (data && (data.error || data.message)) || `Request failed (${res.status})`;
      throw new Error(msg);
    }
    return data;
  }

  document.addEventListener('DOMContentLoaded', renderNav);

  window.BV = { Store, toast, uid, fmt, escapeHtml, api, recordHistory, exportData, importData, NAV, PIPELINE_COLUMNS: ['Idea', 'Scripted', 'Recorded', 'Scheduled', 'Published'] };
})();

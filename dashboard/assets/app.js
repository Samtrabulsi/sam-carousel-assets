/* Brand Victory Operations Dashboard — shared front-end logic.
   Renders the sidebar nav on every page and provides localStorage helpers. */

(function () {
  // ---- Navigation (single source of truth, reused on every page) ----
  const NAV = [
    { href: 'dashboard.html',   label: 'Command Center',   ico: '◆' },
    { href: 'pipeline.html',    label: 'Content Pipeline', ico: '▦' },
    { href: 'research.html',    label: 'Content Research', ico: '✦' },
    { href: 'performance.html', label: 'Performance',      ico: '📈' },
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

  window.BV = { Store, toast, uid, fmt, escapeHtml, api, NAV, PIPELINE_COLUMNS: ['Idea', 'Scripted', 'Recorded', 'Scheduled', 'Published'] };
})();

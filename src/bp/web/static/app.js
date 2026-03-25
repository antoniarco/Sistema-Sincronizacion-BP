/* Sistema B — Web UI JavaScript */

// ── Toast Notifications ──────────────────────────────────

function toast(message, type = 'success') {
  const container = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

// ── API Helper ───────────────────────────────────────────

async function api(method, url, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!data.ok) {
    toast(data.message, 'error');
    return null;
  }
  return data;
}

// ── Safe DOM helpers ─────────────────────────────────────
// All dynamic content uses textContent or DOM APIs to prevent XSS.
// Only static, developer-controlled markup uses template literals.

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'className') e.className = v;
    else if (k === 'textContent') e.textContent = v;
    else if (k === 'onclick') e.addEventListener('click', v);
    else if (k === 'type') e.type = v;
    else if (k === 'value') e.value = v;
    else if (k === 'placeholder') e.placeholder = v;
    else if (k === 'min') e.min = v;
    else if (k === 'max') e.max = v;
    else if (k === 'checked') e.checked = v;
    else if (k === 'htmlFor') e.htmlFor = v;
    else if (k === 'selected') e.selected = v;
    else if (k === 'id') e.id = v;
    else if (k === 'title') e.title = v;
    else if (k.startsWith('data-')) e.setAttribute(k, v);
    else e.setAttribute(k, v);
  }
  for (const c of children) {
    if (typeof c === 'string') e.appendChild(document.createTextNode(c));
    else if (c) e.appendChild(c);
  }
  return e;
}

// ── Dashboard ────────────────────────────────────────────

let refreshInterval = null;

async function loadDashboard() {
  const main = document.getElementById('main-content');
  main.replaceChildren(
    el('div', { className: 'loading' }, [
      el('div', { className: 'spinner' }),
      'Cargando...'
    ])
  );

  const data = await api('GET', '/api/status');
  if (!data) return;

  if (!data.initialized) {
    main.replaceChildren(
      el('div', { className: 'empty-state' }, [
        el('div', { className: 'icon', textContent: '📥' }),
        el('h2', { textContent: 'Bienvenido a Sistema B' }),
        el('p', { textContent: 'Aun no has descargado los modelos. Haz clic para empezar.' }),
        el('button', { className: 'btn btn-primary', onclick: doGet, textContent: '📥 Descargar modelos' }),
      ])
    );
    return;
  }

  const fragment = document.createDocumentFragment();

  // Action bar
  fragment.appendChild(
    el('div', { className: 'action-bar' }, [
      el('button', { className: 'btn btn-primary', onclick: doGet, textContent: '📥 Actualizar modelos' }),
    ])
  );

  // Model cards
  const grid = el('div', { className: 'models-grid' });
  for (const m of data.models) {
    grid.appendChild(renderModelCard(m, data.user));
  }
  fragment.appendChild(grid);

  main.replaceChildren(fragment);

  // History (loaded after cards are shown)
  const histData = await api('GET', '/api/history');
  if (histData && histData.entries.length > 0) {
    main.appendChild(renderHistory(histData.entries.slice(0, 10)));
  }
}

function renderModelCard(m, user) {
  // Status badge
  let statusBadge;
  if (m.local_status === 'synced') {
    statusBadge = el('span', { className: 'badge badge-green', textContent: '✅ Al dia' });
  } else if (m.local_status === 'modified') {
    statusBadge = el('span', { className: 'badge badge-yellow', textContent: '✏️ Con cambios' });
  } else {
    statusBadge = el('span', { className: 'badge badge-red', textContent: '⬇️ Desactualizado' });
  }

  // Lock badge
  let lockBadge;
  if (m.lock) {
    if (m.lock.is_mine) {
      lockBadge = el('span', { className: 'badge badge-cyan', textContent: `🔒 Reservado por ti (${m.lock.hours}h)` });
    } else {
      lockBadge = el('span', { className: 'badge badge-yellow', textContent: `🔒 ${m.lock.user} (${m.lock.hours}h)` });
    }
  } else {
    lockBadge = el('span', { className: 'badge badge-green', textContent: '🔓 Libre' });
  }

  // Icon
  let icon = '📄';
  if (m.lock && m.lock.is_mine && m.local_status === 'modified') icon = '📝';
  else if (m.lock && !m.lock.is_mine) icon = '🔒';
  else if (m.local_status === 'modified') icon = '✏️';
  else if (m.local_status === 'outdated') icon = '⬇️';

  // Actions
  const actions = el('div', { className: 'model-actions' }, [
    el('button', { className: 'btn btn-ghost btn-sm', onclick: () => doOpen(m.name), textContent: '📂 Abrir en Excel' }),
    el('button', { className: 'btn btn-ghost btn-sm', onclick: () => doDownload(m.name), textContent: '⬇️ Descargar' }),
  ]);

  if (!m.lock) {
    actions.appendChild(
      el('button', { className: 'btn btn-primary btn-sm', onclick: () => doLock(m.name), textContent: '🔒 Reservar' })
    );
  } else if (m.lock.is_mine) {
    if (m.local_status === 'modified') {
      actions.appendChild(
        el('button', { className: 'btn btn-green btn-sm', onclick: () => showPushModal(m.name), textContent: '📤 Subir cambios' })
      );
    }
    actions.appendChild(
      el('button', { className: 'btn btn-yellow btn-sm', onclick: () => doUnlock(m.name), textContent: '🔓 Liberar' })
    );
  } else {
    actions.appendChild(
      el('button', { className: 'btn btn-red btn-sm', onclick: () => doForceUnlock(m.name), title: 'Solo admin', textContent: '⚡ Forzar liberacion' })
    );
  }

  // Meta
  const card = el('div', { className: 'model-card' }, [
    el('div', { className: 'model-header' }, [
      el('div', { className: 'model-name' }, [
        el('span', { className: 'icon', textContent: icon }),
        m.name,
      ]),
      el('div', { className: 'model-badges' }, [statusBadge, lockBadge]),
    ]),
  ]);

  if (m.last_change) {
    card.appendChild(
      el('div', { className: 'model-meta', textContent: `Ultimo cambio: ${m.last_author} · ${m.last_date} · "${m.last_change}"` })
    );
  }

  card.appendChild(actions);
  return card;
}

function renderHistory(entries) {
  const tbody = el('tbody');
  for (const e of entries) {
    const icon = e.action === 'revert' ? '⏪' : '📤';
    tbody.appendChild(
      el('tr', {}, [
        el('td', { textContent: icon }),
        el('td', {}, [el('strong', { textContent: `v${e.version}` })]),
        el('td', { textContent: e.model }),
        el('td', { textContent: e.author }),
        el('td', { textContent: e.date }),
        el('td', { textContent: e.comment }),
      ])
    );
  }

  const table = el('table', { className: 'history-table' }, [
    el('thead', {}, [
      el('tr', {}, [
        el('th', { textContent: '' }),
        el('th', { textContent: 'Version' }),
        el('th', { textContent: 'Modelo' }),
        el('th', { textContent: 'Autor' }),
        el('th', { textContent: 'Fecha' }),
        el('th', { textContent: 'Comentario' }),
      ]),
    ]),
    tbody,
  ]);

  return el('div', { className: 'history-section' }, [
    el('h2', { textContent: '📜 Historial reciente' }),
    table,
  ]);
}

// ── Actions ──────────────────────────────────────────────

async function doGet() {
  toast('Descargando ultima version...', 'info');
  const data = await api('POST', '/api/get');
  if (data) {
    toast(data.message);
    loadDashboard();
  }
}

async function doLock(model) {
  const data = await api('POST', `/api/lock/${encodeURIComponent(model)}`);
  if (data) {
    toast(data.message);
    loadDashboard();
  }
}

async function doUnlock(model) {
  const data = await api('POST', `/api/unlock/${encodeURIComponent(model)}`);
  if (data) {
    toast(data.message);
    loadDashboard();
  }
}

async function doForceUnlock(model) {
  if (!confirm(`¿Forzar liberacion de "${model}"? Esta accion requiere permisos de admin.`)) return;
  const data = await api('POST', `/api/force-unlock/${encodeURIComponent(model)}`);
  if (data) {
    toast(data.message);
    loadDashboard();
  }
}

async function doOpen(model) {
  await api('POST', `/api/open/${encodeURIComponent(model)}`);
}

function doDownload(model) {
  const link = document.createElement('a');
  link.href = `/api/download/${encodeURIComponent(model)}`;
  link.download = model;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

// ── Push Modal ───────────────────────────────────────────

let pushModel = '';

function showPushModal(model) {
  pushModel = model;
  document.getElementById('push-modal').classList.add('active');
  const input = document.getElementById('push-comment');
  input.value = '';
  input.focus();
}

function closePushModal() {
  document.getElementById('push-modal').classList.remove('active');
}

async function doPush() {
  const comment = document.getElementById('push-comment').value.trim();
  if (!comment) {
    toast('Escribe un comentario describiendo tus cambios', 'error');
    return;
  }
  closePushModal();
  toast('Subiendo cambios...', 'info');
  const data = await api('POST', '/api/push', { comment });
  if (data) {
    toast(data.message);
    loadDashboard();
  }
}

// Handle Enter key in push modal
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && document.getElementById('push-modal').classList.contains('active')) {
    e.preventDefault();
    doPush();
  }
  if (e.key === 'Escape') {
    closePushModal();
  }
});

// ── Settings ─────────────────────────────────────────────

async function loadSettings() {
  const main = document.getElementById('main-content');
  main.replaceChildren(
    el('div', { className: 'loading' }, [
      el('div', { className: 'spinner' }),
      'Cargando...'
    ])
  );

  const data = await api('GET', '/api/settings');
  if (!data) return;

  const s = data;

  // Build form using safe DOM methods
  const fragment = document.createDocumentFragment();
  fragment.appendChild(el('h2', { textContent: '⚙️ Ajustes' }));
  fragment.appendChild(el('p', {
    className: 'settings-meta',
  }, [`Archivo de configuracion: ${s.config_path}`]));

  // User section
  const userSection = el('div', { className: 'settings-section' }, [
    el('h3', { textContent: '👤 Tu perfil' }),
    el('div', { className: 'form-row' }, [
      el('div', { className: 'form-group' }, [
        el('label', { textContent: 'Nombre completo' }),
        el('input', { id: 's-nombre', value: s.user.nombre }),
      ]),
      el('div', { className: 'form-group' }, [
        el('label', { textContent: 'Email' }),
        el('input', { id: 's-email', value: s.user.email }),
      ]),
    ]),
  ]);
  const rolSelect = el('select', { id: 's-rol' }, [
    el('option', { value: 'user', selected: s.user.rol === 'user', textContent: 'Usuario' }),
    el('option', { value: 'admin', selected: s.user.rol === 'admin', textContent: 'Administrador' }),
  ]);
  userSection.appendChild(
    el('div', { className: 'form-group' }, [el('label', { textContent: 'Rol' }), rolSelect])
  );
  fragment.appendChild(userSection);

  // Repo section
  fragment.appendChild(el('div', { className: 'settings-section' }, [
    el('h3', { textContent: '📁 Repositorio' }),
    el('div', { className: 'form-group' }, [
      el('label', { textContent: 'URL del repositorio central' }),
      el('input', { id: 's-repo-url', value: s.repositorio.url, placeholder: 'git@github.com:org/repo.git' }),
    ]),
    el('div', { className: 'form-group' }, [
      el('label', { textContent: 'Carpeta de trabajo local' }),
      el('input', { id: 's-workspace', value: s.repositorio.workspace, placeholder: '~/bp-workspace' }),
    ]),
  ]));

  // Slack section
  const slackCheck = el('input', { type: 'checkbox', id: 's-slack-active', checked: s.slack.activado });
  fragment.appendChild(el('div', { className: 'settings-section' }, [
    el('h3', { textContent: '💬 Slack' }),
    el('div', { className: 'form-group' }, [
      el('label', { textContent: 'Webhook URL' }),
      el('input', { id: 's-slack-url', value: s.slack.webhook_url, placeholder: 'https://hooks.slack.com/services/...' }),
    ]),
    el('div', { className: 'form-row' }, [
      el('div', { className: 'form-group' }, [
        el('label', { textContent: 'Canal' }),
        el('input', { id: 's-slack-canal', value: s.slack.canal, placeholder: '#bp-control' }),
      ]),
      el('div', { className: 'form-group' }, [
        el('label', { textContent: '\u00A0' }),
        el('div', { className: 'form-check' }, [
          slackCheck,
          el('label', { htmlFor: 's-slack-active', textContent: 'Notificaciones activadas' }),
        ]),
      ]),
    ]),
  ]));

  // Lock section
  const autoUnlockCheck = el('input', { type: 'checkbox', id: 's-auto-unlock', checked: s.bloqueo.auto_liberar_tras_push });
  fragment.appendChild(el('div', { className: 'settings-section' }, [
    el('h3', { textContent: '🔒 Bloqueos' }),
    el('div', { className: 'form-row' }, [
      el('div', { className: 'form-group' }, [
        el('label', { textContent: 'Horas hasta que expire una reserva' }),
        el('input', { id: 's-lock-hours', type: 'number', value: String(s.bloqueo.expiracion_horas), min: '1', max: '168' }),
      ]),
      el('div', { className: 'form-group' }, [
        el('label', { textContent: '\u00A0' }),
        el('div', { className: 'form-check' }, [
          autoUnlockCheck,
          el('label', { htmlFor: 's-auto-unlock', textContent: 'Liberar reserva al subir cambios' }),
        ]),
      ]),
    ]),
  ]));

  // Buttons
  fragment.appendChild(el('div', { className: 'action-bar', style: 'justify-content: flex-end;' }, [
    el('button', { className: 'btn btn-ghost', onclick: loadSettings, textContent: 'Descartar' }),
    el('button', { className: 'btn btn-green', onclick: saveSettings, textContent: '💾 Guardar cambios' }),
  ]));

  main.replaceChildren(fragment);
}

async function saveSettings() {
  const payload = {
    user: {
      nombre: document.getElementById('s-nombre').value,
      email: document.getElementById('s-email').value,
      rol: document.getElementById('s-rol').value,
    },
    repositorio: {
      url: document.getElementById('s-repo-url').value,
      workspace: document.getElementById('s-workspace').value,
    },
    slack: {
      webhook_url: document.getElementById('s-slack-url').value,
      canal: document.getElementById('s-slack-canal').value,
      activado: document.getElementById('s-slack-active').checked,
    },
    bloqueo: {
      expiracion_horas: parseInt(document.getElementById('s-lock-hours').value) || 24,
      auto_liberar_tras_push: document.getElementById('s-auto-unlock').checked,
    },
  };

  const data = await api('POST', '/api/settings', payload);
  if (data) {
    toast(data.message);
  }
}

// ── Navigation ───────────────────────────────────────────

function navigate(page) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  if (page === 'dashboard') {
    document.getElementById('nav-dashboard').classList.add('active');
    loadDashboard();
    startAutoRefresh();
  } else if (page === 'settings') {
    document.getElementById('nav-settings').classList.add('active');
    loadSettings();
    stopAutoRefresh();
  }
}

function startAutoRefresh() {
  stopAutoRefresh();
  refreshInterval = setInterval(loadDashboard, 30000);
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

// ── Init ─────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  navigate('dashboard');
});

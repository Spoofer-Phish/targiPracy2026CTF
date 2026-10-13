/* Shared helpers: API calls, hints, flag form and the CRT effects.
   Everything from the server is written with textContent, never innerHTML. */
(() => {
  'use strict';

  const i18n = JSON.parse(document.getElementById('js-i18n').textContent);
  const csrf = document.querySelector('meta[name="csrf-token"]').content;

  const fmt = (text, vars) => text.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? vars[k] : ''));

  async function api(path, body) {
    try {
      const res = await fetch(path, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
        body: JSON.stringify(body || {}),
      });
      let data = {};
      try { data = await res.json(); } catch (e) { /* not JSON */ }
      if (data.ok === undefined) data.ok = res.ok;
      data.status = res.status;
      if (res.status === 429) data.error = 'rate';
      return data;
    } catch (e) {
      return { ok: false, error: 'network', status: 0 };
    }
  }

  async function apiGet(path) {
    try {
      const res = await fetch(path, { credentials: 'same-origin' });
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  function setMsg(el, text, kind) {
    if (!el) return;
    el.textContent = text || '';
    el.classList.toggle('bad', kind === 'bad');
    el.classList.toggle('good', kind === 'good');
  }

  const errorText = (r) => (r && r.error === 'rate' ? i18n.err_rate : i18n.err);

  window.KR = { i18n, fmt, api, apiGet, setMsg, errorText };

  /* ---------------------------------------------------------------- hints */
  const hintBtn = document.getElementById('hint-btn');
  if (hintBtn) {
    const list = document.getElementById('hint-list');
    const label = (count) =>
      count >= 3 ? i18n.hint_all : fmt(i18n.hint_btn, { n: count + 1 });
    hintBtn.addEventListener('click', async () => {
      hintBtn.disabled = true;
      const r = await api('/api/hint');
      if (!r.ok) {
        hintBtn.disabled = false;
        hintBtn.textContent = errorText(r);
        return;
      }
      list.replaceChildren(
        ...r.hints.map((text) => {
          const li = document.createElement('li');
          li.textContent = text;
          return li;
        })
      );
      hintBtn.textContent = label(r.count);
      hintBtn.disabled = r.count >= 3;
    });
  }

  /* ---------------------------------------------------------------- flag form */
  const flagForm = document.getElementById('flag-form');
  if (flagForm) {
    const input = document.getElementById('flag-input');
    const msg = document.getElementById('flag-msg');
    flagForm.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const value = input.value.trim();
      if (!value) { setMsg(msg, i18n.flag_empty, 'bad'); return; }
      const r = await api('/api/flag', { flag: value });
      if (r.ok && r.next) {
        setMsg(msg, i18n.flag_ok, 'good');
        setTimeout(() => { window.location.href = r.next; }, 700);
      } else if (r.error === 'wrong_flag') {
        setMsg(msg, i18n.flag_wrong, 'bad');
      } else {
        setMsg(msg, errorText(r), 'bad');
      }
    });
  }

  /* ---------------------------------------------------------------- CRT effects */
  const FX_KEY = 'kr-fx';
  const body = document.body;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get() { try { return localStorage.getItem(FX_KEY); } catch (e) { return null; } },
    set(v) { try { localStorage.setItem(FX_KEY, v); } catch (e) { /* private mode */ } },
  };
  const fxButton = document.getElementById('fx-toggle');

  function applyFx(on) {
    body.classList.toggle('no-fx', !on);
    if (fxButton) { fxButton.classList.toggle('on', on); fxButton.setAttribute('aria-pressed', String(on)); }
  }
  applyFx(store.get() !== 'off');
  if (fxButton) {
    fxButton.addEventListener('click', () => {
      const turnOn = body.classList.contains('no-fx');
      store.set(turnOn ? 'on' : 'off');
      applyFx(turnOn);
    });
  }

})();

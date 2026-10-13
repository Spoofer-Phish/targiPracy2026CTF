/* Organiser panel: live table, prize desk, stock and reset. All server text goes in via textContent. */
(() => {
  'use strict';
  const { i18n, fmt, api, apiGet, setMsg, errorText } = window.KR;

  const $ = (id) => document.getElementById(id);
  const tbody = document.querySelector('#admin-table tbody');
  const stockInput = $('stock-input');
  const claimInput = $('claim-input');
  const claimMsg = $('claim-msg');
  const giveBtn = $('claim-give');
  let editingStock = false;

  const clock = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  function cell(text, cls) {
    const td = document.createElement('td');
    td.textContent = text;
    if (cls) td.className = cls;
    return td;
  }

  function render(state) {
    $('st-total').textContent = state.total;
    $('st-finished').textContent = state.finished;
    $('st-claimed').textContent = state.claimed;
    $('st-gadgets').textContent = state.gadgets;
    if (!editingStock) stockInput.value = state.gadgets;

    const rows = state.players.map((p, i) => {
      const tr = document.createElement('tr');
      if (p.done) tr.className = 'finished';
      const level = p.done ? i18n.board_done : `${p.level}/4`;
      tr.append(cell(i + 1), cell(p.nickname, 'nick'), cell(level), cell(clock(p.seconds)), cell(p.hints));
      let code = '';
      if (p.claim_code) code = `${p.claim_code.slice(0, 3)}-${p.claim_code.slice(3)}${p.claimed ? ' ✓' : ''}`;
      tr.append(cell(code));
      const td = document.createElement('td');
      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'link';
      del.textContent = i18n.admin_delete;
      del.addEventListener('click', async () => {
        if (!window.confirm(fmt(i18n.admin_delete_confirm, { nick: p.nickname }))) return;
        const r = await api('/api/admin/delete', { id: p.id });
        if (r.ok) render(r);
      });
      td.append(del);
      tr.append(td);
      return tr;
    });
    tbody.replaceChildren(...rows);
  }

  async function refresh() {
    const state = await apiGet('/api/admin/state');
    if (state && state.ok) render(state);
  }

  stockInput.addEventListener('focus', () => { editingStock = true; });
  stockInput.addEventListener('blur', () => { editingStock = false; });
  $('stock-btn').addEventListener('click', async () => {
    const value = parseInt(stockInput.value, 10);
    if (Number.isNaN(value)) return;
    const r = await api('/api/admin/gadgets', { value });
    if (r.ok) { editingStock = false; render(r); }
  });

  $('claim-check').addEventListener('click', async () => {
    giveBtn.hidden = true;
    const r = await api('/api/admin/claim/lookup', { code: claimInput.value });
    if (!r.ok) { setMsg(claimMsg, errorText(r), 'bad'); return; }
    if (!r.found) { setMsg(claimMsg, i18n.admin_code_unknown, 'bad'); return; }
    if (r.claimed) { setMsg(claimMsg, fmt(i18n.admin_already, { nick: r.nickname }), 'bad'); return; }
    setMsg(claimMsg, fmt(i18n.admin_valid, { nick: r.nickname }), 'good');
    giveBtn.hidden = false;
  });

  giveBtn.addEventListener('click', async () => {
    giveBtn.disabled = true;
    const r = await api('/api/admin/claim/give', { code: claimInput.value });
    giveBtn.disabled = false;
    if (r.ok) {
      render(r);
      giveBtn.hidden = true;
      claimInput.value = '';
      setMsg(claimMsg, i18n.admin_given, 'good');
    } else if (r.status === 409 && r.error === 'out of stock') {
      setMsg(claimMsg, i18n.admin_out, 'bad');
    } else {
      setMsg(claimMsg, errorText(r), 'bad');
    }
  });

  $('reset-event').addEventListener('click', async () => {
    const answer = window.prompt(i18n.admin_reset_prompt);
    if (answer !== 'RESET') return;
    const r = await api('/api/admin/reset', { confirm: 'RESET' });
    if (r.ok) render(r);
  });

  refresh();
  setInterval(refresh, 4000);
})();

/* Level 1: airlock key sequence. The server checks the order and hands out the passphrase. */
(() => {
  'use strict';
  const { i18n, fmt, api, setMsg, errorText } = window.KR;

  const keys = [...document.querySelectorAll('#keys .key')];
  const slots = [...document.querySelectorAll('#slots .slot')];
  const log = document.getElementById('breach-log');
  const vault = document.getElementById('vault');
  const waitText = log.textContent;
  let seq = [];
  let busy = false;

  function reset() {
    seq = [];
    busy = false;
    keys.forEach((k) => { k.disabled = false; });
    slots.forEach((s, i) => {
      s.textContent = String(i + 1);
      s.className = 'slot';
    });
  }

  function say(text) { log.textContent = text; }

  keys.forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (busy || seq.length >= 4) return;
      const id = btn.dataset.key;
      const glyph = btn.querySelector('.glyph').textContent;
      const slot = slots[seq.length];
      seq.push(id);
      slot.textContent = glyph;
      slot.className = 'slot filled c-' + id;
      btn.disabled = true;
      say(fmt(i18n.l1_progress, { seq: slots.slice(0, seq.length).map((s) => s.textContent).join(' ') }));

      if (seq.length < 4) return;
      busy = true;
      const r = await api('/api/l1/sequence', { seq });
      if (r.ok && r.passphrase) {
        say(i18n.l1_solved);
        keys.forEach((k) => { k.disabled = true; });
        document.getElementById('passphrase').textContent = r.passphrase;
        vault.hidden = false;
      } else if (r.ok === false && !r.error) {
        say(i18n.l1_wrong);
        setTimeout(() => { reset(); say(waitText); }, 1300);
      } else {
        say(errorText(r));
        setTimeout(() => { reset(); say(waitText); }, 1300);
      }
    });
  });

  document.getElementById('reset-btn').addEventListener('click', () => {
    reset();
    say(waitText);
  });

  document.getElementById('vault-btn').addEventListener('click', async (ev) => {
    const btn = ev.currentTarget;
    const phrase = document.getElementById('passphrase').textContent;
    const r = await api('/api/l1/vault', { passphrase: phrase });
    if (r.ok && r.flag) {
      document.getElementById('vault-flag').textContent = r.flag;
      document.getElementById('vault-result').hidden = false;
      btn.hidden = true;
    } else {
      say(r.error ? errorText(r) : i18n.l1_vault_wrong);
    }
  });

  document.getElementById('fill-flag').addEventListener('click', () => {
    const input = document.getElementById('flag-input');
    input.value = document.getElementById('vault-flag').textContent;
    input.scrollIntoView({ block: 'center', behavior: 'smooth' });
    input.focus({ preventScroll: true });
  });
})();

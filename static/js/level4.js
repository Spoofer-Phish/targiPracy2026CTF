/* Level 4: phishing inbox, the rogue-AI mail and the forensic scanner. */
(() => {
  'use strict';
  const { i18n, api, setMsg, errorText } = window.KR;

  /* ------------------------------------------------------------ inbox */
  const inbox = document.getElementById('inbox');
  if (inbox) {
    inbox.addEventListener('click', async (ev) => {
      const head = ev.target.closest('.mail-head');
      if (head) {
        const body = head.nextElementSibling;
        body.hidden = !body.hidden;
        head.setAttribute('aria-expanded', String(!body.hidden));
        return;
      }
      const btn = ev.target.closest('.report-btn');
      if (!btn) return;
      const msg = btn.parentElement.querySelector('.msg');
      btn.disabled = true;
      const r = await api('/api/l4/report', { id: btn.dataset.id });
      if (r.ok && r.correct) {
        setMsg(msg, i18n.l4_correct, 'good');
        setTimeout(() => { window.location.href = r.next; }, 900);
        return;
      }
      btn.disabled = false;
      setMsg(msg, r.ok ? r.message : errorText(r), 'bad');
    });
  }

  /* ------------------------------------------------------------ compose / send */
  const sendBtn = document.getElementById('send-btn');
  if (sendBtn) {
    const log = document.getElementById('send-log');
    sendBtn.addEventListener('click', async () => {
      const chosen = document.querySelector('input[name="phrase"]:checked');
      if (!chosen) { log.textContent = i18n.l4_pick; return; }
      sendBtn.disabled = true;
      log.textContent = i18n.l4_sending;
      const r = await api('/api/l4/send', { id: chosen.value });
      if (r.ok && r.correct) {
        log.textContent = i18n.l4_leak;
        setTimeout(() => { window.location.href = r.next; }, 1700);
        return;
      }
      sendBtn.disabled = false;
      log.textContent = r.ok ? r.message : errorText(r);
    });
  }

  /* ------------------------------------------------------------ forensic scanner */
  const scanner = document.getElementById('scanner');
  if (scanner) {
    const BLACK_POINT = 6; // the image's background level, see tools/prepare_assets.py
    const canvas = document.getElementById('scan-canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const status = document.getElementById('scan-status');
    const gainEl = document.getElementById('gain');
    const gainVal = document.getElementById('gain-val');
    const uvBtn = document.getElementById('uv-btn');
    const invBtn = document.getElementById('invert-btn');
    let source = null;
    let uv = false;
    let invert = false;
    let queued = false;

    function render() {
      queued = false;
      if (!source) return;
      const gain = Number(gainEl.value);
      gainVal.textContent = String(gain);
      if (gain === 1 && !uv && !invert) { ctx.putImageData(source, 0, 0); return; }
      const out = ctx.createImageData(source.width, source.height);
      const s = source.data;
      const d = out.data;
      for (let i = 0; i < s.length; i += 4) {
        const lum = Math.max(s[i], s[i + 1], s[i + 2]);
        let v = (lum - BLACK_POINT) * gain;
        v = v < 0 ? 0 : v > 255 ? 255 : v;
        if (invert) v = 255 - v;
        if (uv) { d[i] = v * 0.7; d[i + 1] = v * 0.25; d[i + 2] = v; }
        else { d[i] = v * 0.25; d[i + 1] = v; d[i + 2] = v * 0.45; }
        d[i + 3] = 255;
      }
      ctx.putImageData(out, 0, 0);
    }
    const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(render); } };

    const img = new Image();
    img.onload = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);
      source = ctx.getImageData(0, 0, canvas.width, canvas.height);
      setMsg(status, i18n.scan_ready, 'good');
    };
    img.onerror = () => setMsg(status, i18n.scan_failed, 'bad');
    img.src = scanner.dataset.src;

    gainEl.addEventListener('input', schedule);
    uvBtn.addEventListener('click', () => {
      uv = !uv;
      uvBtn.setAttribute('aria-pressed', String(uv));
      uvBtn.classList.toggle('primary', uv);
      schedule();
    });
    invBtn.addEventListener('click', () => {
      invert = !invert;
      invBtn.setAttribute('aria-pressed', String(invert));
      invBtn.classList.toggle('primary', invert);
      schedule();
    });
    document.getElementById('scan-reset').addEventListener('click', () => {
      uv = false; invert = false; gainEl.value = '1';
      uvBtn.classList.remove('primary'); invBtn.classList.remove('primary');
      uvBtn.setAttribute('aria-pressed', 'false'); invBtn.setAttribute('aria-pressed', 'false');
      schedule();
    });
  }

  /* ------------------------------------------------------------ help buttons */
  const phishHelpBtn = document.getElementById('phish-help-btn');
  const phishHelp = document.getElementById('phish-help');
  if (phishHelpBtn && phishHelp) {
    phishHelpBtn.addEventListener('click', () => {
      phishHelp.hidden = !phishHelp.hidden;
      phishHelpBtn.setAttribute('aria-expanded', String(!phishHelp.hidden));
    });
  }

  const stegoHelpBtn = document.getElementById('stego-help-btn');
  const stegoHelp = document.getElementById('stego-help');
  if (stegoHelpBtn && stegoHelp) {
    stegoHelpBtn.addEventListener('click', () => {
      stegoHelp.hidden = !stegoHelp.hidden;
      stegoHelpBtn.setAttribute('aria-expanded', String(!stegoHelp.hidden));
    });
  }
})();

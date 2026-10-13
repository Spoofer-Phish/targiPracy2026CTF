/* Level 2: Caesar decoder (part A) and the simulated terminal (part B).
   Terminal commands are answered by the server; output is added as plain text. */
(() => {
  'use strict';
  const { i18n, api, setMsg, errorText } = window.KR;

  /* ------------------------------------------------------------ part A: Caesar */
  const cipherEl = document.getElementById('cipher');
  if (cipherEl) {
    const plainEl = document.getElementById('plain');
    const slider = document.getElementById('shift');
    const valEl = document.getElementById('shift-val');
    const cipher = cipherEl.textContent;

    const decode = (text, shift) =>
      text.replace(/[A-Za-z]/g, (ch) => {
        const base = ch <= 'Z' ? 65 : 97;
        return String.fromCharCode(((ch.charCodeAt(0) - base - shift + 26) % 26) + base);
      });

    function update() {
      const shift = Number(slider.value);
      valEl.textContent = String(shift);
      plainEl.textContent = decode(cipher, shift);
    }
    slider.addEventListener('input', update);
    document.getElementById('shift-minus').addEventListener('click', () => {
      slider.value = String(Math.max(1, Number(slider.value) - 1));
      update();
    });
    document.getElementById('shift-plus').addEventListener('click', () => {
      slider.value = String(Math.min(25, Number(slider.value) + 1));
      update();
    });
    update();

    const helpBtn = document.getElementById('help-btn');
    const help = document.getElementById('caesar-help');
    helpBtn.addEventListener('click', () => {
      help.hidden = !help.hidden;
      helpBtn.setAttribute('aria-expanded', String(!help.hidden));
    });

    const form = document.getElementById('login-form');
    const msg = document.getElementById('login-msg');
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const pw = document.getElementById('mf-pass').value.trim();
      if (!pw) { setMsg(msg, i18n.pw_empty, 'bad'); return; }
      const r = await api('/api/l2/login', { password: pw });
      if (r.ok && r.next) {
        setMsg(msg, i18n.pw_ok, 'good');
        setTimeout(() => { window.location.href = r.next; }, 600);
      } else if (r.error) {
        setMsg(msg, errorText(r), 'bad');
      } else {
        setMsg(msg, i18n.pw_wrong, 'bad');
      }
    });
  }

  /* ------------------------------------------------------------ part B: terminal */
  const out = document.getElementById('term-out');
  if (out) {
    const form = document.getElementById('term-form');
    const input = document.getElementById('term-in');
    const promptEl = document.getElementById('term-prompt');
    const history = [];
    let histPos = 0;
    let cwd = '/home/captain';
    let promptText = '~';
    let busy = false;

    const prompt = () => `captain@kraknautica:${promptText}$`;
    const write = (text) => {
      out.append(document.createTextNode(text + '\n'));
      out.scrollTop = out.scrollHeight;
    };

    out.append(document.createTextNode(out.dataset.banner));
    promptEl.textContent = prompt();

    async function run(command) {
      if (busy) return;
      busy = true;
      write(`${prompt()} ${command}`);
      if (command.trim()) { history.push(command); histPos = history.length; }
      const r = await api('/api/l2/term', { cmd: command, cwd });
      busy = false;
      if (!r.ok) { write(errorText(r)); return; }
      if (r.clear) out.textContent = '';
      if (r.output) write(r.output);
      cwd = r.cwd;
      promptText = r.prompt;
      promptEl.textContent = prompt();
    }

    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const command = input.value;
      input.value = '';
      run(command);
    });

    input.addEventListener('keydown', (ev) => {
      if (ev.key === 'ArrowUp' && histPos > 0) {
        histPos -= 1; input.value = history[histPos]; ev.preventDefault();
      } else if (ev.key === 'ArrowDown') {
        histPos = Math.min(history.length, histPos + 1);
        input.value = history[histPos] || ''; ev.preventDefault();
      }
    });

    document.getElementById('term-chips').addEventListener('click', (ev) => {
      const chip = ev.target.closest('button');
      if (!chip) return;
      if (chip.dataset.run) {
        run(chip.dataset.run);
      } else if (chip.dataset.fill) {
        input.value = chip.dataset.fill;
        input.focus();
      }
    });
  }
})();

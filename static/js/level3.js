/* Level 3: admin login form (the IDOR part is just the address bar). */
(() => {
  'use strict';
  const { i18n, api, setMsg, errorText } = window.KR;

  const form = document.getElementById('admin-form');
  if (!form) return;
  const msg = document.getElementById('admin-msg');

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const user = document.getElementById('adm-user').value;
    const password = document.getElementById('adm-pass').value;
    if (!user.trim() || !password) { setMsg(msg, i18n.l3_empty, 'bad'); return; }
    const r = await api('/api/l3/login', { user, password });
    if (r.ok && r.next) {
      setMsg(msg, i18n.l3_ok, 'good');
      setTimeout(() => { window.location.href = r.next; }, 600);
    } else if (r.error) {
      setMsg(msg, errorText(r), 'bad');
    } else {
      setMsg(msg, i18n.l3_wrong, 'bad');
    }
  });
})();

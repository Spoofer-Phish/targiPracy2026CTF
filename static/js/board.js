/* Projector leaderboard: refreshes every few seconds. */
(() => {
  'use strict';
  const { i18n, apiGet } = window.KR;

  const tbody = document.querySelector('#board-table tbody');
  const empty = document.getElementById('board-empty');
  const clock = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  function cell(text, cls) {
    const td = document.createElement('td');
    td.textContent = text;
    if (cls) td.className = cls;
    return td;
  }

  async function refresh() {
    const rows = await apiGet('/api/board');
    if (!rows) return;
    empty.hidden = rows.length > 0;
    tbody.replaceChildren(
      ...rows.slice(0, 40).map((p, i) => {
        const tr = document.createElement('tr');
        if (p.done) tr.className = 'finished';
        tr.append(
          cell(i + 1),
          cell(p.nickname, 'nick'),
          cell(p.done ? i18n.board_done : `${p.level}/4`),
          cell(clock(p.seconds)),
          cell(p.hints)
        );
        return tr;
      })
    );
  }
  refresh();
  setInterval(refresh, 5000);
})();

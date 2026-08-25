/* Renders the results tables from docs/data/leaderboard.json and ablations.json,
   copied by scripts/export_site_data.py from results/paper/. */

const DIMS = ["P", "I", "V", "O", "T", "S"];
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const num = (v) => (v == null ? "–" : v.toFixed(2));

/* One hue, one series: the bar under Avg encodes magnitude only. */
function avgCell(value, max) {
  const pct = max ? Math.max(2, (value / max) * 100) : 0;
  return `<td class="strong"><span class="bar">${num(value)}<i style="width:${pct}%"></i></span></td>`;
}

function mainTable(subset, withAux) {
  const max = Math.max(...subset.models.map((m) => m.task1_avg));
  const head = `<tr><th>Model</th><th>Avg</th>${DIMS.map((d) => `<th>${d}</th>`).join("")}
    ${withAux ? "<th>Task 2</th><th>Task 3</th>" : ""}</tr>`;
  let body = "";
  let family = null;
  subset.models.forEach((m) => {
    if (m.family !== family) {
      family = m.family;
      const label = family === "proprietary" ? "Proprietary" : "Open source";
      body += `<tr class="group"><td colspan="${withAux ? 10 : 8}">${label}</td></tr>`;
    }
    body += `<tr><td>${esc(m.name)}</td>${avgCell(m.task1_avg, max)}
      ${m.dims.map((v) => `<td>${num(v)}</td>`).join("")}
      ${withAux ? `<td>${num(m.task2)}</td><td>${num(m.task3)}</td>` : ""}</tr>`;
  });
  return `<thead>${head}</thead><tbody>${body}</tbody>`;
}

function ablationTable(block) {
  const head = `<tr><th rowspan="2">Setting</th><th colspan="7">Social-IQ 2.0</th>
    <th colspan="7">YouTube</th></tr>
    <tr><th>Avg</th>${DIMS.map((d) => `<th>${d}</th>`).join("")}
        <th>Avg</th>${DIMS.map((d) => `<th>${d}</th>`).join("")}</tr>`;
  const body = block.rows.map((r) => {
    const cells = (side) =>
      `<td class="strong">${num(side.avg)}</td>${side.dims.map((v) => `<td>${num(v)}</td>`).join("")}`;
    return `<tr><td>${esc(r.name)}${r.highlight ? " <span class='muted'>(default)</span>" : ""}</td>
      ${cells(r.social_iq)}${cells(r.youtube)}</tr>`;
  }).join("");
  return `<thead>${head}</thead><tbody>${body}</tbody>`;
}

Promise.all([
  fetch("./data/leaderboard.json").then((r) => r.json()),
  fetch("./data/ablations.json").then((r) => r.json()),
]).then(([main, abl]) => {
  document.getElementById("t-socialiq").innerHTML = mainTable(main.subsets.social_iq, true);
  document.getElementById("t-youtube").innerHTML = mainTable(main.subsets.youtube, false);
  document.getElementById("t-modality").innerHTML = ablationTable(abl.input_modality);
  document.getElementById("t-setting").innerHTML = ablationTable(abl.prediction_setting);
  document.getElementById("t-prompting").innerHTML = ablationTable(abl.prompting);
}).catch(() => {
  document.querySelectorAll(".tablewrap").forEach((el) => {
    el.innerHTML = `<p class="note">Results could not be loaded. Serve this folder with
      <code>python3 -m http.server</code> rather than opening the file directly.</p>`;
  });
});

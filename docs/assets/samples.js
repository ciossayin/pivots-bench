/* Renders docs/data/samples.json, which scripts/export_site_data.py generates
   from the released annotation files. Nothing on this page is hand-typed. */

const DIMS = ["P", "I", "V", "O", "T", "S"];
const CLASS = { "-2": "v-2", "-1": "v-1", "0": "v0", "1": "v1", "2": "v2" };

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const fmt = (v) => (v === null || v === undefined ? "–" : v > 0 ? `+${v}` : `${v}`);

function cellClass(v) {
  if (v === null || v === undefined) return "cell vnull";
  return `cell ${CLASS[String(v)] || "v0"}`;
}

function matrix(directions) {
  const head = ['<div class="matrix">', '<div></div>'];
  DIMS.forEach((d) => head.push(`<div class="h">${d}</div>`));
  const rows = directions.map((dir) => {
    const label = `<div class="rowlabel">${esc(dir.subject)} <span class="muted" style="padding:0 .3rem">→</span> ${esc(dir.target)}</div>`;
    const cells = DIMS.map((d) => {
      const entry = dir.scores[d] || {};
      const v = entry.score;
      const title = [
        `${d} = ${fmt(v)}`,
        entry.timestamp_sec != null ? `evidence at ${entry.timestamp_sec}s` : null,
        entry.rationale || null,
      ].filter(Boolean).join(" · ");
      return `<div class="${cellClass(v)}" title="${esc(title)}">${fmt(v)}</div>`;
    }).join("");
    return label + cells;
  });
  return head.join("") + rows.join("") + "</div>";
}

function video(sample) {
  if (sample.youtube_id) {
    const s = Math.round(sample.start_sec || 0);
    const e = Math.round(sample.end_sec || 30);
    const src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(sample.youtube_id)}?start=${s}&end=${e}&rel=0`;
    return `<div class="video"><iframe src="${src}" title="${esc(sample.title || sample.video_id)}"
      loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"
      allowfullscreen></iframe></div>`;
  }
  return `<div class="video"><div class="none">Video identifier released with the dataset.<br>
    Annotations for this clip are shown in full.</div></div>`;
}

function dialogue(sample) {
  if (sample.dialogue && sample.dialogue.length) {
    return `<div class="dialogue">${sample.dialogue
      .map((l) => `<p><b>${esc(l.speaker)}:</b> ${esc(l.text)}</p>`).join("")}</div>`;
  }
  if (sample.transcript_excerpt && sample.transcript_excerpt.length) {
    return `<div class="dialogue">${sample.transcript_excerpt
      .map((l) => `<p><span class="t mono">${esc(l.time)}</span>${esc(l.text)}</p>`).join("")}</div>`;
  }
  return "";
}

function evidence(sample, cues) {
  const rows = [];
  (sample.directions || []).forEach((dir) => {
    DIMS.forEach((d) => {
      const e = dir.scores[d] || {};
      if (!e.rationale) return;
      const tags = [];
      if (e.timestamp_sec != null) tags.push(`frame at ${e.timestamp_sec}s`);
      (e.cues || []).forEach((c) => tags.push(cues[c] || c));
      rows.push(`<div><span class="d">${d}</span><span>
        <span class="r">${esc(e.rationale)}</span>
        ${tags.length ? `<div class="tags">${esc(dir.subject)} → ${esc(dir.target)} · ${tags.map(esc).join(" · ")}</div>`
                      : `<div class="tags">${esc(dir.subject)} → ${esc(dir.target)}</div>`}
      </span></div>`);
    });
  });
  if (!rows.length) return "";
  return `<div class="evidence"><h4>Annotator evidence</h4>${rows.join("")}</div>`;
}

function aux(sample) {
  const blocks = [];
  (sample.keyframe_items || []).forEach((it) => {
    const letters = "ABCDE";
    const opts = it.options_sec.map((t, i) =>
      `<li${letters[i] === it.answer ? ' class="correct"' : ""}>${t}s${letters[i] === it.answer ? " — answer" : ""}</li>`
    ).join("");
    blocks.push(`<div><h4>Task 2 · ${it.dimension}, ${esc(it.subject)} → ${esc(it.target)}</h4>
      <p class="muted small" style="margin-top:.3rem">Which frame best shows it?</p>
      <ol>${opts}</ol></div>`);
  });
  (sample.cue_items || []).forEach((it) => {
    const opts = it.options.map((o, i) =>
      `<li${it.answer.includes(i) ? ' class="correct"' : ""}>${esc(o)}</li>`
    ).join("");
    blocks.push(`<div><h4>Task 3 · ${it.dimension}, frame at ${it.frame_sec}s</h4>
      <p class="muted small" style="margin-top:.3rem">Which two cues carry the score?</p>
      <ol>${opts}</ol></div>`);
  });
  if (!blocks.length) return "";
  return `<div class="aux">${blocks.join("")}</div>`;
}

function render(data) {
  const cues = data.cues || {};
  const html = data.samples.filter((s) => s.youtube_id).map((s) => `
    <article class="sample">
      <div class="kicker">${esc(s.subtitle || s.source)}</div>
      <h3>${esc(s.title || s.video_id)}</h3>
      ${s.summary ? `<p class="summary">${esc(s.summary)}</p>` : ""}
      <div class="split">
        <div>${video(s)}${dialogue(s)}</div>
        <div>
          <h4>PIVOTS scores, both directions</h4>
          ${matrix(s.directions || [])}
          ${evidence(s, cues)}
          ${aux(s)}
        </div>
      </div>
      ${s.provenance ? `<p class="muted small" style="margin-top:1.25rem">${esc(s.provenance)}</p>` : ""}
    </article>`).join("");
  document.getElementById("samples").innerHTML = html;
}

fetch("./data/samples.json")
  .then((r) => r.json())
  .then(render)
  .catch(() => {
    document.getElementById("samples").innerHTML =
      `<p class="note">Sample data could not be loaded. If you opened this file directly from
       disk, serve the folder instead: <code>python3 -m http.server</code> inside <code>docs/</code>.</p>`;
  });

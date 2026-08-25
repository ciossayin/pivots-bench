/* Score distribution: one stacked bar per dimension, diverging red<->blue with a
   gray midpoint. Counts are read from the table below it, which is the table view. */

const STEPS = [
  { key: "-2", css: "--s-neg2" },
  { key: "-1", css: "--s-neg1" },
  { key: "0",  css: "--s-zero" },
  { key: "1",  css: "--s-pos1" },
  { key: "2",  css: "--s-pos2" },
];

const DATA = [
  { dim: "P", counts: [13, 89, 544, 104, 15] },
  { dim: "I", counts: [54, 123, 105, 345, 138] },
  { dim: "V", counts: [24, 86, 147, 424, 84] },
  { dim: "O", counts: [96, 64, 87, 195, 323] },
  { dim: "T", counts: [121, 34, 229, 238, 143] },
  { dim: "S", counts: [13, 73, 124, 425, 130] },
];

const tip = document.createElement("div");
tip.className = "tip";
document.body.appendChild(tip);

function show(e, text) {
  tip.textContent = text;
  tip.classList.add("on");
  tip.style.left = Math.min(e.clientX + 12, window.innerWidth - 200) + "px";
  tip.style.top = e.clientY - 30 + "px";
}
function hide() { tip.classList.remove("on"); }

const host = document.getElementById("dist");
if (host) {
  host.innerHTML = DATA.map((row) => {
    const total = row.counts.reduce((a, b) => a + b, 0);
    const segs = row.counts.map((c, i) => {
      const pct = (c / total) * 100;
      return `<div class="seg" style="width:${pct}%;background:var(${STEPS[i].css})"
        data-label="${row.dim} = ${STEPS[i].key > 0 ? "+" : ""}${STEPS[i].key}: ${c} of ${total} (${pct.toFixed(1)}%)"></div>`;
    }).join("");
    return `<div class="row"><span class="lab">${row.dim}</span>
      <div class="track">${segs}</div><span class="tot">${total}</span></div>`;
  }).join("");

  host.querySelectorAll(".seg").forEach((el) => {
    el.addEventListener("mousemove", (e) => show(e, el.dataset.label));
    el.addEventListener("mouseleave", hide);
  });
}

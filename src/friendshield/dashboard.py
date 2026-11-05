"""Render a self-contained offline dashboard for labeled synthetic reviews."""
import json
from pathlib import Path

from .evaluation import evaluate_labeled_requests


def build_dashboard_data(labeled_records):
    """Evaluate every integer threshold from 0 through 100."""
    rows = []
    for threshold in range(101):
        report = evaluate_labeled_requests(labeled_records, threshold=threshold)
        rows.append({
            "threshold": threshold,
            "metrics": report["metrics"],
            "confusion_matrix": report["confusion_matrix"],
        })
    positive = sum(label for _, label in labeled_records)
    return {
        "sample_count": len(labeled_records),
        "positive_count": positive,
        "routine_count": len(labeled_records) - positive,
        "thresholds": rows,
    }


_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>FriendShield | Evaluation Dashboard</title>
<style>
:root { color-scheme: dark; --bg:#090d1e; --card:#151a33; --edge:#364060;
--text:#f7f8ff; --muted:#c0c9e2; --purple:#ba98ff; --cyan:#6fe0ef; --orange:#ffb982; }
* { box-sizing:border-box; }
body { margin:0; padding:40px 20px; min-height:100vh;
  background:radial-gradient(ellipse at 90% 0%,#302354 0%,transparent 45%),
  radial-gradient(ellipse at 0% 50%,#102947 0%,transparent 43%),var(--bg);
  color:var(--text);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif; }
main { max-width:1130px;margin:auto; }
h1 { font-size:clamp(2.3rem,6vw,3.6rem);letter-spacing:-.04em;margin:0 0 8px; }
h2 { font-size:1.15rem;margin:0 0 9px; }
p { color:var(--muted); }
header p:first-child { color:var(--cyan);font-weight:750;letter-spacing:.17em;text-transform:uppercase;font-size:.8rem; }
.notice { background:#292042;border:1px solid #77669d;border-left:4px solid var(--purple);
  color:#f1e9ff;padding:14px 18px;border-radius:13px;margin:20px 0 24px; }
.grid { display:grid;grid-template-columns:minmax(0,1.65fr) minmax(275px,1fr);gap:18px; }
.card { border:1px solid var(--edge);background:rgba(21,26,51,.95);border-radius:20px;
  padding:clamp(18px,3vw,25px);min-width:0; }
.eyebrow { color:var(--cyan); }
.legend { display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;color:var(--muted); }
.swatch { display:inline-block;width:15px;height:4px;border-radius:5px;margin-right:5px;vertical-align:middle; }
svg { width:100%;height:auto;display:block; }
.axis { fill:var(--muted);font-size:12px; }
.control { display:flex;align-items:center;justify-content:space-between;gap:12px; }
.output { font-size:2.3rem;color:var(--purple);font-weight:800;font-variant-numeric:tabular-nums; }
input[type=range] { accent-color:var(--purple);width:100%;cursor:pointer; }
input:focus-visible { outline:3px solid var(--cyan);outline-offset:4px; }
.ends { display:flex;justify-content:space-between;color:var(--muted);font-size:.78rem; }
.stats,.matrix { display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:20px; }
.tile { padding:13px;background:#1d2542;border-radius:13px;border:1px solid #354265; }
.tile small { display:block;color:var(--muted); }
.tile strong { font-size:1.7rem;font-weight:800;font-variant-numeric:tabular-nums; }
.note { font-size:.85rem; }
.table-wrap { overflow-x:auto; }
table { width:100%;border-collapse:collapse;font-size:.9rem;margin-top:10px; }
td,th { border-bottom:1px solid var(--edge);padding:10px 8px;text-align:left;font-variant-numeric:tabular-nums; }
th { color:var(--muted);font-weight:650; }
.selected { background:#312852; }
footer { padding-top:24px;font-size:.86rem;color:var(--muted); }
@media(max-width:770px) {.grid { grid-template-columns:1fr; }}
</style>
</head>
<body>
<main>
<header>
<p>FriendShield / Offline evaluation</p>
<h1>Evaluation Lab</h1>
<p>Explore the precision, recall, and false-positive tradeoffs behind a human-review score threshold. All data stays inside this file.</p>
</header>
<div class="notice" role="note"><strong>Synthetic example data only.</strong> Scenario labels are not verified bot identities.
These metrics do not measure real-world accuracy. No accounts are connected, blocked, or reported.</div>
<div class="grid">
<section class="card" aria-labelledby="chart-title">
<h2 id="chart-title">Threshold tradeoff curves</h2>
<p class="note">Move the slider to inspect the consequences of different review thresholds.</p>
<div class="legend">
<span><i class="swatch" style="background:var(--purple)"></i>Precision</span>
<span><i class="swatch" style="background:var(--cyan)"></i>Recall</span>
<span><i class="swatch" style="background:var(--orange)"></i>False-positive rate</span>
</div>
<svg id="chart" viewBox="0 0 720 305" role="img" aria-label="Three lines showing precision, recall, and false-positive rate from threshold zero to one hundred"></svg>
<p class="note">Undefined rates are shown as gaps, never as fabricated zeros.</p>
</section>
<section class="card" aria-labelledby="slider-title">
<div class="control"><h2 id="slider-title">Review threshold</h2>
<output class="output" id="threshold-value" for="threshold">__INITIAL__</output></div>
<label for="threshold">Minimum score suggested for human review</label>
<input type="range" id="threshold" min="0" max="100" step="1" value="__INITIAL__">
<div class="ends"><span>0 · More sensitive</span><span>100 · More selective</span></div>
<div class="stats" aria-live="polite">
<div class="tile"><small>Precision</small><strong style="color:var(--purple)" id="precision"></strong></div>
<div class="tile"><small>Recall</small><strong style="color:var(--cyan)" id="recall"></strong></div>
<div class="tile"><small>False-positive rate</small><strong style="color:var(--orange)" id="fpr"></strong></div>
<div class="tile"><small>F1 score</small><strong id="f1"></strong></div>
</div>
</section>
<section class="card" aria-labelledby="matrix-title">
<h2 id="matrix-title">Confusion matrix</h2>
<p class="note">Comparison against synthetic expected-review labels.</p>
<div class="matrix" aria-live="polite">
<div class="tile"><small>True positives</small><strong id="tp"></strong></div>
<div class="tile"><small>False positives</small><strong id="fp"></strong></div>
<div class="tile"><small>True negatives</small><strong id="tn"></strong></div>
<div class="tile"><small>False negatives</small><strong id="fn"></strong></div>
</div>
<p id="counts" class="note"></p>
</section>
<section class="card" aria-labelledby="compare-title">
<h2 id="compare-title">Compare thresholds</h2>
<p class="note">Compare common checkpoints with your selected threshold.</p>
<div class="table-wrap"><table>
<thead><tr><th scope="col">Threshold</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">False-positive rate</th></tr></thead>
<tbody id="comparison"></tbody>
</table></div>
<p class="note">N/A indicates an undefined rate for this sample.</p>
</section>
</div>
<footer>Independent offline educational prototype. Not affiliated with Riot Games.
Any proposed review requires human judgment; scores are not proof of misconduct.</footer>
</main>
<script id="evaluation-data" type="application/json">__PAYLOAD__</script>
<script>
(function () {
  "use strict";
  const data = JSON.parse(document.getElementById("evaluation-data").textContent);
  const svg = document.getElementById("chart");
  const input = document.getElementById("threshold");
  const ns = "http://www.w3.org/2000/svg";
  const L=53, R=696, T=20, B=250;
  const x = t => L + t*(R-L)/100;
  const y = rate => B - rate*(B-T);
  const fmt = value => value === null ? "N/A" : (value*100).toFixed(1)+"%";
  function shape(tag, attrs) {
    const element = document.createElementNS(ns, tag);
    for (const name of Object.keys(attrs)) element.setAttribute(name, String(attrs[name]));
    svg.appendChild(element);
    return element;
  }
  for (const tick of [0,.25,.5,.75,1]) {
    shape("line",{x1:L,y1:y(tick),x2:R,y2:y(tick),stroke:"#3b4769","stroke-width":1});
    const label=shape("text",{x:L-7,y:y(tick)+4,"text-anchor":"end",class:"axis"});
    label.textContent=Math.round(tick*100)+"%";
  }
  for (const tick of [0,20,40,60,80,100]) {
    const label=shape("text",{x:x(tick),y:277,"text-anchor":"middle",class:"axis"});
    label.textContent=String(tick);
  }
  const xlabel=shape("text",{x:(L+R)/2,y:301,"text-anchor":"middle",class:"axis"});
  xlabel.textContent="Review threshold";
  const series=[
    ["precision","#ba98ff"],["recall","#6fe0ef"],["false_positive_rate","#ffb982"]
  ];
  for (const [key,color] of series) {
    let path="",drawing=false;
    for (const item of data.thresholds) {
      const value=item.metrics[key];
      if (value === null) { drawing=false; continue; }
      path+=(drawing?" L":" M")+x(item.threshold).toFixed(2)+" "+y(value).toFixed(2);
      drawing=true;
    }
    shape("path",{d:path,fill:"none",stroke:color,"stroke-width":2.6,"stroke-linejoin":"round"});
  }
  const marker=shape("line",{y1:T,y2:B,stroke:"#e1e8ff","stroke-width":1.3,"stroke-dasharray":"5 5"});
  const points=series.map(([key,color]) => [key,shape("circle",{r:5,fill:color,stroke:"#151a33","stroke-width":2})]);
  function render() {
    const t=Number(input.value),row=data.thresholds[t];
    document.getElementById("threshold-value").textContent=String(t);
    for (const [id,key] of [["precision","precision"],["recall","recall"],["fpr","false_positive_rate"],["f1","f1"]])
      document.getElementById(id).textContent=fmt(row.metrics[key]);
    for (const [id,key] of [["tp","true_positive"],["fp","false_positive"],["tn","true_negative"],["fn","false_negative"]])
      document.getElementById(id).textContent=String(row.confusion_matrix[key]);
    document.getElementById("counts").textContent=data.sample_count+" labeled synthetic requests: "+
      data.positive_count+" annotated review, "+data.routine_count+" annotated routine.";
    marker.setAttribute("x1",x(t));marker.setAttribute("x2",x(t));
    for (const [key,point] of points) {
      const value=row.metrics[key];
      point.setAttribute("cx",x(t));
      point.setAttribute("visibility",value===null?"hidden":"visible");
      if (value!==null) point.setAttribute("cy",y(value));
    }
    const body=document.getElementById("comparison");
    body.replaceChildren();
    for (const at of Array.from(new Set([30,60,80,t])).sort((a,b)=>a-b)) {
      const item=data.thresholds[at],tr=document.createElement("tr");
      if(at===t) tr.className="selected";
      for(const value of [String(at),fmt(item.metrics.precision),fmt(item.metrics.recall),fmt(item.metrics.false_positive_rate)]) {
        const td=document.createElement("td");
        td.textContent=value;
        tr.appendChild(td);
      }
      body.appendChild(tr);
    }
  }
  input.addEventListener("input",render);
  render();
})();
</script>
</body>
</html>
'''


def render_dashboard(labeled_records, initial_threshold=60):
    """Serialize evaluation metrics into portable HTML without network dependencies."""
    if type(initial_threshold) is not int or not 0 <= initial_threshold <= 100:
        raise ValueError("initial threshold must be an integer from 0 to 100")
    payload = json.dumps(build_dashboard_data(labeled_records), allow_nan=False,
                         ensure_ascii=True, separators=(",", ":"))
    # Escape raw script-tag terminators if future datasets carry text.
    for char, replacement in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026")):
        payload = payload.replace(char, replacement)
    return _HTML.replace("__PAYLOAD__", payload).replace("__INITIAL__", str(initial_threshold))


def save_dashboard(labeled_records, path, initial_threshold=60):
    destination = Path(path)
    destination.write_text(render_dashboard(labeled_records, initial_threshold), encoding="utf-8")
    return destination

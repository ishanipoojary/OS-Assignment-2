
import json
from pathlib import Path
from html import escape

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

TRACE_FILE = SCRIPT_DIR / "readers_writers_monitor_trace.json"
OUTPUT_FILE = PROJECT_DIR / "generated_html" / "readers_writers_monitor.html"

with TRACE_FILE.open("r", encoding="utf-8") as file:
    events = json.load(file)

events_json = json.dumps(events).replace("</", "<\\/")

page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Readers-Writers Monitor Simulation</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 24px;
    background: #f3f5f9;
    color: #202536;
}
main { max-width: 1100px; margin: auto; }
.panel {
    background: white;
    padding: 18px;
    margin: 16px 0;
    border-radius: 12px;
    box-shadow: 0 2px 8px #00000012;
}
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
}
.stat { background: #eef2ff; padding: 14px; border-radius: 8px; }
.stat strong { display: block; font-size: 25px; margin-top: 6px; }
button, select {
    padding: 9px 13px;
    margin: 4px;
    cursor: pointer;
}
#status { font-weight: bold; }
.track {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px 0;
}
.track-label { width: 65px; font-weight: bold; }
.bar {
    flex: 1;
    padding: 8px;
    border-radius: 6px;
    background: #e8eaf0;
    min-height: 20px;
}
.reading { background: #c9f2dd; }
.writing { background: #ffd7ad; }
.waiting { background: #fff0ad; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 9px; border-bottom: 1px solid #e4e7ed; text-align: left; }
.timeline { max-height: 420px; overflow: auto; }
small { color: #5c6375; }
</style>
</head>
<body>
<main>
<h1>Readers-Writers Problem</h1>
<p>Monitor-based synchronization replay generated from the recorded Python thread execution.</p>

<section class="panel stats">
  <div class="stat">Readers<strong>4</strong></div>
  <div class="stat">Writers<strong>2</strong></div>
  <div class="stat">Events<strong id="total">0</strong></div>
  <div class="stat">Shared value<strong id="value">0</strong></div>
</section>

<section class="panel">
<h2>Simulation controls</h2>
<button onclick="play()">Play</button>
<button onclick="pause()">Pause</button>
<button onclick="previous()">Previous</button>
<button onclick="next()">Next</button>
<label>Speed
<select id="speed">
<option value="1200">Slow</option>
<option value="600" selected>Normal</option>
<option value="200">Fast</option>
</select>
</label>
<p id="status">Ready</p>
<input id="seek" type="range" min="0" max="0" value="0" style="width:100%">
<p id="counter"></p>
</section>

<section class="panel">
<h2>Current resource state</h2>
<p>Active readers: <strong id="readers">0</strong></p>
<p>Writer active: <strong id="writer">No</strong></p>
<p>Writers waiting: <strong id="waiting">0</strong></p>
<div id="tracks"></div>
<p><small>Readers may share the resource. A writer requires exclusive access.</small></p>
</section>

<section class="panel">
<h2>Current event</h2>
<p><strong id="actor">—</strong>: <span id="action">—</span></p>
<p id="detail"></p>
</section>

<section class="panel timeline">
<h2>Execution timeline</h2>
<table>
<thead><tr><th>#</th><th>Thread</th><th>Action</th><th>Readers</th><th>Writer</th><th>Shared value</th></tr></thead>
<tbody id="log"></tbody>
</table>
</section>
</main>

<script>
const events = __EVENTS__;
let index = 0;
let timer = null;

document.getElementById("total").textContent = events.length;
document.getElementById("seek").max = Math.max(0, events.length - 1);

function render() {
    if (!events.length) return;
    const e = events[index];
    document.getElementById("seek").value = index;
    document.getElementById("counter").textContent =
        `Event ${index + 1} of ${events.length}`;
    document.getElementById("actor").textContent = e.actor ?? "Unknown";
    document.getElementById("action").textContent = e.action ?? "";
    document.getElementById("detail").textContent = e.detail ?? "";
    document.getElementById("readers").textContent = e.active_readers ?? 0;
    document.getElementById("writer").textContent =
        e.active_writer ? "Yes" : "No";
    document.getElementById("waiting").textContent =
        e.waiting_writers ?? 0;
    document.getElementById("value").textContent = e.shared_data ?? 0;

    const states = e.states ?? {};
    document.getElementById("tracks").innerHTML =
        Object.entries(states).map(([name, state]) => {
            let cls = "";
            if (/reading/i.test(state)) cls = "reading";
            else if (/writing/i.test(state)) cls = "writing";
            else if (/waiting/i.test(state)) cls = "waiting";
            return `<div class="track"><div class="track-label">${name}</div>
            <div class="bar ${cls}">${state}</div></div>`;
        }).join("");

    document.getElementById("status").textContent =
        e.active_writer && (e.active_readers ?? 0) > 0
        ? "WARNING: conflicting access recorded!"
        : "Replay loaded from actual execution trace";

    const start = Math.max(0, index - 7);
    const rows = events.slice(start, index + 1).map((item, offset) => {
        const n = start + offset;
        return `<tr ${n === index ? 'style="font-weight:bold;background:#eef2ff"' : ""}>
        <td>${n + 1}</td>
        <td>${item.actor ?? ""}</td>
        <td>${item.action ?? ""}</td>
        <td>${item.active_readers ?? 0}</td>
        <td>${item.active_writer ? "Yes" : "No"}</td>
        <td>${item.shared_data ?? 0}</td></tr>`;
    }).join("");
    document.getElementById("log").innerHTML = rows;
}

function pause() {
    if (timer !== null) clearTimeout(timer);
    timer = null;
}
function next() {
    pause();
    if (index < events.length - 1) index++;
    render();
}
function previous() {
    pause();
    if (index > 0) index--;
    render();
}
function play() {
    pause();
    function tick() {
        if (index >= events.length - 1) {
            timer = null;
            return;
        }
        index++;
        render();
        timer = setTimeout(tick,
            Number(document.getElementById("speed").value));
    }
    timer = setTimeout(tick,
        Number(document.getElementById("speed").value));
}
document.getElementById("seek").addEventListener("input", event => {
    pause();
    index = Number(event.target.value);
    render();
});
render();
</script>
</body>
</html>
"""

page = page.replace("__EVENTS__", events_json)
OUTPUT_FILE.write_text(page, encoding="utf-8")

print("HTML simulation generated successfully.")
print("Events loaded:", len(events))
print("Output file:", OUTPUT_FILE.resolve())

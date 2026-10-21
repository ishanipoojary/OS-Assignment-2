
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

TRACE_FILE = SCRIPT_DIR / "monitor_execution_trace.json"
HTML_FILE = PROJECT_DIR / "generated_html" / "dining_philosophers_monitor.html"

if not TRACE_FILE.exists():
    raise FileNotFoundError(
        "Run dining_philosophers_monitor.py first."
    )

with TRACE_FILE.open("r", encoding="utf-8") as file:
    events = json.load(file)

if not events:
    raise ValueError("The monitor execution trace is empty.")

data = json.dumps(events).replace("</", "<\\/")


page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dining Philosophers — Monitor</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f3f6fa;
    color: #172033;
    padding: 20px;
}
h1, h2 { text-align: center; }
.table {
    position: relative;
    width: 340px;
    height: 340px;
    max-width: 85vw;
    max-height: 85vw;
    margin: 30px auto;
    border: 7px solid #a6b7c9;
    border-radius: 50%;
    background: #e4edf5;
}
.person, .fork {
    position: absolute;
    transform: translate(-50%, -50%);
    text-align: center;
    padding: 10px 4px;
    border-radius: 10px;
    font-size: 12px;
    box-shadow: 0 2px 6px #0002;
}
.person {
    width: 112px;
    background: white;
}
.fork {
    width: 78px;
    background: #fff0c2;
    border: 1px solid #d8b55d;
}
.p0 { left: 50%; top: 7%; }
.p1 { left: 93%; top: 50%; }
.p2 { left: 50%; top: 93%; }
.p3 { left: 7%; top: 50%; }
.f0 { left: 76%; top: 22%; }
.f1 { left: 76%; top: 78%; }
.f2 { left: 24%; top: 78%; }
.f3 { left: 24%; top: 22%; }
.panel {
    max-width: 850px;
    margin: 20px auto;
    padding: 16px;
    background: white;
    border-radius: 12px;
}
.controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin: 12px;
}
button { padding: 9px 16px; cursor: pointer; }
input { width: 100%; }
#log {
    max-height: 250px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
}
.entry {
    padding: 7px;
    border-bottom: 1px solid #ddd;
    cursor: pointer;
}
.active { background: #dff4e5; }
</style>
</head>
<body>
<h1>Dining Philosophers — Monitor</h1>
<p style="text-align:center">
    Four philosopher threads · Monitor lock · Condition variables
</p>

<div class="table">
    <div class="person p0" id="p0"></div>
    <div class="person p1" id="p1"></div>
    <div class="person p2" id="p2"></div>
    <div class="person p3" id="p3"></div>
    <div class="fork f0" id="f0"></div>
    <div class="fork f1" id="f1"></div>
    <div class="fork f2" id="f2"></div>
    <div class="fork f3" id="f3"></div>
</div>

<div class="panel">
    <h2>Execution replay</h2>
    <p id="counter"></p>
    <input type="range" id="timeline" min="0" value="0" step="1">
    <div class="controls">
        <button id="prev">Previous</button>
        <button id="play">Play</button>
        <button id="next">Next</button>
        <button id="reset">Reset</button>
    </div>
    <p id="current"></p>
    <p>Each frame comes from the recorded Python execution trace.</p>
</div>

<div class="panel">
    <h2>Event log</h2>
    <div id="log"></div>
</div>

<script>
const events = __EVENT_DATA__;
let index = 0;
let timer = null;

const slider = document.getElementById("timeline");
slider.max = events.length - 1;

function stop() {
    if (timer !== null) clearInterval(timer);
    timer = null;
    document.getElementById("play").textContent = "Play";
}

function render() {
    const e = events[index];

    for (let i = 0; i < 4; i++) {
        const state = e.states[i];
        const p = document.getElementById("p" + i);
        p.textContent = "P" + i + " · " + state;
        p.style.background = state === "Eating" ? "#c8f2d0" :
            state === "Hungry" ? "#ffe0bd" :
            state === "Finished" ? "#dbeafe" : "white";

        const owner = e.chopstick_owners[i];
        const f = document.getElementById("f" + i);
        f.textContent = owner === null ?
            "C" + i + " · Free" : "C" + i + " · P" + owner;
        f.style.background = owner === null ? "#fff0c2" : "#b8e3fa";
    }

    slider.value = index;
    document.getElementById("counter").textContent =
        "Event " + (index + 1) + " of " + events.length +
        " · Time " + e.time + " seconds";

    document.getElementById("current").textContent =
        "P" + e.philosopher + ": " + e.action +
        (e.detail ? " — " + e.detail : "");

    document.querySelectorAll(".entry").forEach((row, i) =>
        row.classList.toggle("active", i === index)
    );
    document.querySelector(".entry.active")?.scrollIntoView({
        block: "nearest"
    });
}

function moveTo(n) {
    index = Math.max(0, Math.min(events.length - 1, n));
    render();
}

document.getElementById("prev").onclick = () => {
    stop(); moveTo(index - 1);
};
document.getElementById("next").onclick = () => {
    stop(); moveTo(index + 1);
};
document.getElementById("reset").onclick = () => {
    stop(); moveTo(0);
};
document.getElementById("play").onclick = () => {
    if (timer !== null) {
        stop();
        return;
    }
    if (index === events.length - 1) moveTo(0);
    document.getElementById("play").textContent = "Pause";
    timer = setInterval(() => {
        if (index >= events.length - 1) {
            stop();
            return;
        }
        moveTo(index + 1);
    }, 500);
};
slider.oninput = () => {
    stop(); moveTo(Number(slider.value));
};

const log = document.getElementById("log");
events.forEach((e, i) => {
    const row = document.createElement("div");
    row.className = "entry";
    row.textContent = "#" + (i + 1) + " [" + e.time + "s] P" +
        e.philosopher + ": " + e.action +
        (e.detail ? " — " + e.detail : "");
    row.onclick = () => {
        stop(); moveTo(i);
    };
    log.appendChild(row);
});

render();
</script>
</body>
</html>
"""

HTML_FILE.write_text(
    page.replace("__EVENT_DATA__", data),
    encoding="utf-8"
)

print(f"Generated {HTML_FILE.resolve()}")
print(f"Embedded {len(events)} monitor events.")

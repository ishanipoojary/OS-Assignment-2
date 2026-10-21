
import json
from pathlib import Path
from html import escape

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

TRACE_FILE = SCRIPT_DIR / "readers_writers_trace.json"
HTML_FILE = PROJECT_DIR / "generated_html" / "readers_writers_semaphore.html"

if not TRACE_FILE.exists():
    raise FileNotFoundError(
        "Run readers_writers_semaphore.py first."
    )

with TRACE_FILE.open("r", encoding="utf-8") as file:
    events = json.load(file)

if not events:
    raise ValueError("The execution trace is empty.")

data = json.dumps(events).replace("</", "<\\/")


page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Readers-Writers Semaphore Simulation</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f3f6fa;
    color: #172033;
    padding: 20px;
}
h1, h2 { text-align: center; }
.summary { text-align: center; }
.panel {
    max-width: 900px;
    margin: 20px auto;
    padding: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px #0001;
}
.metrics {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
}
.metric {
    padding: 15px;
    border-radius: 10px;
    background: #e7eef8;
    min-width: 120px;
    text-align: center;
}
.metric strong { display: block; font-size: 24px; }
.actors {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
}
.actor {
    padding: 14px;
    text-align: center;
    background: #f1f5f9;
    border-radius: 10px;
    overflow-wrap: anywhere;
}
.reader { border-left: 5px solid #60a5fa; }
.writer { border-left: 5px solid #f59e0b; }
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
    max-height: 300px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
}
.entry {
    padding: 8px;
    border-bottom: 1px solid #ddd;
    cursor: pointer;
}
.active { background: #dff4e5; }
.note { color: #536175; font-size: 13px; }
</style>
</head>
<body>

<h1>Readers-Writers Problem</h1>
<p class="summary">
    Semaphore-based synchronization · Concurrent readers and writers
</p>

<div class="panel">
    <h2>Shared resource</h2>
    <div class="metrics">
        <div class="metric">
            <strong id="value">0</strong>
            Shared data
        </div>
        <div class="metric">
            <strong id="count">0</strong>
            Reader count
        </div>
        <div class="metric">
            <strong id="position">0 / 0</strong>
            Event position
        </div>
    </div>
    <p id="current"></p>
</div>

<div class="panel">
    <h2>Thread states</h2>
    <div class="actors" id="actors"></div>
</div>

<div class="panel">
    <h2>Execution replay</h2>
    <input type="range" id="timeline" min="0" value="0" step="1">
    <div class="controls">
        <button id="prev">Previous</button>
        <button id="play">Play</button>
        <button id="next">Next</button>
        <button id="reset">Reset</button>
    </div>
    <p class="note">
        Replay uses snapshots recorded by the Python program.
        It does not simulate synchronization independently in the browser.
    </p>
</div>

<div class="panel">
    <h2>Execution event log</h2>
    <div id="log"></div>
</div>

<script>
const events = __EVENT_DATA__;
let index = 0;
let timer = null;

const timeline = document.getElementById("timeline");
timeline.max = events.length - 1;

const actorNames = [...new Set(events.map(e => e.actor))];

const actorContainer = document.getElementById("actors");

actorNames.forEach(name => {
    const card = document.createElement("div");
    card.className = "actor " + (name.startsWith("R") ? "reader" : "writer");
    card.id = "actor-" + name;
    actorContainer.appendChild(card);
});

function stop() {
    if (timer !== null) clearInterval(timer);
    timer = null;
    document.getElementById("play").textContent = "Play";
}

function moveTo(n) {
    index = Math.max(0, Math.min(events.length - 1, n));
    render();
}

function render() {
    const event = events[index];

    document.getElementById("value").textContent = event.shared_data;
    document.getElementById("count").textContent = event.read_count;
    document.getElementById("position").textContent =
        (index + 1) + " / " + events.length;

    document.getElementById("current").textContent =
        event.actor + " — " + event.action +
        (event.detail ? ": " + event.detail : "") +
        " · " + event.time + " seconds";

    actorNames.forEach(name => {
        const card = document.getElementById("actor-" + name);
        const state = event.states[name] || "Not started";
        card.textContent = name + " · " + state;
        card.style.background =
            state === "Reading" ? "#dbeafe" :
            state === "Writing" ? "#ffedd5" :
            state === "Waiting" ? "#fef3c7" :
            state === "Completed" ? "#dcfce7" : "#f1f5f9";
    });

    timeline.value = index;

    document.querySelectorAll(".entry").forEach((row, i) => {
        row.classList.toggle("active", i === index);
    });

    document.querySelector(".entry.active")?.scrollIntoView({
        block: "nearest"
    });
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

timeline.oninput = () => {
    stop(); moveTo(Number(timeline.value));
};

const log = document.getElementById("log");

events.forEach((event, i) => {
    const row = document.createElement("div");
    row.className = "entry";
    row.textContent =
        "#" + (i + 1) + " [" + event.time + "s] " +
        event.actor + " (" + event.role + "): " +
        event.action +
        (event.detail ? " — " + event.detail : "");

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
print(f"Embedded {len(events)} recorded events.")


import json
from pathlib import Path
from html import escape

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

TRACE_FILE = SCRIPT_DIR / "execution_trace.json"
HTML_FILE = PROJECT_DIR / "generated_html" / "dining_philosophers.html"

if not TRACE_FILE.exists():
    raise FileNotFoundError(
        "execution_trace.json not found. Run dining_philosophers.py first."
    )

with TRACE_FILE.open("r", encoding="utf-8") as file:
    events = json.load(file)

if not events:
    raise ValueError("The execution trace contains no events.")

trace_json = json.dumps(events).replace("</", "<\\/")


template = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dining Philosophers Simulation</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 24px;
    background: #f3f6fa;
    color: #172033;
}
h1, h2 { text-align: center; }
.summary {
    text-align: center;
    margin-bottom: 20px;
}
.table {
    position: relative;
    width: 340px;
    height: 340px;
    max-width: 90vw;
    max-height: 90vw;
    margin: 20px auto;
    border: 7px solid #a6b7c9;
    border-radius: 50%;
    background: #e4edf5;
}
.philosopher {
    position: absolute;
    width: 112px;
    padding: 10px 4px;
    border-radius: 12px;
    background: white;
    text-align: center;
    box-shadow: 0 2px 7px #0002;
    font-size: 13px;
    transform: translate(-50%, -50%);
}
.p0 { left: 50%; top: 7%; }
.p1 { left: 93%; top: 50%; }
.p2 { left: 50%; top: 93%; }
.p3 { left: 7%; top: 50%; }

.fork {
    position: absolute;
    width: 78px;
    padding: 8px 2px;
    border-radius: 8px;
    background: #fff0c2;
    text-align: center;
    font-size: 12px;
    transform: translate(-50%, -50%);
    border: 1px solid #d8b55d;
}
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
    box-shadow: 0 2px 8px #0001;
}
.controls {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin: 12px;
}
button { padding: 9px 16px; cursor: pointer; }
input { width: 100%; }
#eventList {
    max-height: 250px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
}
.event {
    padding: 7px;
    border-bottom: 1px solid #e5e7eb;
}
.current { background: #e6f4ea; }
.note { color: #536175; font-size: 13px; }
</style>
</head>
<body>

<h1>Dining Philosophers</h1>
<div class="summary">
    Semaphore-based synchronization · 4 philosophers · 4 chopsticks
</div>

<div class="table">
    <div class="philosopher p0" id="p0"></div>
    <div class="philosopher p1" id="p1"></div>
    <div class="philosopher p2" id="p2"></div>
    <div class="philosopher p3" id="p3"></div>

    <div class="fork f0" id="f0"></div>
    <div class="fork f1" id="f1"></div>
    <div class="fork f2" id="f2"></div>
    <div class="fork f3" id="f3"></div>
</div>

<div class="panel">
    <h2>Execution replay</h2>
    <div id="counter"></div>
    <input id="timeline" type="range" min="0" value="0" step="1">
    <div class="controls">
        <button id="prev">Previous</button>
        <button id="play">Play</button>
        <button id="next">Next</button>
        <button id="reset">Reset</button>
    </div>
    <p id="currentEvent"></p>
    <p class="note">
        Each step represents a snapshot recorded by the actual Python run.
        Playback follows the recorded event order.
    </p>
</div>

<div class="panel">
    <h2>Execution event log</h2>
    <div id="eventList"></div>
</div>

<script>
const events = __TRACE__;
let index = 0;
let timer = null;

const timeline = document.getElementById("timeline");
timeline.max = events.length - 1;

function render() {
    const event = events[index];
    if (!event) return;

    for (let i = 0; i < 4; i++) {
        const state = event.states[i];
        const philosopher = document.getElementById("p" + i);
        philosopher.textContent =
            "P" + i + " · " + state;

        philosopher.style.background =
            state === "Eating" ? "#c8f2d0" :
            state === "Hungry" ||
            state === "Waiting for chopsticks" ||
            state === "Acquiring chopsticks" ? "#ffe0bd" :
            state === "Finished" ? "#dbeafe" : "white";

        const owner = event.chopstick_owners[i];
        const fork = document.getElementById("f" + i);
        fork.textContent = owner === null
            ? "C" + i + " · Free"
            : "C" + i + " · P" + owner;
        fork.style.background =
            owner === null ? "#fff0c2" : "#b8e3fa";
    }

    timeline.value = index;
    document.getElementById("counter").textContent =
        "Event " + (index + 1) + " of " + events.length +
        " · Time: " + event.time + " seconds";

    document.getElementById("currentEvent").textContent =
        "P" + event.philosopher + ": " +
        event.action +
        (event.detail ? " — " + event.detail : "");

    document.querySelectorAll(".event").forEach((item, i) => {
        item.classList.toggle("current", i === index);
    });

    document.querySelector(".event.current")?.scrollIntoView({
        block: "nearest"
    });
}

function stop() {
    if (timer !== null) {
        clearInterval(timer);
        timer = null;
    }
    document.getElementById("play").textContent = "Play";
}

function moveTo(value) {
    index = Math.max(0, Math.min(events.length - 1, value));
    render();
}

function togglePlay() {
    if (timer !== null) {
        stop();
        return;
    }

    if (index >= events.length - 1) moveTo(0);

    document.getElementById("play").textContent = "Pause";
    timer = setInterval(() => {
        if (index >= events.length - 1) {
            stop();
            return;
        }
        moveTo(index + 1);
    }, 500);
}

document.getElementById("prev").onclick = () => {
    stop();
    moveTo(index - 1);
};

document.getElementById("next").onclick = () => {
    stop();
    moveTo(index + 1);
};

document.getElementById("play").onclick = togglePlay;

document.getElementById("reset").onclick = () => {
    stop();
    moveTo(0);
};

timeline.oninput = () => {
    stop();
    moveTo(Number(timeline.value));
};

const list = document.getElementById("eventList");
events.forEach((event, i) => {
    const row = document.createElement("div");
    row.className = "event";
    row.textContent =
        "#" + (i + 1) + " [" + event.time + "s] P" +
        event.philosopher + ": " + event.action +
        (event.detail ? " — " + event.detail : "");

    row.onclick = () => {
        stop();
        moveTo(i);
    };

    list.appendChild(row);
});

render();
</script>
</body>
</html>
"""

HTML_FILE.write_text(
    template.replace("__TRACE__", trace_json),
    encoding="utf-8"
)

print(f"Generated {HTML_FILE.resolve()}")
print(f"Embedded {len(events)} events from the execution trace.")

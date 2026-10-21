
import json
from pathlib import Path

trace_path = Path(__file__).resolve().parent / "readers_writers_trace.json"

with trace_path.open("r", encoding="utf-8") as file:
    events = json.load(file)

errors = []
reader_counts = {f"R{i}": 0 for i in range(4)}
writer_counts = {f"W{i}": 0 for i in range(2)}

for number, event in enumerate(events, start=1):
    actor = event.get("actor")
    action = event.get("action")
    states = event.get("states", {})

    # Count actual reader and writer access starts.
    if action == "Started reading" and actor in reader_counts:
        reader_counts[actor] += 1

    if action == "Writing" and actor in writer_counts:
        writer_counts[actor] += 1

    # A writer must never be active while any reader is reading.
    active_readers = [
        name for name, state in states.items()
        if name.startswith("R") and state == "Reading"
    ]
    active_writers = [
        name for name, state in states.items()
        if name.startswith("W") and state == "Writing"
    ]

    if active_readers and active_writers:
        errors.append(
            f"Event {number}: reader-writer overlap in recorded states"
        )

    if len(active_writers) > 1:
        errors.append(
            f"Event {number}: multiple writers active in recorded states"
        )

print("Total events:", len(events))
print("Reader access counts:", reader_counts)
print("Writer access counts:", writer_counts)

if reader_counts != {f"R{i}": 3 for i in range(4)}:
    errors.append("Each reader must complete exactly 3 reads")

if writer_counts != {f"W{i}": 3 for i in range(2)}:
    errors.append("Each writer must complete exactly 3 writes")

if not events:
    errors.append("Execution trace is empty")

if errors:
    print("\nVERIFICATION FAILED")
    for error in errors:
        print("-", error)
else:
    print("\nAll recorded-state and access-count checks passed.")

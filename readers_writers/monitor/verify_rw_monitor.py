from pathlib import Path
import json
from collections import Counter

trace_path = Path(__file__).resolve().parent / "readers_writers_monitor_trace.json"

with trace_path.open("r", encoding="utf-8") as file:
    events = json.load(file)

errors = []
reader_starts = Counter()
writer_starts = Counter()

for event in events:
    action = event.get("action", "")
    actor = event.get("actor", "")
    active_readers = event.get("active_readers", 0)
    active_writer = event.get("active_writer", False)

    # A writer must never overlap with any reader.
    if active_writer and active_readers > 0:
        errors.append(
            f"Reader-writer overlap found at event: {event}"
        )

    # Count completed access-start events per thread.
    if action == "Started reading":
        reader_starts[actor] += 1

    if action == "Writing":
        writer_starts[actor] += 1

print("Total events:", len(events))
print("Reader access counts:", dict(reader_starts))
print("Writer access counts:", dict(writer_starts))

if errors:
    print("\nVERIFICATION FAILED")
    for error in errors:
        print(error)
else:
    print("\nNo reader-writer overlap detected.")

    if (
        len(reader_starts) == 4
        and len(writer_starts) == 2
        and all(count == 3 for count in reader_starts.values())
        and all(count == 3 for count in writer_starts.values())
    ):
        print("All threads completed the expected access rounds.")
        print("ALL CHECKS PASSED")
    else:
        print("WARNING: Expected access counts were not met.")

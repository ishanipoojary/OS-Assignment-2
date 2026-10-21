
import json
from pathlib import Path

N = 4

trace_path = Path(__file__).resolve().parent / "execution_trace.json"

with trace_path.open("r", encoding="utf-8") as file:
    events = json.load(file)

errors = []
eating_counts = [0] * N

for number, event in enumerate(events, start=1):
    owners = event["chopstick_owners"]

    # Check that one chopstick is never assigned
    # to two philosophers.
    held = [owner for owner in owners if owner is not None]

    if len(held) != len(set(
        (stick, owner)
        for stick, owner in enumerate(owners)
        if owner is not None
    )):
        errors.append(
            f"Event {number}: duplicate chopstick ownership"
        )

    # Check that an Eating event has both chopsticks.
    if event["action"] == "Eating":
        pid = event["philosopher"]
        left = pid
        right = (pid + 1) % N

        if owners[left] != pid or owners[right] != pid:
            errors.append(
                f"Event {number}: P{pid} eats without both chopsticks"
            )

        eating_counts[pid] += 1

print("Eating rounds per philosopher:", eating_counts)

if eating_counts != [3, 3, 3, 3]:
    errors.append("Not every philosopher completed three rounds")

if errors:
    print("\nVERIFICATION FAILED")
    for error in errors:
        print("-", error)
else:
    print("\nAll checks passed for the recorded trace.")

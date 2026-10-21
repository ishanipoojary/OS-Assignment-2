from pathlib import Path
import json

N = 4

trace_path = Path(__file__).resolve().parent / "monitor_execution_trace.json"

with trace_path.open("r", encoding="utf-8") as file:
    events = json.load(file)

errors = []
eating_counts = [0] * N

for number, event in enumerate(events, start=1):
    owners = event["chopstick_owners"]

    # Each chopstick must have at most one owner.
    for stick, owner in enumerate(owners):
        if owner is not None and not 0 <= owner < N:
            errors.append(
                f"Event {number}: invalid owner for C{stick}"
            )

    # Verify that adjacent philosophers never eat together.
    states = event["states"]

    for pid in range(N):
        neighbour = (pid + 1) % N

        if states[pid] == "Eating" and states[neighbour] == "Eating":
            errors.append(
                f"Event {number}: adjacent philosophers "
                f"P{pid} and P{neighbour} are both eating"
            )

    # An Eating event must show ownership of both chopsticks.
    if event["action"] == "Eating":
        pid = event["philosopher"]
        left = pid
        right = (pid + 1) % N

        if owners[left] != pid or owners[right] != pid:
            errors.append(
                f"Event {number}: P{pid} does not own both chopsticks"
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

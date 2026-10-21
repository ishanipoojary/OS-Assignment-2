from pathlib import Path
import json
import random
import threading
import time

N = 4
ROUNDS = 3

THINKING = "Thinking"
HUNGRY = "Hungry"
EATING = "Eating"

states = [THINKING] * N
owners = [None] * N
events = []

monitor_lock = threading.RLock()
conditions = [
    threading.Condition(monitor_lock)
    for _ in range(N)
]

start_time = time.monotonic()


def record_event(pid, action, detail=""):
    """Record a snapshot while the monitor lock is held."""
    events.append({
        "time": round(time.monotonic() - start_time, 4),
        "philosopher": pid,
        "action": action,
        "detail": detail,
        "states": states.copy(),
        "chopstick_owners": owners.copy()
    })


def left_of(pid):
    return (pid + N - 1) % N


def right_of(pid):
    return (pid + 1) % N


def test(pid):
    """Allow a hungry philosopher to eat if both neighbours can."""
    if (
        states[pid] == HUNGRY
        and states[left_of(pid)] != EATING
        and states[right_of(pid)] != EATING
    ):
        left_stick = pid
        right_stick = (pid + 1) % N

        states[pid] = EATING
        owners[left_stick] = pid
        owners[right_stick] = pid

        record_event(pid, "Eating", "Both chopsticks available")
        conditions[pid].notify()


def pickup(pid):
    """Request permission to eat through the monitor."""
    with monitor_lock:
        states[pid] = HUNGRY
        record_event(pid, "Hungry", "Requests both chopsticks")

        test(pid)

        while states[pid] != EATING:
            record_event(pid, "Waiting", "Neighbour is eating")
            conditions[pid].wait()


def putdown(pid):
    """Finish eating and notify eligible neighbours."""
    with monitor_lock:
        left_stick = pid
        right_stick = (pid + 1) % N

        owners[left_stick] = None
        owners[right_stick] = None
        states[pid] = THINKING
        record_event(pid, "Put down chopsticks")

        # Check both neighbours after releasing the chopsticks.
        test(left_of(pid))
        test(right_of(pid))


def philosopher_lifecycle(pid):
    for round_no in range(1, ROUNDS + 1):
        with monitor_lock:
            states[pid] = THINKING
            record_event(pid, "Thinking", f"Round {round_no}")

        time.sleep(random.uniform(0.1, 0.3))

        pickup(pid)

        try:
            time.sleep(random.uniform(0.2, 0.5))
        finally:
            putdown(pid)

    with monitor_lock:
        states[pid] = "Finished"
        record_event(pid, "Completed", "All rounds finished")


def main():
    threads = [
        threading.Thread(
            target=philosopher_lifecycle,
            args=(pid,),
            name=f"MonitorPhilosopher-{pid}"
        )
        for pid in range(N)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    trace_path = Path(__file__).resolve().parent / "monitor_execution_trace.json"
    
    with trace_path.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)

    print("\nAll philosophers have finished.")
    print(f"Philosophers: {N}")
    print(f"Eating rounds per philosopher: {ROUNDS}")
    print(f"Total eating rounds: {N * ROUNDS}")
    print(f"Events recorded: {len(events)}")
    print("Saved execution trace to monitor_execution_trace.json")

    
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "generate_monitor_html.py")],
        check=True
    )



if __name__ == "__main__":
    main()



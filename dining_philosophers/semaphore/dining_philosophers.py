from pathlib import Path
import json
import random
import threading
import time

N = 4
ROUNDS = 3

chopsticks = [threading.Semaphore(1) for _ in range(N)]
room = threading.Semaphore(3)

states = ["Thinking"] * N
owners = [None] * N
events = []

log_lock = threading.Lock()
start_time = time.monotonic()


def log_event(pid, action, detail="", state=None, stick=None,
              owner=None, update_owner=False):
    with log_lock:
        if state is not None:
            states[pid] = state

        if update_owner:
            owners[stick] = owner

        events.append({
            "time": round(time.monotonic() - start_time, 4),
            "philosopher": pid,
            "action": action,
            "detail": detail,
            "states": states.copy(),
            "chopstick_owners": owners.copy()
        })


def philosopher_lifecycle(pid):
    left = pid
    right = (pid + 1) % N

    for round_no in range(1, ROUNDS + 1):
        log_event(pid, "Thinking", f"Round {round_no}",
                  state="Thinking")
        time.sleep(random.uniform(0.1, 0.3))

        log_event(pid, "Hungry", f"Round {round_no}",
                  state="Hungry")

        room_held = False
        held_sticks = []

        try:
            room.acquire()
            room_held = True
            log_event(pid, "Entered room", "Permit acquired",
                      state="Waiting for chopsticks")

            chopsticks[left].acquire()
            held_sticks.append(left)
            log_event(pid, "Acquired chopstick", f"C{left}",
                      state="Acquiring chopsticks",
                      stick=left, owner=pid, update_owner=True)

            chopsticks[right].acquire()
            held_sticks.append(right)
            log_event(pid, "Acquired chopstick", f"C{right}",
                      stick=right, owner=pid, update_owner=True)

            log_event(pid, "Eating", f"Round {round_no}",
                      state="Eating")
            time.sleep(random.uniform(0.2, 0.5))

        finally:
            for stick in reversed(held_sticks):
                log_event(pid, "Released chopstick", f"C{stick}",
                          stick=stick, owner=None, update_owner=True)
                chopsticks[stick].release()

            log_event(pid, "Finished round", str(round_no),
                      state="Thinking")

            if room_held:
                room.release()

    log_event(pid, "Completed", "All rounds finished",
              state="Finished")


def main():
    threads = [
        threading.Thread(
            target=philosopher_lifecycle,
            args=(pid,),
            name=f"Philosopher-{pid}"
        )
        for pid in range(N)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    trace_path = Path(__file__).resolve().parent / "execution_trace.json"
    with trace_path.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)

    print("\nAll philosophers have finished.")
    print(f"Philosophers: {N}")
    print(f"Eating rounds per philosopher: {ROUNDS}")
    print(f"Total eating rounds: {N * ROUNDS}")
    print(f"Events recorded: {len(events)}")
    print("Saved execution trace to execution_trace.json")
    import subprocess
    import sys

    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parent / "generate_html.py")
        ],
        check=True
    )


if __name__ == "__main__":
    main()

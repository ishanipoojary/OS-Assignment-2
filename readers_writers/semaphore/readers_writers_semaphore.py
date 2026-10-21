from pathlib import Path

import json
import random
import threading
import time

READER_COUNT = 4
WRITER_COUNT = 2
ROUNDS = 3

# Synchronization primitives
mutex = threading.Semaphore(1)
write_lock = threading.Semaphore(1)

# Shared data
read_count = 0
shared_data = 0

events = []
states = {}
log_lock = threading.Lock()
start_time = time.monotonic()


def record_event(actor, role, action, detail=""):
    """Save a snapshot of the current execution."""
    with log_lock:
        events.append({
            "time": round(time.monotonic() - start_time, 4),
            "actor": actor,
            "role": role,
            "action": action,
            "detail": detail,
            "read_count": read_count,
            "shared_data": shared_data,
            "states": states.copy()
        })


def reader_task(reader_id):
    global read_count

    actor = f"R{reader_id}"

    for round_no in range(1, ROUNDS + 1):
        with log_lock:
            states[actor] = "Waiting"

        record_event(
            actor, "Reader", "Waiting to read",
            f"Round {round_no}"
        )

        mutex.acquire()
        try:
            with log_lock:
                read_count += 1
                first_reader = read_count == 1

            if first_reader:
                write_lock.acquire()

            with log_lock:
                states[actor] = "Reading"

            record_event(
                actor, "Reader", "Started reading",
                f"Round {round_no}"
            )
        finally:
            mutex.release()

        try:
            time.sleep(random.uniform(0.1, 0.3))

            record_event(
                actor, "Reader", "Finished reading",
                f"Observed value {shared_data}"
            )
        finally:
            mutex.acquire()
            try:
                with log_lock:
                    read_count -= 1
                    last_reader = read_count == 0
                    states[actor] = "Finished reading"

                record_event(
                    actor, "Reader", "Left resource"
                )

                if last_reader:
                    write_lock.release()
            finally:
                mutex.release()

        time.sleep(random.uniform(0.1, 0.2))

    with log_lock:
        states[actor] = "Completed"

    record_event(
        actor, "Reader", "Completed",
        "All rounds finished"
    )


def writer_task(writer_id):
    global shared_data

    actor = f"W{writer_id}"

    for round_no in range(1, ROUNDS + 1):
        with log_lock:
            states[actor] = "Waiting"

        record_event(
            actor, "Writer", "Waiting to write",
            f"Round {round_no}"
        )

        write_lock.acquire()
        try:
            with log_lock:
                states[actor] = "Writing"
                old_value = shared_data
                shared_data = old_value + 1
                new_value = shared_data

            record_event(
                actor, "Writer", "Writing",
                f"Changed value from {old_value} to {new_value}"
            )

            time.sleep(random.uniform(0.2, 0.4))
        finally:
            write_lock.release()

        with log_lock:
            states[actor] = "Finished writing"

        record_event(
            actor, "Writer", "Writer finished"
        )

        time.sleep(random.uniform(0.1, 0.2))

    with log_lock:
        states[actor] = "Completed"

    record_event(
        actor, "Writer", "Completed",
        "All rounds finished"
    )


def main():
    threads = []

    for reader_id in range(READER_COUNT):
        threads.append(
            threading.Thread(
                target=reader_task,
                args=(reader_id,),
                name=f"Reader-{reader_id}"
            )
        )

    for writer_id in range(WRITER_COUNT):
        threads.append(
            threading.Thread(
                target=writer_task,
                args=(writer_id,),
                name=f"Writer-{writer_id}"
            )
        )

    random.shuffle(threads)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    trace_path = Path(__file__).resolve().parent / "readers_writers_trace.json"
    with trace_path.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)

    print("\nReaders-Writers execution completed.")
    print(f"Readers: {READER_COUNT}")
    print(f"Writers: {WRITER_COUNT}")
    print(f"Rounds per thread: {ROUNDS}")
    print(f"Final shared value: {shared_data}")
    print(f"Recorded events: {len(events)}")
    print("Saved readers_writers_trace.json")

    
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, (str(Path(__file__).resolve().parent / "generate_rw_semaphore_html.py"))],
        check=True
    )


    expected_value = WRITER_COUNT * ROUNDS

    if shared_data != expected_value:
        raise RuntimeError(
            f"Expected shared value {expected_value}, "
            f"but got {shared_data}."
        )

    print("Final shared value check passed.")


if __name__ == "__main__":
    main()



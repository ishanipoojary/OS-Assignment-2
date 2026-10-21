from pathlib import Path
import json
import random
import threading
import time

READER_COUNT = 4
WRITER_COUNT = 2
ROUNDS = 3

monitor = threading.Condition(threading.RLock())

active_readers = 0
active_writer = False
waiting_writers = 0
shared_data = 0

states = {}
events = []
start_time = time.monotonic()


def record_event(actor, role, action, detail=""):
    """Record a snapshot while holding the monitor lock."""
    events.append({
        "time": round(time.monotonic() - start_time, 4),
        "actor": actor,
        "role": role,
        "action": action,
        "detail": detail,
        "active_readers": active_readers,
        "active_writer": active_writer,
        "waiting_writers": waiting_writers,
        "shared_data": shared_data,
        "states": states.copy()
    })


def reader_task(reader_id):
    global active_readers

    actor = f"R{reader_id}"

    for round_no in range(1, ROUNDS + 1):
        with monitor:
            states[actor] = "Waiting"
            record_event(
                actor, "Reader", "Waiting to read",
                f"Round {round_no}"
            )

            while active_writer or waiting_writers > 0:
                monitor.wait()

            active_readers += 1
            states[actor] = "Reading"
            record_event(
                actor, "Reader", "Started reading",
                f"Round {round_no}"
            )

        try:
            # Multiple readers may be here simultaneously.
            time.sleep(random.uniform(0.1, 0.3))

            with monitor:
                record_event(
                    actor, "Reader", "Finished reading",
                    f"Observed value {shared_data}"
                )
        finally:
            with monitor:
                active_readers -= 1
                states[actor] = "Finished reading"
                record_event(actor, "Reader", "Left resource")

                if active_readers == 0:
                    monitor.notify_all()

        time.sleep(random.uniform(0.1, 0.2))

    with monitor:
        states[actor] = "Completed"
        record_event(
            actor, "Reader", "Completed",
            "All rounds finished"
        )


def writer_task(writer_id):
    global active_writer, waiting_writers, shared_data

    actor = f"W{writer_id}"

    for round_no in range(1, ROUNDS + 1):
        with monitor:
            waiting_writers += 1
            states[actor] = "Waiting"
            record_event(
                actor, "Writer", "Waiting to write",
                f"Round {round_no}"
            )

            try:
                while active_writer or active_readers > 0:
                    monitor.wait()

                active_writer = True
                waiting_writers -= 1

                states[actor] = "Writing"
                old_value = shared_data
                shared_data += 1

                record_event(
                    actor, "Writer", "Writing",
                    f"Changed value from {old_value} to {shared_data}"
                )
            except BaseException:
                waiting_writers -= 1
                monitor.notify_all()
                raise

        try:
            time.sleep(random.uniform(0.2, 0.4))
        finally:
            with monitor:
                active_writer = False
                states[actor] = "Finished writing"
                record_event(actor, "Writer", "Writer finished")
                monitor.notify_all()

        time.sleep(random.uniform(0.1, 0.2))

    with monitor:
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

    trace_path = Path(__file__).resolve().parent / "readers_writers_monitor_trace.json"
    with trace_path.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)

    expected_value = WRITER_COUNT * ROUNDS

    print("\nReaders-Writers monitor execution completed.")
    print(f"Readers: {READER_COUNT}")
    print(f"Writers: {WRITER_COUNT}")
    print(f"Rounds per thread: {ROUNDS}")
    print(f"Final shared value: {shared_data}")
    print(f"Recorded events: {len(events)}")
    print("Saved readers_writers_monitor_trace.json")

    
    import subprocess
    import sys

    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parent / "generate_rw_monitor_html.py"),
        ],
        check=True
    )


    if shared_data != expected_value:
        raise RuntimeError(
            f"Expected {expected_value}, got {shared_data}"
        )

    print("Final shared value check passed.")


if __name__ == "__main__":
    main()

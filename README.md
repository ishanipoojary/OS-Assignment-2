# Operating Systems Programming Assignment

## AI-Assisted Synchronization Algorithms with Program-Generated HTML Simulation

**Student Name:** Ishani Poojary  
**USN:** NNM24IS094  
**Course:** Operating Systems  
**Programming Language:** Python  
**Assignment:** Readers–Writers Problem and Dining Philosophers Problem

---

## 1. Project Overview

This project implements two classical operating-system synchronization problems using semaphore-based and monitor-based approaches. It demonstrates concurrent execution, mutual exclusion, shared-resource management, and execution-event recording.

The project contains four implementations. Each program records execution events and state information in a JSON trace file and generates an HTML simulation from the recorded data. The HTML simulations allow users to inspect and replay recorded execution sequences in a web browser.

## 2. Objectives

- Implement the Readers–Writers problem using semaphores.
- Implement the Readers–Writers problem using a monitor-style approach.
- Implement the Dining Philosophers problem for four philosophers using semaphores.
- Implement the Dining Philosophers problem for four philosophers using a monitor-style approach.
- Demonstrate concurrent execution and shared-resource synchronization.
- Record execution events and generate browser-based HTML simulations.
- Examine mutual exclusion, race conditions, deadlock prevention, and starvation considerations.

## 3. Technologies Used

- **Python:** Implementation of synchronization algorithms and concurrent threads.
- **Python threading module:** Thread creation, locks, semaphores, and condition variables.
- **JSON:** Storage of execution traces and state snapshots.
- **HTML, CSS, and JavaScript:** Browser-based visualization and replay of recorded events.
- **PowerShell:** Running programs and verification scripts on Windows.
- **Git and GitHub:** Version control and source-code hosting.

The implementations use Python's standard library and do not require additional third-party packages under the current configuration.

## 4. Project Structure

```text
DiningPhilosophers/
├── README.md
├── dining_philosophers/
│   ├── semaphore/
│   │   ├── dining_philosophers.py
│   │   ├── generate_html.py
│   │   ├── execution_trace.json
│   │   └── verify_trace.py
│   └── monitor/
│       ├── dining_philosophers_monitor.py
│       ├── generate_monitor_html.py
│       ├── monitor_execution_trace.json
│       └── verify_monitor.py
├── readers_writers/
│   ├── semaphore/
│   │   ├── readers_writers_semaphore.py
│   │   ├── generate_rw_semaphore_html.py
│   │   ├── readers_writers_trace.json
│   │   └── verify_rw_semaphore.py
│   └── monitor/
│       ├── readers_writers_monitor.py
│       ├── generate_rw_monitor_html.py
│       ├── readers_writers_monitor_trace.json
│       └── verify_rw_monitor.py
├── generated_html/
│   ├── dining_philosophers.html
│   ├── dining_philosophers_monitor.html
│   ├── readers_writers_semaphore.html
│   └── readers_writers_monitor.html
├── screenshots/
├── ai_prompts/
├── references/
└── report/
```

The JSON files store execution traces. The HTML files are generated from those traces and display recorded events in a browser. The supporting folders are intended for screenshots, AI prompt documentation, references, and the assignment report.

## 5. Implementation Details

### 5.1 Readers–Writers Problem — Semaphore Based

**Source file:** `readers_writers_semaphore.py`  
**Execution trace:** `readers_writers_trace.json`  
**HTML simulation:** `readers_writers_semaphore.html`

This implementation uses semaphores to coordinate readers and writers accessing a shared resource. Multiple readers may read concurrently, while writing requires exclusive access.

The configuration uses four reader threads, two writer threads, and three rounds per thread. The observed final shared value is `6`, corresponding to six completed writer updates.

The implementation follows a reader-priority approach. Writer starvation may be a consideration if readers continuously arrive.

### 5.2 Readers–Writers Problem — Monitor Based

**Source file:** `readers_writers_monitor.py`  
**Execution trace:** `readers_writers_monitor_trace.json`  
**HTML simulation:** `readers_writers_monitor.html`

This implementation uses a lock and condition-variable-based monitor abstraction to coordinate access to the shared resource.

The configuration uses four reader threads, two writer threads, and three rounds per thread. A recorded run produced 72 events. The verification script checked reader-writer overlap and expected access counts.

The implementation favours waiting writers over newly arriving readers. Continuous writers may therefore delay readers.

### 5.3 Dining Philosophers Problem — Semaphore Based

**Source file:** `dining_philosophers.py`  
**Execution trace:** `execution_trace.json`  
**HTML simulation:** `dining_philosophers.html`

This implementation models four philosophers sharing four chopsticks. Semaphores coordinate access to the chopsticks and limit the number of philosophers allowed to compete for them simultaneously.

The program uses four philosopher threads and three eating rounds per philosopher, giving 12 expected eating rounds. Its verification script checks the recorded chopstick ownership and expected eating counts.

### 5.4 Dining Philosophers Problem — Monitor Based

**Source file:** `dining_philosophers_monitor.py`  
**Execution trace:** `monitor_execution_trace.json`  
**HTML simulation:** `dining_philosophers_monitor.html`

This implementation uses a monitor-style abstraction built with a lock and condition variables. A philosopher may eat only when the neighbouring philosophers are not eating.

The program uses four philosopher threads and three eating rounds per philosopher. The verification script checks the recorded execution for adjacent philosophers eating simultaneously and validates the expected eating rounds.

## 6. Execution Instructions

### Prerequisites

- Python 3 installed.
- Windows PowerShell or another terminal.
- A modern web browser for viewing the HTML simulations.

Open PowerShell in the project root directory:

```powershell
cd C:\Users\POOJARY\Desktop\DiningPhilosophers
```

### Run Dining Philosophers — Semaphore

```powershell
python dining_philosophers\semaphore\dining_philosophers.py
```

### Run Dining Philosophers — Monitor

```powershell
python dining_philosophers\monitor\dining_philosophers_monitor.py
```

### Run Readers–Writers — Semaphore

```powershell
python readers_writers\semaphore\readers_writers_semaphore.py
```

### Run Readers–Writers — Monitor

```powershell
python readers_writers\monitor\readers_writers_monitor.py
```

Each main program records its execution trace and invokes its corresponding HTML generator. If a generator fails, investigate the error rather than treating the run as fully successful.

## 7. Viewing the HTML Simulations

The generated HTML files are stored in `generated_html/`.

| Implementation | HTML file |
|---|---|
| Dining Philosophers — Semaphore | `dining_philosophers.html` |
| Dining Philosophers — Monitor | `dining_philosophers_monitor.html` |
| Readers–Writers — Semaphore | `readers_writers_semaphore.html` |
| Readers–Writers — Monitor | `readers_writers_monitor.html` |

For example, open the Dining Philosophers semaphore simulation from PowerShell:

```powershell
start generated_html\dining_philosophers.html
```

The HTML generators read the JSON traces recorded by the corresponding Python programs. The browser displays the recorded execution sequence rather than rerunning the synchronization algorithm. A new Python run may produce a different event order because of thread scheduling; regenerate the HTML to display the latest trace.

## 8. Verification and Testing

Run the verification scripts from the project root after generating the corresponding execution traces.

### Dining Philosophers — Semaphore

```powershell
python dining_philosophers\semaphore\verify_trace.py
```

### Dining Philosophers — Monitor

```powershell
python dining_philosophers\monitor\verify_monitor.py
```

### Readers–Writers — Semaphore

```powershell
python readers_writers\semaphore\verify_rw_semaphore.py
```

### Readers–Writers — Monitor

```powershell
python readers_writers\monitor\verify_rw_monitor.py
```

The recorded verification runs passed their expected checks:

- Both Dining Philosophers implementations recorded three eating rounds for each of the four philosophers.
- The Readers–Writers semaphore implementation recorded three read accesses for each reader and three write accesses for each writer. Its verifier checked access counts and recorded resource-state snapshots.
- The Readers–Writers monitor implementation passed its recorded checks for reader-writer overlap and expected access counts.

These checks validate the recorded traces and expected access counts. They do not prove correctness for every possible thread schedule. The synchronization logic should also be reviewed and explained during the demonstration.

## 9. Synchronization Concepts

### Mutual Exclusion

Mutual exclusion ensures that incompatible operations do not access a shared resource simultaneously. Writers require exclusive access to the Readers–Writers resource, and neighbouring philosophers must not eat using the same chopstick.

### Race Conditions

A race condition occurs when the result depends on the timing or interleaving of concurrent operations. Locks, semaphores, and condition variables coordinate access to shared state and help prevent unsafe interleavings.

### Deadlock

Deadlock occurs when threads wait indefinitely for resources or conditions that cannot become available. The Dining Philosophers synchronization strategy is designed to avoid deadlock; its correctness should be assessed from the implementation and recorded execution.

### Starvation

Starvation occurs when a thread waits indefinitely because other threads repeatedly obtain access first. Reader-priority solutions can starve writers, while writer-priority solutions can delay readers. Deadlock prevention does not automatically guarantee fairness.

## 10. Semaphore and Monitor Comparison

| Aspect | Semaphore Based | Monitor Based |
|---|---|---|
| Synchronization mechanism | Semaphore acquire and release operations | Shared lock and condition variables |
| Resource coordination | Controlled using semaphore permits | Controlled through shared state and condition checks |
| Mutual exclusion | Depends on correct semaphore usage | Depends on correct locking and condition handling |
| Waiting | Threads block on semaphore operations | Threads wait on condition variables |
| Main consideration | Correct permit acquisition and release | Correct state updates, waiting conditions, and notifications |

Both approaches can implement synchronization correctly when designed and tested carefully. Their behaviour depends on the specific algorithm and fairness policy used.

## 11. AI Assistance Disclosure

Generative AI was used as a programming assistant during the development of this assignment.

- **AI tool used:** ChatGPT.
- **Purpose:** Assistance with algorithm design, Python implementation, debugging, execution-trace recording, HTML generation, verification, and documentation.
- **Follow-up work:** The implementations were executed, errors were investigated, verification scripts were run, and the programs were updated to generate HTML simulations automatically.
- **Student responsibility:** The student is responsible for reviewing the submitted code, understanding the synchronization logic, testing the programs, and explaining the results.

The accompanying AI prompt log should document the prompts actually used during development. Any manual changes, debugging steps, and observed limitations should be described accurately.

## 12. References

1. Python Software Foundation. *threading — Thread-based parallelism.* https://docs.python.org/3/library/threading.html
2. Python Software Foundation. *json — JSON encoder and decoder.* https://docs.python.org/3/library/json.html
3. Python Software Foundation. *subprocess — Subprocess management.* https://docs.python.org/3/library/subprocess.html
4. Operating Systems Programming Assignment: *AI-Assisted Synchronization Algorithms with Program-Generated HTML Simulation.* Assignment specification supplied for this project.

## 13. Declaration

I declare that I have reviewed and tested the submitted programs and will ensure that I understand the synchronization logic and can explain the implementation and results. I have disclosed the AI assistance used during development and will identify relevant external resources. I have not knowingly submitted another student's work or unacknowledged third-party material as my own.

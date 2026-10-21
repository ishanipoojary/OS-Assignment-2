# AI Prompt Log

## Introduction

I used ChatGPT during the development of this Operating Systems assignment to understand the concepts, plan the implementation, fix errors, and check the output. The following is a summary of the main tasks for which I used AI assistance.

## 1. Dining Philosophers Using Semaphores

**Task:** Implement the Dining Philosophers problem for four philosophers and four chopsticks using semaphores.

**Prompt summary:** Asked for help understanding the problem, using threads and semaphores, and preventing multiple philosophers from accessing the same chopsticks at the same time.

**Work done:** Implemented the program and recorded the execution events in a JSON file for the HTML simulation.

**What I learned:** Semaphores help control access to shared resources and prevent conflicting operations.

## 2. Dining Philosophers Using Monitors

**Task:** Implement the same problem using a monitor-based approach.

**Prompt summary:** Asked for help understanding how the monitor controls philosopher states and how a philosopher waits when the required chopsticks are unavailable.

**Work done:** Implemented the monitor version and generated a separate HTML simulation using its execution trace.

**What I learned:** A monitor provides controlled access to shared data and uses condition variables to manage waiting threads.

## 3. Readers-Writers Using Semaphores

**Task:** Implement the Readers-Writers problem using semaphores.

**Prompt summary:** Asked for help managing multiple readers and writers while protecting the shared resource.

**Work done:** Implemented four reader threads and two writer threads, with three rounds per thread. The program records events and the final shared value.

**What I learned:** Multiple readers can access shared data together, but a writer needs exclusive access while writing.

## 4. Readers-Writers Using Monitors

**Task:** Implement the Readers-Writers problem using a monitor-based approach.

**Prompt summary:** Asked for help applying monitor synchronization and checking that readers and writers do not access the shared resource in conflicting ways.

**Work done:** Implemented the monitor version and generated the corresponding HTML simulation.

**What I learned:** Monitor-based synchronization helps coordinate threads and protect shared data.

## 5. HTML Simulation and Execution Traces

**Task:** Generate HTML simulations using data collected from the programs.

**Prompt summary:** Asked for help recording execution events in JSON files and using those files to generate HTML simulations.

**Work done:** Created separate HTML generators for all four implementations. The simulations use recorded execution events to display the program's progress.

**What I learned:** Execution traces help show how concurrent threads behave and make synchronization easier to understand.

## 6. Debugging and File Paths

**Task:** Fix file path problems after organizing the project into folders.

**Prompt summary:** Asked for help correcting paths so the programs could find their JSON trace files and save the generated HTML files in the correct folder.

**Work done:** Updated the scripts to use paths based on their own file locations and tested the programs again.

**What I learned:** Using paths relative to the script location makes a project easier to run after its folders are reorganized.

## 7. Verification and Testing

**Task:** Check whether the recorded execution traces meet the expected conditions.

**Prompt summary:** Asked for help creating verification scripts to check thread counts, completed rounds, and synchronization conditions recorded in the traces.

**Work done:** Created verification scripts for the implementations and ran them to check the recorded results.

**What I learned:** Verification scripts can help identify problems in recorded execution data, although they do not prove correctness for every possible thread schedule.

## 8. Documentation

**Task:** Organize the project and prepare its README.

**Prompt summary:** Asked for help documenting the folder structure, execution commands, verification commands, and references.

**Work done:** Prepared the README structure and documented how to run and verify the programs.

**What I learned:** Clear documentation makes it easier for another person to understand and run the project.

## Note

This file is a summary of the main AI-assisted tasks during development, not a verbatim transcript of every prompt. The implementations, testing, and final explanations should be reviewed and understood by me before submission.

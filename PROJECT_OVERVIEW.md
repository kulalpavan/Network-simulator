# Sliding Window Protocol Simulator

## Overview

This project is a Python desktop application for visualizing and comparing three
sliding-window / ARQ protocols used in data-link and transport-layer networking:

- Stop-and-Wait (One-Bit Sliding Window)
- Go-Back-N ARQ
- Selective Repeat ARQ

The app is designed for learners who want to see what each protocol does, why it
reacts to loss the way it does, and how those choices affect throughput and
efficiency.

## Features

- Tkinter desktop interface with a configuration sidebar and three tabs:
  `Live simulation`, `How it works`, and `Results`.
- Animated timeline of sender and receiver windows, data frames, ACKs, losses,
  timeouts, and retransmissions.
- A plain-language explanation of the current event under the timeline.
- Pause, resume, and single-step playback controls.
- Compact event log with data, ACK, loss, and retransmission color coding.
- Protocol guide with rules, step-by-step behavior, analogies, and things to
  watch for.
- Scenario presets for ideal conditions, packet loss, ACK loss, and combined
  loss, plus editable custom values.
- Summary cards, throughput/efficiency charts, and a fully visible metrics table
  with definitions.
- Tie-aware result badges, insights, and status messages.
- Responsive live layout at the minimum supported window size of `1280x760`.

## Technology stack

- Python 3.11+
- Tkinter for the GUI
- Matplotlib for comparison charts
- NumPy for numerical support
- Pillow for image support

## Application flow

1. `main.py` creates the main window and starts the Tk event loop.
2. The user selects a protocol and a scenario, then optionally edits parameters.
3. `gui/main_window.py` validates the inputs through `InputPanel`.
4. `simulation/simulator.py` dispatches to the selected protocol implementation.
5. The protocol produces transmission events and performance metrics.
6. `gui/animation_panel.py` animates the events step by step.
7. `gui/main_window.py` updates the event log and run summary.
8. Compare runs all three protocols with the same settings and opens the
   `Results` dashboard, including charts and the explained metrics table.

## Main project structure

```text
Sliding-Window-Protocol-Simulator/
├── README.md
├── PROJECT_OVERVIEW.md
├── main.py
├── requirements.txt
├── analysis/
│   ├── charts.py
│   └── performance.py
├── config/
│   └── settings.py
├── gui/
│   ├── animation_panel.py
│   ├── comparison_panel.py
│   ├── input_panel.py
│   ├── main_window.py
│   ├── protocol_guide.py
│   ├── results_panel.py
│   └── theme.py
├── protocols/
│   ├── go_back_n.py
│   ├── selective_repeat.py
│   └── stop_and_wait.py
├── simulation/
│   ├── event_manager.py
│   ├── network.py
│   └── simulator.py
└── tests/
    └── test_animation_events.py
```

## Core modules

### `main.py`

Entry point. Creates `MainWindow` and enters the Tkinter main loop.

### `config/settings.py`

Application constants, protocol metadata, scenario presets, and default window
sizes. The default window is `1320x860`; the minimum is `1280x760`.

### `gui/main_window.py`

Builds the header, body, tabs, status bar, and live simulation controls. It also
coordinates:

- input validation and simulation dispatch
- event-log updates and playback state
- the post-run summary strip
- comparison execution and result routing
- reset behavior
- responsive visibility of the summary when the event log is open

### `gui/input_panel.py`

Configuration sidebar containing:

- protocol selector with a short rule summary
- scenario selector with a description
- frames, window, delay, loss, and timeout fields
- pinned Run, Compare, View results, and Reset actions

`get_comparison_window()` keeps comparisons meaningful when Stop-and-Wait is the
currently selected method: it uses the last configured window value for the
windowed protocols.

### `gui/theme.py`

Shared colors, fonts, card styling, buttons, tooltips, treeview styles, and the
`ScrollFrame` container used by scrollable tabs and the sidebar.

### `gui/animation_panel.py`

Canvas-based sender/receiver visualization. It draws:

- sender and receiver window state
- data and ACK movement
- loss and retransmission markers
- a selected frame/ACK explanation
- an empty-state hint before the first run

### `gui/protocol_guide.py`

The `How it works` tab. Presents protocol rules, numbered behavior steps, a
real-life analogy, a "watch for" note, and a shared explanation of the
visualization symbols.

### `gui/results_panel.py`

Builds the results dashboard:

- summary cards for each protocol
- highest-throughput, highest-efficiency, and fewest-retries badges only when a
  unique winner exists
- the shared scenario parameters
- a seven-row metrics table with plain-language definitions

### `gui/comparison_panel.py`

Draws the throughput and efficiency bar charts and generates a tie-aware insight
line. Charts use rotated protocol labels so names remain readable at smaller
widths.

### `simulation/simulator.py`

Validates requests, selects the protocol implementation, runs the simulation,
and calculates performance metrics.

### `protocols/`

- `stop_and_wait.py` sends one frame at a time and waits for its ACK.
- `go_back_n.py` allows multiple outstanding frames and retransmits the window
  from the missing frame after a timeout.
- `selective_repeat.py` uses individual acknowledgements and retransmits only
  frames that were not acknowledged.

### `analysis/performance.py`

Computes throughput in frames per second and transmission efficiency as a
percentage.

## Simulated parameters

- protocol type
- window size (fixed at 1 for Stop-and-Wait)
- number of frames
- transmission delay
- ACK delay
- data loss percentage
- ACK loss percentage
- timeout duration

## Simulation behavior

- Data and ACK loss use seeded random decisions so runs are reproducible.
- Timeouts trigger protocol-specific recovery.
- Every major transmission stage becomes an event for the animation and log.
- Metrics include frames transmitted, retransmissions, packets lost, ACKs
  received, total time, throughput, and efficiency.
- Comparison runs use the same seed and network settings for all three methods.

## Known modeling limitation

The protocol implementations evaluate transmission rounds sequentially rather
than modeling fully pipelined, independent in-flight packets. As a result, an
ideal network can produce equal throughput for all three methods. The interface
does not hide this: ties are reported as ties. Differences appear when loss or
ACK loss forces retransmissions, timeouts, or selective recovery.

## Tests

The current suite verifies the animation-event contract and protocol-specific
receive behavior:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The five tests cover ideal networks, packet loss, ACK loss, sliding-window
sizes, and protocol-specific receive semantics.

## Execution

```powershell
.\.venv\Scripts\python.exe main.py
```

Install dependencies first with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Educational value

The app turns abstract reliability concepts into an interactive experience. It
is especially useful for understanding:

- how sliding windows bound the number of unacknowledged frames
- why Go-Back-N repeats more work after a loss
- why Selective Repeat can recover with fewer retransmissions
- how timeouts and loss affect throughput and efficiency
- the trade-off between simplicity and bandwidth efficiency

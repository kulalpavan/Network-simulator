# Sliding Window Protocol Simulator

An interactive desktop application for exploring how three ARQ protocols deliver
frames over an unreliable link:

- One-Bit Sliding Window (Stop-and-Wait)
- Go-Back-N ARQ
- Selective Repeat ARQ

The app combines a live sender/receiver timeline, plain-language explanations,
a compact event log, and side-by-side performance comparison.

## Features

- **Live simulation timeline** showing data frames, acknowledgements, losses,
  retransmissions, sender/receiver windows, and a "why this step" explanation.
- **Playback controls** to pause, resume, or step through a run one event at a
  time.
- **Scenario presets** for ideal networks, packet loss, ACK loss, and combined
  loss, plus editable frames, window, delay, loss, and timeout values.
- **How it works guide** covering each protocol's rules, step-by-step behavior,
  real-life analogy, and what to watch for.
- **Results dashboard** with throughput and efficiency charts, summary cards,
  and a metric table written in plain language.
- **Tie-aware comparison** so equal results are reported honestly instead of
  assigning an incorrect winner.
- **Compact event log** that is hidden by default and can be opened when you
  want the full transmission history.

## Comparison behavior

All three protocols run with the same scenario, seed, and network parameters.
Windowed protocols use one shared window size; Stop-and-Wait is always fixed at
window 1. If Stop-and-Wait is selected, the comparison uses the last configured
window value so Go-Back-N and Selective Repeat still have a meaningful window.

The current simulation model processes protocol rounds sequentially rather than
pipelining independent in-flight transmissions. Under an ideal network, the
three methods can therefore report equal throughput. Differences become visible
when data loss, ACK loss, and timeouts cause retransmissions; the UI reports
those results and any ties accurately.

## Requirements

- Python 3.11 or later
- Tkinter (included with Windows Python when Tcl/Tk and IDLE are selected)
- Matplotlib and NumPy for charts
- Pillow for image support

## Installation

In Windows PowerShell, from the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check that Tkinter is available:

```powershell
python -m tkinter
```

If the demo window does not open, modify your Windows Python installation and
enable **Tcl/Tk and IDLE**.

## Run the application

With the virtual environment activated:

```powershell
python main.py
```

Or run it directly without activating the environment:

```powershell
.\.venv\Scripts\python.exe main.py
```

Keyboard shortcuts: `F5` starts a simulation and `Ctrl+R` resets the app.

## Tests

The animation-event contract tests verify that protocol output still produces
the event shapes expected by the UI:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Project layout

```text
Sliding-Window-Protocol-Simulator/
├── main.py
├── requirements.txt
├── README.md
├── PROJECT_OVERVIEW.md
├── analysis/
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
├── simulation/
└── tests/
    └── test_animation_events.py
```

See `PROJECT_OVERVIEW.md` for module responsibilities and implementation notes.

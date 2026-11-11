"""Main GUI for the Sliding Window Protocol Simulator."""

import tkinter as tk
from tkinter import ttk, messagebox

from config.settings import (
    APP_SUBTITLE,
    APP_TITLE,
    MIN_HEIGHT,
    MIN_WIDTH,
    PROTOCOL_INFO,
    PROTOCOL_ORDER,
    SCENARIOS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gui import theme
from gui.dpi import apply_dpi_scaling
from gui.animation_panel import AnimationPanel
from gui.comparison_panel import ComparisonPanel
from gui.input_panel import InputPanel
from gui.protocol_guide import ProtocolGuide
from gui.results_panel import ResultsPanel
from simulation.simulator import Simulator


class MainWindow:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.scale = apply_dpi_scaling(self.root)
        theme.set_scale(self.scale)
        self.root.title(APP_TITLE)
        self.root.geometry(self._window_geometry())
        self.root.minsize(
            min(self._px(MIN_WIDTH), self.root.winfo_screenwidth() - 48),
            min(self._px(MIN_HEIGHT), self.root.winfo_screenheight() - 96),
        )
        self.root.configure(bg=theme.COLORS["bg"])
        theme.apply_theme(self.root)

        self.simulator = Simulator()
        self.current_comparison_results = {}
        self.current_comparison_parameters = {}
        self.last_results = None
        self.last_protocol = None
        self.summary_requested = False

        self.status_var = tk.StringVar(value="Ready")
        self.hint_var = tk.StringVar(
            value=(
                "Pick a method and scenario, then run a simulation. "
                "Open How it works to compare the three rules."
            )
        )
        self.event_count_var = tk.StringVar(value="0 events")
        self.event_status_var = tk.StringVar(value="Ready")

        self._build_header()
        self._build_status_bar()
        self._build_body()
        self._center_window()

        self.root.bind("<F5>", lambda _event: self.start_simulation())
        self.root.bind("<Control-r>", lambda _event: self.reset_simulation())
        self.root.bind("<Configure>", self._on_root_configure, add="+")

    def _px(self, value):
        return int(round(value * self.scale))

    def _window_geometry(self):
        width = min(self._px(WINDOW_WIDTH), self.root.winfo_screenwidth() - 48)
        height = min(
            self._px(WINDOW_HEIGHT), self.root.winfo_screenheight() - 96
        )
        return f"{width}x{height}"

    def _center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = min(self._px(WINDOW_WIDTH), screen_width - 48)
        height = min(self._px(WINDOW_HEIGHT), screen_height - 96)
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2 - 20, 0)
        self.root.geometry(f"+{x}+{y}")

    def _build_header(self):
        header = tk.Frame(self.root, background=theme.COLORS["navy"])
        header.pack(fill="x")

        inner = tk.Frame(header, background=theme.COLORS["navy"])
        inner.pack(fill="x", padx=self._px(24), pady=self._px(14))

        mark = tk.Canvas(
            inner,
            width=self._px(42),
            height=self._px(42),
            background=theme.COLORS["navy"],
            highlightthickness=0,
        )
        mark.pack(side="left", padx=(0, self._px(12)))
        edge = self._px(42) - 1
        mark.create_rectangle(
            1, 1, edge, edge,
            fill=theme.COLORS["primary"],
            outline="",
        )
        mark.create_line(
            self._px(10), self._px(16), self._px(32), self._px(16),
            fill="white",
            width=self._px(2),
            arrow=tk.LAST,
        )
        mark.create_line(
            self._px(32), self._px(27), self._px(10), self._px(27),
            fill="#A7F3D0",
            width=self._px(2),
            arrow=tk.LAST,
        )

        titles = tk.Frame(inner, background=theme.COLORS["navy"])
        titles.pack(side="left")
        tk.Label(
            titles,
            text=APP_TITLE,
            background=theme.COLORS["navy"],
            foreground="white",
            font=theme.font(16, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            titles,
            text=APP_SUBTITLE,
            background=theme.COLORS["navy"],
            foreground="#94A3B8",
            font=theme.font(8),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        pills = tk.Frame(inner, background=theme.COLORS["navy"])
        pills.pack(side="right")
        self.scenario_pill = tk.Label(
            pills,
            text="",
            background=theme.COLORS["navy_soft"],
            foreground="#CBD5E1",
            font=theme.font(8, "bold"),
            padx=12,
            pady=6,
        )
        self.scenario_pill.pack(side="right", padx=(6, 0))
        self.method_pill = tk.Label(
            pills,
            text="",
            background=theme.COLORS["navy_soft"],
            foreground=theme.COLORS["primary"],
            font=theme.font(8, "bold"),
            padx=12,
            pady=6,
        )
        self.method_pill.pack(side="right")

    def _build_status_bar(self):
        bar = tk.Frame(self.root, background=theme.COLORS["navy"])
        bar.pack(side="bottom", fill="x")

        left = tk.Frame(bar, background=theme.COLORS["navy"])
        left.pack(side="left", fill="x", expand=True, padx=16, pady=7)
        self.status_dot = tk.Canvas(
            left,
            width=self._px(10),
            height=self._px(10),
            background=theme.COLORS["navy"],
            highlightthickness=0,
        )
        self.status_dot.pack(side="left", padx=(0, self._px(8)))
        dot = self._px(9)
        self.status_dot_id = self.status_dot.create_oval(
            1, 1, dot, dot,
            fill=theme.COLORS["faint"],
            outline="",
        )
        self.status_label = tk.Label(
            left,
            textvariable=self.status_var,
            background=theme.COLORS["navy"],
            foreground="#E2E8F0",
            font=theme.font(8, "bold"),
            anchor="w",
        )
        self.status_label.pack(side="left")

        tk.Label(
            bar,
            textvariable=self.hint_var,
            background=theme.COLORS["navy"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            anchor="e",
        ).pack(side="right", padx=16)

    def _build_body(self):
        body = tk.Frame(self.root, background=theme.COLORS["bg"])
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(
            body,
            background=theme.COLORS["bg"],
            width=self._px(356),
        )
        sidebar.grid(row=0, column=0, sticky="ns", padx=(16, 8), pady=14)
        sidebar.grid_propagate(False)
        sidebar_scroll = theme.ScrollFrame(
            sidebar, background=theme.COLORS["bg"]
        )
        sidebar_scroll.pack(fill="both", expand=True)

        self.input_panel = InputPanel(
            sidebar_scroll.body,
            on_start=self.start_simulation,
            on_compare=self.compare_protocols,
            on_reset=self.reset_simulation,
            on_view_results=self.view_performance_results,
            on_protocol_change=self._on_protocol_change,
            on_scenario_change=self._on_scenario_change,
            action_parent=sidebar,
        )
        self.input_panel.pack(fill="x", padx=(0, 2))

        self.notebook = ttk.Notebook(body, style="App.TNotebook")
        self.notebook.grid(
            row=0, column=1, sticky="nsew", padx=(8, 16), pady=14
        )

        self.live_tab = tk.Frame(self.notebook, background=theme.COLORS["bg"])
        self.guide_tab = tk.Frame(self.notebook, background=theme.COLORS["bg"])
        self.results_tab = tk.Frame(self.notebook, background=theme.COLORS["bg"])
        self.notebook.add(self.live_tab, text="  Live simulation  ")
        self.notebook.add(self.guide_tab, text="  How it works  ")
        self.notebook.add(self.results_tab, text="  Results  ")

        self._build_live_tab()
        self._build_guide_tab()
        self._build_results_tab()

        self._on_protocol_change(
            PROTOCOL_ORDER[0], PROTOCOL_INFO[PROTOCOL_ORDER[0]]
        )
        self._on_scenario_change("Ideal Network", SCENARIOS["Ideal Network"])

    def _build_live_tab(self):
        self.live_tab.grid_columnconfigure(0, weight=1)
        self.live_tab.grid_rowconfigure(1, weight=1)
        self.live_tab.grid_rowconfigure(2, weight=0)

        toolbar = tk.Frame(
            self.live_tab,
            background=theme.COLORS["surface"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
        )
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar_inner = tk.Frame(toolbar, background=theme.COLORS["surface"])
        toolbar_inner.pack(fill="x", padx=12, pady=7)

        controls = tk.Frame(toolbar_inner, background=theme.COLORS["surface"])
        controls.pack(side="left")
        self.pause_button = theme.make_button(
            controls, "Pause", self._pause_simulation,
            kind="secondary", compact=True,
        )
        self.pause_button.pack(side="left", padx=(0, 5))
        self.resume_button = theme.make_button(
            controls, "Resume", self._resume_simulation,
            kind="secondary", compact=True,
        )
        self.resume_button.pack(side="left", padx=(0, 5))
        self.step_button = theme.make_button(
            controls, "Step forward", self._step_simulation,
            kind="secondary", compact=True,
        )
        self.step_button.pack(side="left")

        self.playback_state = tk.Label(
            toolbar_inner,
            textvariable=self.event_status_var,
            background=theme.COLORS["primary_soft"],
            foreground=theme.COLORS["primary_dark"],
            font=theme.font(8, "bold"),
            padx=10,
            pady=3,
        )
        self.playback_state.pack(side="right")
        self.event_count_label = tk.Label(
            toolbar_inner,
            textvariable=self.event_count_var,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
        )
        self.event_count_label.pack(side="right", padx=(0, 12))
        self.log_toggle_button = theme.make_button(
            toolbar_inner,
            "Show event log",
            self._toggle_event_log,
            kind="ghost",
            compact=True,
        )
        self.log_toggle_button.pack(side="right", padx=(0, 10))

        animation_card, animation_body = theme.make_card(
            self.live_tab,
            title="Live timeline",
            subtitle=(
                "Blue = data · green dashed = ACK · orange = retransmit. "
                "The bar below explains every step."
            ),
            padding=12,
        )
        animation_card.grid(
            row=1, column=0, sticky="nsew", pady=(0, 10)
        )
        animation_body.grid_columnconfigure(0, weight=1)
        animation_body.grid_rowconfigure(0, weight=1)
        self.animation_panel = AnimationPanel(animation_body)
        self.animation_panel.grid(row=0, column=0, sticky="nsew")

        self.result_strip = tk.Frame(
            animation_body,
            background=theme.COLORS["surface_alt"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
        )
        self.summary_values = {}
        strip_items = (
            ("Method", "method", theme.COLORS["primary"]),
            ("Delivered", "delivered", theme.COLORS["success"]),
            ("Retransmissions", "retries", theme.COLORS["warning"]),
            ("Throughput", "throughput", theme.COLORS["primary"]),
            ("Efficiency", "efficiency", theme.COLORS["success"]),
        )
        for column, (label, key, color) in enumerate(strip_items):
            cell = tk.Frame(
                self.result_strip,
                background=theme.COLORS["surface_alt"],
            )
            cell.grid(row=0, column=column, sticky="ew", padx=12, pady=7)
            self.result_strip.grid_columnconfigure(column, weight=1)
            tk.Label(
                cell,
                text=label.upper(),
                background=theme.COLORS["surface_alt"],
                foreground=theme.COLORS["muted"],
                font=theme.font(7, "bold"),
                anchor="w",
            ).pack(fill="x")
            value = tk.Label(
                cell,
                text="—",
                background=theme.COLORS["surface_alt"],
                foreground=color,
                font=theme.font(10, "bold"),
                anchor="w",
            )
            value.pack(fill="x")
            self.summary_values[key] = value

        self.log_card = tk.Frame(
            self.live_tab,
            background=theme.COLORS["surface"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        self.log_card.grid(row=2, column=0, sticky="nsew")

        log_header = tk.Frame(
            self.log_card, background=theme.COLORS["surface"]
        )
        log_header.pack(fill="x", padx=12, pady=(8, 6))
        tk.Label(
            log_header,
            text="Event log",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["ink"],
            font=theme.font(9, "bold"),
            anchor="w",
        ).pack(side="left")
        theme.make_button(
            log_header,
            "Clear log",
            self._clear_event_log,
            kind="ghost",
            compact=True,
        ).pack(side="right")
        tk.Label(
            log_header,
            text=(
                "blue = data  ·  green = ACK  ·  red = loss  ·  "
                "orange = retransmit"
            ),
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["faint"],
            font=theme.font(7),
        ).pack(side="right", padx=(0, 12))

        event_table = tk.Frame(
            self.log_card, background=theme.COLORS["surface"]
        )
        event_table.pack(
            fill="both", expand=True, padx=12, pady=(0, 10)
        )
        columns = ("step", "time", "frame_ack", "event", "status")
        self.event_log = ttk.Treeview(
            event_table,
            columns=columns,
            show="headings",
            height=2,
            style="App.Treeview",
        )
        headings = {
            "step": ("Step", 44),
            "time": ("Time", 60),
            "frame_ack": ("Frame / ACK", 85),
            "event": ("Event", 372),
            "status": ("What happened", 128),
        }
        for column, (heading, width) in headings.items():
            self.event_log.heading(column, text=heading)
            self.event_log.column(
                column,
                width=width,
                minwidth=45,
                anchor="w" if column == "event" else "center",
                stretch=column == "event",
            )

        event_scrollbar = ttk.Scrollbar(
            event_table,
            orient="vertical",
            command=self.event_log.yview,
            style="Vertical.TScrollbar",
        )
        self.event_log.configure(yscrollcommand=event_scrollbar.set)
        self.event_log.pack(side="left", fill="both", expand=True)
        event_scrollbar.pack(side="right", fill="y")

        self.event_log.tag_configure(
            "data_success", background="#EFF6FF", foreground="#1D4ED8"
        )
        self.event_log.tag_configure(
            "ack_success", background="#ECFDF5", foreground="#047857"
        )
        self.event_log.tag_configure(
            "loss", background="#FEF2F2", foreground="#B91C1C"
        )
        self.event_log.tag_configure(
            "retransmission", background="#FFFBEB", foreground="#B45309"
        )
        self.event_log.tag_configure(
            "discarded", background="#F8FAFC", foreground="#64748B"
        )
        self.event_log.tag_configure(
            "received", background="#F0FDF4", foreground="#15803D"
        )
        self.event_log.tag_configure(
            "current", font=theme.font(9, "bold")
        )
        self.current_log_item = None
        self.log_visible = True
        self._toggle_event_log()
        self._set_playback_controls("idle")

    def _toggle_event_log(self):
        self.log_visible = not self.log_visible
        if self.log_visible:
            self.log_card.grid()
            self.log_toggle_button.configure(text="Hide event log")
        else:
            self.log_card.grid_remove()
            self.log_toggle_button.configure(text="Show event log")
        self._sync_summary_visibility()

    def _build_guide_tab(self):
        self.protocol_guide = ProtocolGuide(self.guide_tab)
        self.protocol_guide.pack(fill="both", expand=True)

    def _build_results_tab(self):
        results_scroll = theme.ScrollFrame(
            self.results_tab,
            background=theme.COLORS["bg"],
        )
        results_scroll.pack(fill="both", expand=True)
        content = results_scroll.body

        charts_card, charts_body = theme.make_card(
            content,
            title="Performance overview",
            subtitle=(
                "Both charts use the same scenario. Higher is better in "
                "each chart."
            ),
            padding=12,
        )
        charts_card.pack(fill="x")
        self.comparison_panel = ComparisonPanel(charts_body)
        self.comparison_panel.pack(fill="both", expand=True)

        self.results_panel = ResultsPanel(
            content,
            on_compare=self.compare_protocols,
        )
        self.results_panel.pack(fill="x", pady=(10, 12))

    def _on_protocol_change(self, protocol, info):
        self.method_pill.configure(
            text=f"Method · {info['short']}",
            foreground=theme.protocol_accent(protocol),
        )
        self.protocol_guide.set_protocol(protocol)
        self.hint_var.set(info["tagline"])

    def _on_scenario_change(self, name, info):
        self.scenario_pill.configure(text=f"Scenario · {name}")
        self.hint_var.set(info["description"])

    def _set_status(self, text, state="ready"):
        colors = {
            "ready": theme.COLORS["faint"],
            "running": theme.COLORS["primary"],
            "paused": theme.COLORS["warning"],
            "completed": theme.COLORS["success"],
            "error": theme.COLORS["danger"],
        }
        self.status_var.set(text)
        self.status_dot.itemconfigure(
            self.status_dot_id,
            fill=colors.get(state, theme.COLORS["faint"]),
        )

    def _set_playback_controls(self, state):
        states = {
            "idle": ("disabled", "disabled", "disabled"),
            "running": ("normal", "disabled", "normal"),
            "paused": ("disabled", "normal", "normal"),
            "stepping": ("disabled", "normal", "normal"),
            "completed": ("disabled", "disabled", "disabled"),
        }
        pause, resume, step = states.get(state, states["idle"])
        self.pause_button.configure(state=pause)
        self.resume_button.configure(state=resume)
        self.step_button.configure(state=step)

    def _append_simulation_event(self, record):
        if self.current_log_item:
            tags = tuple(
                tag for tag in self.event_log.item(
                    self.current_log_item, "tags"
                ) if tag != "current"
            )
            self.event_log.item(self.current_log_item, tags=tags)

        kind = record["kind"]
        if kind == "data_tx":
            if not record["transmission_succeeded"]:
                row_tag = "loss"
            else:
                row_tag = (
                    "retransmission" if record["attempt"] > 1
                    else "data_success"
                )
        elif kind == "data_lost" or kind == "ack_lost":
            row_tag = "loss"
        elif kind in ("ack_generated", "ack_received"):
            row_tag = (
                "ack_success" if record["transmission_succeeded"] is not False
                else "loss"
            )
        elif kind == "timeout" or kind == "retransmit":
            row_tag = "retransmission"
        elif kind in ("duplicate", "discard"):
            row_tag = "discarded"
        elif kind in ("received", "delivered", "buffered"):
            row_tag = "received"
        else:
            row_tag = ""

        tags = (row_tag, "current") if row_tag else ("current",)
        self.current_log_item = self.event_log.insert(
            "", "end",
            values=(
                record["step"],
                f"{record['time_ms']:.0f} ms",
                record["frame_ack"],
                record["event"],
                record["status"],
            ),
            tags=tags,
        )
        self.event_count_var.set(
            f"{len(self.event_log.get_children())} events"
        )
        self.event_log.see(self.current_log_item)
        self.event_status_var.set(record["status"])
        self._set_status(
            f"Running step {record['step']} of "
            f"{len(self.animation_panel.records)}",
            "running",
        )

    def _pause_simulation(self):
        self.animation_panel.pause()
        self._set_status("Simulation paused", "paused")

    def _resume_simulation(self):
        self.animation_panel.resume()
        self._set_status("Simulation running", "running")

    def _step_simulation(self):
        self.animation_panel.step_forward()
        self._set_status("Stepping one event at a time", "paused")

    def _simulation_state_changed(self, state):
        if state == "Running":
            self.event_status_var.set("Running")
            self._set_playback_controls("running")
        elif state == "Paused":
            self.event_status_var.set("Paused")
            self._set_playback_controls("paused")
            self._set_status("Simulation paused", "paused")
        elif state == "Stepping":
            self.event_status_var.set("Stepping")
            self._set_playback_controls("paused")
        elif state == "Completed":
            self.event_status_var.set("Completed")
            self._set_playback_controls("completed")

    def _clear_event_log(self):
        self.event_log.delete(*self.event_log.get_children())
        self.current_log_item = None
        self.event_count_var.set("0 events")

    def _show_run_summary(self, protocol, results):
        short = PROTOCOL_INFO[protocol]["short"]
        self.summary_values["method"].configure(text=short)
        self.summary_values["delivered"].configure(
            text=str(results.get("delivered_frames", 0))
        )
        self.summary_values["retries"].configure(
            text=str(results.get("retransmissions", 0))
        )
        self.summary_values["throughput"].configure(
            text=f"{results.get('throughput_fps', 0):.2f} fps"
        )
        self.summary_values["efficiency"].configure(
            text=f"{results.get('efficiency_percent', 0):.1f}%"
        )
        self.summary_requested = True
        self._sync_summary_visibility()

    def _hide_run_summary(self):
        self.summary_requested = False
        self._sync_summary_visibility()

    def _on_root_configure(self, event):
        if event.widget is self.root:
            self._sync_summary_visibility()

    def _sync_summary_visibility(self):
        show = self.summary_requested and not (
            self.log_visible and self.root.winfo_height() < 840
        )
        if show and not self.result_strip.winfo_manager():
            self.result_strip.grid(
                row=1, column=0, sticky="ew", pady=(8, 0)
            )
        elif not show and self.result_strip.winfo_manager():
            self.result_strip.grid_remove()

    def start_simulation(self):
        try:
            inputs = self.input_panel.get_inputs()
        except (ValueError, TypeError) as error:
            messagebox.showerror("Check the simulation settings", str(error))
            return

        protocol = inputs["protocol"]
        self._set_status(f"Running {PROTOCOL_INFO[protocol]['short']}…", "running")
        self.animation_panel.reset()
        self._clear_event_log()
        self._hide_run_summary()
        self.event_status_var.set("Preparing")
        self._set_playback_controls("running")

        self.root.update_idletasks()

        try:
            results = self.simulator.run_simulation(
                protocol_name=protocol,
                number_of_frames=inputs["frames"],
                window_size=inputs["window"],
                transmission_delay=inputs["transmission"],
                ack_delay=inputs["ack"],
                packet_loss=inputs["packet_loss"],
                ack_loss=inputs["ack_loss"],
                timeout=inputs["timeout"],
                seed=self.input_panel.get_seed(),
            )
        except Exception as error:
            self._set_status("Simulation failed", "error")
            self._set_playback_controls("idle")
            self.event_status_var.set("Failed")
            messagebox.showerror("Simulation error", str(error))
            return

        self.last_results = results
        self.last_protocol = protocol
        self.animation_panel.play(
            results["events"],
            protocol,
            inputs,
            on_event=self._append_simulation_event,
            on_complete=lambda: self._simulation_completed(protocol),
            on_state=self._simulation_state_changed,
        )

    def _simulation_completed(self, protocol):
        self.event_status_var.set("Completed")
        self._set_playback_controls("completed")
        self._set_status(
            f"{PROTOCOL_INFO[protocol]['short']} finished",
            "completed",
        )
        if self.last_results is not None:
            self._show_run_summary(protocol, self.last_results)
        self.hint_var.set(
            "Run Compare all three methods to place this result next to the "
            "other protocols."
        )

    def compare_protocols(self):
        try:
            inputs = self.input_panel.get_inputs()
        except (ValueError, TypeError) as error:
            messagebox.showerror("Check the simulation settings", str(error))
            return

        comparison_window = self.input_panel.get_comparison_window()

        self._set_status("Comparing all three methods…", "running")
        self.root.update_idletasks()

        comparison_results = {}
        try:
            for protocol in PROTOCOL_ORDER:
                comparison_results[protocol] = self.simulator.run_simulation(
                    protocol_name=protocol,
                    number_of_frames=inputs["frames"],
                    window_size=comparison_window,
                    transmission_delay=inputs["transmission"],
                    ack_delay=inputs["ack"],
                    packet_loss=inputs["packet_loss"],
                    ack_loss=inputs["ack_loss"],
                    timeout=inputs["timeout"],
                    seed=self.input_panel.get_seed(),
                )
        except Exception as error:
            self._set_status("Comparison failed", "error")
            messagebox.showerror("Comparison error", str(error))
            return

        self.current_comparison_results = comparison_results
        self.current_comparison_parameters = {
            key: inputs[key]
            for key in (
                "frames",
                "window",
                "transmission",
                "ack",
                "packet_loss",
                "ack_loss",
                "timeout",
            )
        }
        self.current_comparison_parameters["window"] = comparison_window

        self.comparison_panel.update_graph(comparison_results)
        self.results_panel.update_results(
            self.current_comparison_results,
            self.current_comparison_parameters,
        )
        self.notebook.select(self.results_tab)
        self.root.update_idletasks()
        self.comparison_panel.canvas.draw_idle()

        best_value = max(
            result.get("throughput_fps", 0)
            for result in comparison_results.values()
        )
        best_names = [
            name for name, result in comparison_results.items()
            if result.get("throughput_fps", 0) == best_value
        ]
        if len(best_names) == 1:
            comparison_note = (
                f"{PROTOCOL_INFO[best_names[0]]['short']} has the highest "
                "throughput"
            )
        elif len(best_names) == len(comparison_results):
            comparison_note = "all three methods tie on throughput"
        else:
            labels = [
                PROTOCOL_INFO[name]["short"] for name in best_names
            ]
            comparison_note = (
                f"{' and '.join(labels)} tie on throughput"
            )
        self._set_status(
            f"Comparison ready · {comparison_note}",
            "completed",
        )
        self.hint_var.set(
            "Results compare every method in the same scenario; "
            "Stop-and-Wait is always fixed at window 1."
        )

    def view_performance_results(self):
        self.notebook.select(self.results_tab)
        if not self.current_comparison_results:
            self._set_status("No comparison results yet", "ready")
            self.hint_var.set(
                "Use Compare all three methods to generate this dashboard."
            )

    def reset_simulation(self):
        self.animation_panel.reset()
        self._clear_event_log()
        self._hide_run_summary()
        self.event_status_var.set("Ready")
        self._set_playback_controls("idle")
        self.current_comparison_results = {}
        self.current_comparison_parameters = {}
        self.last_results = None
        self.last_protocol = None
        self.results_panel.clear()
        self.comparison_panel.reset()
        self._set_status("Ready", "ready")
        self.hint_var.set(
            "Pick a method and scenario, then run a simulation. "
            "Open How it works to compare the three rules."
        )

    def run(self):
        self.root.mainloop()

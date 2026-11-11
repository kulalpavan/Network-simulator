"""Configuration sidebar for running protocol simulations."""

import tkinter as tk
from tkinter import ttk

from config.settings import PROTOCOL_INFO, PROTOCOL_ORDER, SCENARIOS
from gui import theme


class InputPanel(tk.Frame):
    """Build the protocol, scenario, and network parameter controls."""

    def __init__(
        self,
        parent,
        on_start,
        on_compare,
        on_reset,
        on_view_results,
        on_protocol_change=None,
        on_scenario_change=None,
        action_parent=None,
    ):
        super().__init__(parent, background=theme.COLORS["bg"])
        self.on_protocol_change = on_protocol_change
        self.on_scenario_change = on_scenario_change
        self.action_parent = action_parent
        self._last_window_value = "4"
        self._last_scenario = "Ideal Network"

        self.protocol_var = tk.StringVar(value=PROTOCOL_ORDER[0])
        self.scenario_var = tk.StringVar(value="Ideal Network")
        self.frames_var = tk.StringVar()
        self.window_var = tk.StringVar()
        self.transmission_var = tk.StringVar()
        self.ack_var = tk.StringVar()
        self.packet_loss_var = tk.StringVar()
        self.ack_loss_var = tk.StringVar()
        self.timeout_var = tk.StringVar()

        self._build(on_start, on_compare, on_reset, on_view_results)
        self.apply_scenario("Ideal Network", notify=False)
        self._sync_protocol(notify=False)

    def _build(self, on_start, on_compare, on_reset, on_view_results):
        method_card, method = theme.make_card(
            self,
            title="1  Select a method",
            subtitle="Each protocol reacts to loss in a different way.",
            wrap=280,
        )
        method_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            method,
            text="PROTOCOL",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x")
        self.protocol_combo = ttk.Combobox(
            method,
            textvariable=self.protocol_var,
            values=PROTOCOL_ORDER,
            state="readonly",
            style="Field.TCombobox",
        )
        self.protocol_combo.pack(fill="x", pady=(4, 8))
        self.protocol_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._sync_protocol(),
        )

        self.tagline_label = tk.Label(
            method,
            text="",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(9),
            anchor="w",
            justify="left",
            wraplength=300,
        )
        self.tagline_label.pack(fill="x", pady=(0, 8))

        self.rules_frame = tk.Frame(method, background=theme.COLORS["surface"])
        self.rules_frame.pack(fill="x", pady=(0, 10))
        self.window_rule = self._add_rule(self.rules_frame, "Window")
        self.ack_rule = self._add_rule(self.rules_frame, "ACKs")
        self.loss_rule = self._add_rule(self.rules_frame, "On loss")

        tk.Frame(
            method,
            background=theme.COLORS["border"],
            height=1,
        ).pack(fill="x", pady=(0, 10))

        tk.Label(
            method,
            text="SCENARIO",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x")
        self.scenario_combo = ttk.Combobox(
            method,
            textvariable=self.scenario_var,
            values=list(SCENARIOS.keys()),
            state="readonly",
            style="Field.TCombobox",
        )
        self.scenario_combo.pack(fill="x", pady=(4, 6))
        self.scenario_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._on_scenario_selected(),
        )
        self.scenario_description = tk.Label(
            method,
            text="",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            anchor="w",
            justify="left",
            wraplength=300,
        )
        self.scenario_description.pack(fill="x")

        params_card, params = theme.make_card(
            self,
            title="2  Traffic & timing",
            subtitle="All times are in milliseconds.",
            wrap=280,
        )
        params_card.pack(fill="x", pady=(0, 10))

        grid = tk.Frame(params, background=theme.COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self.frames_entry = self._add_field(
            grid, 0, 0, "Frames", self.frames_var,
            "How many data frames the sender must deliver.",
            "frames",
        )
        self.window_entry = self._add_field(
            grid, 0, 1, "Window size", self.window_var,
            "How many unacknowledged frames may be in flight. "
            "Stop-and-Wait always uses 1.",
            "frames",
        )
        self._add_field(
            grid, 1, 0, "Transmission delay", self.transmission_var,
            "Time for a data frame to cross the link.",
            "ms",
        )
        self._add_field(
            grid, 1, 1, "ACK delay", self.ack_var,
            "Time for an acknowledgement to travel back.",
            "ms",
        )
        self._add_field(
            grid, 2, 0, "Timeout", self.timeout_var,
            "How long the sender waits for an ACK before retransmitting.",
            "ms",
        )

        loss_card, loss = theme.make_card(
            self,
            title="3  Network reliability",
            subtitle="Higher loss creates more timeouts and retransmissions.",
            wrap=280,
        )
        loss_card.pack(fill="x", pady=(0, 10))

        loss_grid = tk.Frame(loss, background=theme.COLORS["surface"])
        loss_grid.pack(fill="x")
        loss_grid.grid_columnconfigure(0, weight=1)
        loss_grid.grid_columnconfigure(1, weight=1)
        self._add_field(
            loss_grid, 0, 0, "Data loss", self.packet_loss_var,
            "Chance that the network drops a data frame.",
            "%",
        )
        self._add_field(
            loss_grid, 0, 1, "ACK loss", self.ack_loss_var,
            "Chance that the network drops an acknowledgement.",
            "%",
        )

        host = self.action_parent or self
        actions = tk.Frame(host, background=theme.COLORS["bg"])
        if self.action_parent is not None:
            tk.Frame(
                actions,
                background=theme.COLORS["border"],
                height=1,
            ).pack(fill="x", pady=(0, 10))
            actions.pack(side="bottom", fill="x", padx=(0, 12))
        else:
            actions.pack(fill="x", pady=(0, 10))

        primary = tk.Frame(actions, background=theme.COLORS["bg"])
        primary.pack(fill="x", pady=(0, 6))
        self.run_button = theme.make_button(
            primary,
            "▶  Run simulation",
            on_start,
            kind="success",
            compact=True,
        )
        self.run_button.pack(
            side="left", fill="x", expand=True, padx=(0, 3)
        )
        self.compare_button = theme.make_button(
            primary,
            "Compare methods",
            on_compare,
            kind="primary",
            compact=True,
        )
        self.compare_button.pack(
            side="left", fill="x", expand=True, padx=(3, 0)
        )
        theme.Tooltip(
            self.compare_button,
            "Run all three protocols with the same network settings.",
        )

        secondary = tk.Frame(actions, background=theme.COLORS["bg"])
        secondary.pack(fill="x")
        theme.make_button(
            secondary,
            "View results",
            on_view_results,
            kind="secondary",
            compact=True,
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))
        theme.make_button(
            secondary,
            "Reset",
            on_reset,
            kind="ghost",
            compact=True,
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        tk.Label(
            self,
            text=(
                "Tip: after a run, use Step Forward to inspect one protocol "
                "decision at a time."
            ),
            background=theme.COLORS["bg"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            wraplength=310,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(2, 12))

    def _add_rule(self, parent, label):
        row = tk.Frame(parent, background=theme.COLORS["surface"])
        row.pack(fill="x", pady=2)
        dot = tk.Label(
            row,
            text="●",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["primary"],
            font=theme.font(7),
        )
        dot.pack(side="left", padx=(0, 7))
        tk.Label(
            row,
            text=label,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            width=7,
            anchor="w",
        ).pack(side="left")
        value = tk.Label(
            row,
            text="",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(8, "bold"),
            anchor="w",
        )
        value.pack(side="left", fill="x", expand=True)
        return value

    def _add_field(self, parent, row, column, label, variable, tooltip, unit):
        cell = tk.Frame(parent, background=theme.COLORS["surface"])
        cell.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0, 6) if column == 0 else (6, 0),
            pady=(0, 12) if row < 2 else (0, 0),
        )
        label_widget = tk.Label(
            cell,
            text=label,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            anchor="w",
        )
        label_widget.pack(fill="x", pady=(0, 3))

        field_row = tk.Frame(cell, background=theme.COLORS["surface"])
        field_row.pack(fill="x")
        entry = ttk.Entry(
            field_row,
            textvariable=variable,
            style="Field.TEntry",
            width=9,
        )
        entry.pack(side="left", fill="x", expand=True)
        tk.Label(
            field_row,
            text=unit,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["faint"],
            font=theme.font(8),
            width=max(len(unit), 2),
            anchor="w",
        ).pack(side="left", padx=(6, 0))

        theme.Tooltip(label_widget, tooltip)
        theme.Tooltip(entry, tooltip)
        return entry

    def _sync_protocol(self, notify=True):
        protocol = self.protocol_var.get()
        info = PROTOCOL_INFO[protocol]
        accent = theme.protocol_accent(protocol)

        self.tagline_label.configure(text=info["tagline"])
        self.window_rule.configure(text=info["window_rule"])
        self.ack_rule.configure(text=info["ack_rule"])
        self.loss_rule.configure(text=info["loss_rule"])
        for row in self.rules_frame.winfo_children():
            for child in row.winfo_children():
                if child.cget("text") == "●":
                    child.configure(foreground=accent)

        if protocol == "One-Bit Sliding Window":
            if self.window_var.get().strip() not in ("", "1"):
                self._last_window_value = self.window_var.get().strip()
            self.window_var.set("1")
            self.window_entry.configure(state="disabled")
        else:
            was_disabled = str(self.window_entry.cget("state")) == "disabled"
            self.window_entry.configure(state="normal")
            if was_disabled:
                self.window_var.set(self._last_window_value or "4")

        if notify and self.on_protocol_change:
            self.on_protocol_change(protocol, info)

    def _on_scenario_selected(self):
        name = self.scenario_var.get()
        self.apply_scenario(name)
        if self.on_scenario_change:
            self.on_scenario_change(name, SCENARIOS[name])

    def apply_scenario(self, name, notify=False):
        if name not in SCENARIOS:
            return
        params = SCENARIOS[name]
        self._last_scenario = name
        self._last_window_value = str(params["window"])
        self.frames_var.set(str(params["frames"]))
        self.window_var.set(str(params["window"]))
        self.transmission_var.set(str(params["transmission"]))
        self.ack_var.set(str(params["ack"]))
        self.packet_loss_var.set(str(params["packet_loss"]))
        self.ack_loss_var.set(str(params["ack_loss"]))
        self.timeout_var.set(str(params["timeout"]))
        self.scenario_description.configure(text=params["description"])
        if self.protocol_var.get() == "One-Bit Sliding Window":
            self.window_var.set("1")
        if notify and self.on_scenario_change:
            self.on_scenario_change(name, params)

    def get_seed(self):
        return SCENARIOS.get(self.scenario_var.get(), {}).get("seed", 1)

    def get_comparison_window(self):
        """Return the window used by the windowed methods in a comparison."""
        if self.protocol_var.get() == "One-Bit Sliding Window":
            try:
                return max(1, int(self._last_window_value))
            except (TypeError, ValueError):
                return 4
        return int(self.window_var.get())

    def get_inputs(self):
        """Read and validate the simulation parameters."""
        protocol = self.protocol_var.get()
        try:
            frames = int(self.frames_var.get())
            window = int(self.window_var.get())
            transmission = float(self.transmission_var.get())
            ack = float(self.ack_var.get())
            packet_loss = float(self.packet_loss_var.get())
            ack_loss = float(self.ack_loss_var.get())
            timeout = float(self.timeout_var.get())
        except ValueError as error:
            raise ValueError(
                "Every parameter must be a number. Check the fields in the "
                "configuration panel."
            ) from error

        if frames < 1:
            raise ValueError("Number of frames must be at least 1.")
        if window < 1:
            raise ValueError("Window size must be at least 1.")
        if protocol == "One-Bit Sliding Window":
            window = 1
        if transmission <= 0 or ack < 0:
            raise ValueError(
                "Transmission delay must be positive and ACK delay cannot "
                "be negative."
            )
        if timeout <= 0:
            raise ValueError("Timeout must be positive.")
        if not 0 <= packet_loss <= 100:
            raise ValueError("Data loss must be between 0 and 100%.")
        if not 0 <= ack_loss <= 100:
            raise ValueError("ACK loss must be between 0 and 100%.")

        return {
            "protocol": protocol,
            "frames": frames,
            "window": window,
            "transmission": transmission,
            "ack": ack,
            "packet_loss": packet_loss,
            "ack_loss": ack_loss,
            "timeout": timeout,
        }

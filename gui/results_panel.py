"""Results dashboard comparing the three protocols."""

import tkinter as tk
from tkinter import ttk

from config.settings import PROTOCOL_INFO, PROTOCOL_ORDER
from gui import theme


class ResultsPanel(tk.Frame):
    """Display summary cards and an explained metrics table."""

    METRICS = (
        ("Frames transmitted", "total_frames_transmitted",
         "Every send, including retries."),
        ("Retransmissions", "retransmissions",
         "Extra sends due to loss or timeouts."),
        ("Packets lost", "packets_lost",
         "Data frames lost in transit."),
        ("ACKs received", "acks_received",
         "ACKs that reached the sender."),
        ("Total time (ms)", "total_time_ms",
         "Total simulated transmission time."),
        ("Throughput (fps)", "throughput_fps",
         "Delivered frames per second."),
        ("Efficiency (%)", "efficiency_percent",
         "Delivered ÷ transmitted."),
    )

    def __init__(self, parent, on_compare=None):
        super().__init__(parent, background=theme.COLORS["bg"])
        self.on_compare = on_compare
        self.results = {}
        self.cards = {}
        self._build()
        self.clear()

    def _build(self):
        self.empty_frame = tk.Frame(
            self,
            background=theme.COLORS["surface"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
        )
        empty_inner = tk.Frame(
            self.empty_frame,
            background=theme.COLORS["surface"],
        )
        empty_inner.pack(expand=True, pady=28)
        tk.Label(
            empty_inner,
            text="No comparison yet",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["ink"],
            font=theme.font(13, "bold"),
        ).pack()
        tk.Label(
            empty_inner,
            text=(
                "Run all three methods with the same network settings to see "
                "which one recovers most efficiently."
            ),
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(9),
            wraplength=440,
            justify="center",
        ).pack(pady=(4, 12))
        if self.on_compare is not None:
            theme.make_button(
                empty_inner,
                "Compare all three methods",
                self.on_compare,
                kind="primary",
                compact=True,
            ).pack()

        self.dashboard = tk.Frame(self, background=theme.COLORS["bg"])

        summary = tk.Frame(self.dashboard, background=theme.COLORS["bg"])
        summary.pack(fill="x")
        for column in range(3):
            summary.grid_columnconfigure(column, weight=1, uniform="summary")

        for column, protocol in enumerate(PROTOCOL_ORDER):
            card = self._build_summary_card(summary, protocol)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0, 5) if column < 2 else (0, 0),
            )

        self.parameters_label = tk.Label(
            self.dashboard,
            text="",
            background=theme.COLORS["bg"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            anchor="w",
            justify="left",
            wraplength=880,
        )
        self.parameters_label.pack(
            fill="x", pady=(0, 8), before=summary
        )

        table_card, body = theme.make_card(
            self.dashboard,
            title="Detailed comparison",
            subtitle=(
                "Every metric is defined in plain language. Higher throughput "
                "and efficiency are better."
            ),
            padding=12,
        )
        table_card.pack(fill="both", expand=True)

        table_frame = tk.Frame(body, background=theme.COLORS["surface"])
        columns = (
            "metric",
            "meaning",
            "stop_and_wait",
            "go_back_n",
            "selective_repeat",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=len(self.METRICS),
            style="App.Treeview",
        )

        headings = {
            "metric": "Metric",
            "meaning": "What it means",
            "stop_and_wait": PROTOCOL_INFO["One-Bit Sliding Window"]["short"],
            "go_back_n": PROTOCOL_INFO["Go-Back-N"]["short"],
            "selective_repeat": PROTOCOL_INFO["Selective Repeat"]["short"],
        }
        widths = {
            "metric": 135,
            "meaning": 234,
            "stop_and_wait": 106,
            "go_back_n": 95,
            "selective_repeat": 120,
        }
        for column in columns:
            self.tree.heading(
                column,
                text=headings[column],
                anchor="w" if column in ("metric", "meaning") else "center",
            )
            self.tree.column(
                column,
                width=widths[column],
                minwidth=90,
                anchor="w" if column in ("metric", "meaning") else "center",
                stretch=column == "meaning",
            )

        self.tree.tag_configure("odd", background=theme.COLORS["surface"])
        self.tree.tag_configure("even", background=theme.COLORS["surface_alt"])
        self.tree.pack(fill="both", expand=True)
        table_frame.pack(fill="both", expand=True)

    def _build_summary_card(self, parent, protocol):
        accent = theme.protocol_accent(protocol)
        soft = theme.protocol_soft(protocol)
        card = tk.Frame(
            parent,
            background=theme.COLORS["surface"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
        )
        tk.Frame(card, background=accent, height=3).pack(fill="x")
        inner = tk.Frame(card, background=theme.COLORS["surface"])
        inner.pack(fill="both", expand=True, padx=14, pady=10)

        tk.Label(
            inner,
            text=PROTOCOL_INFO[protocol]["short"],
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["ink"],
            font=theme.font(9, "bold"),
            anchor="w",
        ).pack(fill="x")
        badge = tk.Label(
            inner,
            text="",
            background=theme.COLORS["surface"],
            foreground=accent,
            font=theme.font(7, "bold"),
            padx=6,
            pady=1,
            anchor="w",
        )
        badge.pack(anchor="w", pady=(2, 0))

        value = tk.Label(
            inner,
            text="—",
            background=theme.COLORS["surface"],
            foreground=accent,
            font=theme.font(20, "bold"),
            anchor="w",
        )
        value.pack(fill="x", pady=(4, 0))
        tk.Label(
            inner,
            text="delivered frames per second",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7),
            anchor="w",
        ).pack(fill="x")

        details = tk.Label(
            inner,
            text="Efficiency —",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(8),
            anchor="w",
        )
        details.pack(fill="x", pady=(6, 0))
        stats = tk.Label(
            inner,
            text="",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7),
            anchor="w",
        )
        stats.pack(fill="x", pady=(2, 0))

        self.cards[protocol] = {
            "badge": badge,
            "value": value,
            "details": details,
            "stats": stats,
        }
        return card

    @staticmethod
    def _format_value(value):
        if value is None or value == "":
            return "—"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    def update_results(self, results, parameters):
        """Refresh summary cards, parameters, and the detailed table."""
        self.results = results
        self.empty_frame.pack_forget()
        self.dashboard.pack(fill="both", expand=True)

        self.parameters_label.configure(
            text=(
                f"Same scenario:  {parameters['frames']} frames  ·  "
                f"window {parameters['window']} "
                f"(Stop-and-Wait fixed at 1)  ·  delays "
                f"{parameters['transmission']:g}/{parameters['ack']:g} ms  ·  "
                f"loss {parameters['packet_loss']:g}% / "
                f"{parameters['ack_loss']:g}%  ·  timeout "
                f"{parameters['timeout']:g} ms"
            )
        )

        throughput_values = {
            protocol: float(results.get(protocol, {}).get("throughput_fps", 0))
            for protocol in PROTOCOL_ORDER
        }
        efficiency_values = {
            protocol: float(
                results.get(protocol, {}).get("efficiency_percent", 0)
            )
            for protocol in PROTOCOL_ORDER
        }
        retransmission_values = {
            protocol: int(results.get(protocol, {}).get("retransmissions", 0))
            for protocol in PROTOCOL_ORDER
        }
        best_throughput = max(throughput_values, key=throughput_values.get)
        best_efficiency = max(efficiency_values, key=efficiency_values.get)
        fewest_retries = min(
            retransmission_values, key=retransmission_values.get
        )
        max_throughput = throughput_values[best_throughput]
        max_efficiency = efficiency_values[best_efficiency]
        max_retries = max(retransmission_values.values())
        min_retries = retransmission_values[fewest_retries]
        throughput_winners = [
            name for name, value in throughput_values.items()
            if value == max_throughput
        ]
        efficiency_winners = [
            name for name, value in efficiency_values.items()
            if value == max_efficiency
        ]
        retry_winners = [
            name for name, value in retransmission_values.items()
            if value == min_retries
        ]

        for protocol in PROTOCOL_ORDER:
            result = results.get(protocol, {})
            card = self.cards[protocol]
            throughput = throughput_values[protocol]
            efficiency = efficiency_values[protocol]
            card["value"].configure(text=f"{throughput:.2f}")
            card["details"].configure(
                text=f"Efficiency {efficiency:.1f}%  ·  "
                f"{int(result.get('delivered_frames', 0))} delivered"
            )
            card["stats"].configure(
                text=(
                    f"{int(result.get('retransmissions', 0))} retransmissions"
                    f"  ·  {int(result.get('total_frames_transmitted', 0))} sent"
                )
            )
            badges = []
            if (
                max_throughput > 0
                and len(throughput_winners) == 1
                and protocol in throughput_winners
            ):
                badges.append("BEST THROUGHPUT")
            if (
                max_efficiency > 0
                and len(efficiency_winners) == 1
                and protocol in efficiency_winners
            ):
                badges.append("BEST EFFICIENCY")
            if (
                max_retries > 0
                and len(retry_winners) == 1
                and protocol in retry_winners
            ):
                badges.append("FEWEST RETRIES")
            if badges:
                card["badge"].configure(
                    text=" · ".join(badges[:2]),
                    background=theme.protocol_soft(protocol),
                )
            else:
                card["badge"].configure(
                    text="",
                    background=theme.COLORS["surface"],
                )

        self.tree.delete(*self.tree.get_children())
        keys = {
            "stop_and_wait": "One-Bit Sliding Window",
            "go_back_n": "Go-Back-N",
            "selective_repeat": "Selective Repeat",
        }
        for index, (label, metric_key, meaning) in enumerate(self.METRICS):
            row = [label, meaning]
            for column in ("stop_and_wait", "go_back_n", "selective_repeat"):
                protocol_result = results.get(keys[column], {})
                row.append(
                    self._format_value(protocol_result.get(metric_key))
                )
            self.tree.insert(
                "",
                "end",
                values=row,
                tags=("even" if index % 2 else "odd",),
            )

    def clear(self):
        """Remove any displayed comparison and show the prompt."""
        self.dashboard.pack_forget()
        self.empty_frame.pack(fill="both", expand=True)
        self.parameters_label.configure(text="")
        self.tree.delete(*self.tree.get_children())
        for card in self.cards.values():
            card["badge"].configure(
                text="",
                background=theme.COLORS["surface"],
            )
            card["value"].configure(text="—")
            card["details"].configure(text="Efficiency —")
            card["stats"].configure(text="")

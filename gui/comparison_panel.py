"""Comparison charts for sliding window protocols."""

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config.settings import PROTOCOL_INFO, PROTOCOL_ORDER
from gui import theme


class ComparisonPanel(tk.Frame):
    """Draw throughput and efficiency charts with a written insight."""

    def __init__(self, parent):
        super().__init__(parent, background=theme.COLORS["surface"])
        self.results = {}

        self.figure = Figure(figsize=(8.4, 2.6), dpi=100 * theme.SCALE)
        self.figure.patch.set_facecolor(theme.COLORS["surface"])
        self.throughput_ax = self.figure.add_subplot(121)
        self.efficiency_ax = self.figure.add_subplot(122)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().configure(
            background=theme.COLORS["surface"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.insight_label = tk.Label(
            self,
            text="",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(8),
            justify="left",
            anchor="w",
            wraplength=760,
        )
        self.insight_label.pack(fill="x", pady=(4, 0))
        self.bind("<Configure>", self._on_resize)

        self.show_empty_graph()

    def _on_resize(self, event):
        self.insight_label.configure(wraplength=max(event.width - 10, 300))

    @staticmethod
    def _style_axis(axis, title, ylabel):
        axis.set_facecolor(theme.COLORS["surface"])
        axis.set_title(
            title,
            loc="left",
            fontsize=10,
            fontweight="bold",
            color=theme.COLORS["ink"],
            pad=8,
        )
        axis.set_ylabel(
            ylabel,
            fontsize=8,
            color=theme.COLORS["muted"],
        )
        axis.tick_params(
            axis="x",
            labelsize=7,
            colors=theme.COLORS["body"],
            length=0,
            pad=6,
        )
        axis.tick_params(
            axis="y",
            labelsize=7,
            colors=theme.COLORS["muted"],
            length=0,
        )
        axis.grid(
            axis="y",
            color=theme.COLORS["border"],
            linestyle="--",
            linewidth=0.8,
            alpha=0.8,
        )
        axis.set_axisbelow(True)
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color(theme.COLORS["border_strong"])

    def show_empty_graph(self):
        for axis in (self.throughput_ax, self.efficiency_ax):
            axis.clear()
            axis.set_facecolor(theme.COLORS["surface"])
            axis.set_xticks([])
            axis.set_yticks([])
            for side in axis.spines.values():
                side.set_visible(False)
            axis.text(
                0.5,
                0.55,
                "Run a comparison to see the charts",
                transform=axis.transAxes,
                ha="center",
                va="center",
                fontsize=9,
                color=theme.COLORS["muted"],
            )
            axis.text(
                0.5,
                0.4,
                "Run all three methods on the same scenario.",
                transform=axis.transAxes,
                ha="center",
                va="center",
                fontsize=7.5,
                color=theme.COLORS["faint"],
            )
        self.figure.subplots_adjust(
            left=0.08, right=0.98, top=0.9, bottom=0.14, wspace=0.3
        )
        self.canvas.draw_idle()
        self.insight_label.configure(
            text=(
                "Throughput = delivered frames per second.  "
                "Efficiency = delivered frames ÷ all transmissions.  "
                "Higher is better for both."
            )
        )

    def update_graph(self, results):
        """Display throughput and efficiency side by side."""
        self.results = results
        protocols = [name for name in PROTOCOL_ORDER if name in results]
        if not protocols:
            self.show_empty_graph()
            return

        throughputs = [
            float(results[name].get("throughput_fps", 0.0))
            for name in protocols
        ]
        efficiencies = [
            float(results[name].get("efficiency_percent", 0.0))
            for name in protocols
        ]
        colors = [theme.protocol_accent(name) for name in protocols]
        labels = [PROTOCOL_INFO[name]["short"] for name in protocols]
        x = list(range(len(protocols)))

        self.throughput_ax.clear()
        self.efficiency_ax.clear()

        bars = self.throughput_ax.bar(
            x, throughputs, width=0.58, color=colors, zorder=3
        )
        self._style_axis(
            self.throughput_ax, "Throughput", "frames per second"
        )
        self.throughput_ax.set_xticks(x)
        self.throughput_ax.set_xticklabels(
            labels, rotation=15, ha="right"
        )
        self.throughput_ax.set_xlim(-0.6, len(protocols) - 0.4)
        top = max(throughputs, default=0)
        self.throughput_ax.set_ylim(0, top * 1.28 if top > 0 else 1)
        for bar, value in zip(bars, throughputs):
            self.throughput_ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(top, 0.01) * 0.03,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=theme.COLORS["body"],
            )

        bars = self.efficiency_ax.bar(
            x, efficiencies, width=0.58, color=colors, zorder=3
        )
        self._style_axis(
            self.efficiency_ax, "Efficiency", "delivered ÷ transmitted (%)"
        )
        self.efficiency_ax.set_xticks(x)
        self.efficiency_ax.set_xticklabels(
            labels, rotation=15, ha="right"
        )
        self.efficiency_ax.set_xlim(-0.6, len(protocols) - 0.4)
        top = max(efficiencies, default=0)
        self.efficiency_ax.set_ylim(
            0, min(110, max(20, top * 1.18)) if top > 0 else 10
        )
        for bar, value in zip(bars, efficiencies):
            self.efficiency_ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(top, 0.01) * 0.03,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                color=theme.COLORS["body"],
            )

        self.figure.subplots_adjust(
            left=0.1, right=0.98, top=0.9, bottom=0.22, wspace=0.32
        )
        self.canvas.draw_idle()

        max_throughput = max(throughputs)
        max_efficiency = max(efficiencies)
        throughput_winners = [
            protocols[index] for index, value in enumerate(throughputs)
            if value == max_throughput
        ]
        efficiency_winners = [
            protocols[index] for index, value in enumerate(efficiencies)
            if value == max_efficiency
        ]
        retries = {
            name: int(results[name].get("retransmissions", 0))
            for name in protocols
        }
        min_retries = min(retries.values())
        retry_winners = [
            name for name, value in retries.items() if value == min_retries
        ]

        def joined(names):
            labels = [PROTOCOL_INFO[name]["short"] for name in names]
            if len(labels) == 1:
                return labels[0]
            if len(labels) == 2:
                return f"{labels[0]} and {labels[1]}"
            return f"{labels[0]}, {labels[1]}, and {labels[2]}"

        if len(throughput_winners) == len(protocols):
            throughput_text = (
                f"All three methods tie on throughput "
                f"({max_throughput:.2f} fps)."
            )
        elif len(throughput_winners) == 1:
            throughput_text = (
                f"Fastest delivery: "
                f"{PROTOCOL_INFO[throughput_winners[0]]['short']} "
                f"({max_throughput:.2f} fps)."
            )
        else:
            throughput_text = (
                f"{joined(throughput_winners)} tie for fastest delivery "
                f"({max_throughput:.2f} fps)."
            )

        if len(efficiency_winners) == len(protocols):
            efficiency_text = (
                f"All three tie on efficiency "
                f"({max_efficiency:.1f}%)."
            )
        elif len(efficiency_winners) == 1:
            efficiency_text = (
                f"Least wasted capacity: "
                f"{PROTOCOL_INFO[efficiency_winners[0]]['short']} "
                f"({max_efficiency:.1f}% efficiency)."
            )
        else:
            efficiency_text = (
                f"{joined(efficiency_winners)} tie on efficiency "
                f"({max_efficiency:.1f}%)."
            )

        if min_retries == 0:
            retry_text = "No retransmissions were needed."
        elif len(retry_winners) == 1:
            retry_text = (
                f"Fewest retransmissions: "
                f"{PROTOCOL_INFO[retry_winners[0]]['short']} "
                f"({min_retries})."
            )
        else:
            retry_text = (
                f"{joined(retry_winners)} tie for fewest retransmissions "
                f"({min_retries})."
            )

        self.insight_label.configure(
            text=(
                f"{throughput_text}  {efficiency_text}  {retry_text}  "
                "Efficiency drops whenever frames are sent more than once."
            )
        )

    def reset(self):
        self.results = {}
        self.show_empty_graph()

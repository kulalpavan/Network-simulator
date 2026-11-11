"""Plain-language guide explaining how each protocol behaves."""

import tkinter as tk

from config.settings import PROTOCOL_INFO, PROTOCOL_ORDER
from gui import theme


class ProtocolGuide(tk.Frame):
    """Visual explainer for the three ARQ methods."""

    def __init__(self, parent):
        super().__init__(parent, background=theme.COLORS["bg"])
        self.cards = {}

        scroll = theme.ScrollFrame(self, background=theme.COLORS["bg"])
        scroll.pack(fill="both", expand=True)
        content = scroll.body
        content.configure(padx=2, pady=2)

        self._build_intro(content)

        cards_row = tk.Frame(content, background=theme.COLORS["bg"])
        cards_row.pack(fill="x", pady=(12, 0))
        for column in range(3):
            cards_row.grid_columnconfigure(column, weight=1, uniform="guide")
        cards_row.grid_rowconfigure(0, weight=1)

        for column, protocol in enumerate(PROTOCOL_ORDER):
            card = self._build_protocol_card(cards_row, protocol)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0, 6) if column < 2 else (0, 0),
            )

        self._build_reading_guide(content)

    def _build_intro(self, parent):
        card, body = theme.make_card(
            parent,
            title="How each method works",
            subtitle=(
                "Every protocol follows the same loop: send frames allowed "
                "by the window, collect acknowledgements, slide the window, "
                "and retransmit when something is lost. The difference is "
                "how much gets resent."
            ),
        )
        card.pack(fill="x")

        flow = tk.Frame(body, background=theme.COLORS["surface_alt"])
        flow.pack(fill="x", pady=(10, 0))
        steps = [
            ("1", "Send", "Frames inside the window leave the sender."),
            ("2", "ACK", "The receiver confirms frames it accepted."),
            ("3", "Slide", "The window moves over acknowledged frames."),
            ("4", "Recover", "Loss triggers the retransmission rule."),
        ]
        for index in range(len(steps)):
            flow.grid_columnconfigure(index, weight=1, uniform="flow")
        for index, (number, title, text) in enumerate(steps):
            step = tk.Frame(flow, background=theme.COLORS["surface_alt"])
            step.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(10 if index == 0 else 5, 10 if index == 3 else 5),
                pady=10,
            )
            header = tk.Frame(step, background=theme.COLORS["surface_alt"])
            header.pack(fill="x")
            tk.Label(
                header,
                text=number,
                background=theme.COLORS["primary"],
                foreground="white",
                font=theme.font(8, "bold"),
                width=2,
                pady=2,
            ).pack(side="left")
            tk.Label(
                header,
                text=title,
                background=theme.COLORS["surface_alt"],
                foreground=theme.COLORS["ink"],
                font=theme.font(9, "bold"),
                anchor="w",
            ).pack(side="left", padx=(6, 0))
            tk.Label(
                step,
                text=text,
                background=theme.COLORS["surface_alt"],
                foreground=theme.COLORS["muted"],
                font=theme.font(8),
                anchor="w",
                justify="left",
                wraplength=150,
            ).pack(fill="x", pady=(4, 0))

    def _build_protocol_card(self, parent, protocol):
        info = PROTOCOL_INFO[protocol]
        accent = theme.protocol_accent(protocol)
        soft = theme.protocol_soft(protocol)

        card = tk.Frame(
            parent,
            background=theme.COLORS["surface"],
            highlightbackground=theme.COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        tk.Frame(card, background=accent, height=4).pack(fill="x")

        body = tk.Frame(card, background=theme.COLORS["surface"])
        body.pack(fill="both", expand=True, padx=12, pady=14)

        tk.Label(
            body,
            text=info["short"],
            background=theme.COLORS["surface"],
            foreground=accent,
            font=theme.font(12, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            body,
            text=protocol,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            body,
            text=info["tagline"],
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(9),
            anchor="w",
            justify="left",
            wraplength=190,
        ).pack(fill="x", pady=(8, 12))

        tk.Label(
            body,
            text="HOW IT WORKS",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        for number, step in enumerate(info["steps"], start=1):
            row = tk.Frame(body, background=theme.COLORS["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=str(number),
                background=soft,
                foreground=accent,
                font=theme.font(7, "bold"),
                width=2,
                pady=1,
            ).pack(side="left", anchor="n", padx=(0, 7))
            tk.Label(
                row,
                text=step,
                background=theme.COLORS["surface"],
                foreground=theme.COLORS["body"],
                font=theme.font(8),
                anchor="w",
                justify="left",
                wraplength=170,
            ).pack(side="left", fill="x", expand=True)

        divider = tk.Frame(body, background=theme.COLORS["border"], height=1)
        divider.pack(fill="x", pady=10)

        rules = tk.Frame(body, background=theme.COLORS["surface"])
        rules.pack(fill="x")
        self._rule(rules, "Window", info["window_rule"], accent)
        self._rule(rules, "ACKs", info["ack_rule"], accent)
        self._rule(rules, "On loss", info["loss_rule"], accent)
        self._rule(rules, "Best for", info["best_for"], accent)

        watch = tk.Frame(body, background=soft)
        watch.pack(fill="x", pady=(12, 0))
        tk.Label(
            watch,
            text="WATCH FOR IN THE SIMULATION",
            background=soft,
            foreground=accent,
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(
            watch,
            text=info["watch_for"],
            background=soft,
            foreground=theme.COLORS["body"],
            font=theme.font(8),
            anchor="w",
            justify="left",
            wraplength=165,
        ).pack(fill="x", padx=10, pady=(0, 8))

        self.cards[protocol] = card
        return card

    def _rule(self, parent, label, value, accent):
        row = tk.Frame(parent, background=theme.COLORS["surface"])
        row.pack(fill="x", pady=2)
        tk.Label(
            row,
            text="●",
            background=theme.COLORS["surface"],
            foreground=accent,
            font=theme.font(7),
        ).pack(side="left", padx=(0, 7))
        tk.Label(
            row,
            text=label,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(8),
            width=7,
            anchor="w",
        ).pack(side="left")
        tk.Label(
            row,
            text=value,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(8, "bold"),
            anchor="w",
            justify="left",
            wraplength=140,
        ).pack(side="left", fill="x", expand=True)

    def _build_reading_guide(self, parent):
        card, body = theme.make_card(
            parent,
            title="Reading the simulation",
            subtitle=(
                "The live timeline is a real event log: every row is one "
                "decision made by the protocol."
            ),
        )
        card.pack(fill="x", pady=(12, 12))

        columns = tk.Frame(body, background=theme.COLORS["surface"])
        columns.pack(fill="x")

        left = tk.Frame(columns, background=theme.COLORS["surface"])
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(columns, background=theme.COLORS["surface"])
        right.pack(side="left", fill="both", expand=True, padx=(24, 0))

        tk.Label(
            left,
            text="ARROWS AND COLOURS",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        self._legend(left, theme.COLORS["primary"], False, "Data frame travelling to the receiver")
        self._legend(left, theme.COLORS["success"], True, "ACK travelling back to the sender")
        self._legend(left, theme.COLORS["danger"], False, "Frame or ACK dropped by the network")
        self._legend(left, theme.COLORS["warning"], False, "Retransmission caused by a timeout")
        self._legend(left, theme.COLORS["faint"], True, "Duplicate or out-of-order frame discarded")

        tk.Label(
            right,
            text="WHAT TO NOTICE",
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["muted"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        notes = [
            "The bar above the timeline explains why the current step happened.",
            "Sender and receiver windows update as ACKs arrive.",
            "Pause after any step to compare the rule with the protocol guide.",
            "The status column tells you whether the step succeeded or failed.",
        ]
        for note in notes:
            row = tk.Frame(right, background=theme.COLORS["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text="→",
                background=theme.COLORS["surface"],
                foreground=theme.COLORS["primary"],
                font=theme.font(9, "bold"),
            ).pack(side="left", padx=(0, 7))
            tk.Label(
                row,
                text=note,
                background=theme.COLORS["surface"],
                foreground=theme.COLORS["body"],
                font=theme.font(8),
                anchor="w",
                justify="left",
                wraplength=290,
            ).pack(side="left", fill="x", expand=True)

    def _legend(self, parent, color, dashed, label):
        row = tk.Frame(parent, background=theme.COLORS["surface"])
        row.pack(fill="x", pady=3)
        canvas = tk.Canvas(
            row,
            width=42,
            height=14,
            background=theme.COLORS["surface"],
            highlightthickness=0,
        )
        canvas.pack(side="left", padx=(0, 8))
        canvas.create_line(
            2,
            7,
            40,
            7,
            fill=color,
            width=2,
            arrow=tk.LAST,
            dash=(4, 3) if dashed else (),
        )
        tk.Label(
            row,
            text=label,
            background=theme.COLORS["surface"],
            foreground=theme.COLORS["body"],
            font=theme.font(8),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

    def set_protocol(self, protocol):
        """Emphasise the card matching the selected protocol."""
        for name, card in self.cards.items():
            if name == protocol:
                card.configure(
                    highlightbackground=theme.protocol_accent(name),
                    highlightthickness=2,
                )
            else:
                card.configure(
                    highlightbackground=theme.COLORS["border"],
                    highlightthickness=1,
                )

"""Interactive sender-receiver timeline for ARQ simulations."""

import re
import tkinter as tk
from tkinter import ttk

from gui import theme


_FRAME_PATTERN = re.compile(r"\bFrame\s+(\d+)\b", re.IGNORECASE)
_ACK_PATTERN = re.compile(r"\bACK\s+(\d+)\b", re.IGNORECASE)
_ATTEMPT_PATTERN = re.compile(r"\bAttempt\s+(\d+)\b", re.IGNORECASE)
_WINDOW_PATTERN = re.compile(r"\[(\d+),\s*(\d+)\]")
_SLIDE_PATTERN = re.compile(r"from\s+(\d+)\s+to\s+(\d+)", re.IGNORECASE)

RULE_SUMMARY = {
    "One-Bit Sliding Window": "Window 1 · one frame in flight · timeout resends it",
    "Go-Back-N": "Window N · cumulative ACKs · timeout resends the window",
    "Selective Repeat": "Window N · individual ACKs · resend only missing frames",
}


def normalize_events(events, protocol, parameters):
    """Convert protocol event strings to UI records without inventing events."""

    records = []
    elapsed_ms = 0.0
    transmission_delay = float(parameters["transmission"])
    ack_delay = float(parameters["ack"])
    timeout = float(parameters["timeout"])

    for raw_event in events:
        event = raw_event.strip()
        if not event:
            continue

        lower_event = event.lower()
        frame_match = _FRAME_PATTERN.search(event)
        ack_match = _ACK_PATTERN.search(event)
        attempt_match = _ATTEMPT_PATTERN.search(event)
        window_match = _WINDOW_PATTERN.search(event)
        slide_match = _SLIDE_PATTERN.search(event)

        frame = int(frame_match.group(1)) if frame_match else None
        ack = int(ack_match.group(1)) if ack_match else None
        attempt = int(attempt_match.group(1)) if attempt_match else 1

        if "simulation started" in lower_event:
            kind = "start"
        elif "simulation completed" in lower_event:
            kind = "complete"
        elif "sender: window [" in lower_event:
            kind = "window"
        elif "frame" in lower_event and "sent" in lower_event:
            kind = "data_tx"
            elapsed_ms += transmission_delay
        elif "network: frame" in lower_event and "lost" in lower_event:
            kind = "data_lost"
        elif "network: ack" in lower_event and "lost" in lower_event:
            kind = "ack_lost"
        elif lower_event.startswith("timeout:"):
            kind = "timeout"
            elapsed_ms += timeout
        elif "retransmitting" in lower_event:
            kind = "retransmit"
        elif "window slides from" in lower_event:
            kind = "window_slide"
        elif "ack" in lower_event and "generated" in lower_event:
            kind = "ack_generated"
            elapsed_ms += ack_delay
        elif lower_event.startswith("sender: ack") and "received" in lower_event:
            kind = "ack_received"
        elif "out-of-order" in lower_event and "discard" in lower_event:
            kind = "discard"
        elif "duplicate" in lower_event and "discard" in lower_event:
            kind = "duplicate"
        elif "buffered" in lower_event:
            kind = "buffered"
        elif "received successfully" in lower_event or (
            "accepted" in lower_event and "frame" in lower_event
        ):
            kind = "received"
        elif "delivered to upper layer" in lower_event:
            kind = "delivered"
        elif "frame" in lower_event and "discard" in lower_event:
            kind = "discard"
        elif "ready to transmit" in lower_event:
            kind = "ready"
        else:
            kind = "info"

        if kind == "data_tx":
            status = "Retransmission" if attempt > 1 else "Data sent"
            frame_ack = f"Frame {frame}" if frame is not None else ""
        elif kind == "data_lost":
            status = "Packet loss"
            frame_ack = f"Frame {frame}" if frame is not None else ""
        elif kind == "ack_generated":
            status = "ACK generated"
            frame_ack = f"ACK {ack}" if ack is not None else ""
        elif kind == "ack_lost":
            status = "ACK loss"
            frame_ack = f"ACK {ack}" if ack is not None else ""
        elif kind == "ack_received":
            status = "Successful ACK"
            frame_ack = f"ACK {ack}" if ack is not None else ""
        elif kind == "timeout":
            status = "Timeout"
            frame_ack = f"Frame {frame}" if frame is not None else ""
            if ack is not None:
                frame_ack = f"ACK {ack}"
        elif kind == "retransmit":
            status = "Retransmission"
            frame_ack = ""
        elif kind in ("duplicate", "discard"):
            status = "Discarded frame"
            frame_ack = f"Frame {frame}" if frame is not None else ""
        elif kind in ("received", "delivered", "buffered"):
            status = "Frame received"
            frame_ack = f"Frame {frame}" if frame is not None else ""
        elif kind in ("window", "window_slide"):
            status = "Window update"
            frame_ack = ""
        elif kind == "complete":
            status = "Completed"
            frame_ack = ""
        elif kind == "start":
            status = "Started"
            frame_ack = ""
        else:
            status = "In progress"
            frame_ack = f"Frame {frame}" if frame is not None else (
                f"ACK {ack}" if ack is not None else ""
            )

        records.append({
            "step": len(records) + 1,
            "time_ms": elapsed_ms,
            "protocol": protocol,
            "event": event,
            "frame_ack": frame_ack,
            "status": status,
            "kind": kind,
            "frame": frame,
            "ack": ack,
            "attempt": attempt,
            "window": (
                (int(window_match.group(1)), int(window_match.group(2)))
                if window_match else None
            ),
            "slide": (
                (int(slide_match.group(1)), int(slide_match.group(2)))
                if slide_match else None
            ),
            "transmission_succeeded": None,
        })

    for index, record in enumerate(records):
        if record["kind"] == "data_tx":
            for following in records[index + 1:]:
                if following["kind"] == "data_tx" and (
                    following["frame"] == record["frame"]
                ):
                    break
                if following["kind"] == "data_lost" and (
                    following["frame"] == record["frame"]
                ):
                    record["transmission_succeeded"] = False
                    break
                if following["kind"] in (
                    "received", "buffered", "duplicate", "discard"
                ) and following["frame"] == record["frame"]:
                    record["transmission_succeeded"] = True
                    break
            if record["transmission_succeeded"] is None:
                record["transmission_succeeded"] = True
            if not record["transmission_succeeded"]:
                record["status"] = "Packet loss"

        elif record["kind"] == "ack_generated":
            for following in records[index + 1:]:
                if following["kind"] == "ack_generated":
                    break
                if following["kind"] == "ack_lost" and (
                    following["ack"] == record["ack"]
                ):
                    record["transmission_succeeded"] = False
                    record["status"] = "ACK loss"
                    break
                if following["kind"] == "ack_received" and (
                    following["ack"] == record["ack"]
                ):
                    record["transmission_succeeded"] = True
                    break
            if record["transmission_succeeded"] is None:
                record["transmission_succeeded"] = True

    return records


class AnimationPanel(ttk.Frame):
    """Animate actual protocol events on a scrollable time-ordered diagram."""

    COLORS = theme.COLORS

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="App.TFrame")

        self.header_canvas = tk.Canvas(
            self,
            height=theme.px(104),
            background=self.COLORS["surface"],
            highlightthickness=0,
            bd=0,
        )
        self.header_canvas.pack(fill="x")

        self.explanation_frame = tk.Frame(
            self,
            background=self.COLORS["surface_alt"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=1,
        )
        self.explanation_frame.pack(fill="x", pady=(6, 0))
        self.explanation_frame.bind("<Configure>", self._on_explanation_resize)

        accent_bar = tk.Frame(
            self.explanation_frame,
            background=self.COLORS["primary"],
            width=4,
        )
        accent_bar.pack(side="left", fill="y")
        explanation_inner = tk.Frame(
            self.explanation_frame,
            background=self.COLORS["surface_alt"],
        )
        explanation_inner.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        tk.Label(
            explanation_inner,
            text="WHY THIS STEP",
            background=self.COLORS["surface_alt"],
            foreground=self.COLORS["primary"],
            font=theme.font(7, "bold"),
            anchor="w",
        ).pack(fill="x")
        self.explanation_label = tk.Label(
            explanation_inner,
            text=(
                "Run a simulation to see the protocol's decision explained "
                "at every step."
            ),
            background=self.COLORS["surface_alt"],
            foreground=self.COLORS["body"],
            font=theme.font(9),
            anchor="w",
            justify="left",
            wraplength=700,
        )
        self.explanation_label.pack(fill="x", pady=(3, 0))

        self._build_legend()

        timeline_frame = tk.Frame(self, background=self.COLORS["surface"])
        timeline_frame.pack(fill="both", expand=True, pady=(6, 0))
        self.canvas = tk.Canvas(
            timeline_frame,
            background=self.COLORS["surface"],
            highlightthickness=0,
            bd=0,
            height=30,
        )
        self.scrollbar = ttk.Scrollbar(
            timeline_frame,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.records = []
        self.parameters = {}
        self.protocol = None
        self.current_index = 0
        self.current_record = None
        self.on_event = None
        self.on_complete = None
        self.on_state = None
        self.playback_active = False
        self.paused = False
        self.step_mode = False
        self.after_id = None
        self.marker_ids = ()
        self.marker_x = 0.0
        self.marker_end_x = 0.0
        self.marker_direction = 1
        self.marker_steps = 0
        self.sender_base = 0
        self.receiver_base = 0
        self.received_frames = set()
        self.resize_pending = False

        self.canvas.bind("<Configure>", self._on_configure)
        self._draw_base()

    def _build_legend(self):
        legend = tk.Frame(self, background=self.COLORS["surface"])
        legend.pack(fill="x", pady=(8, 0))
        tk.Label(
            legend,
            text="LEGEND",
            background=self.COLORS["surface"],
            foreground=self.COLORS["faint"],
            font=theme.font(7, "bold"),
        ).pack(side="left", padx=(2, 12))
        items = [
            ("Data frame", self.COLORS["primary"], False, tk.LAST),
            ("ACK", self.COLORS["success"], True, tk.LAST),
            ("Lost", self.COLORS["danger"], False, None),
            ("Retransmission", self.COLORS["warning"], False, tk.LAST),
            ("Discarded", self.COLORS["faint"], True, tk.LAST),
        ]
        for label, color, dashed, arrow in items:
            item = tk.Frame(legend, background=self.COLORS["surface"])
            item.pack(side="left", padx=(0, 16))
            canvas = tk.Canvas(
                item,
                width=32,
                height=12,
                background=self.COLORS["surface"],
                highlightthickness=0,
            )
            canvas.pack(side="left", padx=(0, 5))
            if label == "Lost":
                canvas.create_line(
                    2, 6, 30, 6, fill=color, width=2, dash=(3, 2)
                )
                canvas.create_text(
                    16, 6, text="✕", fill=color, font=theme.font(8, "bold")
                )
            else:
                canvas.create_line(
                    2,
                    6,
                    30,
                    6,
                    fill=color,
                    width=2,
                    dash=(3, 2) if dashed else (),
                    arrow=arrow,
                )
            tk.Label(
                item,
                text=label,
                background=self.COLORS["surface"],
                foreground=self.COLORS["muted"],
                font=theme.font(8),
            ).pack(side="left")

    def _on_explanation_resize(self, event):
        self.explanation_label.configure(wraplength=max(event.width - 150, 240))

    def _layout(self):
        width = max(self.canvas.winfo_width(), 720)
        sender_x = max(130, width * 0.17)
        receiver_x = min(width - 130, width * 0.83)
        return width, sender_x, receiver_x

    def _draw_base(self):
        self.header_canvas.delete("all")
        self.canvas.delete("all")
        width, sender_x, receiver_x = self._layout()
        self.sender_x = sender_x
        self.receiver_x = receiver_x
        self.row_start = theme.px(26)
        self.row_gap = theme.px(50)

        mid = (sender_x + receiver_x) / 2
        protocol = self.protocol
        accent = theme.protocol_accent(protocol) if protocol else self.COLORS["primary"]
        soft = theme.protocol_soft(protocol) if protocol else self.COLORS["primary_soft"]
        display = (
            theme.PROTOCOL_COLORS[protocol]["label"].upper()
            if protocol else "READY TO SIMULATE"
        )
        rule = RULE_SUMMARY.get(
            protocol,
            "Choose a protocol and run a simulation to watch it work.",
        )

        self.protocol_title_id = self.header_canvas.create_text(
            mid,
            theme.px(18),
            text=display,
            fill=accent,
            font=theme.font(10, "bold"),
        )
        self.rule_summary_id = self.header_canvas.create_text(
            mid,
            theme.px(35),
            text=rule,
            fill=self.COLORS["muted"],
            font=theme.font(8),
        )

        self.header_canvas.create_rectangle(
            sender_x - theme.px(82), theme.px(50),
            sender_x + theme.px(82), theme.px(96),
            fill=soft, outline=accent, width=1,
        )
        self.header_canvas.create_text(
            sender_x, theme.px(65),
            text="SENDER",
            fill=accent,
            font=theme.font(9, "bold"),
        )
        self.sender_window_id = self.header_canvas.create_text(
            sender_x, theme.px(82),
            text="window —",
            fill=self.COLORS["body"],
            font=theme.font(8),
        )

        self.header_canvas.create_rectangle(
            receiver_x - theme.px(82), theme.px(50),
            receiver_x + theme.px(82), theme.px(96),
            fill=self.COLORS["success_soft"],
            outline=self.COLORS["success"],
            width=1,
        )
        self.header_canvas.create_text(
            receiver_x, theme.px(65),
            text="RECEIVER",
            fill=self.COLORS["success"],
            font=theme.font(9, "bold"),
        )
        self.receiver_window_id = self.header_canvas.create_text(
            receiver_x, theme.px(82),
            text="expects —",
            fill=self.COLORS["body"],
            font=theme.font(8),
        )

        self.current_status_id = self.header_canvas.create_text(
            mid,
            theme.px(68),
            text="Waiting for a run",
            fill=self.COLORS["muted"],
            font=theme.font(9, "bold"),
        )
        self.header_canvas.create_text(
            mid,
            theme.px(87),
            text="DATA →   ·   ← ACK",
            fill=self.COLORS["faint"],
            font=theme.font(7, "bold"),
        )
        if not self.records:
            hint_y = max(self.canvas.winfo_height() / 2, 90)
            self.canvas.create_text(
                mid,
                hint_y - 8,
                text="No events yet",
                fill=self.COLORS["muted"],
                font=theme.font(11, "bold"),
            )
            self.canvas.create_text(
                mid,
                hint_y + 14,
                text=(
                    "Run a simulation to watch frames travel to the "
                    "receiver and ACKs travel back."
                ),
                fill=self.COLORS["faint"],
                font=theme.font(8),
            )
        self._update_scroll_region()

    def _on_configure(self, _event):
        if self.playback_active:
            self.resize_pending = True
            return
        self._redraw_history()

    def _redraw_history(self):
        current_index = self.current_index
        self._draw_base()
        if self.current_record is not None:
            self.header_canvas.itemconfigure(
                self.current_status_id,
                text=self._status_text(self.current_record),
                fill=self._status_color(self.current_record),
            )
            self._set_explanation(self._explain_record(self.current_record))
        for index, record in enumerate(self.records[:current_index]):
            self._draw_event_row(record, index)
            self._draw_static_event(record, index)
        self._update_window_labels()
        self._update_scroll_region()
        self.resize_pending = False

    def _row_y(self, index):
        return self.row_start + index * self.row_gap

    def _update_scroll_region(self):
        width, _, _ = self._layout()
        row_count = max(
            self.current_index,
            len(self.records) if not self.playback_active else 0,
        )
        content_bottom = (
            self.row_start + row_count * self.row_gap + theme.px(40)
        )
        self.canvas.configure(
            scrollregion=(
                0, 0, width,
                max(self.canvas.winfo_height(), 150, content_bottom)
            )
        )

    def _scroll_to_event(self, index):
        self.canvas.update_idletasks()
        region = self.canvas.cget("scrollregion").split()
        if len(region) != 4:
            return
        content_height = float(region[3])
        viewport_height = max(self.canvas.winfo_height(), 1)
        target_top = max(0, self._row_y(index) - viewport_height / 2)
        self.canvas.yview_moveto(
            min(target_top / max(content_height, 1), 1)
        )

    def _update_window_labels(self):
        frame_count = int(self.parameters.get("frames", 0))
        window_size = int(self.parameters.get("window", 1))
        sender_end = min(self.sender_base + window_size - 1, frame_count - 1)
        if frame_count and self.sender_base < frame_count:
            sender_window = f"window [{self.sender_base}..{sender_end}]"
        elif frame_count:
            sender_window = "window complete"
        else:
            sender_window = "window —"

        protocol = self.protocol or "One-Bit Sliding Window"
        if protocol == "One-Bit Sliding Window":
            receiver_window = f"expects seq {self.receiver_base % 2}"
        else:
            receiver_window = f"expects frame {self.receiver_base}"

        self.header_canvas.itemconfigure(
            self.sender_window_id,
            text=sender_window,
        )
        self.header_canvas.itemconfigure(
            self.receiver_window_id,
            text=receiver_window,
        )

    def _set_explanation(self, text):
        self.explanation_label.configure(text=text)

    def _explain_record(self, record):
        if record is None:
            return ""
        protocol = record.get("protocol") or self.protocol or ""
        kind = record["kind"]
        frame = record["frame"]
        ack = record["ack"]
        attempt = record["attempt"]
        window = int(self.parameters.get("window", 1))

        if kind == "start":
            if protocol == "One-Bit Sliding Window":
                return (
                    "The sender starts with a window of one frame. It will "
                    "send frame 0, wait for its ACK, then send frame 1."
                )
            return (
                f"The sender starts with a window of {window} frames. "
                "Up to that many frames can be unacknowledged at once."
            )
        if kind == "complete":
            return (
                "All frames are delivered. Every lost frame or ACK was "
                "recovered using this protocol's retransmission rule."
            )
        if kind == "data_tx":
            if protocol == "One-Bit Sliding Window":
                if attempt > 1:
                    return (
                        "Stop-and-Wait resends the same frame after a "
                        "timeout. The receiver may see a duplicate and will "
                        "ACK it again."
                    )
                return (
                    f"Stop-and-Wait sends frame {frame} and then stops. "
                    "Because the window is size 1, the next frame cannot "
                    "leave until this frame's ACK returns."
                )
            if protocol == "Go-Back-N":
                if attempt > 1:
                    return (
                        f"Go-Back-N retransmits frame {frame} because the "
                        "timeout rolled the sender back. Every frame from "
                        "the base is sent again, even frames that arrived."
                    )
                return (
                    f"Go-Back-N sends frame {frame} as part of its window. "
                    "The receiver accepts it only if it is the next "
                    "expected frame; later frames are discarded."
                )
            if attempt > 1:
                return (
                    f"Selective Repeat resends only frame {frame}. Frames "
                    "that were already acknowledged stay outside the "
                    "recovery, so no bandwidth is wasted."
                )
            return (
                f"Selective Repeat sends frame {frame}. The receiver can "
                "buffer it and ACK it individually even if earlier frames "
                "are still missing."
            )
        if kind == "data_lost":
            if protocol == "One-Bit Sliding Window":
                return (
                    "The network dropped this frame. The sender will wait "
                    "for its timeout, then send the exact same frame again."
                )
            if protocol == "Go-Back-N":
                return (
                    "The network dropped this frame. Go-Back-N cannot skip "
                    "it: after the timeout, this frame and every frame after "
                    "it in the window are resent."
                )
            return (
                "The network dropped this frame. The receiver will buffer "
                "later frames, and Selective Repeat will resend only this "
                "frame after a timeout."
            )
        if kind == "ack_generated":
            if protocol == "One-Bit Sliding Window":
                return (
                    f"The receiver returns ACK {ack}. Stop-and-Wait uses a "
                    "single alternating bit, so this ACK confirms that the "
                    "sender may move to the next frame."
                )
            if protocol == "Go-Back-N":
                return (
                    f"The receiver returns cumulative ACK {ack}: every "
                    f"frame up to frame {ack} arrived in order. A single "
                    "gap stops later frames from being acknowledged."
                )
            return (
                f"The receiver returns individual ACK {ack}. It confirms "
                f"frame {ack} alone, so missing earlier frames do not block "
                "this acknowledgement."
            )
        if kind == "ack_received":
            if protocol == "One-Bit Sliding Window":
                return (
                    "The ACK reaches the sender. The sender flips its 0/1 "
                    "sequence number and may now send the next frame. Only "
                    "one frame was ever in flight."
                )
            if protocol == "Go-Back-N":
                return (
                    f"The sender receives ACK {ack} and slides its window "
                    "past every frame it covers. Frames behind the base are "
                    "now considered delivered."
                )
            return (
                f"The sender marks frame {ack} as acknowledged. Its window "
                "slides forward once the lowest outstanding frames are all "
                "complete."
            )
        if kind == "ack_lost":
            if protocol == "One-Bit Sliding Window":
                return (
                    "This ACK was dropped. The data arrived, but the sender "
                    "cannot know, so it times out and resends the frame. "
                    "The receiver treats the copy as a duplicate."
                )
            if protocol == "Go-Back-N":
                return (
                    "This ACK was dropped. Go-Back-N depends on cumulative "
                    "ACKs, so the sender's window cannot advance and the "
                    "whole outstanding window will be sent again."
                )
            return (
                "This ACK was dropped. The frame is safely at the receiver, "
                "but after the timeout only this frame will be resent; "
                "later frames keep their acknowledgements."
            )
        if kind == "timeout":
            if protocol == "One-Bit Sliding Window":
                return (
                    "No ACK arrived within the timeout. The sender assumes "
                    "the frame was lost and retransmits the same frame."
                )
            if protocol == "Go-Back-N":
                return (
                    "The timeout fires before a new cumulative ACK arrives. "
                    "The sender goes back to its base and resends the entire "
                    "outstanding window."
                )
            return (
                "The timeout fires for missing ACKs. The sender retransmits "
                "only the unacknowledged frames and leaves acknowledged "
                "frames alone."
            )
        if kind == "retransmit":
            if protocol == "Go-Back-N":
                return (
                    "Recovery begins. Go-Back-N will resend every frame in "
                    "the window starting from the sender's base."
                )
            if protocol == "Selective Repeat":
                return (
                    "Recovery begins. Selective Repeat will resend only the "
                    "frames whose ACKs are still missing."
                )
            return "The sender retransmits the frame that timed out."
        if kind == "received":
            if protocol == "Go-Back-N":
                return (
                    "This is the next expected frame, so the receiver "
                    "accepts it and advances its expected frame number."
                )
            if protocol == "Selective Repeat":
                return (
                    "The frame matches the next expected sequence number, so "
                    "the receiver delivers it and sends its ACK."
                )
            return (
                "The frame matches the expected sequence number, so the "
                "receiver delivers it to the upper layer and prepares an "
                "ACK."
            )
        if kind == "delivered":
            return "The frame is delivered to the application layer."
        if kind == "buffered":
            return (
                "Selective Repeat keeps this out-of-order frame in its "
                "buffer without acknowledging it. When the missing frame "
                "arrives, this frame is delivered and acknowledged then."
            )
        if kind == "duplicate":
            if protocol == "One-Bit Sliding Window":
                return (
                    "The receiver already delivered this frame. It discards "
                    "the copy but sends the ACK again so the sender can "
                    "move on."
                )
            if protocol == "Go-Back-N":
                return (
                    "The receiver has already moved past this frame, so the "
                    "duplicate is discarded. The cumulative ACK still "
                    "reports the highest in-order frame."
                )
            return (
                "The receiver already has this frame, so the duplicate is "
                "discarded. The original ACK may be repeated."
            )
        if kind == "discard":
            if protocol == "Go-Back-N":
                return (
                    "Out-of-order frames are discarded in Go-Back-N. The "
                    "receiver only accepts the next expected frame, so this "
                    "data will be resent later."
                )
            return (
                "The frame is discarded because it is a duplicate or falls "
                "outside the receiver's window."
            )
        if kind == "window":
            if record["window"]:
                start, end = record["window"]
                return (
                    f"The sender's window covers frames {start} to {end}. "
                    "Only these frames may be sent before ACKs move the "
                    "window forward."
                )
            return "The sender's window limits how many frames can be in flight."
        if kind == "window_slide":
            if record["slide"]:
                old, new = record["slide"]
                return (
                    f"ACKs arrived, so the sender's window slides from "
                    f"frame {old} to frame {new}. Acknowledged frames leave "
                    "the window."
                )
            return "The sender's window slides forward after acknowledgements."
        if kind == "ready":
            return "The sender is ready to move on to the next frame."
        return record["event"]

    @staticmethod
    def _status_text(record):
        kind = record["kind"]
        frame = record["frame"]
        ack = record["ack"]
        if kind == "start":
            message = "Simulation started"
        elif kind == "data_tx":
            action = "Retransmitting" if record["attempt"] > 1 else "Sending"
            message = f"{action} frame {frame}"
        elif kind == "data_lost":
            message = f"Frame {frame} lost"
        elif kind == "ack_generated":
            message = f"Sending ACK {ack}"
        elif kind == "ack_lost":
            message = f"ACK {ack} lost"
        elif kind == "ack_received":
            message = f"ACK {ack} received"
        elif kind in ("received", "delivered"):
            message = f"Frame {frame} received"
        elif kind == "buffered":
            message = f"Frame {frame} buffered"
        elif kind in ("duplicate", "discard"):
            message = f"Frame {frame} discarded"
        elif kind == "timeout":
            message = "Timeout"
        elif kind == "retransmit":
            message = "Recovery begins"
        elif kind == "window" and record["window"]:
            message = f"Window {record['window']}"
        elif kind == "window_slide" and record["slide"]:
            message = f"Window slides to {record['slide'][1]}"
        elif kind == "complete":
            message = "Simulation complete"
        else:
            message = record["event"]
        return f"Step {record['step']} · {message}"

    @staticmethod
    def _status_color(record):
        kind = record["kind"]
        if kind in ("data_lost", "ack_lost", "timeout"):
            return theme.COLORS["danger"]
        if kind == "retransmit" or (
            kind == "data_tx" and record["attempt"] > 1
        ):
            return theme.COLORS["warning"]
        if kind in ("duplicate", "discard"):
            return theme.COLORS["muted"]
        if kind in ("received", "delivered", "buffered", "ack_received", "complete"):
            return theme.COLORS["success"]
        if kind == "data_tx":
            return theme.COLORS["primary"]
        if kind == "ack_generated":
            return theme.COLORS["success"]
        return theme.COLORS["body"]

    def _draw_event_row(self, record, index):
        y = self._row_y(index)
        width, _, _ = self._layout()
        is_current = index == self.current_index - 1
        self.canvas.create_rectangle(
            0, y - 23, width, y + 23,
            fill=self.COLORS["surface_tint"] if is_current else "white",
            outline="",
        )
        if is_current:
            self.canvas.create_rectangle(
                0, y - 23, 3, y + 23,
                fill=self.COLORS["primary"],
                outline="",
            )
        self.canvas.create_line(
            0, y + 24, width, y + 24,
            fill=self.COLORS["border"],
            width=1,
        )
        self.canvas.create_line(
            82, y - 23, 82, y + 23,
            fill=self.COLORS["border"],
            width=1,
        )
        self.canvas.create_text(
            14, y - 7, anchor="w",
            text=f"{record['step']:02d}",
            fill=self.COLORS["ink"],
            font=theme.font(9, "bold"),
        )
        self.canvas.create_text(
            14, y + 9, anchor="w",
            text=f"{record['time_ms']:.0f} ms",
            fill=self.COLORS["faint"],
            font=theme.font(7),
        )
        self.canvas.create_line(
            self.sender_x, y, self.sender_x, y + 24,
            fill=self.COLORS["border"],
            width=1,
            dash=(2, 3),
        )
        self.canvas.create_line(
            self.receiver_x, y, self.receiver_x, y + 24,
            fill=self.COLORS["border"],
            width=1,
            dash=(2, 3),
        )

    def _draw_static_event(self, record, index):
        y = self._row_y(index)
        kind = record["kind"]
        frame = record["frame"]
        ack = record["ack"]
        mid = (self.sender_x + self.receiver_x) / 2
        accent = theme.protocol_accent(record["protocol"]) if record["protocol"] else self.COLORS["primary"]

        if kind == "data_tx":
            color = (
                self.COLORS["warning"] if record["attempt"] > 1
                else self.COLORS["primary"]
            )
            target_x = (
                self.sender_x + (self.receiver_x - self.sender_x) * 0.53
                if not record["transmission_succeeded"]
                else self.receiver_x
            )
            self._draw_arrow(
                self.sender_x, y - 9, target_x, y - 9, color,
                f"F{frame}" if frame is not None else "data",
                lost=not record["transmission_succeeded"],
            )
        elif kind == "ack_generated":
            target_x = (
                self.receiver_x - (self.receiver_x - self.sender_x) * 0.53
                if not record["transmission_succeeded"]
                else self.sender_x
            )
            self._draw_arrow(
                self.receiver_x, y + 10, target_x, y + 10,
                self.COLORS["success"],
                f"ACK {ack}" if ack is not None else "ACK",
                dashed=True,
                lost=not record["transmission_succeeded"],
            )
        elif kind == "data_lost":
            self._draw_chip(
                mid, y,
                f"✕  Frame {frame} lost in transit",
                self.COLORS["danger"],
                self.COLORS["danger_soft"],
            )
        elif kind == "ack_lost":
            self._draw_chip(
                mid, y,
                f"✕  ACK {ack} lost on the way back",
                self.COLORS["danger"],
                self.COLORS["danger_soft"],
            )
        elif kind in ("received", "delivered", "buffered"):
            if kind == "buffered":
                label = f"Frame {frame} buffered"
            elif kind == "delivered":
                label = f"Frame {frame} delivered"
            else:
                label = f"Frame {frame} received"
            self._draw_chip(
                self.receiver_x, y,
                f"✓  {label}",
                self.COLORS["success"],
                self.COLORS["success_soft"],
            )
        elif kind in ("duplicate", "discard"):
            self._draw_chip(
                self.receiver_x, y,
                f"✕  Frame {frame} discarded",
                self.COLORS["muted"],
                self.COLORS["slate_soft"],
            )
        elif kind == "ack_received":
            self._draw_chip(
                self.sender_x, y,
                f"✓  ACK {ack} received",
                self.COLORS["success"],
                self.COLORS["success_soft"],
            )
        elif kind == "timeout":
            self._draw_chip(
                mid, y,
                "TIMEOUT  ·  no ACK arrived",
                self.COLORS["danger"],
                self.COLORS["danger_soft"],
            )
        elif kind == "retransmit":
            self._draw_chip(
                mid, y,
                "Recovery begins",
                self.COLORS["warning"],
                self.COLORS["warning_soft"],
            )
        elif kind == "window":
            if record["window"]:
                start, end = record["window"]
                label = f"Sender window [{start}..{end}]"
            else:
                label = "Sender window updated"
            self._draw_chip(
                mid, y,
                label,
                accent,
                theme.protocol_soft(record["protocol"]) if record["protocol"] else self.COLORS["primary_soft"],
            )
        elif kind == "window_slide" and record["slide"]:
            self._draw_chip(
                mid, y,
                f"Window slides {record['slide'][0]} → {record['slide'][1]}",
                accent,
                theme.protocol_soft(record["protocol"]) if record["protocol"] else self.COLORS["primary_soft"],
            )
        elif kind in ("start", "complete"):
            if kind == "start":
                label = "SIMULATION STARTED"
                color = self.COLORS["muted"]
                background = self.COLORS["slate_soft"]
            else:
                label = "SIMULATION COMPLETE"
                color = self.COLORS["success"]
                background = self.COLORS["success_soft"]
            self._draw_chip(mid, y, label, color, background)

    def _draw_chip(self, x, y, text, foreground, background):
        item = self.canvas.create_text(
            x, y,
            text=text,
            fill=foreground,
            font=theme.font(8, "bold"),
        )
        bbox = self.canvas.bbox(item)
        if bbox:
            rectangle = self.canvas.create_rectangle(
                bbox[0] - 10, bbox[1] - 4,
                bbox[2] + 10, bbox[3] + 4,
                fill=background,
                outline="",
            )
            self.canvas.tag_lower(rectangle, item)

    def _draw_arrow(self, start_x, y, end_x, end_y, color, label, dashed=False, lost=False):
        self.canvas.create_line(
            start_x, y, end_x, end_y,
            fill=color, width=2,
            dash=(4, 3) if dashed else (),
            arrow=tk.LAST,
        )
        label_x = (start_x + end_x) / 2
        label_y = y - 12
        item = self.canvas.create_text(
            label_x, label_y,
            text=label,
            fill=color,
            font=theme.font(8, "bold"),
        )
        bbox = self.canvas.bbox(item)
        if bbox:
            background = self.canvas.create_rectangle(
                bbox[0] - 5, bbox[1] - 1,
                bbox[2] + 5, bbox[3] + 1,
                fill="white",
                outline="",
            )
            self.canvas.tag_lower(background, item)
        if lost:
            self.canvas.create_text(
                end_x, end_y,
                text="✕",
                fill=self.COLORS["danger"],
                font=theme.font(11, "bold"),
            )

    def play(
        self, events, protocol=None, parameters=None, on_event=None,
        on_complete=None, on_state=None
    ):
        self.reset()
        if protocol is None:
            source = "\n".join(events).lower()
            if "selective repeat" in source:
                protocol = "Selective Repeat"
            elif "go-back-n" in source:
                protocol = "Go-Back-N"
            else:
                protocol = "One-Bit Sliding Window"
        if parameters is None:
            frame_numbers = [
                int(match.group(1))
                for event in events
                for match in [_FRAME_PATTERN.search(event)]
                if match is not None
            ]
            parameters = {
                "frames": max(frame_numbers, default=0) + 1,
                "window": 1,
                "transmission": 1,
                "ack": 1,
                "timeout": 1,
            }
        self.protocol = protocol
        self.records = normalize_events(events, protocol, parameters)
        self.parameters = parameters
        self.on_event = on_event
        self.on_complete = on_complete
        self.on_state = on_state
        self.playback_active = True
        self.paused = False
        self.step_mode = False
        self._draw_base()
        self._update_window_labels()
        if self.on_state:
            self.on_state("Running")
        self._process_next()

    def reset(self):
        self._cancel_scheduled()
        self.records = []
        self.parameters = {}
        self.protocol = None
        self.current_index = 0
        self.current_record = None
        self.playback_active = False
        self.paused = False
        self.step_mode = False
        self.marker_ids = ()
        self.sender_base = 0
        self.receiver_base = 0
        self.received_frames.clear()
        self.resize_pending = False
        self.on_event = None
        self.on_complete = None
        self.on_state = None
        self._set_explanation(
            "Run a simulation to see the protocol's decision explained at "
            "every step."
        )
        self._draw_base()

    def pause(self):
        if not self.playback_active:
            return
        self.paused = True
        self._cancel_scheduled()
        self.header_canvas.itemconfigure(
            self.current_status_id,
            text="Paused · press Resume or Step Forward",
            fill=self.COLORS["warning"],
        )
        if self.on_state:
            self.on_state("Paused")

    def resume(self):
        if not self.playback_active:
            return
        self.paused = False
        self.step_mode = False
        if self.on_state:
            self.on_state("Running")
        if self.marker_ids:
            self._animate_marker()
        else:
            self._schedule(0, self._process_next)

    def step_forward(self):
        if not self.playback_active:
            return
        self.paused = False
        self.step_mode = True
        if self.on_state:
            self.on_state("Stepping")
        if self.marker_ids:
            self._animate_marker()
        else:
            self._process_next()

    def _process_next(self):
        self.after_id = None
        if self.paused or not self.playback_active:
            return
        if self.current_index >= len(self.records):
            self._complete()
            return

        record = self.records[self.current_index]
        self.current_record = record
        self.current_index += 1
        if self.on_event:
            self.on_event(record)
        self._prepare_record(record)
        self._draw_event_row(record, self.current_index - 1)
        self._update_scroll_region()
        self._scroll_to_event(self.current_index - 1)

        if record["kind"] in ("data_tx", "ack_generated"):
            self._start_marker(record, self.current_index - 1)
        else:
            self._finish_current()

    def _prepare_record(self, record):
        if record["kind"] == "window" and record["window"]:
            self.sender_base = record["window"][0]
        elif record["kind"] == "window_slide" and record["slide"]:
            self.sender_base = record["slide"][1]
        elif (
            record["kind"] == "data_tx"
            and record["attempt"] == 1
            and record["protocol"] == "One-Bit Sliding Window"
        ):
            self.sender_base = record["frame"] or 0
        elif (
            record["kind"] == "ack_received"
            and record["protocol"] == "One-Bit Sliding Window"
        ):
            self.sender_base += 1

        if record["kind"] == "received" and record["frame"] is not None:
            self.received_frames.add(record["frame"])
            while self.receiver_base in self.received_frames:
                self.receiver_base += 1
        elif record["kind"] == "buffered" and record["frame"] is not None:
            self.received_frames.add(record["frame"])
            while self.receiver_base in self.received_frames:
                self.receiver_base += 1

        self._update_window_labels()
        self.header_canvas.itemconfigure(
            self.current_status_id,
            text=self._status_text(record),
            fill=self._status_color(record),
        )
        self._set_explanation(self._explain_record(record))

    def _start_marker(self, record, index):
        y = self._row_y(index)
        is_data = record["kind"] == "data_tx"
        start_x = self.sender_x if is_data else self.receiver_x
        end_x = self.receiver_x if is_data else self.sender_x
        failed = not record["transmission_succeeded"]
        if failed:
            progress = 0.53
            end_x = start_x + (end_x - start_x) * progress

        color = (
            self.COLORS["warning"]
            if is_data and record["attempt"] > 1
            else self.COLORS["primary"] if is_data
            else self.COLORS["success"]
        )
        label = (
            f"F{record['frame']}" if is_data
            else f"ACK {record['ack']}"
        )
        line_y = y - 9 if is_data else y + 10
        line = self.canvas.create_line(
            start_x, line_y, start_x, line_y,
            fill=color, width=2,
            dash=(4, 3) if not is_data else (),
            arrow=tk.LAST,
        )
        marker = self.canvas.create_rectangle(
            start_x - 18, line_y - 10,
            start_x + 18, line_y + 10,
            fill=color,
            outline=color,
        )
        text = self.canvas.create_text(
            start_x, line_y, text=label, fill="white",
            font=theme.font(7, "bold"),
        )
        self.marker_ids = (line, marker, text)
        self.marker_x = start_x
        self.marker_end_x = end_x
        self.marker_direction = 1 if end_x >= start_x else -1
        distance = abs(end_x - start_x)
        self.marker_steps = max(8, min(30, int(distance / 20)))
        self._animate_marker()

    def _animate_marker(self):
        if self.paused or not self.marker_ids:
            return
        line, marker, text = self.marker_ids
        self.marker_x += (
            self.marker_end_x - self.marker_x
        ) / max(self.marker_steps, 1)
        is_data = self.current_record["kind"] == "data_tx"
        line_y = (
            self._row_y(self.current_index - 1) - 9
            if is_data
            else self._row_y(self.current_index - 1) + 10
        )
        self.canvas.coords(
            line, self.sender_x if self.marker_direction > 0 else self.receiver_x,
            line_y, self.marker_x, line_y
        )
        self.canvas.coords(
            marker, self.marker_x - 18, line_y - 10,
            self.marker_x + 18, line_y + 10
        )
        self.canvas.coords(text, self.marker_x, line_y)

        if abs(self.marker_end_x - self.marker_x) < 2:
            self.marker_x = self.marker_end_x
            self.canvas.coords(
                line,
                self.sender_x if self.marker_direction > 0 else self.receiver_x,
                line_y, self.marker_end_x, line_y
            )
            for item_id in self.marker_ids:
                self.canvas.delete(item_id)
            self.marker_ids = ()
            self._finish_current()
            return

        self.marker_steps -= 1
        self._schedule(16, self._animate_marker)

    def _finish_current(self):
        if self.resize_pending:
            self._redraw_history()
        else:
            self._draw_static_event(self.current_record, self.current_index - 1)
        self.marker_ids = ()
        if self.step_mode:
            self.paused = True
            self.header_canvas.itemconfigure(
                self.current_status_id,
                text=f"Paused after step {self.current_record['step']}",
                fill=self.COLORS["warning"],
            )
            if self.on_state:
                self.on_state("Paused")
            return
        self._schedule(120, self._process_next)

    def _complete(self):
        self.playback_active = False
        self.paused = False
        self.header_canvas.itemconfigure(
            self.current_status_id,
            text="Simulation complete",
            fill=self.COLORS["success"],
        )
        if self.current_index:
            self._scroll_to_event(self.current_index - 1)
        if self.on_state:
            self.on_state("Completed")
        if self.on_complete:
            self.on_complete()

    def draw_network(self):
        """Retain the original redraw entry point for existing callers."""
        self._draw_base()

    def animate_next(self):
        """Retain the original event-advance entry point."""
        self._process_next()

    def animate_packet(self, event, is_ack=False):
        """Retain direct packet-animation calls from earlier panel clients."""
        protocol = (
            self.records[0]["protocol"]
            if self.records else "One-Bit Sliding Window"
        )
        parameters = self.parameters or {
            "frames": 1,
            "window": 1,
            "transmission": 1,
            "ack": 1,
            "timeout": 1,
        }
        records = normalize_events([event], protocol, parameters)
        if not records:
            return
        record = records[0]
        if is_ack:
            record["kind"] = "ack_generated"
            record["transmission_succeeded"] = True
        elif record["kind"] != "data_tx":
            return
        self.records.append(record)
        self.current_record = record
        self.current_index = len(self.records)
        self.playback_active = True
        self.paused = False
        self._draw_event_row(record, self.current_index - 1)
        self._start_marker(record, self.current_index - 1)

    def show_loss(self, event):
        """Retain the original loss-indicator entry point."""
        y = self._row_y(max(self.current_index - 1, 0))
        width, _, _ = self._layout()
        self.canvas.create_text(
            width / 2, y, text=f"✕ {event}",
            fill=self.COLORS["danger"], font=theme.font(9, "bold")
        )

    def root_after(self, delay, callback):
        """Retain the original Tkinter scheduling helper."""
        return self.after(delay, callback)

    def _schedule(self, delay, callback):
        if self.paused or not self.playback_active:
            return
        self._cancel_scheduled()
        self.after_id = self.after(delay, callback)

    def _cancel_scheduled(self):
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

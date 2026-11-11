"""Shared visual language for the simulator interface."""

import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg": "#F1F5F9",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFC",
    "surface_tint": "#EFF6FF",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "ink": "#0F172A",
    "body": "#334155",
    "muted": "#64748B",
    "faint": "#94A3B8",
    "navy": "#0B1220",
    "navy_soft": "#16213B",
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "primary_soft": "#DBEAFE",
    "success": "#059669",
    "success_dark": "#047857",
    "success_soft": "#D1FAE5",
    "warning": "#D97706",
    "warning_soft": "#FEF3C7",
    "danger": "#DC2626",
    "danger_soft": "#FEE2E2",
    "info": "#0284C7",
    "info_soft": "#E0F2FE",
    "indigo": "#4F46E5",
    "indigo_soft": "#E0E7FF",
    "slate_soft": "#F1F5F9",
}

PROTOCOL_COLORS = {
    "One-Bit Sliding Window": {
        "accent": "#4F46E5",
        "soft": "#E0E7FF",
        "label": "Stop-and-Wait",
    },
    "Go-Back-N": {
        "accent": "#0284C7",
        "soft": "#E0F2FE",
        "label": "Go-Back-N",
    },
    "Selective Repeat": {
        "accent": "#059669",
        "soft": "#D1FAE5",
        "label": "Selective Repeat",
    },
}

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"

SCALE = 1.0


def set_scale(scale):
    """Record the display scale so pixel sizes track the DPI scaled fonts."""
    global SCALE
    SCALE = max(float(scale), 1.0)


def px(value):
    """Scale a pixel dimension for the current display scale."""
    return int(round(value * SCALE))


def font(size=10, weight="normal", family=FONT_FAMILY):
    """Return a Tk font tuple in the application typeface."""
    return (family, size, weight)


def protocol_accent(protocol):
    """Return the accent colour for a protocol name."""
    return PROTOCOL_COLORS.get(protocol, {}).get("accent", COLORS["primary"])


def protocol_soft(protocol):
    """Return the soft tint colour for a protocol name."""
    return PROTOCOL_COLORS.get(protocol, {}).get("soft", COLORS["primary_soft"])


class Tooltip:
    """Small delayed help popup for a widget."""

    def __init__(self, widget, text, delay=450):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.window = None
        self.after_id = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self.window is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        frame = tk.Frame(
            self.window,
            background=COLORS["navy"],
            padx=10,
            pady=7,
        )
        frame.pack()
        tk.Label(
            frame,
            text=self.text,
            background=COLORS["navy"],
            foreground="#E2E8F0",
            font=font(8),
            justify="left",
            wraplength=280,
        ).pack()

    def _hide(self, _event=None):
        self._cancel()
        if self.window is not None:
            self.window.destroy()
            self.window = None

    def _cancel(self):
        if self.after_id is not None:
            try:
                self.widget.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None


def apply_theme(root):
    """Configure ttk styles used across the application."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "App.TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "App.TNotebook.Tab",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        padding=(px(20), px(11)),
        font=font(9, "bold"),
        borderwidth=0,
    )
    style.map(
        "App.TNotebook.Tab",
        background=[("selected", COLORS["surface"])],
        foreground=[("selected", COLORS["primary"])],
    )

    style.configure(
        "Field.TEntry",
        fieldbackground=COLORS["surface"],
        foreground=COLORS["ink"],
        bordercolor=COLORS["border_strong"],
        lightcolor=COLORS["border_strong"],
        darkcolor=COLORS["border_strong"],
        insertcolor=COLORS["ink"],
        padding=(px(8), px(7)),
        relief="flat",
    )
    style.map(
        "Field.TEntry",
        bordercolor=[("focus", COLORS["primary"])],
        lightcolor=[("focus", COLORS["primary"])],
        darkcolor=[("focus", COLORS["primary"])],
    )
    style.configure(
        "Field.TCombobox",
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        foreground=COLORS["ink"],
        bordercolor=COLORS["border_strong"],
        lightcolor=COLORS["border_strong"],
        darkcolor=COLORS["border_strong"],
        arrowcolor=COLORS["muted"],
        padding=(px(8), px(7)),
        relief="flat",
    )
    style.map(
        "Field.TCombobox",
        bordercolor=[("focus", COLORS["primary"])],
        lightcolor=[("focus", COLORS["primary"])],
        darkcolor=[("focus", COLORS["primary"])],
        fieldbackground=[("readonly", COLORS["surface"])],
        selectbackground=[("readonly", COLORS["surface"])],
        selectforeground=[("readonly", COLORS["ink"])],
    )

    style.configure(
        "App.Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["body"],
        borderwidth=0,
        rowheight=px(30),
        font=font(9),
    )
    style.map(
        "App.Treeview",
        background=[("selected", COLORS["primary_soft"])],
        foreground=[("selected", COLORS["primary_dark"])],
    )
    style.configure(
        "App.Treeview.Heading",
        background=COLORS["slate_soft"],
        foreground=COLORS["muted"],
        font=font(8, "bold"),
        padding=(px(8), px(8)),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "App.Treeview.Heading",
        background=[("active", COLORS["border"])],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["border_strong"],
        troughcolor=COLORS["surface_alt"],
        bordercolor=COLORS["surface_alt"],
        arrowcolor=COLORS["muted"],
        width=px(11),
    )


def make_card(
    parent,
    title=None,
    subtitle=None,
    accent=None,
    padding=16,
    wrap=680,
):
    """Create a bordered white card and return (outer_frame, content_frame)."""
    padding = px(padding)
    outer = tk.Frame(
        parent,
        background=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        bd=0,
    )
    if accent is not None:
        tk.Frame(outer, background=accent, height=px(3)).pack(fill="x")
    inner = tk.Frame(outer, background=COLORS["surface"])
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    if title is not None:
        tk.Label(
            inner,
            text=title,
            background=COLORS["surface"],
            foreground=COLORS["ink"],
            font=font(10, "bold"),
            anchor="w",
        ).pack(fill="x")
    if subtitle is not None:
        tk.Label(
            inner,
            text=subtitle,
            background=COLORS["surface"],
            foreground=COLORS["muted"],
            font=font(8),
            anchor="w",
            justify="left",
            wraplength=px(wrap),
        ).pack(fill="x", pady=(2, 0))
    body = tk.Frame(inner, background=COLORS["surface"])
    body.pack(fill="both", expand=True, pady=(10 if title else 0, 0))
    return outer, body


def make_button(parent, text, command, kind="primary", compact=False, width=None):
    """Create a flat, colour-consistent action button."""
    palettes = {
        "primary": (
            COLORS["primary"],
            "white",
            COLORS["primary_dark"],
            COLORS["primary_dark"],
        ),
        "success": (
            COLORS["success"],
            "white",
            COLORS["success_dark"],
            COLORS["success_dark"],
        ),
        "secondary": (
            "#E8EDF5",
            COLORS["ink"],
            "#DCE3EE",
            COLORS["ink"],
        ),
        "ghost": (
            COLORS["surface"],
            COLORS["muted"],
            COLORS["surface_alt"],
            COLORS["ink"],
        ),
        "danger": (
            COLORS["danger_soft"],
            COLORS["danger"],
            "#FECACA",
            COLORS["danger"],
        ),
    }
    background, foreground, active_background, active_foreground = (
        palettes.get(kind, palettes["primary"])
    )
    options = {
        "text": text,
        "command": command,
        "background": background,
        "foreground": foreground,
        "activebackground": active_background,
        "activeforeground": active_foreground,
        "disabledforeground": COLORS["faint"],
        "relief": "flat",
        "borderwidth": 0,
        "highlightthickness": 0,
        "font": font(9, "bold"),
        "padx": px(14),
        "pady": px(6) if compact else px(9),
        "cursor": "hand2",
        "anchor": "center",
    }
    if width is not None:
        options["width"] = width
    return tk.Button(parent, **options)


def make_pill(parent, text, foreground, background, size=8):
    """Create a small status pill label."""
    return tk.Label(
        parent,
        text=text,
        background=background,
        foreground=foreground,
        font=font(size, "bold"),
        padx=px(9),
        pady=px(3),
    )


def make_rule_row(parent, label, value, accent):
    """Create a labelled row used by the method summaries."""
    row = tk.Frame(parent, background=COLORS["surface"])
    row.pack(fill="x", pady=2)
    tk.Label(
        row,
        text="●",
        background=COLORS["surface"],
        foreground=accent,
        font=font(7),
    ).pack(side="left", padx=(0, px(7)))
    tk.Label(
        row,
        text=label,
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=font(8),
        width=8,
        anchor="w",
    ).pack(side="left")
    tk.Label(
        row,
        text=value,
        background=COLORS["surface"],
        foreground=COLORS["body"],
        font=font(8, "bold"),
        anchor="w",
        justify="left",
    ).pack(side="left", fill="x", expand=True)
    return row


class ScrollFrame(ttk.Frame):
    """Vertically scrollable container for sidebars and guide content."""

    def __init__(self, parent, background=None):
        super().__init__(parent, style="App.TFrame")
        self.background = background or COLORS["bg"]
        self.canvas = tk.Canvas(
            self,
            background=self.background,
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.body = tk.Frame(self.canvas, background=self.background)
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.body, anchor="nw"
        )
        self.body.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_content_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        try:
            widget = self.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            widget = None
        while widget is not None:
            if isinstance(widget, (ttk.Treeview, tk.Text, tk.Listbox)):
                return
            if widget == self.canvas or widget == self.body:
                self.canvas.yview_scroll(int(-event.delta / 120), "units")
                return
            widget = widget.master

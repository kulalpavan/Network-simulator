"""High-DPI support so the interface renders crisply on scaled displays."""

import sys

import tkinter as tk


BASE_DPI = 96.0


def enable_high_dpi() -> None:
    """Mark the process as DPI aware before the Tk root is created.

    Windows otherwise treats the window as DPI unaware, stretches the bitmap
    to match the display scale, and every glyph turns blurry.
    """
    if sys.platform != "win32":
        return

    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return
    except (AttributeError, OSError):
        pass

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def _screen_dpi(root: tk.Tk) -> float:
    """Return the display DPI in physical pixels per inch."""
    if sys.platform == "win32":
        import ctypes

        try:
            return float(ctypes.windll.user32.GetDpiForSystem())
        except (AttributeError, OSError):
            pass

        try:
            dc = ctypes.windll.user32.GetDC(0)
            try:
                return float(ctypes.windll.gdi32.GetDeviceCaps(dc, 88))
            finally:
                ctypes.windll.user32.ReleaseDC(0, dc)
        except (AttributeError, OSError):
            pass

    try:
        return float(root.winfo_fpixels("1i"))
    except tk.TclError:
        return BASE_DPI


def apply_dpi_scaling(root: tk.Tk) -> float:
    """Match Tk's point-to-pixel scaling to the screen DPI.

    Returns the layout scale factor (1.0 at 100% display scaling) so pixel
    based dimensions can be scaled to match the now larger point sized fonts.
    """
    dpi = _screen_dpi(root)
    if dpi < BASE_DPI:
        dpi = BASE_DPI

    root.tk.call("tk", "scaling", dpi / 72.0)
    return dpi / BASE_DPI

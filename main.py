"""Application entry point for the Sliding Window Protocol Simulator."""

from gui.dpi import enable_high_dpi
from gui.main_window import MainWindow


def main() -> None:
    """Create and run the application window."""
    enable_high_dpi()
    MainWindow().run()


if __name__ == "__main__":
    main()

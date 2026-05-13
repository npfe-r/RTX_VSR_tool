import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from main_window import MainWindow


def _check_deps():
    """Run startup dependency check; return True if all OK."""
    try:
        from check_deps import check_dependencies, show_dialog_if_missing
        results = check_dependencies()
        return show_dialog_if_missing(results)
    except Exception:
        return True  # don't block startup on check failure


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RTX 视频超分辨率工具")

    _check_deps()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

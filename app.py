import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, QObject, pyqtSignal

from main_window import MainWindow


class DepChecker(QObject):
    """Run dependency check in a background thread so the UI never freezes."""
    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        if os.environ.get("RTX_BUILD") == "full":
            self.done.emit(None)
            return
        try:
            from check_deps import check_dependencies
            results = check_dependencies()
            self.done.emit(results)
        except Exception as e:
            self.failed.emit(str(e))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RTX 视频超分辨率工具")

    window = MainWindow()
    window.show()

    thread = QThread()
    checker = DepChecker()
    checker.moveToThread(thread)
    thread.started.connect(checker.run)
    checker.done.connect(thread.quit)
    checker.done.connect(window._on_dep_check_done)
    checker.failed.connect(thread.quit)
    checker.failed.connect(window._on_dep_check_failed)
    thread.finished.connect(checker.deleteLater)
    thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

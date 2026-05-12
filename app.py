import sys
import logging
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from theme import load_stylesheet


def main():
    logging.basicConfig(level=logging.WARNING)

    app = QApplication(sys.argv)
    app.setApplicationName("RTX 视频超分辨率工具")
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

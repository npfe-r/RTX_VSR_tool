import sys
import os

from PyQt6.QtWidgets import QApplication

from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RTX 视频超分辨率工具")

    # For non-full builds, check dependencies before showing the window.
    # If any are missing, show the dialog and exit immediately.
    if os.environ.get("RTX_BUILD") != "full":
        try:
            from check_deps import check_dependencies, show_dialog_if_missing
            if not show_dialog_if_missing(check_dependencies()):
                sys.exit(1)
                return
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                None, "依赖检查失败",
                f"无法完成依赖检查，部分功能可能不可用：\n\n{e}\n\n"
                "请确认 torch / nvvfx / opencv-python 已正确安装。"
            )
            sys.exit(1)
            return

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

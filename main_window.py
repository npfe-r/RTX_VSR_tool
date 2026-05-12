import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                              QVBoxLayout, QSplitter, QMessageBox, QSizeGrip)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QAction, QDesktopServices, QActionGroup
from PyQt6.QtCore import QUrl

from file_bar import FileBar
from video_panel import VideoPanel
from param_panel import ParamPanel
from bottom_bar import BottomBar
from title_bar import TitleBar
from worker import WorkerThread
from utils import get_video_info


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTX 视频超分辨率工具")
        self.setMinimumSize(960, 600)
        self.resize(1200, 800)

        # Frameless window with native rounded corners (Win 11)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._enable_rounded_corners()

        self._worker = None
        self._last_output_path = ""

        self._setup_ui()
        self._connect_signals()
        self._load_settings()

    def _enable_rounded_corners(self):
        try:
            import ctypes
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            hwnd = int(self.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTX 视频超分辨率工具")
        self.setMinimumSize(960, 600)
        self.resize(1200, 800)

        self._worker = None
        self._last_output_path = ""

        self._setup_menu()
        self._setup_ui()
        self._connect_signals()
        self._load_settings()

    def _setup_menu(self):
        menubar = self.menuBar()
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        menubar.addAction(about_action)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar (replaces Windows native)
        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)

        # File bar
        self.file_bar = FileBar()
        main_layout.addWidget(self.file_bar)

        # Splitter: video panel | param panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.video_panel = VideoPanel()
        self.param_panel = ParamPanel()
        splitter.addWidget(self.video_panel)
        splitter.addWidget(self.param_panel)
        splitter.setStretchFactor(0, 55)
        splitter.setStretchFactor(1, 45)
        main_layout.addWidget(splitter, 1)

        # Bottom bar
        self.bottom_bar = BottomBar()
        main_layout.addWidget(self.bottom_bar)

        # Resize grip for bottom-right corner
        grip = QSizeGrip(self)
        grip.resize(16, 16)
        grip.setStyleSheet("background: transparent;")

    def _connect_signals(self):
        self.file_bar.input_changed.connect(self._on_input_changed)
        self.bottom_bar.start_clicked.connect(self._start_processing)
        self.bottom_bar.pause_clicked.connect(self._toggle_pause)
        self.bottom_bar.stop_clicked.connect(self._stop_processing)
        self.bottom_bar.open_output_clicked.connect(self._open_output_dir)
        self.bottom_bar.preview_clicked.connect(self._preview_output)
        self.title_bar.about_requested.connect(self._show_about)

    def _on_input_changed(self, path: str):
        if not path or not Path(path).exists():
            self.video_panel.clear_info()
            self.bottom_bar.show_ready()
            self.bottom_bar.btn_start.setEnabled(False)
            return

        info = get_video_info(path)
        if info is None:
            self.bottom_bar.show_error("无法读取视频文件")
            return

        filename = Path(path).name
        self.video_panel.set_info(info, filename)
        if info["thumbnail"] is not None:
            self.video_panel.set_thumbnail(info["thumbnail"])

        # Auto-set output dir if empty
        if not self.file_bar.get_output_path():
            self.file_bar.set_output_path(str(Path(path).parent))

        self.bottom_bar.show_ready()

    def _start_processing(self):
        input_path = self.file_bar.get_input_path()
        if not input_path or not Path(input_path).exists():
            return

        output_dir = self.file_bar.get_output_path()
        if not output_dir:
            output_dir = str(Path(input_path).parent)

        in_name = Path(input_path).stem
        container = self.param_panel.get_params()["container_fmt"]
        out_path = str(Path(output_dir) / f"{in_name}_enhanced.{container}")

        if Path(out_path).exists():
            reply = QMessageBox.question(
                self, "文件已存在",
                f"输出文件已存在:\n{out_path}\n\n是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self._last_output_path = out_path
        params = self.param_panel.get_params()
        self._save_settings()

        self._worker = WorkerThread(input_path, out_path, params)
        self._worker.progress_updated.connect(self.bottom_bar.update_progress)
        self._worker.status_message.connect(self._on_status_message)
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.error_occurred.connect(self._on_processing_error)

        self.bottom_bar.show_processing()
        self.param_panel.setEnabled(False)
        self.file_bar.btn_input.setEnabled(False)
        self.file_bar.btn_output.setEnabled(False)

        self._worker.start()

    def _on_status_message(self, msg: str):
        self.bottom_bar.status_label.setText(msg)

    def _toggle_pause(self):
        if self._worker:
            if self._worker.is_paused:
                self._worker.resume()
            else:
                self._worker.pause()

    def _stop_processing(self):
        if not self._worker:
            return
        reply = QMessageBox.question(
            self, "确认停止",
            "确定要停止处理吗？当前进度不会保存。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._worker.cancel()
            self._worker.wait(5000)
            self._reset_after_stop()

    def _on_processing_finished(self, total_frames: int, elapsed: float):
        self.bottom_bar.show_finished(total_frames, elapsed, self._last_output_path)
        self._reset_controls_enabled()

    def _on_processing_error(self, msg: str):
        self.bottom_bar.show_error(msg)
        self._reset_controls_enabled()

    def _reset_after_stop(self):
        self.bottom_bar.show_ready()
        self._reset_controls_enabled()

    def _reset_controls_enabled(self):
        self.param_panel.setEnabled(True)
        self.file_bar.btn_input.setEnabled(True)
        self.file_bar.btn_output.setEnabled(True)
        self._worker = None

    def _open_output_dir(self):
        if self._last_output_path:
            dir_path = str(Path(self._last_output_path).parent)
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def _preview_output(self):
        if not self._last_output_path or not Path(self._last_output_path).exists():
            return
        fsize = Path(self._last_output_path).stat().st_size
        if fsize < 500 * 1024 * 1024:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._last_output_path))
        else:
            QMessageBox.information(
                self, "文件较大",
                f"输出文件较大 ({fsize / 1024 / 1024:.0f} MB)，请在资源管理器中播放。"
            )

    def _show_about(self):
        QMessageBox.about(
            self, "关于",
            "RTX 视频超分辨率工具\n\n"
            "基于 NVIDIA VFX SDK 的 AI 视频增强工具\n"
            "支持超分辨率放大、降噪、去模糊\n\n"
            "技术栈: PyQt6 · PyTorch · NVIDIA VFX SDK 1.2.0"
        )

    # ---------- Settings persistence ----------

    def _save_settings(self):
        s = QSettings()
        params = self.param_panel.get_params()
        for key in ("output_mode", "custom_w", "custom_h", "container_fmt",
                     "fps_override", "quality_label", "codec_label",
                     "crf", "preset"):
            s.setValue(key, params[key])
        s.setValue("output_dir", self.file_bar.get_output_path())
        s.setValue("window_geometry", self.saveGeometry())
        s.setValue("window_state", self.saveState())

    def _load_settings(self):
        s = QSettings()
        params = {}
        for key in ("output_mode", "custom_w", "custom_h", "container_fmt",
                     "fps_override", "quality_label", "codec_label",
                     "crf", "preset"):
            val = s.value(key)
            if val is not None:
                # QSettings returns int for ints, str for strs automatically
                params[key] = val
        if params:
            self.param_panel.set_params(params)

        out_dir = s.value("output_dir", "")
        if out_dir:
            self.file_bar.set_output_path(out_dir)

        geo = s.value("window_geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        state = s.value("window_state")
        if state is not None:
            self.restoreState(state)

    def closeEvent(self, event):
        s = QSettings()
        s.setValue("window_geometry", self.saveGeometry())
        s.setValue("window_state", self.saveState())
        super().closeEvent(event)

from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QProgressBar, QLabel,
                              QMessageBox, QFrame, QStatusBar)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from widgets import FileBar, VideoPanel, ParamPanel
from worker import WorkerThread
from utils import get_video_info, fmt_time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTX 视频超分辨率工具")
        self.setMinimumSize(960, 600)
        self.resize(960, 600)

        self._worker = None
        self._last_output_path = ""

        self._setup_ui()
        self._connect_signals()
        self._load_settings()

    # ── UI Setup ──────────────────────────────────────────────────
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # File bar
        self.file_bar = FileBar()
        layout.addWidget(self.file_bar)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        # Middle area: video panel | param panel (equal width)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(0)
        self.video_panel = VideoPanel()
        self.param_panel = ParamPanel()
        middle_layout.addWidget(self.video_panel, 1)
        # Vertical separator
        vsep = QFrame()
        vsep.setFrameShape(QFrame.Shape.VLine)
        vsep.setFrameShadow(QFrame.Shadow.Sunken)
        middle_layout.addWidget(vsep)
        middle_layout.addWidget(self.param_panel, 1)
        layout.addLayout(middle_layout, 1)

        # Separator
        sep_pb = QFrame()
        sep_pb.setFrameShape(QFrame.Shape.HLine)
        sep_pb.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep_pb)

        # Status label above progress bar (centered)
        self.status_label = QLabel("就绪 — 选择视频文件后点击开始处理")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Separator
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep3)

        # Status bar — static project info
        status = QStatusBar()
        status.setSizeGripEnabled(False)
        status_label = QLabel("RTX 视频超分辨率工具  v1.0.0  |  PyTorch · NVIDIA VFX SDK")
        status.addWidget(status_label)
        self.setStatusBar(status)

    # ── Signal wiring ────────────────────────────────────────────
    def _connect_signals(self):
        # Processing signals
        self.file_bar.input_changed.connect(self._on_input_changed)

        self.param_panel.start_clicked.connect(self._start_processing)
        self.param_panel.pause_clicked.connect(self._toggle_pause)
        self.param_panel.stop_clicked.connect(self._stop_processing)

    # ── Processing ────────────────────────────────────────────────
    def _on_input_changed(self, path: str):
        if not path or not Path(path).exists():
            self.video_panel.clear_info()
            self.param_panel.show_controls_idle()
            self.progress_bar.setValue(0)
            self.status_label.setText("就绪 — 选择视频文件后点击开始处理")
            return

        info = get_video_info(path)
        if info is None:
            self.progress_bar.setValue(0)
            self.status_label.setText("错误: 无法读取视频文件")
            self.status_label.setStyleSheet("color: red;")
            return

        filename = Path(path).name
        self.video_panel.set_info(info, filename)
        if info["thumbnail"] is not None:
            self.video_panel.set_thumbnail(info["thumbnail"])

        if not self.file_bar.get_output_path():
            self.file_bar.set_output_path(str(Path(path).parent))

        self.param_panel.show_controls_ready()
        self.progress_bar.setValue(0)
        self.status_label.setText(f"已选择: {filename}  ({info['width']}×{info['height']}, {info['fps']:.1f} FPS)")
        self.status_label.setStyleSheet("")

    def _start_processing(self):
        input_path = self.file_bar.get_input_path()
        if not input_path or not Path(input_path).exists():
            return

        output_dir = self.file_bar.get_output_path()
        if not output_dir:
            output_dir = str(Path(input_path).parent)

        in_name = Path(input_path).stem
        params = self.param_panel.get_params()
        container = params["container_fmt"]
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
        self._save_settings()

        self._worker = WorkerThread(input_path, out_path, params)
        self._worker.progress_updated.connect(self._on_progress)
        self._worker.status_message.connect(self._on_status_message)
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.error_occurred.connect(self._on_processing_error)

        self.param_panel.show_controls_processing()
        self.progress_bar.setValue(0)
        self.status_label.setText("正在预热 CUDA ...")
        self.status_label.setStyleSheet("")
        self.param_panel.set_settings_enabled(False)
        self.file_bar.btn_input.setEnabled(False)
        self.file_bar.btn_output.setEnabled(False)

        self._worker.start()

    def _on_progress(self, frame, total, fps, avg_ms, gpu_mem):
        pct = int(frame / total * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        eta = fmt_time((total - frame) / max(fps, 0.01))
        text = f"{frame}/{total}  {pct}%  |  {fps:.1f} FPS  |  {avg_ms:.0f} ms/帧  |  剩余 {eta}"
        if gpu_mem > 0:
            text += f"  |  显存 {gpu_mem:.1f} GB"
        self.status_label.setText(text)

    def _on_status_message(self, msg: str):
        self.status_label.setText(msg)

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
        self.param_panel.show_controls_finished()
        self.progress_bar.setValue(100)
        avg_fps = total_frames / max(elapsed, 0.01)
        self.status_label.setText(
            f"完成! {total_frames} 帧 | 耗时 {fmt_time(elapsed)}"
            f" | 平均 {elapsed / total_frames * 1000:.0f} ms/帧 ({avg_fps:.1f} FPS)"
        )
        self.status_label.setStyleSheet("")
        self._reset_controls_enabled()

    def _on_processing_error(self, msg: str):
        self.param_panel.show_controls_ready()
        self.progress_bar.setValue(0)
        self.status_label.setText(f"错误: {msg}")
        self.status_label.setStyleSheet("color: red;")
        self._reset_controls_enabled()

    def _reset_after_stop(self):
        self.param_panel.show_controls_ready()
        self.progress_bar.setValue(0)
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("")
        self._reset_controls_enabled()

    def _reset_controls_enabled(self):
        self.param_panel.set_settings_enabled(True)
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

    # ── Settings persistence ─────────────────────────────────────
    def _save_settings(self):
        s = QSettings()
        params = self.param_panel.get_params()
        for key in ("output_mode", "custom_w", "custom_h", "container_fmt",
                     "fps_override", "quality_label", "codec_label",
                     "crf", "preset"):
            s.setValue(key, params[key])
        s.setValue("output_dir", self.file_bar.get_output_path())
        s.setValue("window_geometry", self.saveGeometry())

    def _load_settings(self):
        s = QSettings()
        params = {}
        for key in ("output_mode", "custom_w", "custom_h", "container_fmt",
                     "fps_override", "quality_label", "codec_label",
                     "crf", "preset"):
            val = s.value(key)
            if val is not None:
                params[key] = val
        if params:
            self.param_panel.set_params(params)

        out_dir = s.value("output_dir", "")
        if out_dir:
            self.file_bar.set_output_path(out_dir)

        geo = s.value("window_geometry")
        if geo is not None:
            self.restoreGeometry(geo)

    def closeEvent(self, event):
        s = QSettings()
        s.setValue("window_geometry", self.saveGeometry())
        super().closeEvent(event)

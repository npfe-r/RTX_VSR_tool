from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                              QPushButton, QProgressBar, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal

from utils import fmt_time


class BottomBar(QWidget):
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    open_output_clicked = pyqtSignal()
    preview_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._is_paused = False
        self._setup_ui()
        self._show_idle()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 6, 12, 6)
        self.main_layout.setSpacing(4)

        # Control row
        control_row = QHBoxLayout()
        self.btn_start = QPushButton("\U0001f680  开始处理")
        self.btn_start.setObjectName("primaryBtn")
        self.btn_start.setFixedWidth(240)
        self.btn_start.clicked.connect(self.start_clicked.emit)

        self.btn_pause = QPushButton("⏸  暂停")
        self.btn_pause.setFixedWidth(100)
        self.btn_pause.clicked.connect(self._on_pause_clicked)

        self.btn_stop = QPushButton("■  停止")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setFixedWidth(100)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)

        self.btn_open = QPushButton("\U0001f4c2  打开输出目录")
        self.btn_open.clicked.connect(self.open_output_clicked.emit)

        self.btn_preview = QPushButton("▶  播放预览")
        self.btn_preview.clicked.connect(self.preview_clicked.emit)

        self.btn_retry = QPushButton("\U0001f504  继续处理下一个")
        self.btn_retry.clicked.connect(self.start_clicked.emit)

        control_row.addWidget(self.btn_start)
        control_row.addWidget(self.btn_pause)
        control_row.addWidget(self.btn_stop)
        control_row.addWidget(self.btn_open)
        control_row.addWidget(self.btn_preview)
        control_row.addWidget(self.btn_retry)
        control_row.addStretch()

        # Progress row
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("infoValue")

        self.main_layout.addLayout(control_row)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.status_label)

    def _show_idle(self):
        self._reset_status_style()
        self.btn_start.setVisible(True)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_open.setVisible(False)
        self.btn_preview.setVisible(False)
        self.btn_retry.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("就绪 — 选择视频文件后点击开始处理")
        self.btn_start.setEnabled(False)

    def show_ready(self):
        self._reset_status_style()
        self._show_idle()
        self.btn_start.setEnabled(True)

    def show_processing(self):
        self._reset_status_style()
        self.btn_start.setVisible(False)
        self.btn_pause.setVisible(True)
        self.btn_stop.setVisible(True)
        self.btn_open.setVisible(False)
        self.btn_preview.setVisible(False)
        self.btn_retry.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在预热 CUDA ...")

    def update_progress(self, frame: int, total: int, fps: float, avg_ms: float, gpu_mem: float):
        pct = int(frame / total * 100)
        self.progress_bar.setValue(pct)
        eta = fmt_time((total - frame) / max(fps, 0.01))
        mem_text = f" | 显存: {gpu_mem:.1f} GB" if gpu_mem > 0 else ""
        self.progress_bar.setFormat(f"{frame}/{total}  {pct}%")
        self.status_label.setText(
            f"帧: {frame}/{total}  |  {fps:.1f} FPS"
            f" | {avg_ms:.0f} ms/帧 | 剩余 {eta}{mem_text}"
        )

    def show_finished(self, total_frames: int, elapsed: float, output_path: str = ""):
        self._reset_status_style()
        self.btn_start.setVisible(False)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_open.setVisible(True)
        self.btn_preview.setVisible(True)
        self.btn_retry.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(100)
        avg_fps = total_frames / max(elapsed, 0.01)
        self.progress_bar.setFormat("✅ 完成!")
        self.status_label.setText(
            f"处理完成! {total_frames} 帧 | 耗时 {fmt_time(elapsed)}"
            f" | 平均 {elapsed / total_frames * 1000:.0f} ms/帧 ({avg_fps:.1f} FPS)"
        )
        self._last_output = output_path

    def show_error(self, msg: str):
        self.btn_start.setVisible(True)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_open.setVisible(False)
        self.btn_preview.setVisible(False)
        self.btn_retry.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setStyleSheet("color: #B56A6A;")
        self.status_label.setText(f"❌ {msg}")
        self.btn_start.setEnabled(True)

    def set_paused_state(self, paused: bool):
        self._is_paused = paused
        self.btn_pause.setText("▶  继续" if paused else "⏸  暂停")

    def _on_pause_clicked(self):
        self.pause_clicked.emit()
        self.set_paused_state(not self._is_paused)

    def _reset_status_style(self):
        self.status_label.setStyleSheet("")

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QHBoxLayout,
                              QFormLayout, QComboBox, QSpinBox,
                              QSlider, QLabel, QPushButton, QStyle,
                              QStyleOptionSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent


class _JumpSlider(QSlider):
    """QSlider that jumps directly to the clicked position on the track."""
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            groove = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider, opt,
                QStyle.SubControl.SC_SliderGroove, self)
            handle_w = self.style().pixelMetric(
                QStyle.PixelMetric.PM_SliderLength, opt, self)
            avail = groove.width() - handle_w
            if avail > 0:
                x = int(event.position().x()) - groove.x() - handle_w // 2
                x = max(0, min(x, avail))
                val = QStyle.sliderValueFromPosition(
                    self.minimum(), self.maximum(), x, avail)
                self.setValue(val)
                return
        super().mousePressEvent(event)

from utils import list_gpu_devices


quality_options = [
    "BICUBIC (无AI 插值)",
    "LOW (AI 速度优先)",
    "MEDIUM (AI 均衡)",
    "HIGH (AI 质量优先)",
    "ULTRA (AI 极致细节)",
    "DENOISE_LOW (轻度降噪)",
    "DENOISE_MEDIUM (中度降噪)",
    "DENOISE_HIGH (强力降噪)",
    "DEBLUR_LOW (轻度去模糊)",
    "DEBLUR_MEDIUM (中度去模糊)",
    "DEBLUR_HIGH (强力去模糊)",
    "HIGHBITRATE_HIGH (高码率源)",
]


class ParamPanel(QWidget):
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_paused = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # === Output Size ===
        group_out = QGroupBox("输出尺寸")
        out_layout = QFormLayout(group_out)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["2x 放大", "4x 放大", "固定分辨率", "保持原尺寸"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        out_layout.addRow("放大模式:", self.mode_combo)

        size_row = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(320, 7680)
        self.width_spin.setSingleStep(16)
        self.width_spin.setValue(3840)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(240, 4320)
        self.height_spin.setSingleStep(16)
        self.height_spin.setValue(2160)
        size_row.addWidget(QLabel("宽:"))
        size_row.addWidget(self.width_spin, 1)
        size_row.addWidget(QLabel("高:"))
        size_row.addWidget(self.height_spin, 1)
        self._size_row_widgets = [self.width_spin, self.height_spin]
        out_layout.addRow("自定义尺寸:", size_row)

        self.container_combo = QComboBox()
        self.container_combo.addItems(["mp4", "mov", "mkv"])
        out_layout.addRow("封装格式:", self.container_combo)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(0, 120)
        self.fps_spin.setValue(0)
        self.fps_spin.setSpecialValueText("自动 (跟随原片)")
        out_layout.addRow("输出 FPS:", self.fps_spin)

        layout.addWidget(group_out)

        # === AI Processing ===
        group_ai = QGroupBox("AI 处理")
        ai_layout = QFormLayout(group_ai)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(quality_options)
        self.quality_combo.setCurrentText("HIGH (AI 质量优先)")
        ai_layout.addRow("质量/模式:", self.quality_combo)

        self.gpu_combo = QComboBox()
        devices = list_gpu_devices()
        for dev in devices:
            self.gpu_combo.addItem(dev["name"], dev["id"])
        if len(devices) <= 1:
            self.gpu_combo.setEnabled(False)
        ai_layout.addRow("GPU:", self.gpu_combo)

        layout.addWidget(group_ai)

        # === Encoding ===
        group_enc = QGroupBox("编码设置")
        enc_layout = QFormLayout(group_enc)

        self.codec_combo = QComboBox()
        self.codec_combo.addItems([
            "H.264 (libx264)",
            "H.264 (NVENC)",
            "H.265 (libx265)",
            "H.265 (NVENC)",
            "AV1 (libaom-av1)",
            "AV1 (NVENC)",
        ])
        self.codec_combo.setToolTip(
            "NVENC 硬件编码速度极快，适合大多数场景；"
            "软件编码同码率画质略好。AV1 NVENC 仅 RTX 40 系列支持"
        )
        enc_layout.addRow("视频编码器:", self.codec_combo)

        crf_row = QHBoxLayout()
        self.crf_slider = _JumpSlider(Qt.Orientation.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(18)
        self.crf_spin = QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(18)
        self.crf_slider.valueChanged.connect(self.crf_spin.setValue)
        self.crf_spin.valueChanged.connect(self.crf_slider.setValue)
        self.crf_slider.setToolTip("0=无损, 18=视觉无损, 23=默认, 28=有损, 51=最差")
        crf_row.addWidget(self.crf_slider, 1)
        crf_row.addWidget(self.crf_spin)
        enc_layout.addRow("CRF:", crf_row)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "ultrafast", "superfast", "veryfast", "faster", "fast",
            "medium", "slow", "slower", "veryslow",
        ])
        self.preset_combo.setCurrentText("medium")
        self.preset_combo.setToolTip("越慢压缩率越高，文件越小")
        enc_layout.addRow("编码速度:", self.preset_combo)

        layout.addWidget(group_enc)
        layout.addStretch()

        # === Start button (tall, fills width) ===
        self.btn_start = QPushButton("开始处理")
        self.btn_start.setMinimumHeight(100)
        self.btn_start.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.btn_start)

        # === Pause / Stop row ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self.btn_pause = QPushButton("暂停")
        self.btn_pause.setMinimumHeight(100)
        self.btn_pause.clicked.connect(self._on_pause_clicked)
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setMinimumHeight(100)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        self._on_mode_changed("2x 放大")
        self.show_controls_idle()

    def _on_mode_changed(self, mode: str):
        enabled = (mode == "固定分辨率")
        for w in self._size_row_widgets:
            w.setEnabled(enabled)

    def get_params(self) -> dict:
        codec_map = {
            "H.264 (libx264)": "libx264",
            "H.264 (NVENC)": "h264_nvenc",
            "H.265 (libx265)": "libx265",
            "H.265 (NVENC)": "hevc_nvenc",
            "AV1 (libaom-av1)": "libaom-av1",
            "AV1 (NVENC)": "av1_nvenc",
        }
        return {
            "output_mode": self.mode_combo.currentText(),
            "custom_w": self.width_spin.value(),
            "custom_h": self.height_spin.value(),
            "container_fmt": self.container_combo.currentText(),
            "fps_override": self.fps_spin.value(),
            "quality_label": self.quality_combo.currentText(),
            "device_id": self.gpu_combo.currentData() or 0,
            "enc_codec": codec_map.get(self.codec_combo.currentText(), "libx264"),
            "crf": self.crf_slider.value(),
            "preset": self.preset_combo.currentText(),
            "codec_label": self.codec_combo.currentText(),
        }

    def set_params(self, params: dict):
        if "output_mode" in params:
            self.mode_combo.setCurrentText(params["output_mode"])
        if "custom_w" in params:
            self.width_spin.setValue(params["custom_w"])
        if "custom_h" in params:
            self.height_spin.setValue(params["custom_h"])
        if "container_fmt" in params:
            self.container_combo.setCurrentText(params["container_fmt"])
        if "fps_override" in params:
            self.fps_spin.setValue(params["fps_override"])
        if "quality_label" in params:
            self.quality_combo.setCurrentText(params["quality_label"])
        if "codec_label" in params:
            self.codec_combo.setCurrentText(params["codec_label"])
        if "crf" in params:
            self.crf_slider.setValue(params["crf"])
        if "preset" in params:
            self.preset_combo.setCurrentText(params["preset"])

    # ── Button state control ─────────────────────────────────────
    def set_settings_enabled(self, enabled: bool):
        """Enable/disable only the setting controls, keeping buttons always responsive."""
        for w in (self.mode_combo, self.width_spin, self.height_spin,
                  self.container_combo, self.fps_spin, self.quality_combo,
                  self.gpu_combo, self.codec_combo, self.crf_slider,
                  self.crf_spin, self.preset_combo):
            w.setEnabled(enabled)
        for child in self.findChildren(QGroupBox):
            child.setEnabled(enabled)

    def show_controls_idle(self):
        self.btn_start.setEnabled(False)
        self.btn_start.setVisible(True)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)

    def show_controls_ready(self):
        self.btn_start.setEnabled(True)
        self.btn_start.setVisible(True)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)

    def show_controls_processing(self):
        self.btn_start.setVisible(False)
        self.btn_pause.setVisible(True)
        self.btn_pause.setText("暂停")
        self.btn_stop.setVisible(True)
        self._is_paused = False

    def show_controls_finished(self):
        self.btn_start.setVisible(True)
        self.btn_start.setEnabled(True)
        self.btn_pause.setVisible(False)
        self.btn_stop.setVisible(False)

    def set_paused_state(self, paused: bool):
        self._is_paused = paused
        self.btn_pause.setText("继续" if paused else "暂停")

    def _on_pause_clicked(self):
        self.pause_clicked.emit()
        self.set_paused_state(not self._is_paused)

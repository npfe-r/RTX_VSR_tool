from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox,
                              QFormLayout, QComboBox, QSpinBox,
                              QSlider, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

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


class CollapsibleGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked):
        for child in self.findChildren(QWidget):
            if child is not self:
                child.setVisible(checked)


class ParamPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # === Output Size ===
        group_out = CollapsibleGroupBox("📐 输出尺寸")
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
        group_ai = CollapsibleGroupBox("🧠 AI 处理")
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
        group_enc = CollapsibleGroupBox("🎞 编码设置")
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
        self.crf_slider = QSlider(Qt.Orientation.Horizontal)
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

        self._on_mode_changed("2x 放大")

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
        }

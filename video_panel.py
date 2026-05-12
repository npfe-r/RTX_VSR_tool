import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                              QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage


class VideoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._info_data = None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet(
            "QLabel { background-color: #2D2D2D; border: 2px dashed #555555;"
            " border-radius: 4px; }"
        )
        self.preview_label.setText("拖拽视频文件到此处")
        layout.addWidget(self.preview_label, 1)

        # Info card
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "QFrame { background-color: #4A4A4A; border: 1px solid #555555;"
            " border-radius: 4px; padding: 8px; }"
        )
        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(4)

        self.info_labels = {}
        fields = [
            ("文件名", "filename", ""),
            ("分辨率", "resolution", ""),
            ("时长", "duration", ""),
            ("帧率", "fps", ""),
            ("编码", "codec", ""),
            ("文件大小", "filesize", ""),
        ]
        for row, (label, key, _) in enumerate(fields):
            lbl = QLabel(f"{label}:")
            lbl.setObjectName("infoLabel")
            val = QLabel("--")
            val.setObjectName("infoValue")
            info_layout.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignLeft)
            info_layout.addWidget(val, row, 1, Qt.AlignmentFlag.AlignRight)
            self.info_labels[key] = val

        layout.addWidget(info_frame)

    def set_thumbnail(self, rgb_array: np.ndarray):
        h, w, ch = rgb_array.shape
        bytes_per_line = w * ch
        qimg = QImage(rgb_array.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(
            self.preview_label.width() - 4,
            400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)
        self.preview_label.setText("")

    def set_info(self, info: dict, filename: str):
        self._info_data = info
        self.info_labels["filename"].setText(filename)
        self.info_labels["resolution"].setText(f"{info['width']} × {info['height']}")
        self.info_labels["duration"].setText(f"{info['duration']:.1f}s ({info['frames']} 帧)")
        self.info_labels["fps"].setText(f"{info['fps']:.2f} FPS")
        self.info_labels["codec"].setText(info["codec"])
        self.info_labels["filesize"].setText(f"{info['size_mb']:.1f} MB")

    def clear_info(self):
        for key in self.info_labels:
            self.info_labels[key].setText("--")
        self.preview_label.setText("拖拽视频文件到此处")
        self.preview_label.setPixmap(QPixmap())
        self._info_data = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._info_data and self._info_data.get("thumbnail") is not None:
            thumb = self._info_data["thumbnail"]
            self.set_thumbnail(thumb)

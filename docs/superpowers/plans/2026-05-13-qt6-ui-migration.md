# PyQt6 UI 迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the RTX VSR tool from Streamlit to a native PyQt6 desktop application with Blender-style UI.

**Architecture:** Single-window Qt6 app with QMainWindow + QSplitter dividing video preview (left) and parameter panels (right). GPU processing runs in a QThread with signal/slot progress updates. QSS stylesheet provides Blender-inspired dark theme.

**Tech Stack:** PyQt6, PyTorch (existing), OpenCV (existing), NVIDIA VFX SDK (existing)

---

### Task 1: Project Foundation

**Files:**
- Create: `requirements.txt`
- Create: `styles/blender.qss`
- Create: `theme.py`

- [ ] **Step 1: Update requirements.txt**

```txt
PyQt6>=6.5
nvidia-vfx==0.1.0.1
torch==2.11.0+cu128
torchvision==0.26.0+cu128
opencv-python-headless==4.13.0.92
numpy
```

- [ ] **Step 2: Create theme.py with color constants and QSS loader**

```python
import os
from PyQt6.QtWidgets import QApplication

# Blender-inspired low-saturation palette
COLORS = {
    "window_bg": "#3D3D3D",
    "panel_bg": "#4A4A4A",
    "widget_bg": "#575757",
    "widget_hover": "#636363",
    "widget_pressed": "#4E4E4E",
    "input_bg": "#464646",
    "border": "#555555",
    "text_primary": "#D3D3D3",
    "text_secondary": "#888888",
    "accent": "#5C9BD5",
    "success": "#6BAF6D",
    "warning": "#B5A36A",
    "danger": "#B56A6A",
}

def load_stylesheet(app: QApplication):
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "blender.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
```

- [ ] **Step 3: Create styles/blender.qss**

```qss
/* === Global === */
QMainWindow, QWidget {
    background-color: #3D3D3D;
    color: #D3D3D3;
    font-family: "Microsoft YaHei", "Noto Sans SC", sans-serif;
    font-size: 12px;
}

/* === GroupBox === */
QGroupBox {
    background-color: #4A4A4A;
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 12px;
    padding: 16px 8px 8px 8px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: #D3D3D3;
}

/* === Buttons === */
QPushButton {
    background-color: #575757;
    color: #D3D3D3;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 12px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #636363;
}
QPushButton:pressed {
    background-color: #4E4E4E;
}
QPushButton:disabled {
    color: #888888;
    background-color: #4A4A4A;
}
QPushButton#primaryBtn {
    background-color: #5C9BD5;
    color: #FFFFFF;
    font-weight: bold;
    border: none;
    padding: 8px 24px;
}
QPushButton#primaryBtn:hover {
    background-color: #6BA8E0;
}
QPushButton#primaryBtn:disabled {
    background-color: #4A4A4A;
    color: #888888;
}
QPushButton#dangerBtn {
    color: #B56A6A;
}
QPushButton#dangerBtn:hover {
    background-color: #5A3A3A;
}

/* === LineEdit / SpinBox === */
QLineEdit, QSpinBox {
    background-color: #464646;
    color: #D3D3D3;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 22px;
}
QLineEdit:focus, QSpinBox:focus {
    border-color: #5C9BD5;
}
QLineEdit:disabled, QSpinBox:disabled {
    color: #888888;
    background-color: #3D3D3D;
}

/* === ComboBox === */
QComboBox {
    background-color: #575757;
    color: #D3D3D3;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 2px 8px;
    min-height: 24px;
}
QComboBox:hover {
    background-color: #636363;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #4A4A4A;
    color: #D3D3D3;
    border: 1px solid #555555;
    selection-background-color: #5C9BD5;
    selection-color: #FFFFFF;
}

/* === Slider === */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #464646;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #5C9BD5;
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #6BA8E0;
}
QSlider::sub-page:horizontal {
    background: #5C9BD5;
    border-radius: 2px;
}

/* === ProgressBar === */
QProgressBar {
    background-color: #464646;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #D3D3D3;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #5C9BD5;
    border-radius: 4px;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #555555;
    width: 1px;
}

/* === ScrollArea === */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #3D3D3D;
    width: 8px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #575757;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #636363;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* === Label === */
QLabel {
    color: #D3D3D3;
}
QLabel#infoValue {
    color: #D3D3D3;
    font-weight: normal;
}
QLabel#infoLabel {
    color: #888888;
}

/* === RadioButton === */
QRadioButton {
    color: #D3D3D3;
    spacing: 6px;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 2px solid #575757;
    background: #464646;
}
QRadioButton::indicator:checked {
    background: #5C9BD5;
    border-color: #5C9BD5;
}
```

---

### Task 2: Utility Functions

**Files:**
- Create: `utils.py`

- [ ] **Step 1: Create utils.py**

```python
import time
import torch
import numpy as np
import cv2
from pathlib import Path


def auto_gpu_name() -> str:
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0)
    return "未检测到 GPU"


def list_gpu_devices() -> list[dict]:
    devices = []
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            devices.append({
                "id": i,
                "name": torch.cuda.get_device_name(i),
            })
    return devices


def calc_output_size(mode: str, w: int, h: int, cw: int, ch: int) -> tuple[int, int]:
    if mode == "2x 放大":
        return w * 2, h * 2
    elif mode == "4x 放大":
        return w * 4, h * 4
    elif mode == "固定分辨率":
        return cw, ch
    return w, h


def fmt_time(seconds: float) -> str:
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds:.0f}s"
    return f"{int(seconds // 60)}m {int(seconds % 60)}s"


def get_video_info(path: str) -> dict | None:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = frames / fps if fps > 0 else 0
    codec_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec_str = "".join(chr((codec_int >> 8 * i) & 0xFF) for i in range(4))
    size_mb = Path(path).stat().st_size / 1024 / 1024

    ret, frame = cap.read()
    thumb_rgb = None
    if ret:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        thumb_rgb = cv2.resize(rgb, (min(w, 640), min(h, 360)))
    cap.release()

    return {
        "width": w,
        "height": h,
        "fps": fps,
        "frames": frames,
        "duration": dur,
        "codec": codec_str.strip(),
        "size_mb": round(size_mb, 1),
        "thumbnail": thumb_rgb,
    }
```

---

### Task 3: Worker Thread

**Files:**
- Create: `worker.py`

- [ ] **Step 1: Create worker.py with GPU processing thread**

```python
import time
import torch
import cv2
import numpy as np
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from nvvfx import VideoSuperRes
from nvvfx.effects.video_super_res import QualityLevel


quality_map = {
    "BICUBIC (无AI 插值)": QualityLevel.BICUBIC,
    "LOW (AI 速度优先)": QualityLevel.LOW,
    "MEDIUM (AI 均衡)": QualityLevel.MEDIUM,
    "HIGH (AI 质量优先)": QualityLevel.HIGH,
    "ULTRA (AI 极致细节)": QualityLevel.ULTRA,
    "DENOISE_LOW (轻度降噪)": QualityLevel.DENOISE_LOW,
    "DENOISE_MEDIUM (中度降噪)": QualityLevel.DENOISE_MEDIUM,
    "DENOISE_HIGH (强力降噪)": QualityLevel.DENOISE_HIGH,
    "DEBLUR_LOW (轻度去模糊)": QualityLevel.DEBLUR_LOW,
    "DEBLUR_MEDIUM (中度去模糊)": QualityLevel.DEBLUR_MEDIUM,
    "DEBLUR_HIGH (强力去模糊)": QualityLevel.DEBLUR_HIGH,
    "HIGHBITRATE_HIGH (高码率源)": QualityLevel.HIGHBITRATE_HIGH,
}


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int, int, float, float, float)
    # frame, total, fps, avg_ms, gpu_mem_gb
    status_message = pyqtSignal(str)
    finished = pyqtSignal(int, float)  # total_frames, elapsed_seconds
    error_occurred = pyqtSignal(str)

    def __init__(self, input_path, output_path, params):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.params = params
        self._paused = False
        self._cancelled = False

    def run(self):
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.error_occurred.emit("无法打开视频文件")
            return

        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out_fps = self.params.get("fps_override", 0) or orig_fps

        out_w, out_h = calc_output_size(
            self.params["output_mode"],
            orig_w, orig_h,
            self.params.get("custom_w", 3840),
            self.params.get("custom_h", 2160),
        )
        out_w += out_w % 2
        out_h += out_h % 2

        tmp_path = self.output_path.rsplit(".", 1)[0] + "_tmp.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(tmp_path, fourcc, out_fps, (out_w, out_h))
        if not writer.isOpened():
            self.error_occurred.emit("无法创建临时视频文件")
            cap.release()
            return

        quality = quality_map.get(self.params["quality_label"], QualityLevel.HIGH)
        device_id = self.params.get("device_id", 0)
        wall_start = time.time()

        self.status_message.emit("预热 CUDA ...")

        try:
            with VideoSuperRes(quality=quality, device=device_id) as sr:
                sr.output_width = out_w
                sr.output_height = out_h
                sr.load()

                dummy = torch.zeros(3, orig_h, orig_w, device=f"cuda:{device_id}")
                torch.from_dlpack(sr.run(dummy).image).clone()
                torch.cuda.empty_cache()

                frame_count = 0
                total_time = 0.0

                while True:
                    if self._cancelled:
                        break

                    if self._paused:
                        self.status_message.emit("已暂停")
                        while self._paused:
                            if self._cancelled:
                                break
                            self.msleep(100)
                        continue

                    ret, frame_bgr = cap.read()
                    if not ret:
                        break

                    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    tensor = (
                        torch.from_numpy(rgb)
                        .permute(2, 0, 1)
                        .float()
                        .div_(255.0)
                        .contiguous()
                        .to(f"cuda:{device_id}", non_blocking=True)
                    )

                    t0 = time.perf_counter()
                    result = sr.run(tensor)
                    torch.cuda.synchronize(f"cuda:{device_id}")
                    t1 = time.perf_counter()

                    out_t = torch.from_dlpack(result.image).clone()
                    out_np = out_t.mul_(255.0).byte().permute(1, 2, 0).cpu().numpy()
                    out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)
                    writer.write(out_bgr)

                    frame_count += 1
                    total_time += t1 - t0

                    if frame_count % max(1, total_frames // 100) == 0 or frame_count == total_frames:
                        now = time.time()
                        fps = frame_count / (now - wall_start + 1e-9)
                        avg_ms = (total_time / frame_count) * 1000
                        mem = 0
                        if torch.cuda.is_available():
                            mem = torch.cuda.memory_allocated(device_id) / 1024**3
                        self.progress_updated.emit(frame_count, total_frames, fps, avg_ms, mem)

        except Exception as e:
            self.error_occurred.emit(str(e))
            cap.release()
            writer.release()
            return

        cap.release()
        writer.release()

        if self._cancelled:
            Path(tmp_path).unlink(missing_ok=True)
            return

        if frame_count == 0:
            self.error_occurred.emit("未能读取到任何帧")
            return

        # ffmpeg final encode
        self.status_message.emit("正在编码输出 ...")
        try:
            import subprocess
            has_audio = False
            try:
                prob = subprocess.run(
                    ["ffprobe", "-i", self.input_path, "-show_streams",
                     "-select_streams", "a", "-loglevel", "error"],
                    capture_output=True, text=True, timeout=30,
                )
                has_audio = bool(prob.stdout.strip())
            except Exception:
                pass

            cmd = ["ffmpeg", "-y", "-i", tmp_path]
            if has_audio:
                cmd += ["-i", self.input_path]
            cmd += ["-map", "0:v:0"]
            if has_audio:
                cmd += ["-map", "1:a:0"]
            cmd += [
                "-c:v", self.params.get("enc_codec", "libx264"),
                "-crf", str(self.params.get("crf", 18)),
                "-preset", self.params.get("preset", "medium"),
            ]
            if has_audio:
                cmd += ["-c:a", "aac"]
            cmd += ["-loglevel", "error", self.output_path]
            subprocess.run(cmd, timeout=600)
        except Exception:
            # fallback: keep the OpenCV tmp file
            import os as _os
            _os.replace(tmp_path, self.output_path)

        Path(tmp_path).unlink(missing_ok=True)
        elapsed = time.time() - wall_start
        self.finished.emit(frame_count, elapsed)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self.status_message.emit("继续处理 ...")

    def cancel(self):
        self._cancelled = True
        self._paused = False


def calc_output_size(mode, w, h, cw, ch):
    if mode == "2x 放大":
        return w * 2, h * 2
    if mode == "4x 放大":
        return w * 4, h * 4
    if mode == "固定分辨率":
        return cw, ch
    return w, h
```

---

### Task 4: File Bar Widget

**Files:**
- Create: `file_bar.py`

- [ ] **Step 1: Create file_bar.py**

```python
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                              QLineEdit, QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropLineEdit(QLineEdit):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText("拖拽视频文件到此处，或点击右侧按钮选择")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                "QLineEdit { border-color: #6BAF6D; }"
            )

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.setText(path)
            self.file_dropped.emit(path)


class FileBar(QWidget):
    input_changed = pyqtSignal(str)
    output_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Input row
        input_row = QHBoxLayout()
        input_label = QLabel("📁 输入:")
        input_label.setFixedWidth(50)
        self.input_edit = DropLineEdit()
        self.input_edit.textChanged.connect(self._on_input_text_changed)
        self.input_edit.file_dropped.connect(self._on_input_text_changed)
        self.btn_input = QPushButton("选择文件")
        self.btn_input.clicked.connect(self._pick_input)
        input_row.addWidget(input_label)
        input_row.addWidget(self.input_edit, 1)
        input_row.addWidget(self.btn_input)

        # Output row
        output_row = QHBoxLayout()
        output_label = QLabel("📁 输出:")
        output_label.setFixedWidth(50)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("留空则使用视频所在目录")
        self.btn_output = QPushButton("选择目录")
        self.btn_output.clicked.connect(self._pick_output)
        output_row.addWidget(output_label)
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(self.btn_output)

        layout.addLayout(input_row)
        layout.addLayout(output_row)

    def _on_input_text_changed(self, text=None):
        self.input_changed.emit(self.input_edit.text())

    def _pick_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv);;所有文件 (*.*)"
        )
        if path:
            self.input_edit.setText(path)
            self.input_changed.emit(path)

    def _pick_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_edit.setText(path)
            self.output_changed.emit(path)

    def get_input_path(self) -> str:
        return self.input_edit.text()

    def get_output_path(self) -> str:
        return self.output_edit.text()

    def set_output_path(self, path: str):
        self.output_edit.setText(path)
```

---

### Task 5: Video Panel

**Files:**
- Create: `video_panel.py`

- [ ] **Step 1: Create video_panel.py**

```python
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage, QFont


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
            # re-scale on window resize
            thumb = self._info_data["thumbnail"]
            self.set_thumbnail(thumb)
```

---

### Task 6: Parameter Panel

**Files:**
- Create: `param_panel.py`

- [ ] **Step 1: Create param_panel.py**

```python
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox,
                              QFormLayout, QComboBox, QSpinBox,
                              QSlider, QLabel, QHBoxLayout, QRadioButton)
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
        # When unchecked, hide child widgets but keep the title visible
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
            "H.265 (libx265)",
            "AV1 (libaom-av1)",
        ])
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
            "H.265 (libx265)": "libx265",
            "AV1 (libaom-av1)": "libaom-av1",
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
```

---

### Task 7: Bottom Bar

**Files:**
- Create: `bottom_bar.py`

- [ ] **Step 1: Create bottom_bar.py**

```python
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
        self._setup_ui()
        self._show_idle()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 6, 12, 6)
        self.main_layout.setSpacing(4)

        # Control row
        control_row = QHBoxLayout()
        self.btn_start = QPushButton("🚀  开始处理")
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

        self.btn_open = QPushButton("📂  打开输出目录")
        self.btn_open.clicked.connect(self.open_output_clicked.emit)

        self.btn_preview = QPushButton("▶  播放预览")
        self.btn_preview.clicked.connect(self.preview_clicked.emit)

        self.btn_retry = QPushButton("🔄  继续处理下一个")
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
        self._show_idle()
        self.btn_start.setEnabled(True)

    def show_processing(self):
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
        self.btn_pause.setText("▶  继续" if paused else "⏸  暂停")

    def _on_pause_clicked(self):
        is_paused = self.btn_pause.text().startswith("▶")
        self.pause_clicked.emit()
        self.set_paused_state(not is_paused)

    def _reset_status_style(self):
        self.status_label.setStyleSheet("")
```

---

### Task 8: Main Window

**Files:**
- Create: `main_window.py`

- [ ] **Step 1: Create main_window.py**

```python
import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                              QVBoxLayout, QSplitter, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtCore import QUrl

from file_bar import FileBar
from video_panel import VideoPanel
from param_panel import ParamPanel
from bottom_bar import BottomBar
from worker import WorkerThread
from utils import get_video_info


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

        # File bar (top)
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

    def _connect_signals(self):
        self.file_bar.input_changed.connect(self._on_input_changed)
        self.bottom_bar.start_clicked.connect(self._start_processing)
        self.bottom_bar.pause_clicked.connect(self._toggle_pause)
        self.bottom_bar.stop_clicked.connect(self._stop_processing)
        self.bottom_bar.open_output_clicked.connect(self._open_output_dir)
        self.bottom_bar.preview_clicked.connect(self._preview_output)

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
            if self._worker._paused:
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
            # Launch system default player
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
```

---

### Task 9: Entry Point

**Files:**
- Create: `app.py` (rewrite existing)

- [ ] **Step 1: Rewrite app.py as entry point**

```python
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from theme import load_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RTX 视频超分辨率工具")
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Task 10: Update start.bat

**Files:**
- Modify: `start.bat`

- [ ] **Step 1: Update start.bat**

```bat
@echo off
cd /d "H:\Project\RTX_VSR_tool"
call venv\Scripts\activate
python app.py
pause
```

---

### Task 11: Remove Streamlit Dependencies & Verify

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Remove streamlit and tkinter from requirements.txt**

Final `requirements.txt`:
```txt
PyQt6>=6.5
nvidia-vfx==0.1.0.1
torch==2.11.0+cu128
torchvision==0.26.0+cu128
opencv-python-headless==4.13.0.92
numpy
```

- [ ] **Step 2: Run the application to verify it launches**

```bash
cd "H:/Project/RTX_VSR_tool" && python app.py
```
Expected: PyQt6 window opens with Blender-style dark theme, all panels visible.

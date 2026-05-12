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
        scale = min(640 / w, 360 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        thumb_rgb = cv2.resize(rgb, (new_w, new_h))
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

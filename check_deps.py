"""Check required system dependencies at startup for the Light bundle."""

import importlib
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DepResult:
    name: str
    label: str
    ok: bool
    hint: str = ""
    children: list["DepResult"] = field(default_factory=list)


def _check_py_module(name: str, label: str) -> DepResult:
    try:
        importlib.import_module(name)
        return DepResult(name=name, label=label, ok=True)
    except ImportError as e:
        return DepResult(name=name, label=label, ok=False, hint=str(e))
    except Exception as e:
        # nvvfx might fail if CUDA is not available
        return DepResult(name=name, label=label, ok=False, hint=str(e))


def _check_exe(name: str, label: str) -> DepResult:
    exe = shutil.which(name)
    if exe:
        try:
            r = subprocess.run([name, "-version"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return DepResult(name=name, label=label, ok=True)
            return DepResult(name=name, label=label, ok=False, hint=f"binary found but returned error")
        except Exception as e:
            return DepResult(name=name, label=label, ok=False, hint=str(e))
    return DepResult(name=name, label=label, ok=False, hint="not found in PATH")


def check_dependencies() -> list[DepResult]:
    """Check all external dependencies. Returns list of results."""
    results = []

    # Python packages
    results.append(DepResult(
        name="torch", label="Python 包",
        ok=True, children=[
            _check_py_module("torch", "torch (PyTorch)"),
            _check_py_module("torchvision", "torchvision"),
            _check_py_module("nvvfx", "nvvfx (NVIDIA VFX SDK)"),
            _check_py_module("nvvfx.effects.video_super_res", "nvvfx.effects.video_super_res"),
            _check_py_module("cv2", "opencv-python-headless"),
        ]
    ))

    # System executables
    results.append(DepResult(
        name="ffmpeg", label="系统工具",
        ok=True, children=[
            _check_exe("ffmpeg", "ffmpeg"),
            _check_exe("ffprobe", "ffprobe"),
        ]
    ))

    # Mark parent ok only if all children ok
    for r in results:
        r.ok = all(c.ok for c in r.children)

    return results


def missing_deps(results: list[DepResult]) -> list[DepResult]:
    """Flatten and filter only failed deps."""
    out = []
    for r in results:
        for c in r.children:
            if not c.ok:
                out.append(c)
    return out


BUILD_MODE_FILE = None  # set by app.py at startup


_INSTALL_GUIDE = """
💡 推荐：双击运行本程序目录下的 install_deps.bat 可一键安装以上所有依赖。

或手动安装：

• torch / torchvision:
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

• nvvfx (NVIDIA VFX SDK):
    pip install nvidia-vfx

• opencv-python-headless:
    pip install opencv-python-headless

• ffmpeg:
    从 https://ffmpeg.org/download.html 下载并添加到系统 PATH

请确保所有依赖安装完成后重新启动本程序。
"""


def show_dialog_if_missing(results: list[DepResult], parent=None) -> bool:
    """Show a dialog if any deps are missing. Returns True if all OK, False otherwise."""
    missing = missing_deps(results)
    if not missing:
        return True

    lines = []
    for d in missing:
        lines.append(f"  • {d.label}")
    dep_list = "\n".join(lines)

    msg = (
        f"以下依赖未找到，视频处理功能将无法使用：\n\n"
        f"{dep_list}\n\n"
        f"请确认它们已安装在您系统的 Python 环境中：\n"
        f"{_INSTALL_GUIDE}"
    )

    try:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, "依赖检查 - RTX 视频超分辨率工具", msg)
    except ImportError:
        # Fallback if PyQt6 not available either
        print("警告：缺少依赖", file=sys.stderr)
        print(msg, file=sys.stderr)

    return False

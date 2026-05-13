# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

sys.setrecursionlimit(5000)

ROOT = Path(r"H:\Project\RTX_VSR_tool")
FFMPEG = Path(r"D:\Program Files\ffmpeg\bin")

# Resolve site-packages from the venv (not the system Python) to avoid
# version mismatches between torch/torchvision/nvvfx.
_VENV = ROOT / "venv"
SITE = _VENV / "Lib" / "site-packages"

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT), str(SITE)],
    binaries=[
        (str(FFMPEG / "ffmpeg.exe"), "."),
        (str(FFMPEG / "ffprobe.exe"), "."),
        *[(str(f), "nvvfx/libs") for f in (SITE / "nvvfx/libs").glob("*.dll")],
    ],
    datas=[],
    hiddenimports=[
        "numpy",
        "cv2",
        "torch",
        "nvvfx",
        "nvvfx._ext",
        "nvvfx.effects",
        "nvvfx.effects.video_super_res",
        "nvvfx.effects.base",
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "rthook_full_build.py")],
    excludes=[
        # Torch submodules — only exclude ones that are lazy-loaded or
        # unreferenced. torch core unconditionally imports the rest.
        # NOTE: torch.testing is unconditionally imported by
        # torch.autograd.gradcheck (via nn.modules.batchnorm).
        # torch.onnx, torch._dynamo, torch._inductor,
        # torch.utils.benchmark are lazy-loaded and safe to exclude.
        "torch.onnx",           # ONNX export, ~2 MB
        "torch._dynamo",        # torch.compile frontend, ~7 MB
        "torch._inductor",      # torch.compile backend, ~16 MB
        "torch.utils.benchmark",
        "torch.backends._coreml", "torch.backends._nnapi",
        # torchvision — not imported by app or nvvfx, ~23 MB saved
        "torchvision",
        # Unused general libs
        "tkinter", "matplotlib", "scipy", "PIL", "pandas",
        "tensorflow", "tensorflow-plugins", "keras", "jax", "jaxlib",
        "triton", "IPython", "jedi", "parso", "yapf_third_party",
        "jinja2", "urllib3", "chardet", "charset_normalizer",
        "cryptography", "lxml", "pygments", "psutil", "fsspec",
        "win32com", "pythoncom", "pywintypes", "prompt_toolkit",
        "wcwidth", "pygame", "sqlite3", "setuptools", "pkg_resources",
        "distutils", "pyparsing",
    ],
    noarchive=False,
)

# ── Post-process: drop unnecessary DLLs to shrink the package ──────────────
# Dependency analysis shows these are NOT load-time requirements of
# torch_cuda/torch_cpu/torch_python, and are not used by the app:
#   - Profiling / compilation: nvperf, nvrtc.alt, nvJitLink, curand
#   - Multi-GPU solver: cusolverMg (single-GPU VSR only)
#   - FFTW wrapper: cufftw (app uses cuFFT directly through torch)
#   - Qt extras: Pdf, Network, software OpenGL (NVIDIA GPU available)
#   - Protobuf compiler: protoc (not needed at runtime)

_EXCLUDE_BIN = {
    # CUDA profiling — not needed for inference
    "nvperf_host.dll",           #  21 MB
    # NVRTC alt variant — main nvrtc kept for cudnn compat
    "nvrtc64_120_0.alt.dll",     #  83 MB
    # Random number generation — not used during inference
    "curand64_10.dll",           #  69 MB
    # Multi-GPU solver — single-GPU VSR only
    "cusolverMg64_11.dll",       # 150 MB
    # FFTW wrapper — app uses cuFFT directly through torch
    "cufftw64_11.dll",           # 160 KB
    # Qt extras — not used by this app
    "Qt6Pdf.dll",                # 4.4 MB
    "Qt6Network.dll",            # 1.7 MB
    "opengl32sw.dll",            #  20 MB — software OpenGL fallback
    # Protobuf compiler — not needed at runtime
    "protoc.exe",                # 2.7 MB
    # NOTE: nvJitLink_120_0.dll (75 MB) is kept because
    # cusparse64_12.dll → loads it at load time.
    # torchvision excluded via excludes[] above (~23 MB).
}
a.binaries = [
    b for b in a.binaries
    if os.path.basename(b[0]) not in _EXCLUDE_BIN
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts,
    exclude_binaries=True,
    name="RTX-VSR-Tool",
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[],
    runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False, argv_emulation=False,
    target_arch=None, codesign_identity=None, entitlements_file=None,
)

coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name="RTX-VSR-Tool-Full",
)

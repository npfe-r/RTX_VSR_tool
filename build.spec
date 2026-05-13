# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

sys.setrecursionlimit(5000)

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(r"H:\Project\RTX_VSR_tool")
FFMPEG = Path(r"D:\Program Files\ffmpeg\bin")

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=[
        # ffmpeg + ffprobe only
        (str(FFMPEG / "ffmpeg.exe"), "."),
        (str(FFMPEG / "ffprobe.exe"), "."),
    ],
    datas=[],
    hiddenimports=[
        "check_deps",
        "numpy",
        "cv2",
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "rthook_find_packages.py")],
    excludes=[
        # Exclude large libs — loaded from system Python at runtime
        "torch",
        "torchvision",
        "nvvfx",
        "nvvfx._ext",
        "nvvfx.effects",
        "nvvfx.effects.video_super_res",
        "nvvfx.effects.base",
        "onnx",
        # Unused
        "tkinter",
        "matplotlib",
        "scipy",
        "PIL",
        "pandas",
        "tensorflow",
        "tensorflow-plugins",
        "keras",
        "jax",
        "jaxlib",
        "triton",
        "IPython",
        "jedi",
        "parso",
        "yapf_third_party",
        "jinja2",
        "urllib3",
        "chardet",
        "charset_normalizer",
        "cryptography",
        "lxml",
        "pygments",
        "psutil",
        "fsspec",
        "win32com",
        "pythoncom",
        "pywintypes",
        "prompt_toolkit",
        "wcwidth",
        "pygame",
        "sqlite3",
        "setuptools",
        "pkg_resources",
        "distutils",
        "pyparsing",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="RTX-VSR-Tool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RTX-VSR-Tool",
)

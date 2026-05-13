@echo off
chcp 65001 >nul
title RTX-VSR-Tool 依赖安装脚本

echo +----------------------------------------------+
echo ^| RTX-VSR-Tool 依赖安装脚本                      ^|
echo ^| 轻量包需要以下依赖才能运行：                    ^|
echo ^|   - PyTorch (CUDA 12.4)                       ^|
echo ^|   - nvidia-vfx (NVIDIA VFX SDK)               ^|
echo ^|   - opencv-python-headless                    ^|
echo ^|   - ffmpeg                                    ^|
echo +----------------------------------------------+
echo.

:: ── 检查 Python ─────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10 或更新版本。
    echo        下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python 版本:
python --version
echo.

:: ── 检测 CUDA ───────────────────────────────────────
echo [检测] 检查 PyTorch CUDA 版本 ...
where nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [提示] 未找到 nvidia-smi，将继续安装默认 CUDA 12.4 版本。
    echo        如果您的 CUDA 版本不同，请手动修改 pip 安装命令。
) else (
    nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>&1
)
echo.

:: ── 安装 PyTorch ────────────────────────────────────
echo [1/4] 安装 PyTorch + torchvision (CUDA 12.4) ...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
if errorlevel 1 (
    echo [警告] PyTorch 安装失败，请手动安装:
    echo    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
    echo.
)
echo.

:: ── 安装 NVIDIA VFX SDK ─────────────────────────────
echo [2/4] 安装 nvidia-vfx (NVIDIA VFX SDK) ...
python -m pip install nvidia-vfx
if errorlevel 1 (
    echo [警告] nvidia-vfx 安装失败，请手动安装:
    echo    pip install nvidia-vfx
    echo.
)
echo.

:: ── 安装 OpenCV ─────────────────────────────────────
echo [3/4] 安装 opencv-python-headless ...
python -m pip install opencv-python-headless
if errorlevel 1 (
    echo [警告] opencv-python-headless 安装失败，请手动安装:
    echo    pip install opencv-python-headless
    echo.
)
echo.

:: ── 检查 ffmpeg ─────────────────────────────────────
echo [4/4] 检查 ffmpeg ...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [提示] 未找到 ffmpeg，视频编码阶段将无法完成。
    echo        请从 https://ffmpeg.org/download.html 下载
    echo        并将 bin 目录添加到系统 PATH 环境变量。
    echo.
    echo        快速安装: winget install ffmpeg
) else (
    for /f "tokens=*" %%i in ('ffmpeg -version 2^>^&1 ^| findstr /i "ffmpeg version"') do echo ffmpeg: %%i
)
echo.

:: ── 完成 ─────────────────────────────────────────────
echo +----------------------------------------------+
echo ^| 依赖安装完成！                                ^|
echo ^| 如果部分组件安装失败，请根据上方提示手动安装。  ^|
echo ^| 安装完成后，双击 RTX-VSR-Tool.exe 即可运行。  ^|
echo +----------------------------------------------+
pause

@echo off
chcp 65001 >nul
title RTX-VSR-Tool 环境部署脚本

setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "VENV_DIR=%ROOT%venv"
set "REQUIREMENTS=%ROOT%requirements.txt"

echo +----------------------------------------------+
echo ^| RTX-VSR-Tool 环境部署脚本                      ^|
echo ^| 自动创建虚拟环境并安装所有依赖                   ^|
echo +----------------------------------------------+
echo.

:: ── 1. 检查 Python ─────────────────────────────────
echo [1/5] 检查 Python ...
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10 或更新版本。
    echo        下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

:: ── 2. 创建虚拟环境 ───────────────────────────────
echo [2/5] 检查 / 创建虚拟环境 ...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [跳过] 虚拟环境已存在: %VENV_DIR%
) else (
    echo [创建] 正在创建虚拟环境 ...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败！
        pause
        exit /b 1
    )
    echo [完成] 虚拟环境已创建
)
echo.

:: ── 3. 升级 pip ──────────────────────────────────
echo [3/5] 升级 pip ...
call "%VENV_DIR%\Scripts\python" -m pip install --upgrade pip
echo.

:: ── 4. 安装依赖 ──────────────────────────────────
echo [4/5] 安装依赖 ...

if exist "%REQUIREMENTS%" (
    echo 从 requirements.txt 安装 ...

    :: PyTorch 需要指定 --index-url，从 requirements.txt 中提取
    call "%VENV_DIR%\Scripts\pip" install -r "%REQUIREMENTS%"
    if errorlevel 1 (
        echo [警告] 部分依赖安装失败，尝试逐个安装 ...
        echo.
        echo 安装 PyTorch (CUDA 12.8) ...
        call "%VENV_DIR%\Scripts\pip" install torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128
        echo.
        echo 安装 nvidia-vfx ...
        call "%VENV_DIR%\Scripts\pip" install nvidia-vfx==0.1.0.1
        echo.
        echo 安装 opencv-python-headless ...
        call "%VENV_DIR%\Scripts\pip" install opencv-python-headless==4.13.0.92
        echo.
        echo 安装 PyQt6 ...
        call "%VENV_DIR%\Scripts\pip" install "PyQt6>=6.5"
        echo.
        call "%VENV_DIR%\Scripts\pip" install "numpy>=1.24,<3"
    )
) else (
    echo [提示] 未找到 requirements.txt，安装默认依赖 ...
    call "%VENV_DIR%\Scripts\pip" install torch torchvision --index-url https://download.pytorch.org/whl/cu128
    call "%VENV_DIR%\Scripts\pip" install nvidia-vfx
    call "%VENV_DIR%\Scripts\pip" install opencv-python-headless
    call "%VENV_DIR%\Scripts\pip" install "PyQt6>=6.5"
    call "%VENV_DIR%\Scripts\pip" install "numpy>=1.24,<3"
)
echo.

:: ── 5. 验证安装 ──────────────────────────────────
echo [5/5] 验证关键包 ...
set "MISSING="
call "%VENV_DIR%\Scripts\python" -c "import torch; print('  torch    ', torch.__version__)" 2>nul || set "MISSING=1"
call "%VENV_DIR%\Scripts\python" -c "import torchvision; print('  torchvision', torchvision.__version__)" 2>nul || set "MISSING=1"
call "%VENV_DIR%\Scripts\python" -c "import nvvfx; print('  nvvfx    ok')" 2>nul || set "MISSING=1"
call "%VENV_DIR%\Scripts\python" -c "import cv2; print('  cv2      ', cv2.__version__)" 2>nul || set "MISSING=1"
call "%VENV_DIR%\Scripts\python" -c "import PyQt6; print('  PyQt6    ok')" 2>nul || set "MISSING=1"
call "%VENV_DIR%\Scripts\python" -c "import numpy; print('  numpy    ', numpy.__version__)" 2>nul || set "MISSING=1"
echo.

if defined MISSING (
    echo +----------------------------------------------+
    echo ^| 部分包安装失败，请根据上方错误信息手动处理。     ^|
    echo +----------------------------------------------+
) else (
    echo +----------------------------------------------+
    echo ^| 环境部署成功！                                 ^|
    echo ^|                                              ^|
    echo ^| 启动程序: start.bat                           ^|
    echo ^| 激活环境: venv\Scripts\activate               ^|
    echo +----------------------------------------------+
)

echo.
echo 如需打包可执行文件，运行: build_all.bat
echo.
pause
endlocal

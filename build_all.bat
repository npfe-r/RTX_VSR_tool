@echo off
title RTX-VSR-Tool 打包工具
chcp 65001 >nul

echo ============================================
echo  RTX-VSR-Tool 一键打包脚本
echo ============================================
echo.

:: ── 轻量包 ──────────────────────────────────────
echo [1/2] 正在构建 轻量包 (Light) ...
echo       仅打包 PyQt6+numpy，其余依赖从系统加载
echo       预计大小: ~200 MB
echo.
call python -m PyInstaller --clean build_light.spec
if errorlevel 1 (
    echo [错误] 轻量包构建失败!
    pause
    exit /b 1
)
echo [完成] 轻量包: dist\RTX-VSR-Tool-Light\
echo.

:: ── 全量包 ──────────────────────────────────────
echo [2/2] 正在构建 全量包 (Full) ...
echo       包括 torch+nvvfx+cv2+ffmpeg，开箱即用
echo       预计大小: ~2.7 GB
echo.
call python -m PyInstaller --clean build_full.spec
if errorlevel 1 (
    echo [错误] 全量包构建失败!
    pause
    exit /b 1
)
echo [完成] 全量包: dist\RTX-VSR-Tool-Full\
echo.

echo ============================================
echo  全部构建完成!
echo ============================================
echo.
echo  轻量包: dist\RTX-VSR-Tool-Light\   (~200 MB)
echo     → 需系统安装: torch, nvvfx, opencv-python, ffmpeg
echo.
echo  全量包: dist\RTX-VSR-Tool-Full\    (~2.7 GB)
echo     → 开箱即用，但需要 NVIDIA GPU + CUDA 驱动
echo.
pause

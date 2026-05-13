@echo off
title RTX-VSR-Tool Builder

echo +------------------------------------------+
echo ^| RTX-VSR-Tool Build Script                ^|
echo +------------------------------------------+
echo.

:: ---- Light Build ----------------------------
echo [1/2] Building Light package ...
echo       PyQt6+numpy only, system deps required
echo.
call python -m PyInstaller --clean build_light.spec
if errorlevel 1 (
    echo [ERROR] Light build failed!
    pause
    exit /b 1
)
echo [DONE] Light package: dist\RTX-VSR-Tool-Light\
echo.

:: ---- Full Build -----------------------------
echo [2/2] Building Full package ...
echo       Bundles torch+nvvfx+cv2+ffmpeg
echo.
call python -m PyInstaller --clean build_full.spec
if errorlevel 1 (
    echo [ERROR] Full build failed!
    pause
    exit /b 1
)
echo [DONE] Full package: dist\RTX-VSR-Tool-Full\
echo.

echo +------------------------------------------+
echo ^| All builds complete!                     ^|
echo +------------------------------------------+
echo.
echo  Light: dist\RTX-VSR-Tool-Light\   (~200 MB)
echo    -> Requires: torch, nvvfx, opencv-python, ffmpeg
echo.
echo  Full:  dist\RTX-VSR-Tool-Full\    (~2.7 GB)
echo    -> Ready to use, needs NVIDIA GPU + CUDA
echo.
pause

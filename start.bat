@echo off
cd /d "H:\Project\RTX_VSR_tool"
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    pause
    exit /b 1
)
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate venv
    pause
    exit /b 1
)
echo Starting RTX VSR Tool...
python app.py 2>error.log
if errorlevel 1 (
    echo.
    type error.log
    pause
    exit /b 1
)
pause

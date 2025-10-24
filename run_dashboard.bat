@echo off
title Value Investment Dashboard
cls

echo ========================================
echo   Value Investment Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found

REM Install requirements
echo.
echo 📦 Installing required packages...
pip install -r requirements.txt >nul 2>&1

if errorlevel 1 (
    echo ❌ Failed to install some packages
    echo.
    echo Trying to install manually...
    pip install streamlit yfinance pandas numpy plotly requests
    if errorlevel 1 (
        echo ❌ Installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo ✅ All packages installed

REM Start the dashboard
echo.
echo 🚀 Starting Value Investment Dashboard...
echo.
echo The dashboard will open in your web browser shortly.
echo To stop the application, close this window or press Ctrl+C
echo.
echo ========================================

python run_desktop.py

pause
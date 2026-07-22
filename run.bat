@echo off
title DocFlow
echo ==========================================
echo    DocFlow
echo ==========================================
echo.
echo Starting, please wait...
echo.

cd /d "%~dp0"

REM Use venv Python directly (works in both CMD and PowerShell)
F:\doc_converter_env\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start.
    echo Please check:
    echo 1. Have you run install.bat to install dependencies?
    echo 2. Check error messages above.
    echo.
    pause
)

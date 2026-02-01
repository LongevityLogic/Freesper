@echo off
if not exist .venv (
    echo Virtual environment not found. Please run run_windows.bat first.
    pause
    exit /b
)
call .venv\Scripts\activate
python debug_full.py
pause

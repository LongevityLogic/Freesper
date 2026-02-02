@echo off
SETLOCAL
cd /d "%~dp0"

IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
CALL .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting WhisperTyping...
python main.py

PAUSE

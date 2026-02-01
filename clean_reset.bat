@echo off
echo Cleaning up environment...

IF EXIST ".venv" (
    echo Deleting virtual environment...
    rmdir /s /q .venv
)

echo Cleanup done.
echo Now run 'run_windows.bat' to reinstall correctly.
PAUSE

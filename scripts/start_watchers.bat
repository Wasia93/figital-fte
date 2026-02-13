@echo off
echo ==========================================
echo   Digital FTE - Watcher Runner
echo ==========================================
echo.
echo Starting all enabled watchers...
cd /d "%~dp0\.."
python -m src.watchers.watcher_runner
pause

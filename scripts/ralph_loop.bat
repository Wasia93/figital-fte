@echo off
echo ==========================================
echo   Digital FTE - Ralph Wiggum Orchestrator
echo ==========================================
echo.
echo Starting orchestrator...
cd /d "%~dp0\.."
python -m src.core.orchestrator
pause

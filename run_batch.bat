@echo off
echo ========================================
echo Starting Batch Churn Pipeline at %date% %time%
echo ========================================

:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

:: Activate the virtual environment
call .\venv\Scripts\activate

:: Run the scoring script
python src\score.py

:: Check for errors
if %errorlevel% neq 0 (
    echo Pipeline FAILED. Please check the logs.
    exit /b %errorlevel%
) else (
    echo Pipeline completed successfully.
)
@echo off
REM ============================================================================
REM Agent Framework v0.1 - Setup Script (Windows)
REM ============================================================================
REM
REM Purpose:
REM   - Creates project directories
REM   - Installs Python dependencies
REM   - Validates example configurations
REM   - Works on Windows (CMD and PowerShell)
REM
REM Usage:
REM   Double-click this file, or from command prompt:
REM   setup.bat
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo ==================================================
echo Agent Framework v0.1 - Setup
echo ==================================================
echo.

REM Get script directory
cd /d "%~dp0\.."
set PROJECT_ROOT=%cd%

echo.
echo 1. Creating project directories...
mkdir data\inbox 2>nul
mkdir data\processed 2>nul
mkdir data\errors 2>nul
mkdir logs 2>nul
echo    [OK] Directories created

echo.
echo 2. Installing Python dependencies...

REM Check if pip is available
python --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Python not found. Please install Python 3.9+
    echo    Download: https://www.python.org/downloads/
    exit /b 1
)

REM Install requirements
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo    [ERROR] Failed to install dependencies
    exit /b 1
)
echo    [OK] Dependencies installed

echo.
echo 3. Verifying Python runtime...

python -c "from runtime import Agent; print('   [OK] Runtime verified')" 2>nul
if errorlevel 1 (
    echo    [ERROR] Runtime verification failed
    exit /b 1
)

echo.
echo 4. Checking example configurations...

python -c "
import sys
sys.path.insert(0, '.')
from runtime.config import Config
try:
    Config('agents/examples/file_validator/config.yaml')
    print('   [OK] Example agent config valid')
except Exception as e:
    print(f'   [ERROR] Config error: {e}')
    sys.exit(1)
" 2>nul

if errorlevel 1 (
    exit /b 1
)

echo.
echo ==================================================
echo [SUCCESS] Setup complete!
echo ==================================================
echo.
echo Next steps:
echo   1. Run example agent:
echo      scripts\run.bat examples\file_validator
echo.
echo   2. In another terminal, test it:
echo      (Create a JSON file in data\inbox\)
echo.
echo   3. Create your own agent:
echo      scripts\new_agent.bat my_agent
echo.
pause

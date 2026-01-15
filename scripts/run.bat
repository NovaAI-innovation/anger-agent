@echo off
REM ============================================================================
REM Agent Framework - Run Agent (Windows)
REM ============================================================================
REM
REM Purpose: Run any agent by name
REM
REM Usage:
REM   run.bat examples\file_validator
REM   run.bat my_agent
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM Check arguments
if "%1"=="" (
    echo Usage: run.bat ^<agent_name^>
    echo.
    echo Examples:
    echo   run.bat examples\file_validator
    echo   run.bat examples\document_categorizer
    echo   run.bat my_agent
    echo.
    echo Available agents:
    for /d %%I in (agents\*) do echo   %%~nxI
    exit /b 1
)

REM Get agent name and validate path
set AGENT_NAME=%1
set AGENT_DIR=agents\%AGENT_NAME%

if not exist "%AGENT_DIR%" (
    echo Error: Agent not found: agents\%AGENT_NAME%
    exit /b 1
)

if not exist "%AGENT_DIR%\run.py" (
    echo Error: No run.py found in agents\%AGENT_NAME%
    exit /b 1
)

echo Starting agent: %AGENT_NAME%
echo Config: %AGENT_DIR%\config.yaml
echo.

cd /d "%AGENT_DIR%"
python run.py

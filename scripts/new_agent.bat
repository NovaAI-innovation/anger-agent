@echo off
REM ============================================================================
REM Agent Framework - Generate New Agent (Windows)
REM ============================================================================
REM
REM Purpose: Create a new agent from template
REM
REM Usage:
REM   new_agent.bat my_agent
REM   new_agent.bat data_processor
REM
REM ============================================================================

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: new_agent.bat ^<agent_name^>
    echo.
    echo Examples:
    echo   new_agent.bat my_validator
    echo   new_agent.bat data_processor
    exit /b 1
)

set AGENT_NAME=%1
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set TEMPLATE_DIR=%PROJECT_ROOT%\agents\_template
set TARGET_DIR=%PROJECT_ROOT%\agents\%AGENT_NAME%

REM Check if template exists
if not exist "%TEMPLATE_DIR%" (
    echo Error: Template not found at %TEMPLATE_DIR%
    exit /b 1
)

REM Check if agent already exists
if exist "%TARGET_DIR%" (
    echo Error: Agent already exists: agents\%AGENT_NAME%
    exit /b 1
)

REM Copy template
echo Creating new agent: %AGENT_NAME%
xcopy "%TEMPLATE_DIR%" "%TARGET_DIR%" /E /I /Y >nul
echo [OK] Created: agents\%AGENT_NAME%

echo.
echo Next steps:
echo   1. Edit configuration:
echo      agents\%AGENT_NAME%\config.yaml
echo.
echo   2. Edit documentation:
echo      agents\%AGENT_NAME%\AGENTS.md
echo.
echo   3. Run setup from agent directory:
echo      cd agents\%AGENT_NAME%
echo      setup.bat
echo.
echo   4. Run your agent:
echo      scripts\run.bat %AGENT_NAME%
echo.
echo For more help, see: docs/CREATE_AGENT.md

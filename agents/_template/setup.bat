@echo off
REM ============================================================================
REM Agent Template - Setup Script (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

echo ==================================================
echo Agent - Setup
echo ==================================================
echo.

REM Get script directory
cd /d "%~dp0"
set AGENT_DIR=%cd%

echo 1. Creating data directories...
mkdir data\inbox 2>nul
mkdir data\processed 2>nul
mkdir data\errors 2>nul
mkdir logs 2>nul
echo    [OK] Directories created

echo.
echo 2. Configuring environment...

if exist .env (
    echo    [INFO] .env file already exists
    set /p OVERWRITE="    Overwrite? (y/n): "
    if /i not "!OVERWRITE!"=="y" (
        echo    Skipping .env creation
        goto skip_env
    )
)

if exist .env.example (
    copy .env.example .env >nul
    echo    [OK] Created .env from template
) else (
    echo    [WARNING] .env.example not found
)

:skip_env
echo.
echo 3. Verifying configuration...

if not exist run.py (
    echo    [ERROR] run.py not found
    exit /b 1
)
echo    [OK] Agent runner found

echo.
echo ==================================================
echo [SUCCESS] Setup complete!
echo ==================================================
echo.
echo Next steps:
echo   1. Edit your agent configuration:
echo      notepad config.yaml
echo.
echo   2. Verify your .env file:
echo      type .env
echo.
echo   3. From project root, run the agent:
echo      scripts\run.bat ^<agent_name^>
echo.
pause

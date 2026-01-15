@echo off
REM ============================================================================
REM Document Categorizer Agent - Setup Script (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

echo ==================================================
echo Document Categorizer Agent - Setup
echo ==================================================
echo.

REM Get script directory
cd /d "%~dp0"
set AGENT_DIR=%cd%

echo 1. Creating data directories...
mkdir data\inbox 2>nul
mkdir data\processed 2>nul
mkdir data\errors 2>nul
mkdir data\review 2>nul
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
echo 3. LLM Provider Configuration (Optional)
echo    Available options:
echo      1) mock   - Fast, no API key needed (default)
echo      2) openai - GPT-3.5/GPT-4, requires OPENAI_API_KEY
echo      3) claude - Claude models, requires ANTHROPIC_API_KEY
echo.
set /p PROVIDER="    Choose provider (1-3, default=1): "

if "%PROVIDER%"=="2" (
    echo.
    echo    OpenAI Provider selected
    set /p API_KEY="    Enter OPENAI_API_KEY (leave blank to skip): "
    if not "!API_KEY!"=="" (
        echo OPENAI_API_KEY=!API_KEY! >> .env
        echo    [OK] API key added to .env
    )
) else if "%PROVIDER%"=="3" (
    echo.
    echo    Claude Provider selected
    set /p API_KEY="    Enter ANTHROPIC_API_KEY (leave blank to skip): "
    if not "!API_KEY!"=="" (
        echo ANTHROPIC_API_KEY=!API_KEY! >> .env
        echo    [OK] API key added to .env
    )
) else (
    echo.
    echo    Mock Provider selected (default)
)

echo.
echo 4. Verifying configuration...

if not exist schema.json (
    echo    [ERROR] schema.json not found
    exit /b 1
)
echo    [OK] Schema file found

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
echo   1. Verify your .env file:
echo      type .env
echo.
echo   2. From project root, run the agent:
echo      scripts\run.bat examples\document_categorizer
echo.
echo   3. In another terminal, test it:
echo      (Create a .txt file in data\inbox\)
echo.
pause

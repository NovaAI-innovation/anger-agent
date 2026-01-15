# ============================================================================
# Agent Framework v0.1 - Setup Script (PowerShell)
# ============================================================================
#
# Purpose:
#   - Creates project directories
#   - Installs Python dependencies
#   - Validates example configurations
#
# Usage:
#   .\setup.ps1
#
# Note:
#   On Windows, you may need to allow script execution:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#
# ============================================================================

param(
    [switch]$Quiet = $false
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Agent Framework v0.1 - Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Push-Location $ProjectRoot

try {
    # Step 1: Create directories
    Write-Host "1. Creating project directories..." -ForegroundColor Yellow

    $dirs = @(
        "data\inbox",
        "data\processed",
        "data\errors",
        "logs"
    )

    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Write-Host "   [OK] Directories created" -ForegroundColor Green

    # Step 2: Install Python dependencies
    Write-Host ""
    Write-Host "2. Installing Python dependencies..." -ForegroundColor Yellow

    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "   Found: $pythonVersion"
    } catch {
        Write-Host "   [ERROR] Python not found. Please install Python 3.9+" -ForegroundColor Red
        Write-Host "   Download: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }

    # Install requirements
    python -m pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "   [OK] Dependencies installed" -ForegroundColor Green

    # Step 3: Verify Python runtime
    Write-Host ""
    Write-Host "3. Verifying Python runtime..." -ForegroundColor Yellow

    python -c "from runtime import Agent; print('   [OK] Runtime verified')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [ERROR] Runtime verification failed" -ForegroundColor Red
        exit 1
    }

    # Step 4: Check example configurations
    Write-Host ""
    Write-Host "4. Checking example configurations..." -ForegroundColor Yellow

    python -c @"
import sys
sys.path.insert(0, '.')
from runtime.config import Config
try:
    Config('agents/examples/file_validator/config.yaml')
    print('   [OK] Example agent config valid')
except Exception as e:
    print(f'   [ERROR] Config error: {e}')
    sys.exit(1)
"@

    if ($LASTEXITCODE -ne 0) {
        exit 1
    }

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[SUCCESS] Setup complete!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Run example agent:"
    Write-Host "     .\scripts\run.bat examples\file_validator"
    Write-Host ""
    Write-Host "  2. In another terminal, test it:"
    Write-Host "     (Create a JSON file in data\inbox\)"
    Write-Host ""
    Write-Host "  3. Create your own agent:"
    Write-Host "     .\scripts\new_agent.bat my_agent"
    Write-Host ""
}
finally {
    Pop-Location
}

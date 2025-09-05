# Setup script for gRPC Python project on Windows
# This script creates a virtual environment and installs all required packages

# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

try {
    Write-Status "Starting gRPC project setup..."

    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>$null
        Write-Status "Found Python: $pythonVersion"
    }
    catch {
        Write-Error "Python is not installed or not in PATH. Please install Python first."
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Check if pip is installed
    try {
        $pipVersion = pip --version 2>$null
        Write-Status "Found pip: $pipVersion"
    }
    catch {
        Write-Error "pip is not installed or not in PATH. Please install pip first."
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Define virtual environment name
    $VENV_NAME = "grpc_env"

    # Check if virtual environment already exists
    if (Test-Path $VENV_NAME) {
        Write-Warning "Virtual environment '$VENV_NAME' already exists."
        $choice = Read-Host "Do you want to remove it and create a new one? (y/N)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            Write-Status "Removing existing virtual environment..."
            Remove-Item -Recurse -Force $VENV_NAME
        } else {
            Write-Status "Using existing virtual environment..."
        }
    }

    # Create virtual environment if it doesn't exist
    if (-not (Test-Path $VENV_NAME)) {
        Write-Status "Creating virtual environment '$VENV_NAME'..."
        python -m venv $VENV_NAME
        Write-Success "Virtual environment created successfully!"
    }

    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & "$VENV_NAME\Scripts\Activate.ps1"

    # Upgrade pip to latest version
    Write-Status "Upgrading pip to latest version..."
    python -m pip install --upgrade pip

    # Check if requirements.txt exists
    if (-not (Test-Path "requirment.txt")) {
        Write-Error "requirment.txt file not found in current directory!"
        Write-Error "Please make sure you're running this script from the project root directory."
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Install packages from requirements.txt
    Write-Status "Installing packages from requirment.txt..."
    pip install -r requirment.txt

    Write-Success "All packages installed successfully!"

    # Display installed packages
    Write-Status "Installed packages:"
    pip list

    # Create activation helper scripts
    @"
@echo off
call grpc_env\Scripts\activate.bat
echo Virtual environment activated!
echo To deactivate, run: deactivate
"@ | Out-File -FilePath "activate_env.bat" -Encoding ASCII

    @"
# PowerShell activation script
& "grpc_env\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "To deactivate, run: deactivate" -ForegroundColor Yellow
"@ | Out-File -FilePath "activate_env.ps1" -Encoding UTF8

    Write-Success "Setup completed successfully!"
    Write-Host ""
    Write-Status "To activate the virtual environment in the future, run:"
    Write-Host "  grpc_env\Scripts\activate.bat  (Command Prompt)" -ForegroundColor Cyan
    Write-Host "  grpc_env\Scripts\Activate.ps1  (PowerShell)" -ForegroundColor Cyan
    Write-Host "  or use the helper scripts:" -ForegroundColor Cyan
    Write-Host "  activate_env.bat  (Command Prompt)" -ForegroundColor Cyan
    Write-Host "  activate_env.ps1  (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Status "To deactivate the virtual environment, run:"
    Write-Host "  deactivate" -ForegroundColor Cyan
    Write-Host ""
    Write-Status "Happy coding! 🚀"
}
catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"
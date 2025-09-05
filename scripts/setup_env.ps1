# Setup script for gRPC Python project (PowerShell)
# Creates a virtual environment and installs required packages

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Resolve-Path "$ScriptDir\.."
$VenvName = "grpc_env"
$VenvPath = Join-Path $RootDir $VenvName
$ActivateDir = Join-Path $RootDir "activate"
$RequirementsFile = Join-Path $RootDir "requirment.txt"

Write-Host "[INFO] Starting gRPC project setup..."

# Check for Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed. Please install Python first."
    exit 1
}

# Check for pip
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] pip is not installed. Please install pip first."
    exit 1
}

# Remove existing venv if user agrees
if (Test-Path $VenvPath) {
    Write-Host "[WARNING] Virtual environment '$VenvName' already exists."
    $response = Read-Host "Do you want to remove it and create a new one? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force $VenvPath
        Write-Host "[INFO] Removed existing virtual environment."
    } else {
        Write-Host "[INFO] Using existing virtual environment."
    }
}

# Create venv if not exists
if (-not (Test-Path $VenvPath)) {
    python -m venv $VenvPath
    Write-Host "[SUCCESS] Virtual environment created successfully!"
}

# Activate venv
$activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
Write-Host "[INFO] Activating virtual environment..."
& $activateScript

# Upgrade pip
Write-Host "[INFO] Upgrading pip..."
pip install --upgrade pip

# Check requirements.txt
if (-not (Test-Path $RequirementsFile)) {
    Write-Host "[ERROR] requirment.txt file not found in $RootDir!"
    Write-Host "[ERROR] Please make sure you're running this script from the project root directory."
    exit 1
}

# Install requirements
Write-Host "[INFO] Installing packages from requirment.txt..."
pip install -r $RequirementsFile

Write-Host "[SUCCESS] All packages installed successfully!"
Write-Host "[INFO] Installed packages:"
pip list

# Create activate directory if not exists
if (-not (Test-Path $ActivateDir)) {
    New-Item -ItemType Directory -Path $ActivateDir | Out-Null
}

# Create activation helper script in activate folder
$activateHelper = Join-Path $ActivateDir "activate_env.ps1"
@"
# Helper script to activate the virtual environment
`$venvPath = "$VenvPath"
& `"$venvPath\Scripts\Activate.ps1`"
Write-Host "Virtual environment activated!"
Write-Host "To deactivate, run: deactivate"
"@ | Set-Content $activateHelper

Write-Host "[SUCCESS] Setup completed successfully!"
Write-Host ""
Write-Host "[INFO] To activate the virtual environment in the future, run:"
Write-Host "  & $activateScript"
Write-Host "  or"
Write-Host "  & $activateHelper"
Write-Host ""
Write-Host "[INFO] To deactivate the virtual environment, run:"
Write-Host "  deactivate"
Write-Host ""
Write-Host "[INFO] Happy coding! 🚀"
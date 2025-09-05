#!/bin/bash

# Setup script for gRPC Python project
# This script creates a virtual environment and installs all required packages

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

print_status "Starting gRPC project setup..."

# Define virtual environment name
VENV_NAME="grpc_env"

# Check if virtual environment already exists
if [ -d "$VENV_NAME" ]; then
    print_warning "Virtual environment '$VENV_NAME' already exists."
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing virtual environment..."
        rm -rf "$VENV_NAME"
    else
        print_status "Using existing virtual environment..."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    print_status "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    print_success "Virtual environment created successfully!"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip to latest version
print_status "Upgrading pip to latest version..."
pip install --upgrade pip

# Check if requirements.txt exists
if [ ! -f "requirment.txt" ]; then
    print_error "requirment.txt file not found in current directory!"
    print_error "Please make sure you're running this script from the project root directory."
    exit 1
fi

# Install packages from requirements.txt
print_status "Installing packages from requirment.txt..."
pip install -r requirment.txt

print_success "All packages installed successfully!"

# Display installed packages
print_status "Installed packages:"
pip list

# Create activation helper script
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Helper script to activate the virtual environment
source grpc_env/bin/activate
echo "Virtual environment activated!"
echo "To deactivate, run: deactivate"
EOF

chmod +x activate_env.sh

print_success "Setup completed successfully!"
echo
print_status "To activate the virtual environment in the future, run:"
echo "  source grpc_env/bin/activate"
echo "  or"
echo "  ./activate_env.sh"
echo
print_status "To deactivate the virtual environment, run:"
echo "  deactivate"
echo
print_status "Happy coding! 🚀"
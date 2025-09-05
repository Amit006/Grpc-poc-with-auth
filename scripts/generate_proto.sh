#!/bin/bash

# Script to generate Python gRPC code from protobuf files
# This script compiles .proto files into Python gRPC stubs

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROTO_DIR="$PROJECT_ROOT/proto"
OUT_DIR="$PROJECT_ROOT/generated"

echo -e "${BLUE}[INFO]${NC} Starting protobuf generation..."
echo -e "${BLUE}[INFO]${NC} Proto directory: $PROTO_DIR"
echo -e "${BLUE}[INFO]${NC} Output directory: $OUT_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUT_DIR"

# Create __init__.py file to make it a Python package
touch "$OUT_DIR/__init__.py"

# Check if proto files exist
if [ ! -d "$PROTO_DIR" ] || [ -z "$(ls -A "$PROTO_DIR"/*.proto 2>/dev/null)" ]; then
    echo -e "${RED}[ERROR]${NC} No .proto files found in $PROTO_DIR"
    exit 1
fi

# Generate Python gRPC code from proto files
echo -e "${BLUE}[INFO]${NC} Generating Python gRPC code..."
python3 -m grpc_tools.protoc -I "$PROTO_DIR" --python_out="$OUT_DIR" --grpc_python_out="$OUT_DIR" "$PROTO_DIR"/*.proto

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} Protobuf files generated successfully!"
    echo -e "${BLUE}[INFO]${NC} Generated files:"
    ls -la "$OUT_DIR"/*.py 2>/dev/null || echo "No Python files found in output directory"
else
    echo -e "${RED}[ERROR]${NC} Failed to generate protobuf files"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} Protobuf generation completed!"
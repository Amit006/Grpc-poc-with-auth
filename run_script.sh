#!/bin/bash

# Get the absolute path to the directory containing this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$ROOT_DIR/scripts"
SRC_SERVER_DIR="$ROOT_DIR/src/server"
SRC_CLIENT_DIR="$ROOT_DIR/src/client"

case "$1" in 
    run_server_en)
        echo "Running server with encryption..."
        PYTHONPATH="$ROOT_DIR/generated:$PYTHONPATH" python3 "$SRC_SERVER_DIR/server_enhanced.py"
        ;;
    run_server)
        echo "Running server with encryption..."
        PYTHONPATH="$ROOT_DIR/generated:$PYTHONPATH" python3 "$SRC_SERVER_DIR/server.py"
        ;;
    run_client_en)
        echo "Running server with encryption..."
        PYTHONPATH="$ROOT_DIR/generated:$PYTHONPATH" python3 "$SRC_CLIENT_DIR/client_enhanced.py"
        ;;
    run_client)
        echo "Running server with encryption..."
        PYTHONPATH="$ROOT_DIR/generated:$PYTHONPATH" python3 "$SRC_CLIENT_DIR/client.py"
        ;;
    certificate)
        echo "Generating certificates..."
        bash "$SCRIPT_DIR/generate_certificates.sh"
        ;;
    env)
        bash "$SCRIPT_DIR/setup_env.sh"
        ;;
    proto)
        bash "$SCRIPT_DIR/generate_proto.sh"
        ;;
    activate)
        bash "$ROOT_DIR/activate/activate_env.sh"
        ;;
    *)
        echo "Usage: $0 {certificate|env|proto|folder|activate}"
        exit 1
        ;;
esac

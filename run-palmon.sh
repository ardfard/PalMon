#!/usr/bin/env bash

# Exit on error, undefined variables, and pipe failures
set -euo pipefail
trap 'echo "Error on line $LINENO"' ERR

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle cleanup on exit
cleanup() {
    echo "Shutting down services..."
    # Kill any remaining python processes
    pkill -f "python -m palmon" || true
    exit 0
}

# Function to handle errors
error_handler() {
    echo "Error occurred in script at line $1"
    cleanup
    exit 1
}

# Set up trap for cleanup and errors
trap cleanup SIGINT SIGTERM
trap 'error_handler ${LINENO}' ERR

# Function to install Nix using the preferred available method
install_nix() {
    # Check if we're on macOS
    if [ "$(uname)" == "Darwin" ]; then
        if command_exists curl; then
            echo "Installing Nix on macOS using curl..."
            sh <(curl -L https://nixos.org/nix/install) --daemon || error_handler ${LINENO}
        elif command_exists wget; then
            echo "Installing Nix on macOS using wget..."
            sh <(wget -qO- https://nixos.org/nix/install) --daemon || error_handler ${LINENO}
        else
            echo "Error: Neither curl nor wget is available."
            echo "Please install curl using Homebrew: brew install curl"
            exit 1
        fi
    else
        # Linux installation
        if command_exists curl; then
            echo "Installing Nix using curl..."
            sh <(curl -L https://nixos.org/nix/install) --no-daemon || error_handler ${LINENO}
        elif command_exists wget; then
            echo "Installing Nix using wget..."
            sh <(wget -qO- https://nixos.org/nix/install) --no-daemon || error_handler ${LINENO}
        else
            echo "Error: Neither curl nor wget is available."
            echo "Please install either curl or wget first and run this script again."
            echo "Debian/Ubuntu: sudo apt-get install curl"
            echo "Fedora: sudo dnf install curl"
            exit 1
        fi
    fi
}

echo "=== Pokemon Scraper and API Server Setup ==="
echo "Step 1: Checking Nix installation..."

# Check if Nix is already installed
if command_exists nix; then
    echo "✓ Nix is already installed!"
    nix --version
else
    echo "Nix is not installed. Starting installation..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        echo "Please do not run this script as root or with sudo."
        exit 1
    fi

    # Check system type
    if [ "$(uname)" == "Darwin" ]; then
        # macOS-specific checks
        if ! command_exists xcode-select; then
            echo "Installing Xcode Command Line Tools..."
            xcode-select --install || error_handler ${LINENO}
        fi
    fi

    # Install Nix
    install_nix

    # Try sourcing again and waiting a bit if nix command isn't available immediately
    if ! command_exists nix; then
        echo "Waiting for Nix installation to complete..."
        sleep 5
    fi

    if command_exists nix; then
        echo "✓ Nix has been successfully installed!"
        nix --version
    else
        echo "Something went wrong with the Nix installation."
        echo "Please check the installation logs above for errors."
        echo "You might need to restart your shell and run this script again."
        exit 1
    fi
fi

echo "Step 2: Checking Nix flakes..."
# Check if flakes are enabled
if ! nix show-config | grep -q "experimental-features.*flakes"; then
    echo "Enabling Nix flakes..."
    mkdir -p ~/.config/nix
    echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
fi

echo "Step 3: Setting up development environment..."

# Create a temporary script file
TMP_SCRIPT=$(mktemp)
trap 'rm -f $TMP_SCRIPT' EXIT

# Write the commands to the temporary script
cat << 'INNERSCRIPT' > $TMP_SCRIPT
    set -euo pipefail
    
    echo "Installing dependencies..."
    # Always install dependencies to ensure they're up to date
    uv pip install -e .
    
    echo "Running Pokemon Scraper..."
    python -m palmon.scraper.pokemon_scraper
    
    echo "✓ Pokemon Scraper has completed!"
    echo "Starting API Server..."
    echo "API will be available at http://localhost:8000"
    echo "Documentation available at http://localhost:8000/docs"
    
    # Run the server in background
    python -m palmon.api.app &
    SERVER_PID=$!
    
    # Run smoke tests
    echo "Running smoke tests..."
    chmod +x smoke_test.sh
    ./smoke_test.sh || { kill $SERVER_PID; exit 1; }
    
    echo "Smoke tests passed!"
    
    # If running in CI, exit after smoke tests
    if [ -n "${CI:-}" ]; then
        kill $SERVER_PID
        exit 0
    fi
    
    # Otherwise, keep running for local development
    echo "Server is ready for use."
    echo "Press Ctrl+C to stop the server"
    wait $SERVER_PID
INNERSCRIPT

# Execute the script with nix develop and capture the exit code
nix develop --command bash $TMP_SCRIPT
RESULT=$?

# Exit with the captured exit code
exit $RESULT

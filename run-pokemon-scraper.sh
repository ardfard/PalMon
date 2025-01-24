#!/usr/bin/env bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Nix using the preferred available method
install_nix() {
    # Check if we're on macOS
    if [ "$(uname)" == "Darwin" ]; then
        if command_exists curl; then
            echo "Installing Nix on macOS using curl..."
            sh <(curl -L https://nixos.org/nix/install) --daemon
        elif command_exists wget; then
            echo "Installing Nix on macOS using wget..."
            sh <(wget -qO- https://nixos.org/nix/install) --daemon
        else
            echo "Error: Neither curl nor wget is available."
            echo "Please install curl using Homebrew: brew install curl"
            exit 1
        fi
    else
        # Linux installation
        if command_exists curl; then
            echo "Installing Nix using curl..."
            sh <(curl -L https://nixos.org/nix/install) --no-daemon
        elif command_exists wget; then
            echo "Installing Nix using wget..."
            sh <(wget -qO- https://nixos.org/nix/install) --no-daemon
        else
            echo "Error: Neither curl nor wget is available."
            echo "Please install either curl or wget first and run this script again."
            echo "Debian/Ubuntu: sudo apt-get install curl"
            echo "Fedora: sudo dnf install curl"
            exit 1
        fi
    fi
}

echo "=== Pokemon Scraper Setup and Runner ==="
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
            xcode-select --install
        fi
    fi

    # Install Nix
    install_nix

    echo "Sourcing Nix environment..."
    source_nix

    # Try sourcing again and waiting a bit if nix command isn't available immediately
    if ! command_exists nix; then
        echo "Waiting for Nix installation to complete..."
        sleep 5
        source_nix
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
    echo "Flakes have been enabled. Please restart your shell for changes to take effect."
    echo "Please run this script again after restarting your shell."
    exit 0
fi

echo "Step 3: Setting up development environment..."
# Enter nix development shell and run the scraper
echo "Starting Pokemon Scraper..."
nix develop --command bash -c '
    if [ ! -f .venv/pyvenv.cfg ]; then
        echo "Installing dependencies..."
        uv pip install -e .
    fi
    echo "Running Pokemon Scraper..."
    python -m scraper.pokemon_scraper
'

echo "✓ Pokemon Scraper has completed!" 

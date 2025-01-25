{
  description = "Pokemon Scraper Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, systems, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Python
            python311
            
            # Build tools
            uv
            
            # Development tools
            ruff
            black
            
            # System dependencies
            gcc
            sqlite
            stdenv.cc.cc.lib  # Adds libstdc++
            
            # Additional system libraries
            zlib
            openssl
          ];

          buildInputs = with pkgs; [
            # Python packages needed at build time
            python311Packages.greenlet
          ];

          shellHook = ''
            # Create and activate virtual environment if it doesn't exist
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              ${pkgs.python311}/bin/python -m venv .venv
            fi
            source .venv/bin/activate

            # Create database directory
            mkdir -p data

            # Set environment variables
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            export DATABASE_PATH="$PWD/data/pokemon.db"
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH

            # Install dependencies using uv
            if [ ! -f .venv/pyvenv.cfg ]; then
              echo "Installing dependencies with uv..."
              uv pip install -e .
            fi

            echo "Pokemon Scraper development environment ready!"
          '';
        };
      }
    );
} 
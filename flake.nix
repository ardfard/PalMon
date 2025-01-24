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
          ];

          shellHook = ''
            # Create and activate virtual environment if it doesn't exist
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              ${pkgs.python311}/bin/python -m venv .venv
            fi
            source .venv/bin/activate

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
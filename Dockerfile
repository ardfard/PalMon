# Use the official Nix image
FROM nixos/nix:2.14.1

# Set up Nix environment
ENV USER=root
ENV PATH=/root/.nix-profile/bin:/root/.nix-profile/sbin:/nix/var/nix/profiles/default/bin:/nix/var/nix/profiles/default/sbin:$PATH

# Enable Nix flakes globally
RUN mkdir -p /etc/nix && \
    echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

# Create and set working directory
WORKDIR /app

# Copy only files needed for flake dependency resolution
COPY flake.nix flake.lock ./

# Pre-download flake dependencies in a separate layer
RUN nix develop --profile /nix-profile --command true

# Copy only Python dependency files for caching
COPY pyproject.toml README.md ./

# Install Python dependencies in a separate layer
RUN nix develop --profile /nix-profile --command bash -c "uv pip install -e ."

# Now copy the rest of the project files
COPY . .

# Make the run-palmon.sh script executable
RUN chmod +x run-palmon.sh

# Run the setup script
CMD ["./run-palmon.sh"] 
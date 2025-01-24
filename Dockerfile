# Use a minimal base image
FROM debian:bullseye-slim

# Install dependencies for Nix
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Nix
RUN curl -L https://nixos.org/nix/install | sh

# Set up Nix environment
ENV USER=root
ENV PATH=/root/.nix-profile/bin:/root/.nix-profile/sbin:/nix/var/nix/profiles/default/bin:/nix/var/nix/profiles/default/sbin:$PATH
RUN . /root/.nix-profile/etc/profile.d/nix.sh

# Copy the project files into the container
WORKDIR /app
COPY . .

# Make the script executable
RUN chmod +x run-palmon.sh

# Run the setup script
CMD ["./run-palmon.sh"] 
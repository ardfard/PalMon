#!/usr/bin/env bash

# Exit on error
set -e

# Define the image name
IMAGE_NAME="palmon"

# Create data directory if it doesn't exist
mkdir -p ./data

# Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME .

# Run the Docker container
echo "Running the Docker container..."
docker run --rm -it \
    -v "$(pwd)/data:/app/data" \
    -p 8000:8000 \
    $IMAGE_NAME 
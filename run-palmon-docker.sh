#!/usr/bin/env bash

# Exit on error
set -e

# Define the image name
IMAGE_NAME="palmon"

# Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME .

# Run the Docker container
echo "Running the Docker container..."
docker run --rm -it $IMAGE_NAME 
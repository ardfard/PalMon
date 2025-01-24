#!/usr/bin/env bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Installing test dependencies..."
uv pip install -e ".[test]"

echo "Running tests with coverage..."
pytest --cov=pokemon_api --cov-report=term-missing --cov-report=html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo "Coverage report available in htmlcov/index.html"
else
    echo -e "${RED}Tests failed!${NC}"
    exit 1
fi 
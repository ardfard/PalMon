#!/usr/bin/env bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test API endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo "Testing: $description"
    
    response=$(curl -s -w "\n%{http_code}" "http://localhost:8000$endpoint")
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ Status $status OK${NC}"
        # Check if response is valid JSON
        echo $(echo "$body" | jq .)
        if echo "$body" | jq . >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Valid JSON response${NC}"
        else
            echo -e "${RED}✗ Invalid JSON response${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Expected status $expected_status but got $status${NC}"
        return 1
    fi
    echo
}

# Wait for server to be ready
echo "Waiting for API server to be ready..."
for i in {1..30}; do
    if curl -s "http://localhost:8000/api/pokemon" >/dev/null; then
        echo "Server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Server did not start within 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Run tests
echo "Starting smoke tests..."
echo "===================="

# Test listing Pokemon
test_endpoint "/api/pokemon?page=1&limit=10" 200 "List first 10 Pokemon" || exit 1

# Test getting specific Pokemon
test_endpoint "/api/pokemon/1" 200 "Get Bulbasaur (ID: 1)" || exit 1
test_endpoint "/api/pokemon/4" 200 "Get Charmander (ID: 4)" || exit 1

# Test invalid Pokemon ID
test_endpoint "/api/pokemon/9999" 404 "Get non-existent Pokemon" || exit 1

# Test pagination
test_endpoint "/api/pokemon?page=2&limit=5" 200 "Test pagination" || exit 1

echo -e "${GREEN}All smoke tests passed!${NC}" 
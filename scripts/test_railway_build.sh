#!/bin/bash

# ================================
# JardAIn Garden Planner - Railway Build Test
# ================================
# Test the Railway Dockerfile locally before deployment
# This helps catch build issues early

set -e  # Exit on any error

echo "🌱 JardAIn Garden Planner - Railway Build Test"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker availability..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running or not accessible"
    exit 1
fi
print_success "Docker is available"

# Clean up any existing test containers
print_status "Cleaning up any existing test containers..."
docker rm -f jardain-railway-test 2>/dev/null || true

# Build the Railway Docker image
print_status "Building Railway Docker image..."
if docker build -f Dockerfile.railway -t jardain-railway-test .; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the container startup
print_status "Testing container startup..."
if docker run -d --name jardain-railway-test -p 8001:8000 -e PORT=8000 jardain-railway-test; then
    print_success "Container started successfully"
else
    print_error "Container failed to start"
    exit 1
fi

# Wait for the application to start
print_status "Waiting for application to start..."
sleep 10

# Test the health endpoint
print_status "Testing health endpoint..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Health endpoint is responding"
    
    # Get health status
    health_response=$(curl -s http://localhost:8001/health)
    echo "Health Response: $health_response"
else
    print_warning "Health endpoint not responding yet, checking container logs..."
    docker logs jardain-railway-test
fi

# Clean up
print_status "Cleaning up test container..."
docker stop jardain-railway-test > /dev/null 2>&1
docker rm jardain-railway-test > /dev/null 2>&1

print_success "Railway build test completed!"
echo ""
echo "🚀 If all tests passed, you can now deploy to Railway with:"
echo "   railway up"
echo ""
echo "📋 If there were issues, check the Docker logs above for details." 
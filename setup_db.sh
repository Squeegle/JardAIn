#!/bin/bash

# JardAIn Database Quick Setup Script
# This script provides a quick way to set up PostgreSQL for JardAIn

set -e  # Exit on any error

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

print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}🌱 JardAIn Database Quick Setup${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    print_success "Python 3 is available"
}

# Check if we're in the right directory
check_directory() {
    if [[ ! -f "main.py" ]] || [[ ! -d "scripts" ]]; then
        print_error "Please run this script from the JardAIn project root directory"
        exit 1
    fi
    print_success "Running from correct directory"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    if [[ -f "requirements.txt" ]]; then
        python3 -m pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Main setup function
main() {
    print_header
    
    print_status "Starting JardAIn database setup..."
    
    # Basic checks
    check_python
    check_directory
    
    # Install dependencies
    install_dependencies
    
    # Check if enhanced setup script exists
    if [[ -f "scripts/setup_database_enhanced.py" ]]; then
        print_status "Running enhanced database setup script..."
        python3 scripts/setup_database_enhanced.py
    elif [[ -f "scripts/setup_database.py" ]]; then
        print_status "Running standard database setup script..."
        python3 scripts/setup_database.py
    else
        print_error "Database setup script not found!"
        print_status "Please ensure you have the setup scripts in the scripts/ directory"
        exit 1
    fi
    
    # Check if setup was successful
    if [[ $? -eq 0 ]]; then
        print_success "Database setup completed successfully!"
        echo
        print_status "Next steps:"
        echo "  1. Start the application: python3 main.py"
        echo "  2. Visit: http://localhost:8000"
        echo "  3. Check API docs: http://localhost:8000/docs"
        echo
        print_status "For troubleshooting, run: python3 scripts/quick_health_check.py"
    else
        print_error "Database setup failed!"
        print_status "For help, check:"
        echo "  - DATABASE_SETUP.md for detailed instructions"
        echo "  - scripts/README.md for testing guides"
        echo "  - Run: python3 scripts/quick_health_check.py"
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Setup interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@" 
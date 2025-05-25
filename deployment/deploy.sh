#!/bin/bash

# JardAIn Garden Planner - Deployment Script
# This script automates the deployment process for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="jardain"
IMAGE_NAME="jardain-app"
CONTAINER_NAME="jardain_app"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "JardAIn Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build           Build Docker image"
    echo "  dev             Start development environment"
    echo "  prod            Start production environment"
    echo "  stop            Stop all containers"
    echo "  clean           Clean up containers and images"
    echo "  logs            Show application logs"
    echo "  test            Run tests in container"
    echo "  backup          Backup database"
    echo "  restore         Restore database from backup"
    echo ""
    echo "Options:"
    echo "  --no-cache      Build without Docker cache"
    echo "  --pull          Pull latest base images"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build --no-cache"
    echo "  $0 dev"
    echo "  $0 prod"
    echo "  $0 logs"
}

check_requirements() {
    log_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

build_image() {
    log_info "Building Docker image..."
    
    BUILD_ARGS=""
    if [[ "$*" == *"--no-cache"* ]]; then
        BUILD_ARGS="$BUILD_ARGS --no-cache"
        log_info "Building without cache"
    fi
    
    if [[ "$*" == *"--pull"* ]]; then
        BUILD_ARGS="$BUILD_ARGS --pull"
        log_info "Pulling latest base images"
    fi
    
    docker build $BUILD_ARGS -t $IMAGE_NAME:latest .
    log_success "Docker image built successfully"
}

start_dev() {
    log_info "Starting development environment..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from env.example..."
        cp env.example .env
        log_warning "Please edit .env file with your configuration"
    fi
    
    docker-compose up -d postgres
    log_info "Waiting for database to be ready..."
    sleep 10
    
    docker-compose up -d app
    log_success "Development environment started"
    log_info "Application available at: http://localhost:8000"
    log_info "API documentation at: http://localhost:8000/docs"
}

start_prod() {
    log_info "Starting production environment..."
    
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please create it from env.production template"
        exit 1
    fi
    
    # Validate production environment
    if grep -q "your-" .env; then
        log_error "Please update .env file with your production values"
        exit 1
    fi
    
    docker-compose --profile production up -d
    log_success "Production environment started"
    log_info "Application available at: http://localhost"
}

stop_containers() {
    log_info "Stopping all containers..."
    docker-compose down
    log_success "All containers stopped"
}

clean_up() {
    log_info "Cleaning up containers and images..."
    docker-compose down -v --remove-orphans
    docker image prune -f
    docker volume prune -f
    log_success "Cleanup completed"
}

show_logs() {
    log_info "Showing application logs..."
    docker-compose logs -f app
}

run_tests() {
    log_info "Running tests in container..."
    docker-compose exec app python -m pytest tests/ -v
    log_success "Tests completed"
}

backup_database() {
    log_info "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec postgres pg_dump -U jardain_user jardain > $BACKUP_FILE
    log_success "Database backup created: $BACKUP_FILE"
}

restore_database() {
    if [ -z "$2" ]; then
        log_error "Please specify backup file: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$2"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    log_info "Restoring database from: $BACKUP_FILE"
    docker-compose exec -T postgres psql -U jardain_user jardain < $BACKUP_FILE
    log_success "Database restored successfully"
}

# Main script logic
case "$1" in
    "build")
        check_requirements
        build_image "$@"
        ;;
    "dev")
        check_requirements
        build_image
        start_dev
        ;;
    "prod")
        check_requirements
        build_image
        start_prod
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        clean_up
        ;;
    "logs")
        show_logs
        ;;
    "test")
        run_tests
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        restore_database "$@"
        ;;
    "--help"|"help"|"")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 
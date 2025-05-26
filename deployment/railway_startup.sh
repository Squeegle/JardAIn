#!/bin/bash
# JardAIn Garden Planner - Railway Production Startup Script
# Handles database initialization, migrations, and application startup

set -e  # Exit on any error

echo "🚀 Starting JardAIn Garden Planner on Railway..."

# ========================
# Environment Validation
# ========================
echo "📋 Validating environment configuration..."

# Check required environment variables
required_vars=("OPENAI_API_KEY" "DATABASE_URL")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '   - %s\n' "${missing_vars[@]}"
    echo "Please set these variables in your Railway project settings."
    exit 1
fi

echo "✅ Environment validation passed"

# ========================
# Database Setup
# ========================
echo "🗄️  Setting up database..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import asyncio
import sys
from sqlalchemy import text
from models.database import get_database_manager

async def check_db():
    try:
        db_manager = get_database_manager()
        async with db_manager.async_session_maker() as session:
            await session.execute(text('SELECT 1'))
        print('✅ Database connection successful')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

if not asyncio.run(check_db()):
    sys.exit(1)
"

# Run database migrations if alembic is configured
if [ -f "alembic.ini" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head || {
        echo "⚠️  Migration failed, but continuing startup..."
    }
else
    echo "ℹ️  No alembic configuration found, skipping migrations"
fi

# ========================
# Application Validation
# ========================
echo "🔍 Validating application configuration..."

# Check if plant data exists
if [ ! -f "/app/data/common_vegetables.json" ]; then
    echo "⚠️  Warning: Plant data file not found"
    echo "   The application may not function correctly without plant data"
fi

# Test WeasyPrint installation
echo "🧪 Testing WeasyPrint PDF generation..."
python /app/deployment/test_weasyprint.py || {
    echo "⚠️  WeasyPrint test failed, but continuing startup..."
    echo "   PDF generation may not work correctly"
}

# Validate OpenAI connection
echo "🤖 Testing OpenAI API connection..."
python -c "
import os
from openai import OpenAI

try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # Test with a minimal request
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('✅ OpenAI API connection successful')
except Exception as e:
    print(f'❌ OpenAI API connection failed: {e}')
    print('Please check your OPENAI_API_KEY')
    exit(1)
"

# ========================
# Create Required Directories
# ========================
echo "📁 Creating required directories..."
mkdir -p /tmp/logs /tmp/generated_plans
echo "✅ Directories created"

# ========================
# Start Application
# ========================
echo "🌱 Starting JardAIn Garden Planner..."
echo "🌐 Server will be available on port ${PORT:-8000}"
echo "📚 Health check endpoint: /health"

# Start the application with production settings
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --access-log \
    --log-level info \
    --no-use-colors 
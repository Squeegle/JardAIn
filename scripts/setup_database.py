#!/usr/bin/env python3
"""
Database Setup Script for JardAIn
This script helps set up the PostgreSQL database for the JardAIn application.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config import settings
from models.database import init_database, get_database_manager
from sqlalchemy import text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def print_step(step_num: int, description: str):
    """Print a formatted step description"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)


def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    print_step(1, "Checking PostgreSQL Connection")
    
    try:
        # Try to connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database='postgres'  # Connect to default postgres database
        )
        conn.close()
        print("✅ PostgreSQL server is accessible")
        return True
    except psycopg2.Error as e:
        print(f"❌ Cannot connect to PostgreSQL server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your database credentials in .env file")
        print("3. For Docker: run 'docker-compose up postgres -d'")
        return False


def create_database_if_not_exists():
    """Create the jardain database if it doesn't exist"""
    print_step(2, "Creating Database")
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (settings.postgres_db,)
        )
        
        if cursor.fetchone():
            print(f"✅ Database '{settings.postgres_db}' already exists")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE "{settings.postgres_db}"')
            print(f"✅ Created database '{settings.postgres_db}'")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False


async def test_application_database_connection():
    """Test the application's database connection"""
    print_step(3, "Testing Application Database Connection")
    
    try:
        # Initialize database manager
        db_manager = init_database(settings.database_url_computed, **settings.database_config)
        
        # Test connection
        async with db_manager.async_session_maker() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Application database connection failed: {e}")
        return False


def run_alembic_migrations():
    """Run Alembic migrations to create/update database schema"""
    print_step(4, "Running Database Migrations")
    
    try:
        # Check if we're in the right directory
        if not os.path.exists('alembic.ini'):
            print("❌ alembic.ini not found. Make sure you're in the project root directory.")
            return False
        
        # Run migrations
        print("Running Alembic migrations...")
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            if result.stdout:
                print("Migration output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


async def verify_database_schema():
    """Verify that the database schema was created correctly"""
    print_step(5, "Verifying Database Schema")
    
    try:
        db_manager = init_database(settings.database_url_computed, **settings.database_config)
        
        async with db_manager.async_session_maker() as session:
            # Check if plants table exists
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'plants'
            """))
            
            if result.fetchone():
                print("✅ Plants table exists")
                
                # Check table structure
                result = await session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'plants' 
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                print(f"✅ Plants table has {len(columns)} columns:")
                for col_name, col_type in columns:
                    print(f"   - {col_name}: {col_type}")
                
            else:
                print("❌ Plants table not found")
                return False
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False


def print_configuration_info():
    """Print current database configuration"""
    print_step(0, "Current Database Configuration")
    
    print(f"Database Host: {settings.postgres_host}")
    print(f"Database Port: {settings.postgres_port}")
    print(f"Database Name: {settings.postgres_db}")
    print(f"Database User: {settings.postgres_user}")
    print(f"Database URL: {settings.database_url_computed}")
    print(f"Configuration Valid: {settings.validate_database_config()}")


async def main():
    """Main setup function"""
    print("🌱 JardAIn Database Setup")
    print("This script will set up your PostgreSQL database for JardAIn")
    
    # Print configuration
    print_configuration_info()
    
    # Check if configuration is valid
    if not settings.validate_database_config():
        print("\n❌ Database configuration is incomplete!")
        print("Please check your .env file and ensure all database settings are configured.")
        return False
    
    # Step 1: Check PostgreSQL connection
    if not check_postgresql_connection():
        return False
    
    # Step 2: Create database if needed
    if not create_database_if_not_exists():
        return False
    
    # Step 3: Test application connection
    if not await test_application_database_connection():
        return False
    
    # Step 4: Run migrations
    if not run_alembic_migrations():
        return False
    
    # Step 5: Verify schema
    if not await verify_database_schema():
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the application: python main.py")
    print("2. Visit http://localhost:8000 to use JardAIn")
    print("3. Check the API docs at http://localhost:8000/docs")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 
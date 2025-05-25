#!/usr/bin/env python3
"""
Enhanced Database Setup Script for JardAIn
===========================================

This script provides a comprehensive, user-friendly way to set up PostgreSQL 
for the JardAIn Garden Planner application. It includes:

- Multiple PostgreSQL installation options (Docker, native, cloud)
- Automatic database configuration
- Environment file generation
- Step-by-step guidance with troubleshooting
- Verification and testing

Usage:
    python scripts/setup_database_enhanced.py

Requirements:
    - Python 3.8+
    - pip install psycopg2-binary (will be installed if missing)
"""

import os
import sys
import asyncio
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a colorful header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"🌱 {text}")
    print(f"{'='*60}{Colors.ENDC}")


def print_step(step_num: int, description: str):
    """Print a formatted step description"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}Step {step_num}: {description}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'─'*50}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def check_python_dependencies():
    """Check and install required Python dependencies"""
    print_step(1, "Checking Python Dependencies")
    
    required_packages = [
        'psycopg2-binary',
        'sqlalchemy',
        'asyncpg',
        'alembic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            missing_packages.append(package)
            print_warning(f"{package} is missing")
    
    if missing_packages:
        print_info("Installing missing packages...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages, check=True)
            print_success("All required packages installed successfully")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install packages: {e}")
            return False
    
    return True


def detect_system():
    """Detect the operating system and provide appropriate instructions"""
    system = platform.system().lower()
    print_step(2, "Detecting System Environment")
    
    print_info(f"Operating System: {platform.system()} {platform.release()}")
    print_info(f"Architecture: {platform.machine()}")
    
    if system == "linux":
        # Check if running in WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    print_info("Running in Windows Subsystem for Linux (WSL)")
                    return "wsl"
        except:
            pass
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"


def check_docker_availability():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Docker is available: {result.stdout.strip()}")
            
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_success("Docker daemon is running")
                return True
            else:
                print_warning("Docker is installed but not running")
                return False
        else:
            return False
    except FileNotFoundError:
        return False


def provide_installation_options(system_type: str):
    """Provide PostgreSQL installation options based on system type"""
    print_step(3, "PostgreSQL Installation Options")
    
    print(f"{Colors.BOLD}Choose your preferred PostgreSQL setup method:{Colors.ENDC}\n")
    
    options = []
    
    # Option 1: Docker (recommended for development)
    if check_docker_availability():
        options.append("docker")
        print(f"{Colors.OKGREEN}1. 🐳 Docker (Recommended for Development){Colors.ENDC}")
        print("   ✅ Easy setup and cleanup")
        print("   ✅ Isolated environment")
        print("   ✅ Consistent across all systems")
        print("   ✅ Includes pgAdmin web interface")
        print()
    
    # Option 2: Native installation
    options.append("native")
    print(f"{Colors.OKBLUE}2. 💻 Native Installation{Colors.ENDC}")
    print("   ✅ Better performance")
    print("   ✅ System integration")
    print("   ⚠️  Requires manual setup")
    
    if system_type == "linux":
        print("   📋 Command: sudo apt-get install postgresql postgresql-contrib")
    elif system_type == "macos":
        print("   📋 Command: brew install postgresql")
    elif system_type == "windows":
        print("   📋 Download from: https://www.postgresql.org/download/windows/")
    print()
    
    # Option 3: Cloud/Existing
    options.append("existing")
    print(f"{Colors.OKCYAN}3. ☁️  Use Existing/Cloud PostgreSQL{Colors.ENDC}")
    print("   ✅ Production-ready")
    print("   ✅ Managed service")
    print("   ⚠️  Requires connection details")
    print("   📋 Examples: AWS RDS, Google Cloud SQL, Heroku Postgres")
    print()
    
    while True:
        try:
            choice = input(f"{Colors.BOLD}Enter your choice (1-{len(options)}): {Colors.ENDC}").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            else:
                print_error("Invalid choice. Please try again.")
        except ValueError:
            print_error("Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            sys.exit(1)


def setup_docker_postgres():
    """Set up PostgreSQL using Docker"""
    print_step(4, "Setting Up PostgreSQL with Docker")
    
    # Check if docker-compose.yml exists
    compose_file = project_root / "docker-compose.yml"
    if compose_file.exists():
        print_info("Found existing docker-compose.yml")
        
        # Ask if user wants to use existing or create new
        while True:
            choice = input("Use existing docker-compose.yml? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                break
            elif choice in ['n', 'no']:
                return setup_docker_postgres_standalone()
            else:
                print_error("Please enter 'y' or 'n'")
        
        # Generate secure password for docker-compose
        import secrets
        import string
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        
        print_info("Starting PostgreSQL with docker-compose...")
        try:
            # Set environment variables for docker-compose
            env = os.environ.copy()
            env.update({
                'POSTGRES_DB': 'jardain',
                'POSTGRES_USER': 'jardain_user',
                'POSTGRES_PASSWORD': password,
                'POSTGRES_PORT': '5432'
            })
            
            result = subprocess.run([
                'docker-compose', 'up', '-d', 'postgres'
            ], cwd=project_root, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print_success("PostgreSQL container started successfully")
                
                # Wait for PostgreSQL to be ready
                print_info("Waiting for PostgreSQL to be ready...")
                import time
                for i in range(30):
                    check_cmd = [
                        'docker', 'exec', 'jardain_postgres',
                        'pg_isready', '-U', 'jardain_user', '-d', 'jardain'
                    ]
                    result = subprocess.run(check_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print_success("PostgreSQL is ready!")
                        break
                    time.sleep(1)
                    print(".", end="", flush=True)
                else:
                    print_error("PostgreSQL failed to start within 30 seconds")
                    return None
                
                return {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'jardain',
                    'username': 'jardain_user',
                    'password': password
                }
            else:
                print_error(f"Failed to start container: {result.stderr}")
                return None
        except FileNotFoundError:
            print_error("docker-compose not found. Installing...")
            return setup_docker_postgres_standalone()
    else:
        return setup_docker_postgres_standalone()


def setup_docker_postgres_standalone():
    """Set up PostgreSQL using standalone Docker container"""
    print_info("Setting up standalone PostgreSQL Docker container...")
    
    # Generate random password
    import secrets
    import string
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    container_name = "jardain_postgres"
    
    # Stop and remove existing container if it exists
    subprocess.run(['docker', 'stop', container_name], 
                  capture_output=True, text=True)
    subprocess.run(['docker', 'rm', container_name], 
                  capture_output=True, text=True)
    
    # Start new PostgreSQL container
    docker_cmd = [
        'docker', 'run', '-d',
        '--name', container_name,
        '-e', 'POSTGRES_DB=jardain',
        '-e', 'POSTGRES_USER=jardain_user',
        '-e', f'POSTGRES_PASSWORD={password}',
        '-p', '5432:5432',
        '-v', 'jardain_postgres_data:/var/lib/postgresql/data',
        'postgres:15'
    ]
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print_success("PostgreSQL container created and started")
            print_info("Waiting for PostgreSQL to be ready...")
            
            # Wait for PostgreSQL to be ready
            import time
            for i in range(30):
                check_cmd = [
                    'docker', 'exec', container_name,
                    'pg_isready', '-U', 'jardain_user', '-d', 'jardain'
                ]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print_success("PostgreSQL is ready!")
                    break
                time.sleep(1)
                print(".", end="", flush=True)
            else:
                print_error("PostgreSQL failed to start within 30 seconds")
                return None
            
            return {
                'host': 'localhost',
                'port': 5432,
                'database': 'jardain',
                'username': 'jardain_user',
                'password': password
            }
        else:
            print_error(f"Failed to create container: {result.stderr}")
            return None
    except Exception as e:
        print_error(f"Error setting up Docker container: {e}")
        return None


def setup_native_postgres(system_type: str):
    """Guide user through native PostgreSQL setup"""
    print_step(4, "Setting Up Native PostgreSQL")
    
    print_info("Please install PostgreSQL using your system's package manager:")
    
    if system_type == "linux":
        print(f"{Colors.BOLD}Ubuntu/Debian:{Colors.ENDC}")
        print("sudo apt-get update")
        print("sudo apt-get install postgresql postgresql-contrib")
        print()
        print(f"{Colors.BOLD}CentOS/RHEL/Fedora:{Colors.ENDC}")
        print("sudo dnf install postgresql postgresql-server postgresql-contrib")
        print("sudo postgresql-setup --initdb")
        print("sudo systemctl enable postgresql")
        print("sudo systemctl start postgresql")
    
    elif system_type == "macos":
        print(f"{Colors.BOLD}Using Homebrew:{Colors.ENDC}")
        print("brew install postgresql")
        print("brew services start postgresql")
        print()
        print(f"{Colors.BOLD}Using MacPorts:{Colors.ENDC}")
        print("sudo port install postgresql15 +server")
    
    elif system_type == "windows":
        print(f"{Colors.BOLD}Download and install from:{Colors.ENDC}")
        print("https://www.postgresql.org/download/windows/")
        print("Choose the latest stable version (15.x recommended)")
    
    print()
    input("Press Enter after installing PostgreSQL...")
    
    # Guide user through database setup
    print_info("Now we need to create a database and user for JardAIn")
    
    db_config = {}
    
    # Get connection details
    db_config['host'] = input("PostgreSQL host (default: localhost): ").strip() or 'localhost'
    db_config['port'] = int(input("PostgreSQL port (default: 5432): ").strip() or '5432')
    
    print()
    print_info("We need to create a database user for JardAIn.")
    print_info("You'll need PostgreSQL superuser access for this step.")
    
    admin_user = input("PostgreSQL admin username (default: postgres): ").strip() or 'postgres'
    admin_password = input("PostgreSQL admin password: ").strip()
    
    # Generate database credentials
    import secrets
    import string
    db_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    db_config['database'] = 'jardain'
    db_config['username'] = 'jardain_user'
    db_config['password'] = db_password
    
    # Create database and user
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect as admin
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=admin_user,
            password=admin_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user
        cursor.execute(f"CREATE USER {db_config['username']} WITH PASSWORD '{db_config['password']}'")
        print_success(f"Created user: {db_config['username']}")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {db_config['database']} OWNER {db_config['username']}")
        print_success(f"Created database: {db_config['database']}")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['username']}")
        print_success("Granted privileges")
        
        cursor.close()
        conn.close()
        
        return db_config
        
    except Exception as e:
        print_error(f"Failed to create database: {e}")
        print_info("You may need to create the database manually:")
        print(f"CREATE USER {db_config['username']} WITH PASSWORD '{db_config['password']}';")
        print(f"CREATE DATABASE {db_config['database']} OWNER {db_config['username']};")
        print(f"GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['username']};")
        
        # Ask user to confirm manual setup
        while True:
            choice = input("Have you created the database manually? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return db_config
            elif choice in ['n', 'no']:
                return None
            else:
                print_error("Please enter 'y' or 'n'")


def setup_existing_postgres():
    """Set up connection to existing PostgreSQL instance"""
    print_step(4, "Configuring Existing PostgreSQL Connection")
    
    print_info("Please provide your PostgreSQL connection details:")
    
    db_config = {}
    db_config['host'] = input("PostgreSQL host: ").strip()
    db_config['port'] = int(input("PostgreSQL port (default: 5432): ").strip() or '5432')
    db_config['database'] = input("Database name: ").strip()
    db_config['username'] = input("Username: ").strip()
    db_config['password'] = input("Password: ").strip()
    
    return db_config


def test_database_connection(db_config: Dict[str, Any]):
    """Test the database connection"""
    print_step(5, "Testing Database Connection")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print_success("Database connection successful!")
        print_info(f"PostgreSQL version: {version}")
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def create_env_file(db_config: Dict[str, Any]):
    """Create or update the .env file with database configuration"""
    print_step(6, "Creating Environment Configuration")
    
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    # Read the example file as a template
    if env_example.exists():
        with open(env_example, 'r') as f:
            env_content = f.read()
    else:
        # Create basic env content if example doesn't exist
        env_content = """# JardAIn Environment Configuration
# Database Configuration (PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jardain
POSTGRES_USER=jardain_user
POSTGRES_PASSWORD=your_secure_password_here

# Application Settings
APP_NAME=JardAIn Garden Planner
DEBUG=true
HOST=0.0.0.0
PORT=8000

# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
"""
    
    # Update database configuration
    lines = env_content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('POSTGRES_HOST='):
            updated_lines.append(f"POSTGRES_HOST={db_config['host']}")
        elif line.startswith('POSTGRES_PORT='):
            updated_lines.append(f"POSTGRES_PORT={db_config['port']}")
        elif line.startswith('POSTGRES_DB='):
            updated_lines.append(f"POSTGRES_DB={db_config['database']}")
        elif line.startswith('POSTGRES_USER='):
            updated_lines.append(f"POSTGRES_USER={db_config['username']}")
        elif line.startswith('POSTGRES_PASSWORD='):
            updated_lines.append(f"POSTGRES_PASSWORD={db_config['password']}")
        else:
            updated_lines.append(line)
    
    # Write the updated content
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print_success(f"Environment file created: {env_file}")
    print_info("Database configuration has been saved to .env file")


async def run_database_migrations():
    """Run Alembic migrations to set up the database schema"""
    print_step(7, "Setting Up Database Schema")
    
    try:
        # Import after dependencies are installed
        from config import settings
        from models.database import init_database
        
        # Test application database connection
        print_info("Testing application database connection...")
        db_manager = init_database(settings.database_url_computed, **settings.database_config)
        
        async with db_manager.async_session_maker() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        
        await db_manager.close()
        print_success("Application can connect to database")
        
        # Run Alembic migrations
        print_info("Running database migrations...")
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Database schema created successfully")
            if result.stdout:
                print_info("Migration output:")
                print(result.stdout)
            return True
        else:
            print_error(f"Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error setting up database schema: {e}")
        return False


def verify_setup():
    """Verify the complete database setup"""
    print_step(8, "Verifying Database Setup")
    
    try:
        # Import application modules
        from config import settings
        from models.database import init_database
        from sqlalchemy import text
        
        db_manager = init_database(settings.database_url_computed, **settings.database_config)
        
        async def check_tables():
            async with db_manager.async_session_maker() as session:
                # Check if main tables exist
                result = await session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    print_success(f"Found {len(tables)} database tables:")
                    for table in tables:
                        print(f"   - {table}")
                    return True
                else:
                    print_warning("No tables found in database")
                    return False
            
            await db_manager.close()
        
        # Run the check in a new event loop
        result = asyncio.run(check_tables())
        
        return result
        
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete! 🎉")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}Your PostgreSQL database is ready for JardAIn!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("1. 🚀 Start the application:")
    print("   python main.py")
    print()
    print("2. 🌐 Open your browser and visit:")
    print("   http://localhost:8000")
    print()
    print("3. 📚 Check the API documentation:")
    print("   http://localhost:8000/docs")
    print()
    print("4. 🧪 Run tests to verify everything works:")
    print("   python scripts/quick_health_check.py")
    print()
    
    print(f"{Colors.BOLD}Useful Commands:{Colors.ENDC}")
    print("• Test database: python scripts/setup_database.py")
    print("• View logs: tail -f logs/jardain.log")
    print("• Reset database: alembic downgrade base && alembic upgrade head")
    print()
    
    print(f"{Colors.BOLD}Troubleshooting:{Colors.ENDC}")
    print("• Check scripts/README.md for testing guides")
    print("• Run python scripts/quick_health_check.py for diagnostics")
    print("• Check logs/ directory for error details")


async def main():
    """Main setup function"""
    print_header("JardAIn Database Setup Wizard")
    
    print(f"{Colors.BOLD}Welcome to the JardAIn Database Setup Wizard!{Colors.ENDC}")
    print("This script will help you set up PostgreSQL for your JardAIn installation.\n")
    
    try:
        # Step 1: Check Python dependencies
        if not check_python_dependencies():
            print_error("Failed to install required Python packages")
            return False
        
        # Step 2: Detect system
        system_type = detect_system()
        
        # Step 3: Choose installation method
        setup_method = provide_installation_options(system_type)
        
        # Step 4: Set up PostgreSQL based on chosen method
        db_config = None
        if setup_method == "docker":
            db_config = setup_docker_postgres()
        elif setup_method == "native":
            db_config = setup_native_postgres(system_type)
        elif setup_method == "existing":
            db_config = setup_existing_postgres()
        
        if not db_config:
            print_error("Database setup failed")
            return False
        
        # Step 5: Test connection
        if not test_database_connection(db_config):
            print_error("Database connection test failed")
            return False
        
        # Step 6: Create .env file
        create_env_file(db_config)
        
        # Step 7: Run migrations
        if not await run_database_migrations():
            print_error("Database migration failed")
            return False
        
        # Step 8: Verify setup
        if not verify_setup():
            print_warning("Setup verification had issues, but database should work")
        
        # Success!
        print_next_steps()
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1) 
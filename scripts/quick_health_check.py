#!/usr/bin/env python3
"""
Quick Health Check for JardAIn Garden Planner
A simple script to verify the application is working without running full tests.
"""

import sys
import os
import asyncio
import requests
import time
from pathlib import Path

# Add current directory to path
sys.path.append('..')
sys.path.append('.')

def print_header():
    """Print a nice header for the health check"""
    print("🌱 JardAIn Garden Planner - Quick Health Check")
    print("=" * 50)

def check_application_startup():
    """Check if the application can start up properly"""
    print("\n🚀 Checking Application Startup...")
    
    try:
        # Import main components to check for import errors
        from main import app
        from config import settings
        from services.plant_service import plant_service
        
        print("   ✅ Main application imports successfully")
        print(f"   ✅ App name: {settings.app_name}")
        print(f"   ✅ LLM Provider: {settings.llm_provider}")
        print(f"   ✅ Debug mode: {settings.debug}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Application startup failed: {e}")
        return False

def check_configuration():
    """Check application configuration"""
    print("\n⚙️  Checking Configuration...")
    
    try:
        from config import settings
        
        # Check LLM configuration
        llm_configured = settings.validate_llm_config()
        print(f"   LLM Provider: {settings.llm_provider}")
        print(f"   LLM Configured: {'✅' if llm_configured else '⚠️'} {llm_configured}")
        
        # Check database configuration
        db_configured = settings.validate_database_config()
        print(f"   Database Configured: {'✅' if db_configured else '⚠️'} {db_configured}")
        
        # Check paths
        paths_ok = True
        for path_name, path_value in [
            ("Plant Data", settings.plant_data_path),
            ("Generated Plans", settings.generated_plans_path),
            ("Plant Images", settings.plant_images_path)
        ]:
            if Path(path_value).exists():
                print(f"   {path_name} Path: ✅ {path_value}")
            else:
                print(f"   {path_name} Path: ⚠️  {path_value} (not found)")
                paths_ok = False
        
        return llm_configured and paths_ok
        
    except Exception as e:
        print(f"   ❌ Configuration check failed: {e}")
        return False

async def check_plant_service():
    """Check if the plant service is working"""
    print("\n🌿 Checking Plant Service...")
    
    try:
        from services.plant_service import plant_service
        
        # Test getting a simple plant
        plant = await plant_service.get_plant_info("basil")
        
        if plant:
            print(f"   ✅ Plant service working - Retrieved: {plant.name}")
            print(f"   ✅ Plant type: {plant.plant_type}")
            print(f"   ✅ Scientific name: {plant.scientific_name}")
            return True
        else:
            print("   ⚠️  Plant service returned no data (may need LLM configuration)")
            return False
            
    except Exception as e:
        print(f"   ❌ Plant service error: {e}")
        return False

def check_static_files():
    """Check if static files are available"""
    print("\n📁 Checking Static Files...")
    
    static_files = [
        "static/index.html",
        "static/style.css", 
        "static/script.js"
    ]
    
    files_found = 0
    for file_path in static_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            files_found += 1
        else:
            print(f"   ⚠️  {file_path} (not found)")
    
    print(f"   Found {files_found}/{len(static_files)} static files")
    return files_found > 0

def check_data_files():
    """Check if data files are available"""
    print("\n📊 Checking Data Files...")
    
    try:
        from config import settings
        
        data_files = [
            settings.plant_data_path,
            "requirements.txt",
            "config.py"
        ]
        
        files_found = 0
        for file_path in data_files:
            if Path(file_path).exists():
                print(f"   ✅ {file_path}")
                files_found += 1
            else:
                print(f"   ❌ {file_path} (missing)")
        
        return files_found == len(data_files)
        
    except Exception as e:
        print(f"   ❌ Data files check failed: {e}")
        return False

async def run_health_check():
    """Run all health checks"""
    print_header()
    
    checks = []
    
    # Run all checks
    checks.append(("Application Startup", check_application_startup()))
    checks.append(("Configuration", check_configuration()))
    checks.append(("Plant Service", await check_plant_service()))
    checks.append(("Static Files", check_static_files()))
    checks.append(("Data Files", check_data_files()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Health Check Summary:")
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your JardAIn application is ready to use.")
        print("\n💡 Next steps:")
        print("   • Run: python -m uvicorn main:app --reload")
        print("   • Visit: http://localhost:8000")
        print("   • API docs: http://localhost:8000/docs")
        return True
    else:
        print("⚠️  Some checks failed. Review the issues above.")
        print("\n💡 Common fixes:")
        if not check_configuration():
            print("   • Check your .env file for LLM configuration")
            print("   • Ensure database settings are correct")
        print("   • Run: pip install -r requirements.txt")
        print("   • Check file permissions")
        return False

def main():
    """Main entry point"""
    try:
        # Run the async health check
        result = asyncio.run(run_health_check())
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
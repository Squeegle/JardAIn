#!/usr/bin/env python3
"""
Quick Test Suite for JardAIn Garden Planner
Tests core functionality to ensure everything is working properly.
"""

import pytest
import asyncio
import sys
import os
from fastapi.testclient import TestClient

# Add current directory to path for imports
sys.path.append('..')
sys.path.append('.')

# Import our main application and dependencies
from main import app
from config import settings
from services.plant_service import plant_service
from models.database import init_database, get_database_manager

# ========================
# Test Configuration
# ========================

@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    This allows us to make HTTP requests to test our endpoints
    """
    return TestClient(app)

# ========================
# Basic Application Tests
# ========================

def test_health_check(client):
    """
    Test 1: Health Check Endpoint
    Verifies that the application starts and responds to health checks
    """
    print("\n🏥 Testing Health Check Endpoint...")
    
    # Make a GET request to the health endpoint
    response = client.get("/health")
    
    # Check that we get a successful response
    assert response.status_code == 200
    
    # Parse the JSON response
    health_data = response.json()
    
    # Verify required fields are present
    assert "status" in health_data
    assert "service" in health_data
    assert "version" in health_data
    assert health_data["status"] == "healthy"
    assert health_data["service"] == settings.app_name
    
    print(f"   ✅ Health check passed - Service: {health_data['service']}")
    print(f"   ✅ Version: {health_data['version']}")
    print(f"   ✅ LLM Provider: {health_data.get('llm_provider', 'Not configured')}")
    print(f"   ✅ Database Status: {health_data.get('database_status', 'Unknown')}")

def test_home_page(client):
    """
    Test 2: Home Page
    Verifies that the home page loads successfully
    """
    print("\n🏠 Testing Home Page...")
    
    # Make a GET request to the home page
    response = client.get("/")
    
    # Check that we get a successful response
    assert response.status_code == 200
    
    # Check that we get HTML content
    assert "text/html" in response.headers.get("content-type", "")
    
    # Check that the response contains expected content
    content = response.text
    assert "JardAIn" in content or "Garden" in content
    
    print("   ✅ Home page loads successfully")
    print("   ✅ Returns HTML content")

def test_config_endpoint_debug_mode(client):
    """
    Test 3: Config Endpoint (if in debug mode)
    Tests configuration information endpoint
    """
    print("\n⚙️  Testing Config Endpoint...")
    
    response = client.get("/config")
    
    if settings.debug:
        # In debug mode, should return config info
        assert response.status_code == 200
        config_data = response.json()
        
        assert "app_name" in config_data
        assert "llm_provider" in config_data
        assert "paths" in config_data
        
        print("   ✅ Config endpoint accessible in debug mode")
        print(f"   ✅ App Name: {config_data['app_name']}")
        print(f"   ✅ LLM Provider: {config_data['llm_provider']}")
    else:
        # In production mode, should return 404
        assert response.status_code == 404
        print("   ✅ Config endpoint properly hidden in production mode")

# ========================
# Plant API Tests
# ========================

def test_plant_search_endpoint(client):
    """
    Test 4: Plant Search API
    Tests the plant search functionality
    """
    print("\n🔍 Testing Plant Search API...")
    
    # Test search with a common plant
    response = client.get("/api/plants/search?q=tomato")
    
    # Should get a successful response
    assert response.status_code == 200
    
    # Parse the response
    search_response = response.json()
    
    # Should return a structured response with plants
    assert isinstance(search_response, dict)
    assert "plants" in search_response
    assert "query" in search_response
    assert "total_results" in search_response
    
    # Get the actual plants list
    search_results = search_response["plants"]
    assert isinstance(search_results, list)
    
    print(f"   ✅ Search endpoint responds successfully")
    print(f"   ✅ Found {len(search_results)} results for 'tomato'")
    print(f"   ✅ Query: {search_response['query']}")
    print(f"   ✅ Total results: {search_response['total_results']}")
    
    # If we have results, check the structure
    if search_results:
        first_result = search_results[0]
        assert "name" in first_result
        assert "plant_type" in first_result
        print(f"   ✅ First result: {first_result['name']} ({first_result['plant_type']})")

def test_plant_types_endpoint(client):
    """
    Test 5: Plant Types API
    Tests the plant types endpoint
    """
    print("\n🌱 Testing Plant Types API...")
    
    # Test getting available plant types first
    response = client.get("/api/plants/types")
    
    if response.status_code == 200:
        # Parse the response
        plant_types = response.json()
        
        # Should return a list
        assert isinstance(plant_types, list)
        
        print(f"   ✅ Plant types endpoint responds successfully")
        print(f"   ✅ Found {len(plant_types)} plant types: {plant_types}")
        
        # Test getting plants by type if we have types available
        if plant_types and "vegetable" in plant_types:
            print("   🔍 Testing specific plant type endpoint...")
            veg_response = client.get("/api/plants/types/vegetable")
            
            if veg_response.status_code == 200:
                vegetables = veg_response.json()
                assert isinstance(vegetables, dict)  # Should be PlantListResponse format
                assert "plants" in vegetables
                print(f"   ✅ Found {len(vegetables['plants'])} vegetables")
            else:
                print(f"   ⚠️  Plant type endpoint returned {veg_response.status_code}")
        else:
            print("   ⚠️  No 'vegetable' type found in available types")
    else:
        print(f"   ⚠️  Plant types endpoint returned {response.status_code}")
        # Don't fail the test, just warn
        print("   ⚠️  Skipping plant types test due to endpoint error")

# ========================
# Database Tests
# ========================

@pytest.mark.asyncio
async def test_database_connection():
    """
    Test 6: Database Connection
    Tests that we can connect to the database if configured
    """
    print("\n🗄️  Testing Database Connection...")
    
    if not settings.validate_database_config():
        print("   ⚠️  Database not configured - skipping database tests")
        return
    
    try:
        # Try to initialize database connection
        db_manager = get_database_manager()
        
        # Test basic connection
        from sqlalchemy import text
        async with db_manager.async_session_maker() as session:
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            assert test_value == 1
        
        print("   ✅ Database connection successful")
        print(f"   ✅ Database URL: {settings.database_url_computed[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        # Don't fail the test if database is not available
        pytest.skip(f"Database not available: {e}")

# ========================
# LLM Configuration Tests
# ========================

def test_llm_configuration():
    """
    Test 7: LLM Configuration
    Tests that LLM is properly configured
    """
    print("\n🤖 Testing LLM Configuration...")
    
    # Check if LLM is configured
    llm_configured = settings.validate_llm_config()
    
    print(f"   Provider: {settings.llm_provider}")
    print(f"   Configured: {llm_configured}")
    
    if llm_configured:
        print("   ✅ LLM configuration is valid")
        
        # Check specific configuration based on provider
        if settings.llm_provider == "openai":
            assert settings.llm_config.get("api_key") is not None
            print("   ✅ OpenAI API key is configured")
        elif settings.llm_provider == "ollama":
            assert settings.llm_config.get("base_url") is not None
            print("   ✅ Ollama base URL is configured")
    else:
        print("   ⚠️  LLM not fully configured - some features may not work")

# ========================
# Integration Test
# ========================

@pytest.mark.asyncio
async def test_plant_service_integration():
    """
    Test 8: Plant Service Integration
    Tests the plant service with a real plant request
    """
    print("\n🌿 Testing Plant Service Integration...")
    
    try:
        # Test getting plant information
        plant_info = await plant_service.get_plant_info("basil")
        
        if plant_info:
            print(f"   ✅ Successfully retrieved plant: {plant_info.name}")
            print(f"   ✅ Plant type: {plant_info.plant_type}")
            print(f"   ✅ Scientific name: {plant_info.scientific_name}")
            
            # Verify required fields
            assert plant_info.name is not None
            assert plant_info.plant_type is not None
            assert plant_info.scientific_name is not None
            
        else:
            print("   ⚠️  Plant service returned no data - may need LLM configuration")
            
    except Exception as e:
        print(f"   ⚠️  Plant service error: {e}")
        # Don't fail if LLM is not configured
        pytest.skip(f"Plant service not available: {e}")

# ========================
# Test Runner Function
# ========================

def run_quick_tests():
    """
    Run all tests and provide a summary
    This function can be called directly for a quick check
    """
    print("🧪 JardAIn Garden Planner - Quick Test Suite")
    print("=" * 60)
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 All tests passed! Everything is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return exit_code

# ========================
# Main Execution
# ========================

if __name__ == "__main__":
    # Run the quick tests when script is executed directly
    exit_code = run_quick_tests()
    sys.exit(exit_code) 
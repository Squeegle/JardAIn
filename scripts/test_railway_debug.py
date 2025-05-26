#!/usr/bin/env python3
"""
Railway Debugging Script for JardAIn Garden Planner

This script tests all the components that might cause the app to hang on Railway:
1. Location service API calls
2. LLM service timeouts
3. Network connectivity
4. Environment variables
5. Full garden plan generation

Run this on Railway to identify where the hang occurs.
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, '/app' if os.path.exists('/app') else '.')

async def test_environment():
    """Test 1: Environment Variables and Configuration"""
    print("🔧 Test 1: Environment Variables and Configuration")
    print("-" * 50)
    
    try:
        from config import settings
        
        print(f"✅ App Name: {settings.app_name}")
        print(f"✅ Debug Mode: {settings.debug}")
        print(f"✅ LLM Provider: {settings.llm_provider}")
        print(f"✅ OpenAI Key Present: {bool(settings.openai_api_key)}")
        print(f"✅ OpenAI Key Length: {len(settings.openai_api_key) if settings.openai_api_key else 0}")
        print(f"✅ OpenAI Model: {settings.openai_model}")
        print(f"✅ Host: {settings.host}")
        print(f"✅ Port: {settings.port}")
        
        # Test LLM configuration
        llm_configured = settings.validate_llm_config()
        print(f"✅ LLM Configured: {llm_configured}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

async def test_network_connectivity():
    """Test 2: Basic Network Connectivity"""
    print("\n🌐 Test 2: Basic Network Connectivity")
    print("-" * 50)
    
    try:
        import httpx
        
        # Test basic HTTP connectivity
        timeout_config = httpx.Timeout(connect=5.0, read=10.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            
            # Test 1: Simple HTTP request
            print("📡 Testing basic HTTP connectivity...")
            start_time = time.time()
            response = await asyncio.wait_for(
                client.get("https://httpbin.org/get"), 
                timeout=10.0
            )
            elapsed = time.time() - start_time
            print(f"✅ Basic HTTP: {response.status_code} ({elapsed:.2f}s)")
            
            # Test 2: Location API
            print("📍 Testing location API connectivity...")
            start_time = time.time()
            try:
                response = await asyncio.wait_for(
                    client.get("http://api.zippopotam.us/us/90210"), 
                    timeout=8.0
                )
                elapsed = time.time() - start_time
                print(f"✅ Location API: {response.status_code} ({elapsed:.2f}s)")
            except asyncio.TimeoutError:
                print(f"⏰ Location API timeout after 8 seconds")
            except Exception as e:
                print(f"❌ Location API error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False

async def test_location_service():
    """Test 3: Location Service with Timeouts"""
    print("\n📍 Test 3: Location Service")
    print("-" * 50)
    
    try:
        from services.location_service import location_service
        
        test_zip = "90210"
        print(f"🔍 Testing location lookup for: {test_zip}")
        
        start_time = time.time()
        
        # Add overall timeout for the entire location lookup
        location_info = await asyncio.wait_for(
            location_service.get_location_info(test_zip),
            timeout=30.0  # 30 second max for entire location lookup
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ Location lookup completed in {elapsed:.2f}s")
        print(f"   City: {location_info.city}")
        print(f"   State: {location_info.state}")
        print(f"   Zone: {location_info.usda_zone}")
        print(f"   Climate: {location_info.climate_type}")
        print(f"   Growing Season: {location_info.growing_season_days} days")
        
        return True
        
    except asyncio.TimeoutError:
        print(f"⏰ Location service timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Location service test failed: {e}")
        return False

async def test_llm_service():
    """Test 4: LLM Service with Timeouts"""
    print("\n🤖 Test 4: LLM Service")
    print("-" * 50)
    
    try:
        from services.llm_service import llm_service
        
        # Test LLM configuration
        is_configured = llm_service.is_configured()
        print(f"🔧 LLM Configured: {is_configured}")
        
        if not is_configured:
            print("❌ LLM not configured, skipping generation test")
            return False
        
        # Test simple generation
        simple_prompt = "Generate a JSON object with plant name 'tomato' and type 'vegetable'."
        print(f"📝 Testing simple LLM generation...")
        
        start_time = time.time()
        
        # Add overall timeout for LLM generation
        response = await asyncio.wait_for(
            llm_service.generate_plant_info(simple_prompt),
            timeout=20.0  # 20 second max for LLM generation
        )
        
        elapsed = time.time() - start_time
        
        if response:
            print(f"✅ LLM generation completed in {elapsed:.2f}s")
            print(f"   Response length: {len(response)} chars")
            print(f"   Response preview: {response[:100]}...")
            return True
        else:
            print(f"❌ LLM returned empty response")
            return False
        
    except asyncio.TimeoutError:
        print(f"⏰ LLM service timeout after 20 seconds")
        return False
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

async def test_plant_service():
    """Test 5: Plant Service"""
    print("\n🌱 Test 5: Plant Service")
    print("-" * 50)
    
    try:
        from services.plant_service import plant_service
        
        # Test getting a common plant
        test_plant = "tomato"
        print(f"🔍 Testing plant lookup for: {test_plant}")
        
        start_time = time.time()
        
        plant_info = await asyncio.wait_for(
            plant_service.get_plant_info(test_plant),
            timeout=25.0  # 25 second max for plant lookup
        )
        
        elapsed = time.time() - start_time
        
        if plant_info:
            print(f"✅ Plant lookup completed in {elapsed:.2f}s")
            print(f"   Name: {plant_info.name}")
            print(f"   Type: {plant_info.plant_type}")
            print(f"   Days to harvest: {plant_info.days_to_harvest}")
            return True
        else:
            print(f"❌ Plant lookup failed")
            return False
        
    except asyncio.TimeoutError:
        print(f"⏰ Plant service timeout after 25 seconds")
        return False
    except Exception as e:
        print(f"❌ Plant service test failed: {e}")
        return False

async def test_garden_plan_generation():
    """Test 6: Full Garden Plan Generation"""
    print("\n🌻 Test 6: Full Garden Plan Generation")
    print("-" * 50)
    
    try:
        from services.garden_plan_service import garden_plan_service
        from models.garden_plan import PlanRequest
        
        # Create a simple test request
        request = PlanRequest(
            zip_code="90210",
            selected_plants=["tomato", "lettuce"],
            garden_size="small",
            experience_level="beginner"
        )
        
        print(f"🌱 Testing garden plan generation...")
        print(f"   Zip code: {request.zip_code}")
        print(f"   Plants: {request.selected_plants}")
        
        start_time = time.time()
        
        # Add overall timeout for garden plan generation
        garden_plan = await asyncio.wait_for(
            garden_plan_service.create_garden_plan(request),
            timeout=60.0  # 60 second max for full garden plan
        )
        
        elapsed = time.time() - start_time
        
        if garden_plan:
            print(f"✅ Garden plan generation completed in {elapsed:.2f}s")
            print(f"   Plan ID: {garden_plan.plan_id}")
            print(f"   Location: {garden_plan.location.city}, {garden_plan.location.state}")
            print(f"   Plants: {len(garden_plan.plant_information)}")
            print(f"   Schedules: {len(garden_plan.planting_schedules)}")
            print(f"   Instructions: {len(garden_plan.growing_instructions)}")
            return True
        else:
            print(f"❌ Garden plan generation failed")
            return False
        
    except asyncio.TimeoutError:
        print(f"⏰ Garden plan generation timeout after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Garden plan generation test failed: {e}")
        return False

async def main():
    """Run all Railway debugging tests"""
    print("🚂 Railway Debugging Script for JardAIn Garden Planner")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🌍 Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Network Connectivity", test_network_connectivity),
        ("Location Service", test_location_service),
        ("LLM Service", test_llm_service),
        ("Plant Service", test_plant_service),
        ("Garden Plan Generation", test_garden_plan_generation),
    ]
    
    results = {}
    overall_start = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n⏱️  Starting {test_name} test...")
            test_start = time.time()
            
            result = await test_func()
            test_elapsed = time.time() - test_start
            
            results[test_name] = {
                "success": result,
                "duration": test_elapsed
            }
            
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"🏁 {test_name}: {status} ({test_elapsed:.2f}s)")
            
        except Exception as e:
            test_elapsed = time.time() - test_start
            results[test_name] = {
                "success": False,
                "duration": test_elapsed,
                "error": str(e)
            }
            print(f"💥 {test_name}: CRASHED ({test_elapsed:.2f}s) - {e}")
    
    # Summary
    overall_elapsed = time.time() - overall_start
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 RAILWAY DEBUG SUMMARY")
    print("=" * 60)
    print(f"🕐 Total time: {overall_elapsed:.2f}s")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        duration = result["duration"]
        error = f" - {result.get('error', '')}" if not result["success"] and "error" in result else ""
        print(f"{status} {test_name}: {duration:.2f}s{error}")
    
    if passed == total:
        print("\n🎉 All tests passed! The app should work on Railway.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the failures above.")
        
        # Identify likely culprit
        if not results.get("Location Service", {}).get("success"):
            print("🔍 LIKELY ISSUE: Location service API calls are timing out on Railway.")
            print("   💡 Solution: The app should now use fallback location data.")
        
        if not results.get("LLM Service", {}).get("success"):
            print("🔍 LIKELY ISSUE: LLM service (OpenAI API) calls are timing out on Railway.")
            print("   💡 Solution: Check OpenAI API key and network connectivity.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 
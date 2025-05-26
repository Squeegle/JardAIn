#!/usr/bin/env python3
"""
Test script to diagnose production API issues with plant search and AI generation.
This script can be run against the production Railway deployment to check if the OpenAI integration is working.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any

# Production URL
PRODUCTION_URL = "https://jardain-app-production.up.railway.app"

async def test_api_endpoint(session: aiohttp.ClientSession, endpoint: str, description: str) -> Dict[str, Any]:
    """Test a specific API endpoint and return results"""
    print(f"\n🔍 Testing: {description}")
    print(f"📡 URL: {PRODUCTION_URL}{endpoint}")
    
    try:
        async with session.get(f"{PRODUCTION_URL}{endpoint}") as response:
            status = response.status
            
            if status == 200:
                data = await response.json()
                print(f"✅ Success (200): {description}")
                return {"success": True, "status": status, "data": data}
            else:
                text = await response.text()
                print(f"❌ Failed ({status}): {description}")
                print(f"📄 Response: {text[:200]}...")
                return {"success": False, "status": status, "error": text}
                
    except Exception as e:
        print(f"❌ Exception: {description} - {e}")
        return {"success": False, "error": str(e)}

async def test_production_api():
    """Test the production API endpoints"""
    print("🚀 Testing JardAIn Production API")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Basic health check
        health_result = await test_api_endpoint(
            session, 
            "/ping", 
            "Health Check"
        )
        
        # Test 2: LLM service configuration
        llm_test_result = await test_api_endpoint(
            session, 
            "/api/plants/debug/llm-test", 
            "LLM Service Configuration"
        )
        
        # Test 3: Plant search (static database)
        search_tomato_result = await test_api_endpoint(
            session, 
            "/api/plants/search?q=tomato", 
            "Search for 'tomato' (should be in static DB)"
        )
        
        # Test 4: Plant search with AI generation disabled
        search_pineapple_result = await test_api_endpoint(
            session, 
            "/api/plants/search?q=pineapple&include_generated=false", 
            "Search for 'pineapple' (not in static DB, AI disabled)"
        )
        
        # Test 5: Plant search with AI generation enabled
        search_pineapple_ai_result = await test_api_endpoint(
            session, 
            "/api/plants/search?q=pineapple&include_generated=true", 
            "Search for 'pineapple' (not in static DB, AI enabled)"
        )
        
        # Test 6: Direct plant lookup with AI
        direct_pineapple_result = await test_api_endpoint(
            session, 
            "/api/plants/pineapple", 
            "Direct lookup for 'pineapple' (should trigger AI)"
        )
        
        # Test 7: Plant search debugging endpoint
        debug_search_result = await test_api_endpoint(
            session, 
            "/api/plants/debug/plant-search-test?plant_name=pineapple", 
            "Debug plant search for 'pineapple'"
        )
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        tests = [
            ("Health Check", health_result),
            ("LLM Configuration", llm_test_result),
            ("Search Tomato", search_tomato_result),
            ("Search Pineapple (No AI)", search_pineapple_result),
            ("Search Pineapple (With AI)", search_pineapple_ai_result),
            ("Direct Pineapple Lookup", direct_pineapple_result),
            ("Debug Search", debug_search_result)
        ]
        
        for test_name, result in tests:
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            print(f"{status} {test_name}")
        
        # Detailed analysis
        print("\n📋 DETAILED ANALYSIS")
        print("-" * 30)
        
        if llm_test_result.get("success"):
            llm_data = llm_test_result["data"]
            config = llm_data.get("config", {})
            print(f"🤖 LLM Provider: {config.get('provider', 'unknown')}")
            print(f"🔧 Is Configured: {config.get('is_configured', False)}")
            print(f"🏭 Is Production: {config.get('is_production', False)}")
            print(f"🔑 OpenAI Key Present: {config.get('openai_key_present', False)}")
            
            test_gen = llm_data.get("test_generation", {})
            print(f"🧪 Test Generation Success: {test_gen.get('success', False)}")
            if not test_gen.get("success"):
                print(f"❌ Test Generation Error: {test_gen.get('error', 'Unknown')}")
        
        if debug_search_result.get("success"):
            debug_data = debug_search_result["data"]
            steps = debug_data.get("steps", {})
            print(f"\n🔍 Search Debug for 'pineapple':")
            print(f"   Static Search Results: {steps.get('static_search', {}).get('results_count', 0)}")
            print(f"   Direct Lookup Found: {steps.get('direct_lookup', {}).get('found', False)}")
            print(f"   LLM Service Configured: {steps.get('llm_service', {}).get('configured', False)}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 20)
        
        if not llm_test_result.get("success"):
            print("❌ LLM test endpoint failed - check if debug endpoints are enabled")
        elif not llm_test_result["data"]["config"].get("is_configured"):
            print("❌ LLM service not configured - check OPENAI_API_KEY environment variable")
        elif not search_pineapple_ai_result.get("success"):
            print("❌ AI search failed - check OpenAI API key validity and quota")
        else:
            print("✅ All tests passed - the issue might be intermittent or resolved")

if __name__ == "__main__":
    print("🧪 JardAIn Production API Test")
    print("This script tests the production deployment to diagnose plant search issues.")
    print()
    
    try:
        asyncio.run(test_production_api())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 
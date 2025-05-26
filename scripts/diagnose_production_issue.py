#!/usr/bin/env python3
"""
Production Diagnostic Script for JardAIn NetworkError
This script will help identify the exact cause of the NetworkError in your Railway deployment.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Your production URL
PRODUCTION_URL = "https://jardain-app-production.up.railway.app"

async def diagnose_production_issue():
    """
    Comprehensive diagnostic of the production NetworkError issue
    """
    print("🔍 JardAIn Production Diagnostic Tool")
    print("=" * 50)
    print(f"🌐 Testing: {PRODUCTION_URL}")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    print()

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        
        # Test 1: Basic connectivity
        print("1️⃣ Testing Basic Connectivity")
        print("-" * 30)
        try:
            async with session.get(f"{PRODUCTION_URL}/ping") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Basic connectivity: OK")
                    print(f"   Status: {data.get('status')}")
                else:
                    print(f"❌ Basic connectivity failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot reach server: {e}")
            return

        # Test 2: Health check
        print("\n2️⃣ Testing Health Check")
        print("-" * 30)
        try:
            async with session.get(f"{PRODUCTION_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check: {health_data.get('status')}")
                    print(f"   LLM Provider: {health_data.get('llm_provider')}")
                    print(f"   LLM Configured: {health_data.get('llm_configured')}")
                    print(f"   Environment: {health_data.get('environment')}")
                    
                    if not health_data.get('llm_configured'):
                        print("❌ ISSUE FOUND: LLM not configured!")
                        print("   This is likely the cause of your NetworkError")
                        print("   Solution: Set OPENAI_API_KEY in Railway environment variables")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

        # Test 3: LLM Debug endpoint (if available)
        print("\n3️⃣ Testing LLM Configuration")
        print("-" * 30)
        try:
            async with session.get(f"{PRODUCTION_URL}/api/plants/debug/llm-test") as response:
                if response.status == 200:
                    llm_data = await response.json()
                    config = llm_data.get('config', {})
                    test_gen = llm_data.get('test_generation', {})
                    
                    print(f"   Provider: {config.get('provider')}")
                    print(f"   Configured: {config.get('is_configured')}")
                    print(f"   OpenAI Key Present: {config.get('openai_key_present')}")
                    print(f"   Key Length: {config.get('openai_key_length')}")
                    print(f"   Test Generation Success: {test_gen.get('success')}")
                    
                    if not config.get('is_configured'):
                        print("❌ ISSUE CONFIRMED: OpenAI API key missing or invalid")
                    elif not test_gen.get('success'):
                        print("❌ ISSUE CONFIRMED: OpenAI API calls failing")
                        print(f"   Error: {test_gen.get('error', 'Unknown')}")
                    else:
                        print("✅ LLM configuration appears correct")
                        
                elif response.status == 404:
                    print("⚠️  Debug endpoint not available (production mode)")
                else:
                    print(f"❌ LLM test failed: {response.status}")
        except Exception as e:
            print(f"❌ LLM test error: {e}")

        # Test 4: Simple plant search
        print("\n4️⃣ Testing Plant Search (No AI)")
        print("-" * 30)
        try:
            async with session.get(f"{PRODUCTION_URL}/api/plants/search?q=tomato") as response:
                if response.status == 200:
                    search_data = await response.json()
                    print(f"✅ Plant search: Found {search_data.get('total_results', 0)} results")
                else:
                    print(f"❌ Plant search failed: {response.status}")
        except Exception as e:
            print(f"❌ Plant search error: {e}")

        # Test 5: Garden plan validation
        print("\n5️⃣ Testing Garden Plan Validation")
        print("-" * 30)
        validation_data = {
            "zip_code": "90210",
            "selected_plants": ["tomato", "lettuce"],
            "garden_size": "medium",
            "experience_level": "beginner"
        }
        
        try:
            async with session.post(
                f"{PRODUCTION_URL}/api/plans/validate",
                json=validation_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    val_data = await response.json()
                    print(f"✅ Validation: {val_data.get('valid')}")
                    print(f"   Available plants: {len(val_data.get('available_plants', []))}")
                else:
                    error_text = await response.text()
                    print(f"❌ Validation failed: {response.status}")
                    print(f"   Error: {error_text[:200]}...")
        except Exception as e:
            print(f"❌ Validation error: {e}")

        # Test 6: Attempt garden plan generation (this will likely fail)
        print("\n6️⃣ Testing Garden Plan Generation")
        print("-" * 30)
        plan_data = {
            "zip_code": "90210",
            "selected_plants": ["tomato"],
            "garden_size": "small",
            "experience_level": "beginner"
        }
        
        try:
            print("   Attempting garden plan generation...")
            async with session.post(
                f"{PRODUCTION_URL}/api/plans/",
                json=plan_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    plan_result = await response.json()
                    print(f"✅ Garden plan generated successfully!")
                    print(f"   Plan ID: {plan_result.get('plan_id')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Garden plan generation failed: {response.status}")
                    print(f"   Error: {error_text[:300]}...")
                    
                    # Try to parse error details
                    try:
                        error_json = json.loads(error_text)
                        print(f"   Detail: {error_json.get('detail', 'No details')}")
                    except:
                        pass
        except Exception as e:
            print(f"❌ Garden plan generation error: {e}")

    # Summary and recommendations
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY & SOLUTIONS")
    print("=" * 50)
    print()
    print("🔧 LIKELY SOLUTIONS:")
    print()
    print("1. Set OpenAI API Key in Railway:")
    print("   • Go to your Railway project dashboard")
    print("   • Navigate to Variables tab")
    print("   • Add: OPENAI_API_KEY = your_actual_api_key")
    print("   • Redeploy the application")
    print()
    print("2. Verify OpenAI API Key:")
    print("   • Check that your API key is valid")
    print("   • Ensure you have sufficient credits")
    print("   • Test the key with OpenAI's API directly")
    print()
    print("3. Alternative - Switch to Ollama (Local LLM):")
    print("   • Set LLM_PROVIDER=ollama in Railway variables")
    print("   • Set OLLAMA_BASE_URL to a public Ollama instance")
    print("   • This removes dependency on OpenAI")
    print()
    print("4. Check Railway Logs:")
    print("   • View deployment logs in Railway dashboard")
    print("   • Look for LLM configuration warnings")
    print("   • Check for network timeout errors")

if __name__ == "__main__":
    asyncio.run(diagnose_production_issue()) 
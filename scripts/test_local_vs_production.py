#!/usr/bin/env python3
"""
Compare local vs production API behavior to identify NetworkError issues
"""

import asyncio
import aiohttp
import json
from datetime import datetime

LOCAL_URL = "http://localhost:8000"
PRODUCTION_URL = "https://jardain-app-production.up.railway.app"

async def test_endpoint(session, base_url, endpoint, method="GET", data=None):
    """Test a specific endpoint and return results"""
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            async with session.get(url) as response:
                result = await response.json()
                return {"success": True, "status": response.status, "data": result}
        else:  # POST
            async with session.post(url, json=data, headers={"Content-Type": "application/json"}) as response:
                result = await response.json()
                return {"success": True, "status": response.status, "data": result}
                
    except Exception as e:
        return {"success": False, "error": str(e)}

async def compare_environments():
    """Compare local vs production environments"""
    
    print("🔍 Comparing Local vs Production Environments")
    print("=" * 60)
    print(f"🏠 Local: {LOCAL_URL}")
    print(f"🌐 Production: {PRODUCTION_URL}")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    print()

    # Test data
    garden_plan_data = {
        "zip_code": "90210",
        "selected_plants": ["tomato"],
        "garden_size": "small",
        "experience_level": "beginner"
    }

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
        
        tests = [
            ("Health Check", "/health", "GET", None),
            ("Plant Search", "/api/plants/search?q=tomato", "GET", None),
            ("Garden Plan Generation", "/api/plans/", "POST", garden_plan_data)
        ]

        for test_name, endpoint, method, data in tests:
            print(f"🧪 Testing: {test_name}")
            print("-" * 40)
            
            # Test local
            print("🏠 Local:")
            local_result = await test_endpoint(session, LOCAL_URL, endpoint, method, data)
            if local_result["success"]:
                print(f"   ✅ Status: {local_result['status']}")
                if test_name == "Garden Plan Generation":
                    plan_data = local_result["data"]
                    print(f"   📋 Plan ID: {plan_data.get('plan_id', 'N/A')}")
                    print(f"   📍 Location: {plan_data.get('location', {}).get('city', 'N/A')}")
            else:
                print(f"   ❌ Error: {local_result['error']}")
            
            # Test production
            print("🌐 Production:")
            prod_result = await test_endpoint(session, PRODUCTION_URL, endpoint, method, data)
            if prod_result["success"]:
                print(f"   ✅ Status: {prod_result['status']}")
                if test_name == "Garden Plan Generation":
                    plan_data = prod_result["data"]
                    print(f"   📋 Plan ID: {plan_data.get('plan_id', 'N/A')}")
                    print(f"   📍 Location: {plan_data.get('location', {}).get('city', 'N/A')}")
            else:
                print(f"   ❌ Error: {prod_result['error']}")
            
            # Compare results
            if local_result["success"] and prod_result["success"]:
                print("   🎉 Both environments working!")
            elif local_result["success"] and not prod_result["success"]:
                print("   ⚠️  Production issue detected!")
            elif not local_result["success"] and prod_result["success"]:
                print("   ⚠️  Local issue detected!")
            else:
                print("   ❌ Both environments have issues!")
            
            print()

if __name__ == "__main__":
    print("Starting local server test...")
    print("Make sure your local server is running: uvicorn main:app --reload")
    print()
    
    try:
        asyncio.run(compare_environments())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}") 
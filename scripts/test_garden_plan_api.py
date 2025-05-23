#!/usr/bin/env python3
"""
Test the garden plan generation API - the core feature of JardAIn!
"""

import sys
import os
import asyncio
import json
import httpx

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_garden_plan_api():
    """Test the garden plan generation API endpoints"""
    
    print("🧠 Testing Garden Plan Generation API")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=120) as client:  # Longer timeout for AI generation
        
        # Test 1: Location validation
        print("📍 Test 1: Location Information")
        print("-" * 30)
        
        test_locations = ["90210", "K1A 0A6", "10001"]
        
        for postal_code in test_locations:
            try:
                response = await client.get(f"{base_url}/api/plans/location/{postal_code}")
                if response.status_code == 200:
                    data = response.json()
                    flag = "🇺🇸" if len(postal_code) == 5 else "🇨🇦"
                    print(f"  {flag} {postal_code}: {data['city']}, {data['state']} (Zone {data['usda_zone']})")
                else:
                    print(f"  ❌ {postal_code}: Error {response.status_code}")
            except Exception as e:
                print(f"  ❌ {postal_code}: {e}")
        
        # Test 2: Plant suggestions
        print(f"\n💡 Test 2: Plant Suggestions")
        print("-" * 30)
        
        try:
            response = await client.get(f"{base_url}/api/plans/suggestions/90210?experience_level=beginner")
            if response.status_code == 200:
                data = response.json()
                print(f"  Beginner plants: {data['recommendations']['beginner_friendly'][:5]}...")
                print(f"  Quick growing: {data['recommendations']['quick_growing'][:5]}...")
            else:
                print(f"  ❌ Suggestions error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Suggestions error: {e}")
        
        # Test 3: Plan validation
        print(f"\n✅ Test 3: Plan Validation")
        print("-" * 30)
        
        validation_request = {
            "zip_code": "90210",
            "selected_plants": ["tomato", "basil", "lettuce"],
            "garden_size": "medium",
            "experience_level": "beginner"
        }
        
        try:
            response = await client.post(f"{base_url}/api/plans/validate", json=validation_request)
            if response.status_code == 200:
                data = response.json()
                print(f"  Valid: {data['valid']}")
                print(f"  Available plants: {data['available_plants']}")
                print(f"  Estimated time: {data['estimated_generation_time_seconds']}s")
                if data['warnings']:
                    print(f"  Warnings: {data['warnings']}")
            else:
                print(f"  ❌ Validation error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Validation error: {e}")
        
        # Test 4: The Main Event - Garden Plan Generation!
        print(f"\n🌱 Test 4: GARDEN PLAN GENERATION (The Main Feature!)")
        print("-" * 50)
        
        plan_request = {
            "zip_code": "90210",
            "selected_plants": ["tomato", "basil", "lettuce"],
            "garden_size": "medium", 
            "experience_level": "beginner"
        }
        
        try:
            print("  🤖 Generating AI-powered garden plan...")
            print("  (This may take 30-60 seconds as the AI creates your personalized plan)")
            
            response = await client.post(f"{base_url}/api/plans/", json=plan_request)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n  🎉 SUCCESS! Garden plan created!")
                print(f"  📋 Plan ID: {data['plan_id']}")
                print(f"  📍 Location: {data['location']['city']}, {data['location']['state']}")
                print(f"  🌱 Plants: {', '.join(data['selected_plants'])}")
                print(f"  📅 Growing season: {data['location']['growing_season_days']} days")
                
                # Show planting schedule sample
                if data['planting_schedules']:
                    print(f"\n  📅 Sample Planting Schedule:")
                    for schedule in data['planting_schedules'][:2]:  # Show first 2
                        print(f"    • {schedule['plant_name']}:")
                        if schedule['start_indoors_date']:
                            print(f"      Start indoors: {schedule['start_indoors_date']}")
                        if schedule['direct_sow_date']:
                            print(f"      Direct sow: {schedule['direct_sow_date']}")
                        if schedule['harvest_start_date']:
                            print(f"      Harvest: {schedule['harvest_start_date']}")
                
                # Show growing instructions sample
                if data['growing_instructions']:
                    print(f"\n  📋 Sample Growing Instructions:")
                    first_instruction = data['growing_instructions'][0]
                    print(f"    • {first_instruction['plant_name']}:")
                    print(f"      Prep: {first_instruction['preparation_steps'][0] if first_instruction['preparation_steps'] else 'N/A'}")
                    print(f"      Plant: {first_instruction['planting_steps'][0] if first_instruction['planting_steps'] else 'N/A'}")
                
                # Show general tips
                if data['general_tips']:
                    print(f"\n  💡 General Tips:")
                    for tip in data['general_tips'][:3]:  # Show first 3
                        print(f"    • {tip}")
                
                print(f"\n  ✨ Your personalized garden plan is ready!")
                
            else:
                print(f"  ❌ Plan generation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"  Error response: {response.text}")
                    
        except Exception as e:
            print(f"  ❌ Plan generation error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Garden Plan API test completed!")
    
    print("\n🚀 Try these endpoints in your browser:")
    print("   • Location info: http://localhost:8000/api/plans/location/90210")
    print("   • Plant suggestions: http://localhost:8000/api/plans/suggestions/90210")
    print("   • API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        asyncio.run(test_garden_plan_api())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
#!/usr/bin/env python3
"""
Test the improved garden plan generation with better AI responses and Canadian support.
"""

import sys
import os
import asyncio
import json
import httpx

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_improvements():
    """Test the improved garden plan generation"""
    
    print("🔧 Testing Garden Plan Improvements")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=180) as client:  # Longer timeout for detailed AI generation
        
        # Test 1: Canadian postal code support
        print("🇨🇦 Test 1: Canadian Postal Code Support")
        print("-" * 40)
        
        canadian_codes = ["K1A 0A6", "M5V 3A8", "V6B 1A1"]
        
        for postal_code in canadian_codes:
            try:
                response = await client.get(f"{base_url}/api/plans/location/{postal_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {postal_code}: {data['city']}, {data['state']} (Zone {data['usda_zone']})")
                else:
                    print(f"  ❌ {postal_code}: Error {response.status_code}")
            except Exception as e:
                print(f"  ❌ {postal_code}: {e}")
        
        # Test 2: Enhanced AI Garden Plan Generation
        print(f"\n🧠 Test 2: Enhanced AI Garden Plan Generation")
        print("-" * 50)
        
        plan_request = {
            "zip_code": "K1A 0A6",  # Test with Canadian postal code
            "selected_plants": ["tomato", "basil"],  # Fewer plants for faster testing
            "garden_size": "medium", 
            "experience_level": "beginner"
        }
        
        try:
            print("  🤖 Generating enhanced AI garden plan...")
            print("  (This should now provide detailed, specific instructions)")
            
            response = await client.post(f"{base_url}/api/plans/", json=plan_request)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n  🎉 SUCCESS! Enhanced garden plan created!")
                print(f"  📋 Plan ID: {data['plan_id']}")
                print(f"  📍 Location: {data['location']['city']}, {data['location']['state']}")
                
                # Check quality of growing instructions
                if data['growing_instructions']:
                    print(f"\n  📋 Quality Check - Growing Instructions:")
                    for instruction in data['growing_instructions']:
                        print(f"\n    🌱 {instruction['plant_name']}:")
                        
                        # Check preparation steps
                        prep_step = instruction['preparation_steps'][0] if instruction['preparation_steps'] else "None"
                        if len(prep_step) > 50 and any(word in prep_step.lower() for word in ['specific', 'temperature', 'ph', 'inches', 'weeks']):
                            print(f"      ✅ Detailed prep: {prep_step[:80]}...")
                        else:
                            print(f"      ⚠️  Generic prep: {prep_step}")
                        
                        # Check planting steps
                        plant_step = instruction['planting_steps'][0] if instruction['planting_steps'] else "None"
                        if len(plant_step) > 50 and any(word in plant_step.lower() for word in ['temperature', 'depth', 'weeks', 'frost']):
                            print(f"      ✅ Detailed planting: {plant_step[:80]}...")
                        else:
                            print(f"      ⚠️  Generic planting: {plant_step}")
                
                # Check planting schedules
                if data['planting_schedules']:
                    print(f"\n  📅 Planting Schedules:")
                    for schedule in data['planting_schedules']:
                        print(f"    • {schedule['plant_name']}:")
                        if schedule['start_indoors_date']:
                            print(f"      Start indoors: {schedule['start_indoors_date']}")
                        if schedule['direct_sow_date']:
                            print(f"      Direct sow: {schedule['direct_sow_date']}")
                        if schedule['harvest_start_date']:
                            print(f"      Harvest starts: {schedule['harvest_start_date']}")
                
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
    print("🎉 Improvement test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_improvements())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
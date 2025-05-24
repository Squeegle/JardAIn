#!/usr/bin/env python3
"""
Test AI plant integration in garden plans
This script tests the complete flow from AI plant generation to garden plan creation.
"""

import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.plant_service import plant_service
from services.garden_plan_service import GardenPlanService
from models.garden_plan import PlanRequest

async def test_ai_plant_garden_plan():
    """Test that AI-generated plants are included in garden plans"""
    
    print("🧪 Testing AI Plant → Garden Plan Integration")
    print("=" * 60)
    
    # Step 1: Generate an AI plant
    test_plant_name = "Purple Kale"
    print(f"🤖 Step 1: Generating AI plant '{test_plant_name}'...")
    
    ai_plant = await plant_service.get_plant_info(test_plant_name)
    if not ai_plant:
        print(f"❌ Failed to generate AI plant for '{test_plant_name}'")
        return False
    
    print(f"✅ AI plant generated: {ai_plant.name}")
    print(f"   Type: {ai_plant.plant_type}")
    print(f"   Days to harvest: {ai_plant.days_to_harvest}")
    
    # Step 2: Create garden plan with the AI plant
    print(f"\n🌱 Step 2: Creating garden plan with AI plant...")
    
    # Add a static plant too for comparison
    static_plant = "Tomato"
    selected_plants = [ai_plant.name, static_plant]
    
    plan_request = PlanRequest(
        zip_code="12345",  # Example zip code
        selected_plants=selected_plants,
        garden_size="medium",
        experience_level="beginner"
    )
    
    garden_plan_service = GardenPlanService()
    
    try:
        garden_plan = await garden_plan_service.create_garden_plan(plan_request)
        
        # Step 3: Verify results
        print(f"\n📋 Step 3: Verifying garden plan results...")
        
        plan_plant_names = [p.name for p in garden_plan.plant_information]
        print(f"Requested plants: {selected_plants}")
        print(f"Plants in plan: {plan_plant_names}")
        
        # Check if AI plant is included
        ai_plant_included = ai_plant.name in plan_plant_names
        static_plant_included = static_plant in plan_plant_names
        
        print(f"\n✅ Results:")
        print(f"   Static plant '{static_plant}' included: {static_plant_included}")
        print(f"   AI plant '{ai_plant.name}' included: {ai_plant_included}")
        print(f"   Total plants in plan: {len(garden_plan.plant_information)}")
        
        if ai_plant_included and static_plant_included:
            print(f"\n🎉 SUCCESS: Both AI and static plants are in the garden plan!")
            
            # Show some plan details
            print(f"\n📅 Planting schedules generated: {len(garden_plan.planting_schedules)}")
            print(f"📋 Growing instructions generated: {len(garden_plan.growing_instructions)}")
            
            return True
        else:
            print(f"\n❌ FAILURE: Missing plants in garden plan")
            if not ai_plant_included:
                print(f"   - AI plant '{ai_plant.name}' is missing!")
            if not static_plant_included:
                print(f"   - Static plant '{static_plant}' is missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating garden plan: {e}")
        return False

async def test_cache_functionality():
    """Test that the cache is working correctly"""
    
    print("\n🗄️ Testing Cache Functionality")
    print("=" * 40)
    
    # Test plant name variations
    test_variations = [
        "purple kale",
        "Purple Kale", 
        "PURPLE KALE",
        "Purple kale",
        " Purple Kale "  # with spaces
    ]
    
    # Generate one plant
    original_name = test_variations[0]
    print(f"🤖 Generating plant for '{original_name}'...")
    original_plant = await plant_service.get_plant_info(original_name)
    
    if not original_plant:
        print(f"❌ Failed to generate plant")
        return False
    
    print(f"✅ Plant generated: {original_plant.name}")
    
    # Test cache retrieval with different variations
    print(f"\n💾 Testing cache retrieval with name variations...")
    
    cache_results = {}
    for variation in test_variations[1:]:  # Skip the original
        print(f"   Testing '{variation}'...")
        cached_plant = await plant_service.get_plant_info(variation)
        cache_results[variation] = cached_plant is not None
        
        if cached_plant:
            print(f"   ✅ Found in cache")
        else:
            print(f"   ❌ Not found in cache")
    
    successful_lookups = sum(cache_results.values())
    total_lookups = len(cache_results)
    
    print(f"\n📊 Cache Results: {successful_lookups}/{total_lookups} variations found")
    
    if successful_lookups == total_lookups:
        print("🎉 Cache working perfectly!")
        return True
    else:
        print("⚠️  Cache has some issues with name variations")
        return False

async def main():
    """Run all tests"""
    
    print("🌱 JardAIn AI Plant Integration Tests")
    print("=" * 50)
    
    # Test 1: Basic AI plant generation and garden plan inclusion
    test1_success = await test_ai_plant_garden_plan()
    
    # Test 2: Cache functionality
    test2_success = await test_cache_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ AI Plant → Garden Plan: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Cache Functionality: {'PASS' if test2_success else 'FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! AI plant integration is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    return test1_success and test2_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
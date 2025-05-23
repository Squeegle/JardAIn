"""
Debug the actual garden plan service methods to find the difference
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.garden_plan_service import garden_plan_service
from services.location_service import location_service
from services.plant_service import plant_service
from models.garden_plan import PlanRequest

async def debug_actual_methods():
    """Debug the actual garden plan service methods"""
    
    print("🔍 Debugging Actual Garden Plan Service Methods...")
    print("=" * 60)
    
    # Set up test data exactly like the garden plan service
    request = PlanRequest(
        zip_code="K1A 0A6",
        selected_plants=["Tomato", "Lettuce"],
        garden_size="medium",
        experience_level="beginner"
    )
    
    # Get the same data the service gets
    location_info = await location_service.get_location_info(request.zip_code)
    plant_information = await plant_service.get_multiple_plants(request.selected_plants)
    
    print(f"📍 Location: {location_info.city}, {location_info.state}")
    print(f"🌱 Plants: {[p.name for p in plant_information]}")
    print()
    
    # Test 1: Call the actual planting schedules method
    print("1️⃣ TESTING ACTUAL _generate_planting_schedules METHOD")
    print("-" * 50)
    
    try:
        schedules = await garden_plan_service._generate_planting_schedules(
            plant_information, location_info, request
        )
        print(f"✅ Schedules generated: {len(schedules)} schedules")
        for schedule in schedules:
            print(f"   📅 {schedule.plant_name}: {schedule.direct_sow_date or schedule.start_indoors_date}")
    except Exception as e:
        print(f"❌ Schedules failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Call the actual layout recommendations method
    print("2️⃣ TESTING ACTUAL _generate_layout_recommendations METHOD")
    print("-" * 50)
    
    try:
        layout = await garden_plan_service._generate_layout_recommendations(
            plant_information, request
        )
        print(f"✅ Layout generated: {type(layout)}")
        print(f"   📐 Dimensions: {layout.get('garden_dimensions', 'N/A')}")
        print(f"   👥 Groups: {len(layout.get('plant_groupings', []))}")
    except Exception as e:
        print(f"❌ Layout failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Call the actual general tips method
    print("3️⃣ TESTING ACTUAL _generate_general_tips METHOD")
    print("-" * 50)
    
    try:
        tips = await garden_plan_service._generate_general_tips(
            plant_information, location_info, request
        )
        print(f"✅ Tips generated: {len(tips)} tips")
        for i, tip in enumerate(tips[:3], 1):
            print(f"   💡 {i}. {tip[:80]}...")
    except Exception as e:
        print(f"❌ Tips failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🎯 Method testing complete!")

if __name__ == "__main__":
    asyncio.run(debug_actual_methods()) 
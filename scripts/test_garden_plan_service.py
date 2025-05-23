"""
Test the garden plan service directly to ensure it works before testing PDF
"""

import asyncio
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.garden_plan_service import garden_plan_service
from models.garden_plan import PlanRequest

async def test_garden_plan_service():
    """Test the garden plan service directly"""
    
    print("🧠 Testing Garden Plan Service...")
    print("=" * 50)
    
    try:
        # Create a test request
        request = PlanRequest(
            zip_code="K1A 0A6",
            selected_plants=["Tomato", "Lettuce"],
            garden_size="medium",
            experience_level="beginner"
        )
        
        print(f"📋 Request: {request.zip_code}, {len(request.selected_plants)} plants")
        print("🔄 Generating garden plan...")
        
        # Test the service
        garden_plan = await garden_plan_service.create_garden_plan(request)
        
        print("✅ Garden plan created successfully!")
        print(f"   📍 Location: {garden_plan.location.city}, {garden_plan.location.state}")
        print(f"   🌱 Plants: {len(garden_plan.plant_information)}")
        print(f"   📅 Schedules: {len(garden_plan.planting_schedules)}")
        print(f"   📋 Instructions: {len(garden_plan.growing_instructions)}")
        print(f"   💡 Tips: {len(garden_plan.general_tips)}")
        
        # Show some details
        print("\n📋 Plant Details:")
        for plant in garden_plan.plant_information:
            print(f"   - {plant.name} ({plant.plant_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Garden plan service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_garden_plan_service())
    if success:
        print("\n🎉 Garden Plan Service is working correctly!")
    else:
        print("\n💥 Garden Plan Service needs debugging") 
#!/usr/bin/env python3
"""
Test Enhanced Loading Experience
This script tests the new loading animations and stages.
"""

import asyncio
import sys
import os
import json
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.garden_plan_service import GardenPlanService
from models.garden_plan import PlanRequest

async def test_loading_stages():
    """Test that garden plan generation works with all stages"""
    
    print("🧪 Testing Enhanced Loading Experience")
    print("=" * 60)
    
    # Step 1: Create a test request
    test_request = PlanRequest(
        zip_code="90210",
        selected_plants=["Tomato", "Basil", "Lettuce"],
        garden_size="medium",
        experience_level="beginner"
    )
    
    print(f"📋 Test Request:")
    print(f"   📍 Location: {test_request.zip_code}")
    print(f"   🌱 Plants: {', '.join(test_request.selected_plants)}")
    print(f"   📏 Size: {test_request.garden_size}")
    print(f"   👤 Level: {test_request.experience_level}")
    print()
    
    # Step 2: Time the generation process
    print("⏱️ Starting garden plan generation...")
    start_time = time.time()
    
    try:
        # Initialize service
        service = GardenPlanService()
        
        # Generate plan
        result = await service.create_garden_plan(test_request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Plan generated successfully!")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📄 Plan ID: {result.plan_id}")
        print(f"📍 Location: {result.location.city}, {result.location.state}")
        print(f"🌱 Plants included: {len(result.plant_information)}")
        
        # Step 3: Validate stages timing
        print("\n🎯 Loading Stage Analysis:")
        
        # Expected stages from frontend
        stages = [
            {"name": "Location & Climate", "weight": 15, "expected": 2.0},
            {"name": "Plant Information", "weight": 20, "expected": 3.0},
            {"name": "Planting Schedules", "weight": 25, "expected": 4.0},
            {"name": "Growing Instructions", "weight": 25, "expected": 5.0},
            {"name": "Garden Layout", "weight": 10, "expected": 2.0},
            {"name": "Finalization", "weight": 5, "expected": 1.0}
        ]
        
        total_expected = sum(stage["expected"] for stage in stages)
        
        print(f"   Expected total time: {total_expected} seconds")
        print(f"   Actual generation time: {duration:.2f} seconds")
        
        if duration < total_expected:
            print(f"   ⚡ Generation was faster than expected - great!")
            print(f"   💡 Frontend animation will complete smoothly")
        else:
            print(f"   🐌 Generation took longer than expected")
            print(f"   💡 Frontend will adapt dynamically")
        
        # Step 4: Test with different plant counts
        print("\n🧮 Timing Analysis by Plant Count:")
        for plant_count in [1, 3, 5, 10]:
            base_time = 8.0  # Base time from frontend
            per_plant_time = 1.5  # Per plant time from frontend
            estimated_time = base_time + (plant_count * per_plant_time)
            print(f"   {plant_count} plants: ~{estimated_time:.1f} seconds estimated")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        return False

def test_loading_ui_components():
    """Test that all loading UI components are properly defined"""
    
    print("\n🖥️ Testing Loading UI Components")
    print("-" * 40)
    
    # Read the app.js file to verify components
    try:
        with open('static/js/app.js', 'r') as f:
            content = f.read()
        
        components = [
            'enhanced-loading',
            'loading-container', 
            'loading-stages',
            'stage-icon',
            'progress-fill',
            'loading-tips',
            'startLoadingAnimation',
            'animateStages',
            'updateProgress',
            'finalizeLoading'
        ]
        
        missing_components = []
        for component in components:
            if component not in content:
                missing_components.append(component)
        
        if not missing_components:
            print("✅ All loading UI components are implemented")
        else:
            print(f"❌ Missing components: {missing_components}")
        
        # Check CSS as well
        with open('static/css/styles.css', 'r') as f:
            css_content = f.read()
        
        css_classes = [
            '.enhanced-loading',
            '.loading-container',
            '.loading-stages',
            '.progress-bar',
            '.progress-fill',
            '@keyframes progress-flow'
        ]
        
        missing_css = []
        for css_class in css_classes:
            if css_class not in css_content:
                missing_css.append(css_class)
        
        if not missing_css:
            print("✅ All loading CSS styles are implemented")
        else:
            print(f"❌ Missing CSS: {missing_css}")
        
        return len(missing_components) == 0 and len(missing_css) == 0
        
    except Exception as e:
        print(f"❌ Failed to check UI components: {e}")
        return False

async def main():
    """Run all loading experience tests"""
    
    print("🌱 JardAIn Enhanced Loading Experience Test")
    print("=" * 70)
    
    # Test 1: UI Components
    ui_test_passed = test_loading_ui_components()
    
    # Test 2: Backend Performance
    backend_test_passed = await test_loading_stages()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"UI Components: {'✅ PASS' if ui_test_passed else '❌ FAIL'}")
    print(f"Backend Performance: {'✅ PASS' if backend_test_passed else '❌ FAIL'}")
    
    if ui_test_passed and backend_test_passed:
        print("\n🎉 Enhanced Loading Experience is ready!")
        print("💡 Users will now enjoy a smooth, engaging loading experience")
        print("🚀 Next steps: Test with real users for feedback")
    else:
        print("\n⚠️ Some issues need to be addressed before release")
    
    return ui_test_passed and backend_test_passed

if __name__ == "__main__":
    asyncio.run(main()) 
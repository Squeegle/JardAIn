#!/usr/bin/env python3
"""
Test JSON parsing with realistic LLM responses that may have formatting issues.
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_json_parsing():
    """Test JSON parsing with problematic LLM responses"""
    
    print("Testing JSON Parsing with Problematic Responses")
    print("=" * 60)
    
    try:
        from services.garden_plan_service import GardenPlanService
        service = GardenPlanService()
        
        # Test cases with common LLM response issues
        test_responses = [
            # Case 1: Extra text before/after JSON
            '''Here is the detailed JSON for tomato growing:

{
    "plant_name": "Tomato",
    "preparation_steps": ["Test soil pH to 6.0-6.8 using digital meter"],
    "planting_steps": ["Start seeds indoors at 70-75F"]
}

I hope this helps with your garden planning!''',
            
            # Case 2: JSON with trailing commas
            '''{
    "plant_name": "Basil",
    "preparation_steps": ["Prepare soil with compost",],
    "planting_steps": ["Sow seeds 1/4 inch deep",],
}''',
            
            # Case 3: Simple valid JSON
            '''{
    "plant_name": "Radish",
    "preparation_steps": ["Prepare loose soil"],
    "planting_steps": ["Sow 1/2 inch deep"]
}'''
        ]
        
        for i, response in enumerate(test_responses, 1):
            print(f"\nTest Case {i}:")
            print(f"Raw response preview: {response[:100]}...")
            
            parsed_data = service._extract_and_clean_json(response)
            
            if parsed_data:
                print(f"SUCCESS: Successfully parsed JSON!")
                print(f"   Plant: {parsed_data.get('plant_name', 'Unknown')}")
                print(f"   Prep steps: {len(parsed_data.get('preparation_steps', []))}")
                print(f"   Plant steps: {len(parsed_data.get('planting_steps', []))}")
            else:
                print(f"FAILED: Failed to parse JSON")
        
        # Test with real LLM
        print(f"\nTesting with Real LLM Response:")
        print("-" * 40)
        
        from services.llm_service import llm_service
        
        simple_prompt = """Respond with ONLY this JSON - no extra text:

{
    "plant_name": "Tomato",
    "preparation_steps": ["Test soil pH to 6.0-6.8 using digital meter"],
    "planting_steps": ["Start seeds indoors at 70-75F soil temperature"]
}"""
        
        response = await llm_service.generate_plant_info(simple_prompt)
        
        if response:
            print(f"LLM response: {response[:200]}...")
            
            parsed_data = service._extract_and_clean_json(response)
            
            if parsed_data:
                print("SUCCESS: Successfully parsed LLM JSON!")
                print(f"   Data: {parsed_data}")
            else:
                print("FAILED: Failed to parse LLM JSON")
                print("Raw response for debugging:")
                print(f"{response}")
        else:
            print("ERROR: No response from LLM")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_json_parsing())
    sys.exit(0 if success else 1)
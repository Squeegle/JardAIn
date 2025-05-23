"""
Debug LLM responses for garden plan generation
"""

import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import llm_service
from services.location_service import location_service
from services.plant_service import plant_service
from models.garden_plan import PlanRequest

async def debug_llm_responses():
    """Debug each LLM call to see what's failing"""
    
    print("🔍 Debugging LLM Responses...")
    print("=" * 60)
    
    # Set up test data
    zip_code = "K1A 0A6"
    plant_names = ["Tomato", "Lettuce"]
    
    # Get location and plants
    location_info = await location_service.get_location_info(zip_code)
    plants = await plant_service.get_multiple_plants(plant_names)
    
    print(f"📍 Location: {location_info.city}, {location_info.state}")
    print(f"🌱 Plants: {[p.name for p in plants]}")
    print()
    
    # Test 1: Planting Schedules Prompt
    print("1️⃣ TESTING PLANTING SCHEDULES")
    print("-" * 40)
    
    plants_info = []
    for plant in plants:
        plants_info.append({
            "name": plant.name,
            "type": plant.plant_type,
            "days_to_harvest": plant.days_to_harvest,
            "spacing": plant.spacing_inches
        })
    
    schedule_prompt = f"""
You are an expert garden planner. Create precise planting schedules for the following plants based on the location and climate information.

LOCATION INFORMATION:
- Location: {location_info.city}, {location_info.state} ({location_info.zip_code})
- USDA Zone: {location_info.usda_zone}
- Last Frost Date: {location_info.last_frost_date}
- First Frost Date: {location_info.first_frost_date}
- Growing Season: {location_info.growing_season_days} days
- Climate Type: {location_info.climate_type}

PLANTS TO SCHEDULE:
{json.dumps(plants_info, indent=2)}

Please provide a JSON array of planting schedules with this exact structure:
[
    {{
        "plant_name": "Tomato",
        "start_indoors_date": "2024-03-15",
        "direct_sow_date": null,
        "transplant_date": "2024-05-15",
        "harvest_start_date": "2024-07-15",
        "harvest_end_date": "2024-10-01",
        "succession_planting_interval": 14
    }}
]

CRITICAL: Respond with ONLY the JSON array - no explanations, no extra text.
"""
    
    try:
        print("📝 Sending planting schedule prompt...")
        response = await llm_service.generate_plant_info(schedule_prompt)
        print(f"📄 Response length: {len(response) if response else 0}")
        print(f"📄 Response preview: {repr(response[:200]) if response else 'None'}")
        
        if response:
            try:
                parsed = json.loads(response.strip())
                print("✅ JSON parsing successful!")
                print(f"📊 Parsed data: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print("🔧 Attempting to clean response...")
                
                # Try to find JSON in the response
                start_idx = response.find('[')
                end_idx = response.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_part = response[start_idx:end_idx + 1]
                    print(f"🔍 Extracted JSON: {json_part}")
                    try:
                        parsed = json.loads(json_part)
                        print("✅ Cleaned JSON parsing successful!")
                    except:
                        print("❌ Even cleaned JSON failed")
        else:
            print("❌ Empty response from LLM")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Layout Recommendations Prompt
    print("2️⃣ TESTING LAYOUT RECOMMENDATIONS")
    print("-" * 40)
    
    layout_prompt = f"""
Create garden layout recommendations for: {[p.name for p in plants]}

Respond with ONLY valid JSON in this exact format:
{{
    "garden_dimensions": "Recommended for medium garden",
    "plant_groupings": [
        {{
            "group_name": "Main Garden",
            "plants": ["Tomato", "Lettuce"]
        }}
    ],
    "spacing_guide": {{
        "Tomato": "24 inches apart",
        "Lettuce": "6 inches apart"
    }},
    "companion_planting_tips": [
        "Plant lettuce near tomatoes for ground cover"
    ],
    "layout_tips": [
        "Place taller plants on north side"
    ]
}}
"""
    
    try:
        print("📝 Sending layout prompt...")
        response = await llm_service.generate_plant_info(layout_prompt)
        print(f"📄 Response length: {len(response) if response else 0}")
        print(f"📄 Response preview: {repr(response[:200]) if response else 'None'}")
        
        if response:
            try:
                parsed = json.loads(response.strip())
                print("✅ JSON parsing successful!")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print("❌ Empty response from LLM")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: General Tips Prompt
    print("3️⃣ TESTING GENERAL TIPS")
    print("-" * 40)
    
    tips_prompt = f"""
Provide 5 gardening tips for growing {[p.name for p in plants]} in {location_info.city}, {location_info.state}.

Respond with ONLY a JSON array of strings:
["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"]
"""
    
    try:
        print("📝 Sending tips prompt...")
        response = await llm_service.generate_plant_info(tips_prompt)
        print(f"📄 Response length: {len(response) if response else 0}")
        print(f"📄 Response preview: {repr(response[:200]) if response else 'None'}")
        
        if response:
            try:
                parsed = json.loads(response.strip())
                print("✅ JSON parsing successful!")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print("❌ Empty response from LLM")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_llm_responses()) 
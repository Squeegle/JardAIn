#!/usr/bin/env python3
"""
Test script for the plant database.
Verifies data loading and provides useful database statistics.
"""

import sys
import os
import json
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_plant_database():
    """Analyze and display statistics about our plant database"""
    
    print("🌱 JardAIn Plant Database Analysis")
    print("=" * 50)
    
    try:
        # Load the plant database
        with open('data/common_vegetables.json', 'r') as f:
            plants = json.load(f)
        
        print(f"✅ Database loaded successfully!")
        print(f"📊 Total plants in database: {len(plants)}")
        print()
        
        # Analyze plant types
        plant_types = Counter(plant['plant_type'] for plant in plants)
        print("🏷️  Plant Types:")
        for plant_type, count in plant_types.items():
            print(f"   {plant_type.title()}: {count}")
        print()
        
        # Analyze growing requirements
        sun_requirements = Counter(plant['sun_requirements'] for plant in plants)
        print("☀️  Sun Requirements:")
        for requirement, count in sun_requirements.items():
            print(f"   {requirement.title()}: {count}")
        print()
        
        # Analyze harvest times
        harvest_times = [plant['days_to_harvest'] for plant in plants]
        print("⏱️  Harvest Time Statistics:")
        print(f"   Fastest: {min(harvest_times)} days ({[p['name'] for p in plants if p['days_to_harvest'] == min(harvest_times)][0]})")
        print(f"   Slowest: {max(harvest_times)} days ({[p['name'] for p in plants if p['days_to_harvest'] == max(harvest_times)][0]})")
        print(f"   Average: {sum(harvest_times) / len(harvest_times):.1f} days")
        print()
        
        # Show some examples
        print("🌿 Sample Plants:")
        for i, plant in enumerate(plants[:5]):
            print(f"   {i+1}. {plant['name']} ({plant['scientific_name']})")
            print(f"      Type: {plant['plant_type']}, Harvest: {plant['days_to_harvest']} days")
            print(f"      Companions: {', '.join(plant['companion_plants'][:3])}...")
        print()
        
        # Validate data integrity
        print("🔍 Data Validation:")
        required_fields = ['name', 'scientific_name', 'plant_type', 'days_to_harvest', 
                          'spacing_inches', 'planting_depth_inches', 'sun_requirements',
                          'water_requirements', 'soil_ph_range', 'companion_plants', 
                          'avoid_planting_with']
        
        valid_plants = 0
        for plant in plants:
            if all(field in plant for field in required_fields):
                valid_plants += 1
        
        print(f"   Valid plants: {valid_plants}/{len(plants)}")
        print(f"   Data integrity: {(valid_plants/len(plants)*100):.1f}%")
        
        print("\n🎉 Plant database analysis complete!")
        return True
        
    except FileNotFoundError:
        print("❌ Plant database file not found at 'data/common_vegetables.json'")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in plant database file")
        return False
    except Exception as e:
        print(f"❌ Error analyzing plant database: {e}")
        return False

def search_plants(query):
    """Search for plants by name"""
    try:
        with open('data/common_vegetables.json', 'r') as f:
            plants = json.load(f)
        
        results = [plant for plant in plants if query.lower() in plant['name'].lower()]
        
        if results:
            print(f"\n🔍 Search results for '{query}':")
            for plant in results:
                print(f"   • {plant['name']} - {plant['days_to_harvest']} days to harvest")
        else:
            print(f"\n❌ No plants found matching '{query}'")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

if __name__ == "__main__":
    success = analyze_plant_database()
    
    if success:
        print("\n" + "─" * 50)
        print("💡 Try searching for plants:")
        print("   python scripts/test_plant_database.py tomato")
        print("   python scripts/test_plant_database.py herb")
        
        # If search query provided
        if len(sys.argv) > 1:
            search_plants(sys.argv[1])
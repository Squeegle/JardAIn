#!/usr/bin/env python3
"""
Simple database viewer for JardAIn - follows the same pattern as working test scripts
"""
import os
import sys
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from config import settings
from services.plant_service import PlantService

async def main():
    """Main function to display database contents"""
    print("🗄️  JardAIn Database Viewer")
    print("=" * 50)
    
    try:
        # Initialize plant service (this will handle database setup)
        plant_service = PlantService()
        
        # Check if database is available
        print(f"Database available: {plant_service.database_available}")
        
        if plant_service.database_available:
            # Get all plants from database
            all_plants = await plant_service.get_all_plants()
            print(f"\n🌱 Total plants in database: {len(all_plants)}")
            
            # Group by type
            by_type = {}
            for plant in all_plants:
                if plant.plant_type not in by_type:
                    by_type[plant.plant_type] = []
                by_type[plant.plant_type].append(plant)
            
            print(f"\n🏷️  Plants by type:")
            for plant_type, plants in by_type.items():
                print(f"  - {plant_type}: {len(plants)}")
            
            # Show first 15 plants
            print(f"\n🌿 First 15 plants:")
            print(f"{'Name':<20} {'Type':<12} {'Days':<6} {'Sun':<12}")
            print("-" * 55)
            for plant in all_plants[:15]:
                print(f'{plant.name:<20} {plant.plant_type:<12} {plant.days_to_harvest:<6} {plant.sun_requirements:<12}')
            
            # Test search functionality
            search_results = await plant_service.search_plants("tom")
            print(f"\n🔍 Search results for 'tom': {len(search_results)} found")
            for plant in search_results:
                print(f"  - {plant.name} ({plant.plant_type})")
                
        else:
            print("❌ Database not available - using static JSON data")
            static_plants = plant_service.get_all_static_plants()
            print(f"📄 Static plants available: {len(static_plants)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
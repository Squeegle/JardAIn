#!/usr/bin/env python3
"""
Test script to verify plant persistence in PostgreSQL database
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

from services.plant_service import plant_service
from models.database import init_database, get_database_manager
from config import settings

async def test_plant_persistence():
    """Test if LLM-generated plants persist in database"""
    
    print("🧪 Testing Plant Persistence in PostgreSQL")
    print("=" * 50)
    
    # Initialize database exactly like main.py does
    if settings.validate_database_config():
        try:
            db_manager = init_database(settings.database_url_computed, **settings.database_config)
            print(f"✅ Database connected: {settings.postgres_db}")
            await db_manager.create_tables()
            print("🏗️  Database tables ready")
            
            # Notify plant service that database is now available
            plant_service.refresh_database_status()
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return
    else:
        print("❌ Database configuration incomplete")
        return
    
    test_plant = "Purple Cabbage"
    
    print(f"🔍 Step 1: Clear cache to force database lookup")
    plant_service.cache.clear()
    
    print(f"📊 Step 2: Check database stats before test")
    stats_before = await plant_service.get_database_stats()
    if "error" in stats_before:
        print(f"   ❌ Database stats error: {stats_before['error']}")
        return
    print(f"   Plants in database: {stats_before['total_plants']}")
    print(f"   LLM-generated plants: {stats_before['llm_generated_plants']}")
    
    print(f"🌱 Step 3: First request for '{test_plant}' (should generate via LLM)")
    plant1 = await plant_service.get_plant_info(test_plant)
    if plant1:
        print(f"   ✅ Generated: {plant1.name} ({plant1.plant_type})")
    else:
        print(f"   ❌ Failed to generate {test_plant}")
        return
    
    print(f"📊 Step 4: Check database stats after generation")
    stats_after = await plant_service.get_database_stats()
    if "error" in stats_after:
        print(f"   ❌ Database stats error: {stats_after['error']}")
        return
    print(f"   Plants in database: {stats_after['total_plants']}")
    print(f"   LLM-generated plants: {stats_after['llm_generated_plants']}")
    print(f"   Total increase: {stats_after['total_plants'] - stats_before['total_plants']}")
    print(f"   LLM increase: {stats_after['llm_generated_plants'] - stats_before['llm_generated_plants']}")
    
    print(f"🧹 Step 5: Clear cache again to force database lookup")
    plant_service.cache.clear()
    
    print(f"🔍 Step 6: Second request for '{test_plant}' (should come from database)")
    plant2 = await plant_service.get_plant_info(test_plant)
    if plant2:
        print(f"   ✅ Retrieved: {plant2.name} ({plant2.plant_type})")
        
        # Compare the plants
        if plant1.name == plant2.name and plant1.scientific_name == plant2.scientific_name:
            print(f"   ✅ PERSISTENCE WORKS: Same plant data retrieved!")
        else:
            print(f"   ❌ PERSISTENCE FAILED: Different data retrieved")
            print(f"      First:  {plant1.name} - {plant1.scientific_name}")
            print(f"      Second: {plant2.name} - {plant2.scientific_name}")
    else:
        print(f"   ❌ Failed to retrieve {test_plant} from database")
    
    # Test with a third request to see if it's cached
    print(f"⚡ Step 7: Third request for '{test_plant}' (should come from cache)")
    plant3 = await plant_service.get_plant_info(test_plant)
    if plant3:
        print(f"   ✅ Retrieved: {plant3.name} (from cache)")
    
    print(f"\n📊 Final database stats:")
    final_stats = await plant_service.get_database_stats()
    if "error" not in final_stats:
        print(f"   Total plants: {final_stats['total_plants']}")
        print(f"   Static plants: {final_stats['static_plants']}")
        print(f"   LLM-generated plants: {final_stats['llm_generated_plants']}")
        print(f"   Most popular plants:")
        for plant in final_stats['most_popular']:
            print(f"     - {plant['name']}: {plant['usage_count']} uses")
    else:
        print(f"   ❌ Error: {final_stats['error']}")

if __name__ == "__main__":
    asyncio.run(test_plant_persistence()) 
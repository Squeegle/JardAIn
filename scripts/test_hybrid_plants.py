#!/usr/bin/env python3
"""
Test the hybrid plant service.
Tests both static database and LLM generation capabilities.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_hybrid_plant_service():
    """Test the hybrid plant service functionality"""
    
    print("🧪 Testing Hybrid Plant Service")
    print("=" * 50)
    
    try:
        from services.plant_service import plant_service
        
        # Test 1: Static database plants
        print("📖 Testing static database plants...")
        static_plant = await plant_service.get_plant_info("tomato")
        if static_plant:
            print(f"✅ Static: {static_plant.name} - {static_plant.days_to_harvest} days")
            print(f"   Scientific: {static_plant.scientific_name}")
            print(f"   Companions: {', '.join(static_plant.companion_plants[:3])}...")
        else:
            print("❌ Failed to get static plant")
        
        # Test 2: Cache statistics
        print(f"\n📊 Initial cache stats: {plant_service.get_cache_stats()}")
        
        # Test 3: Search functionality
        print(f"\n🔍 Searching for 'tom'...")
        search_results = plant_service.search_static_plants("tom")
        print(f"   Found {len(search_results)} plants: {[p.name for p in search_results]}")
        
        # Test 4: LLM generation (if available)
        print("\n🤖 Testing LLM generation...")
        print("   Attempting to generate info for 'Dragon Fruit'...")
        
        unique_plant = await plant_service.get_plant_info("Dragon Fruit")
        if unique_plant:
            print(f"✅ LLM Generated: {unique_plant.name}")
            print(f"   Scientific: {unique_plant.scientific_name}")
            print(f"   Type: {unique_plant.plant_type}")
            print(f"   Days to harvest: {unique_plant.days_to_harvest}")
        else:
            print("⚠️  LLM generation failed or not configured")
        
        # Test 5: Final cache stats
        final_stats = plant_service.get_cache_stats()
        print(f"\n📊 Final cache stats: {final_stats}")
        
        print("\n🎉 Hybrid plant service test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hybrid_plant_service())
    sys.exit(0 if success else 1)
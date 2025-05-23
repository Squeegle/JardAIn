#!/usr/bin/env python3
"""
Test Ollama setup and integration with our plant service.
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_ollama_direct():
    """Test Ollama directly"""
    print("🤖 Testing Ollama Direct Connection")
    print("-" * 40)
    
    try:
        import ollama
        
        # Simple test
        response = ollama.generate(
            model='llama3.1',
            prompt='What is a tomato? Respond in one sentence.',
        )
        
        print("✅ Ollama connection successful!")
        print(f"📝 Response: {response['response'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

async def test_plant_generation():
    """Test plant information generation via our LLM service"""
    print("\n🌱 Testing Plant Information Generation")
    print("-" * 40)
    
    try:
        from services.llm_service import llm_service
        
        prompt = """
        You are an expert gardener. Provide growing information for: "Dragon Fruit"
        
        Respond with ONLY valid JSON:
        {
            "name": "Dragon Fruit",
            "scientific_name": "scientific name or null",
            "plant_type": "fruit",
            "days_to_harvest": 365,
            "spacing_inches": 72,
            "planting_depth_inches": 1.0,
            "sun_requirements": "full sun",
            "water_requirements": "moderate",
            "soil_ph_range": "6.0-7.0",
            "companion_plants": ["plant1", "plant2"],
            "avoid_planting_with": ["plant1"]
        }
        """
        
        response = await llm_service.generate_plant_info(prompt)
        
        if response:
            print("✅ Plant generation successful!")
            print(f"📝 Raw response: {response[:200]}...")
            
            # Try to parse as JSON
            try:
                plant_data = json.loads(response.strip())
                print("✅ Valid JSON response!")
                print(f"🌱 Generated plant: {plant_data.get('name', 'Unknown')}")
                return True
            except json.JSONDecodeError:
                print("⚠️  Response generated but not valid JSON")
                return False
        else:
            print("❌ No response from LLM service")
            return False
            
    except Exception as e:
        print(f"❌ Plant generation test failed: {e}")
        return False

async def test_hybrid_service():
    """Test our hybrid plant service"""
    print("\n🔄 Testing Hybrid Plant Service")
    print("-" * 40)
    
    try:
        from services.plant_service import plant_service
        
        # Test static plant
        print("Testing static plant (Tomato)...")
        tomato = await plant_service.get_plant_info("tomato")
        if tomato:
            print(f"✅ Static: {tomato.name} loaded from database")
        
        # Test LLM plant
        print("Testing LLM plant (Dragon Fruit)...")
        dragon_fruit = await plant_service.get_plant_info("Dragon Fruit")
        if dragon_fruit:
            print(f"✅ LLM: {dragon_fruit.name} generated successfully")
            print(f"   Days to harvest: {dragon_fruit.days_to_harvest}")
            print(f"   Scientific name: {dragon_fruit.scientific_name}")
        
        # Show cache stats
        stats = plant_service.get_cache_stats()
        print(f"📊 Cache stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Ollama Setup and Integration Test")
    print("=" * 50)
    
    # Test 1: Direct Ollama
    ollama_ok = await test_ollama_direct()
    
    if not ollama_ok:
        print("\n❌ Ollama setup incomplete. Please check:")
        print("   1. Is Ollama service running? (ollama serve)")
        print("   2. Is llama3.1 model downloaded? (ollama pull llama3.1)")
        print("   3. Is Python ollama package installed? (pip install ollama)")
        return False
    
    # Test 2: Plant generation
    plant_gen_ok = await test_plant_generation()
    
    # Test 3: Hybrid service
    hybrid_ok = await test_hybrid_service()
    
    print("\n" + "=" * 50)
    if ollama_ok and plant_gen_ok and hybrid_ok:
        print("🎉 All tests passed! Ollama integration is working!")
        print("\n✅ You can now:")
        print("   • Generate unlimited plant varieties")
        print("   • Use both static database and LLM")
        print("   • Run the full garden planner")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return ollama_ok and plant_gen_ok and hybrid_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
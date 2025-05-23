"""
Compare LLM responses between our debug script and the actual service calls
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import llm_service

async def compare_llm_responses():
    """Compare LLM responses for the same prompt"""
    
    print("🔍 Comparing LLM Responses...")
    print("=" * 50)
    
    # Simple test prompt
    simple_prompt = """
Provide 3 gardening tips for tomatoes.

Return as a simple JSON array:
["Tip 1", "Tip 2", "Tip 3"]
"""
    
    print("📝 Testing simple prompt 5 times...")
    
    for i in range(5):
        print(f"\n🔄 Test {i+1}:")
        try:
            response = await llm_service.generate_plant_info(simple_prompt)
            if response:
                print(f"   ✅ Response length: {len(response)}")
                print(f"   📄 Preview: {repr(response[:100])}")
            else:
                print(f"   ❌ Empty response: {repr(response)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 LLM consistency test complete!")

if __name__ == "__main__":
    asyncio.run(compare_llm_responses()) 
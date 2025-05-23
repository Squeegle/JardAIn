#!/usr/bin/env python3
"""
Test AI response quality specifically for detailed instructions.
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_ai_quality():
    """Test AI quality with a simple prompt"""
    
    print("🧠 Testing AI Response Quality")
    print("=" * 50)
    
    try:
        from services.llm_service import llm_service
        
        # Simple test prompt demanding specific details
        test_prompt = """
        You are a master gardener. Provide SPECIFIC, DETAILED growing instructions for tomatoes in Beverly Hills, CA (Zone 9b).

        REQUIREMENTS - INCLUDE EXACT NUMBERS:
        - Specific temperatures (°F)
        - Exact measurements (inches, tablespoons)
        - Precise timing (dates, days, weeks)
        - NO generic advice like "water as needed"

        Respond with JSON:
        {
            "plant_name": "Tomato",
            "preparation_steps": ["Exact step with measurements"],
            "planting_steps": ["Specific step with temperature and timing"],
            "care_instructions": ["Detailed care with exact amounts"]
        }

        Include numbers, temperatures, and measurements in EVERY instruction.
        """
        
        print("🤖 Testing AI with quality-demanding prompt...")
        response = await llm_service.generate_plant_info(test_prompt)
        
        if response:
            print(f"📝 Response length: {len(response)} characters")
            print(f"📋 Response preview:")
            print("-" * 30)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 30)
            
            # Check for specific detail indicators
            detail_indicators = ['inches', '°f', 'degrees', 'tablespoons', 'weeks', 'days', 'temperature', 'march', 'april', 'may']
            found_details = [indicator for indicator in detail_indicators if indicator.lower() in response.lower()]
            
            print(f"🔍 Detail indicators found: {found_details}")
            print(f"📊 Quality score: {len(found_details)}/10 detail indicators")
            
            # Try to parse as JSON
            try:
                data = json.loads(response.strip())
                print("✅ Valid JSON format")
                
                # Check each section for details
                for section in ['preparation_steps', 'planting_steps', 'care_instructions']:
                    if section in data:
                        steps = data[section]
                        detailed_steps = [step for step in steps if any(indicator in step.lower() for indicator in detail_indicators)]
                        print(f"📋 {section}: {len(detailed_steps)}/{len(steps)} steps contain specific details")
                        if detailed_steps:
                            print(f"   Example: {detailed_steps[0][:100]}...")
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON format")
        else:
            print("❌ No response from AI")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_quality())
    sys.exit(0 if success else 1) 
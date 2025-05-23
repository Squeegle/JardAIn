#!/usr/bin/env python3
"""
Quick configuration test script.
Run this to verify config loads properly before proceeding.
"""

import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config():
    """Quick test of configuration system"""
    print("🔧 Testing JardAIn Configuration...")
    
    try:
        # Import and test basic config loading
        from config import settings
        
        print(f"✅ Configuration loaded successfully")
        print(f"📱 App Name: {settings.app_name}")
        print(f"🤖 LLM Provider: {settings.llm_provider}")
        print(f"🌐 Host: {settings.host}:{settings.port}")
        print(f"📁 Generated Plans Path: {settings.generated_plans_path}")
        
        # Test LLM config
        llm_config = settings.llm_config
        print(f"🔗 LLM Config: {llm_config['provider']} - {llm_config.get('model', 'N/A')}")
        
        # Test validation
        is_valid = settings.validate_llm_config()
        print(f"✅ LLM Configuration Valid: {is_valid}")
        
        if not is_valid:
            print("⚠️  Note: LLM configuration incomplete - this is normal for initial setup")
        
        print("\n🎉 Configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        print(f"💡 Make sure you're running from the project root directory")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
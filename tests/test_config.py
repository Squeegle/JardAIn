"""
Test configuration loading and validation.
Ensures the config system works properly before building other components.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
from config import Settings

class TestConfiguration:
    """Test suite for configuration management"""
    
    def test_default_settings_load(self):
        """Test that default settings load without errors"""
        settings = Settings()
        
        # Check core settings exist
        assert settings.app_name == "JardAIn Garden Planner"
        assert settings.debug is True
        assert settings.llm_provider in ["ollama", "openai"]
        assert settings.port == 8000
        
        print("✅ Default settings loaded successfully")
    
    def test_environment_variable_override(self):
        """Test that environment variables properly override defaults"""
        with patch.dict(os.environ, {
            'APP_NAME': 'Test Garden App',
            'DEBUG': 'false',
            'LLM_PROVIDER': 'openai',
            'PORT': '9000'
        }):
            settings = Settings()
            
            assert settings.app_name == "Test Garden App"
            assert settings.debug is False
            assert settings.llm_provider == "openai"
            assert settings.port == 9000
        
        print("✅ Environment variable overrides work correctly")
    
    def test_llm_config_property(self):
        """Test LLM configuration property returns correct format"""
        # Test Ollama config
        settings = Settings(llm_provider="ollama")
        ollama_config = settings.llm_config
        
        assert ollama_config["provider"] == "ollama"
        assert "base_url" in ollama_config
        assert "model" in ollama_config
        
        # Test OpenAI config
        settings = Settings(llm_provider="openai", openai_api_key="test-key")
        openai_config = settings.llm_config
        
        assert openai_config["provider"] == "openai"
        assert "api_key" in openai_config
        assert "model" in openai_config
        
        print("✅ LLM configuration properties work correctly")
    
    def test_llm_validation(self):
        """Test LLM configuration validation"""
        # Valid Ollama config
        settings = Settings(llm_provider="ollama")
        assert settings.validate_llm_config() is True
        
        # Invalid OpenAI config (no API key)
        settings = Settings(llm_provider="openai", openai_api_key="")
        assert settings.validate_llm_config() is False
        
        # Valid OpenAI config
        settings = Settings(llm_provider="openai", openai_api_key="test-key")
        assert settings.validate_llm_config() is True
        
        print("✅ LLM validation works correctly")
    
    def test_directory_creation(self):
        """Test that necessary directories are created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create custom paths within temp directory
            custom_settings = Settings(
                generated_plans_path=os.path.join(temp_dir, "plans"),
                plant_images_path=os.path.join(temp_dir, "images"),
                logs_path=os.path.join(temp_dir, "logs"),
                plant_data_path=os.path.join(temp_dir, "data", "plants.json")
            )
            
            # Check directories were created
            assert os.path.exists(custom_settings.generated_plans_path)
            assert os.path.exists(custom_settings.plant_images_path)
            assert os.path.exists(custom_settings.logs_path)
            assert os.path.exists(os.path.dirname(custom_settings.plant_data_path))
        
        print("✅ Directory creation works correctly")
    
    def test_production_detection(self):
        """Test production vs development mode detection"""
        # Development mode
        dev_settings = Settings(debug=True)
        assert dev_settings.is_production is False
        
        # Production mode
        prod_settings = Settings(debug=False)
        assert prod_settings.is_production is True
        
        print("✅ Production detection works correctly")

def run_config_tests():
    """
    Run all configuration tests manually
    (since we don't have pytest installed yet)
    """
    print("🧪 Testing Configuration System...")
    print("-" * 50)
    
    test_suite = TestConfiguration()
    
    try:
        test_suite.test_default_settings_load()
        test_suite.test_environment_variable_override()
        test_suite.test_llm_config_property()
        test_suite.test_llm_validation()
        test_suite.test_directory_creation()
        test_suite.test_production_detection()
        
        print("-" * 50)
        print("🎉 All configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    run_config_tests()
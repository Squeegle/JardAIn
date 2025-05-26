"""
Configuration settings for the JardAIn Garden Planner application.
Handles environment variables, LLM provider switching, and application settings.
"""

import os
from typing import Literal, List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    All settings can be overridden via environment variables.
    """
    
    # ========================
    # Application Settings
    # ========================
    app_name: str = Field(default="JardAIn Garden Planner", description="Application name")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="info", description="Logging level")
    
    # ========================
    # LLM Provider Configuration
    # ========================
    llm_provider: Literal["ollama", "openai"] = Field(
        default="ollama", 
        description="LLM provider: 'ollama' for local dev, 'openai' for production"
    )
    
    # OpenAI Settings (Production)
    openai_api_key: str = Field(
        default="", 
        description="OpenAI API key for production use"
    )
    openai_model: str = Field(
        default="gpt-3.5-turbo", 
        description="OpenAI model to use"
    )
    openai_max_tokens: int = Field(
        default=2000, 
        description="Maximum tokens for OpenAI responses"
    )
    
    # Ollama Settings (Local Development)
    ollama_base_url: str = Field(
        default="http://localhost:11434", 
        description="Ollama server URL"
    )
    ollama_model: str = Field(
        default="llama3.1", 
        description="Ollama model name"
    )
    ollama_timeout: int = Field(
        default=60, 
        description="Ollama request timeout in seconds"
    )
    
    # ========================
    # External APIs
    # ========================
    weather_api_key: str = Field(
        default="", 
        description="Weather API key for location data"
    )
    weather_api_base_url: str = Field(
        default="http://api.weatherapi.com/v1", 
        description="Weather API base URL"
    )
    
    # ========================
    # Database Configuration (PostgreSQL)
    # ========================
    database_url: str = Field(
        default="", 
        description="Complete PostgreSQL database URL (overrides individual settings)"
    )
    postgres_host: str = Field(
        default="localhost", 
        description="PostgreSQL host address"
    )
    postgres_port: int = Field(
        default=5432, 
        description="PostgreSQL port"
    )
    postgres_db: str = Field(
        default="jardain", 
        description="PostgreSQL database name"
    )
    postgres_user: str = Field(
        default="jardain_user", 
        description="PostgreSQL username"
    )
    postgres_password: str = Field(
        default="", 
        description="PostgreSQL password"
    )
    database_pool_size: int = Field(
        default=5, 
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10, 
        description="Database connection pool max overflow"
    )
    
    # ========================
    # File Paths
    # ========================
    plant_data_path: str = Field(
        default="data/common_vegetables.json", 
        description="Path to plant database JSON file"
    )
    plant_images_path: str = Field(
        default="data/plant_images/", 
        description="Directory for plant images"
    )
    generated_plans_path: str = Field(
        default="generated_plans/", 
        description="Directory for generated PDF plans"
    )
    logs_path: str = Field(
        default="logs/", 
        description="Directory for application logs"
    )
    
    # ========================
    # PDF Generation Settings
    # ========================
    pdf_page_size: str = Field(
        default="A4", 
        description="PDF page size (A4, Letter, etc.)"
    )
    pdf_margin: str = Field(
        default="1in", 
        description="PDF page margins"
    )
    pdf_font_family: str = Field(
        default="Arial", 
        description="PDF font family"
    )
    
    # ========================
    # Web Server Settings
    # ========================
    host: str = Field(
        default="0.0.0.0", 
        description="Server host address"
    )
    port: int = Field(
        default=8000, 
        description="Server port"
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], 
        description="CORS allowed origins"
    )
    
    # ========================
    # Garden Planning Settings
    # ========================
    default_garden_size: str = Field(
        default="medium", 
        description="Default garden size (small, medium, large)"
    )
    default_experience_level: str = Field(
        default="beginner", 
        description="Default gardening experience level"
    )
    max_selected_plants: int = Field(
        default=20, 
        description="Maximum number of plants per garden plan"
    )
    
    class Config:
        # Load environment variables from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Make field names case insensitive for env vars
        case_sensitive = False
    
    def __init__(self, **kwargs):
        """
        Initialize settings and create necessary directories
        """
        super().__init__(**kwargs)
        self._create_directories()
    
    def _create_directories(self):
        """
        Create necessary directories if they don't exist
        """
        directories = [
            self.generated_plans_path,
            self.plant_images_path,
            self.logs_path,
            os.path.dirname(self.plant_data_path)  # data/ directory
        ]
        
        for directory in directories:
            if directory:  # Only create if not empty string
                os.makedirs(directory, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """
        Check if running in production mode
        Detects Railway environment and production settings
        """
        # Check for Railway environment variables
        railway_env = os.getenv("RAILWAY_ENVIRONMENT") is not None
        # Check for production indicators
        production_indicators = [
            not self.debug,
            self.llm_provider == "openai",
            os.getenv("RAILWAY_PROJECT_ID") is not None,
            os.getenv("PORT") is not None  # Railway sets PORT
        ]
        
        return railway_env or any(production_indicators)
    
    @property
    def llm_config(self) -> dict:
        """
        Get current LLM provider configuration
        """
        if self.llm_provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "max_tokens": self.openai_max_tokens
            }
        else:  # ollama
            return {
                "provider": "ollama",
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
                "timeout": self.ollama_timeout
            }
    
    def validate_llm_config(self) -> bool:
        """
        Validate that required LLM configuration is present
        """
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        else:  # ollama
            return bool(self.ollama_base_url and self.ollama_model)
    
    @property
    def database_url_computed(self) -> str:
        """
        Get the complete database URL, either from DATABASE_URL env var 
        or constructed from individual components
        """
        if self.database_url:
            return self.database_url
        
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    def validate_database_config(self) -> bool:
        """
        Validate that required database configuration is present
        """
        if self.database_url:
            return True
        
        return bool(
            self.postgres_host and 
            self.postgres_user and 
            self.postgres_password and 
            self.postgres_db
        )
    
    @property
    def database_config(self) -> dict:
        """
        Get database configuration for SQLAlchemy (without URL since it's passed separately)
        """
        return {
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.debug  # SQL logging in debug mode
        }

# ========================
# Global Settings Instance
# ========================
settings = Settings()

# Validate configuration on import
if not settings.validate_llm_config():
    if settings.llm_provider == "openai":
        print("⚠️  Warning: OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
    else:
        print("⚠️  Warning: Ollama configuration incomplete. Check OLLAMA_BASE_URL and OLLAMA_MODEL.")

print(f"✅ JardAIn configured with {settings.llm_provider.upper()} as LLM provider")
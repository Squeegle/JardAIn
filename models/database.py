"""
SQLAlchemy database models for the JardAIn application.
Defines the PostgreSQL table structures for storing plant data and other entities.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List
import json

# Create the declarative base
Base = declarative_base()

class PlantModel(Base):
    """
    SQLAlchemy model for plant data storage.
    Maps to the 'plants' table in PostgreSQL.
    """
    __tablename__ = "plants"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Plant identification
    name = Column(String(255), unique=True, nullable=False, index=True)
    scientific_name = Column(String(255), nullable=True)
    plant_type = Column(String(50), nullable=False, index=True)
    
    # Growing characteristics
    days_to_harvest = Column(Integer, nullable=False)
    spacing_inches = Column(Float, nullable=False)
    planting_depth_inches = Column(Float, nullable=False)
    
    # Requirements
    sun_requirements = Column(String(50), nullable=False)
    water_requirements = Column(String(50), nullable=False)
    soil_ph_range = Column(String(50), nullable=False)
    
    # Companion planting (stored as JSON text)
    companion_plants = Column(Text, nullable=True)  # JSON array of plant names
    avoid_planting_with = Column(Text, nullable=True)  # JSON array of plant names
    
    # Metadata
    source = Column(String(20), nullable=False, default="llm")  # 'static' or 'llm'
    created_at = Column(DateTime, default=func.now(), nullable=False)
    llm_model = Column(String(50), nullable=True)  # Track which LLM model generated it
    usage_count = Column(Integer, default=1, nullable=False)  # Track popularity
    
    def __repr__(self):
        return f"<PlantModel(name='{self.name}', type='{self.plant_type}', source='{self.source}')>"
    
    @property
    def companion_plants_list(self) -> List[str]:
        """Get companion plants as a Python list"""
        if not self.companion_plants:
            return []
        try:
            return json.loads(self.companion_plants)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @companion_plants_list.setter
    def companion_plants_list(self, value: List[str]):
        """Set companion plants from a Python list"""
        self.companion_plants = json.dumps(value) if value else None
    
    @property
    def avoid_planting_with_list(self) -> List[str]:
        """Get avoid planting with plants as a Python list"""
        if not self.avoid_planting_with:
            return []
        try:
            return json.loads(self.avoid_planting_with)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @avoid_planting_with_list.setter
    def avoid_planting_with_list(self, value: List[str]):
        """Set avoid planting with plants from a Python list"""
        self.avoid_planting_with = json.dumps(value) if value else None

# Database session and engine management
class DatabaseManager:
    """
    Manages database connections and sessions for the application.
    Provides both sync and async database access.
    """
    
    def __init__(self, database_url: str, **engine_kwargs):
        """
        Initialize database manager with connection parameters.
        
        Args:
            database_url: PostgreSQL connection URL
            **engine_kwargs: Additional SQLAlchemy engine configuration
        """
        self.database_url = database_url
        
        # Create async engine for the main application
        self.async_engine = create_async_engine(
            database_url,
            **engine_kwargs
        )
        
        # Create sync engine for migrations and utilities
        sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self.sync_engine = create_engine(sync_url)
        
        # Session makers
        self.async_session_maker = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.sync_session_maker = sessionmaker(bind=self.sync_engine)
    
    async def get_async_session(self) -> AsyncSession:
        """Get an async database session"""
        async with self.async_session_maker() as session:
            yield session
    
    def get_sync_session(self):
        """Get a sync database session"""
        with self.sync_session_maker() as session:
            yield session
    
    async def create_tables(self):
        """Create all tables (async)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    def create_tables_sync(self):
        """Create all tables (sync) - useful for migrations"""
        Base.metadata.create_all(bind=self.sync_engine)
    
    async def drop_tables(self):
        """Drop all tables (async) - be careful!"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        """Close database connections"""
        await self.async_engine.dispose()

# Global database manager instance (will be initialized in main.py)
database_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    if database_manager is None:
        raise RuntimeError("Database manager not initialized. Call init_database() first.")
    return database_manager

def init_database(database_url: str, **engine_kwargs) -> DatabaseManager:
    """
    Initialize the global database manager.
    This should be called once during application startup.
    """
    global database_manager
    database_manager = DatabaseManager(database_url, **engine_kwargs)
    return database_manager

async def get_db_session() -> AsyncSession:
    """
    Dependency function for FastAPI to get database sessions.
    Use this in FastAPI route dependencies.
    """
    db_manager = get_database_manager()
    async with db_manager.async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close() 
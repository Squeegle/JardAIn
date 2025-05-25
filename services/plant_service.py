"""
Plant data service with 3-tier hybrid approach.
Combines in-memory cache (fastest), PostgreSQL database (fast + persistent), and LLM generation (unlimited variety).
"""

import json
import os
import asyncio
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from models.garden_plan import PlantInfo
from models.database import PlantModel, get_database_manager
from services.llm_service import llm_service
from config import settings
from sqlalchemy import select, func, or_
from sqlalchemy.exc import SQLAlchemyError

class PlantCache:
    """
    Simple in-memory cache for recently accessed plant data.
    This provides the fastest possible access for frequently used plants.
    """
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour (shorter since we have DB now)
    
    def get(self, plant_name: str) -> Optional[PlantInfo]:
        """Get cached plant info if it exists and isn't expired"""
        key = plant_name.lower().strip()
        
        if key not in self._cache:
            return None
        
        # Check if cache entry is expired
        if datetime.now() - self._timestamps[key] > self.cache_duration:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def store(self, plant_name: str, plant_info: PlantInfo):
        """Store plant info in cache with multiple key variations for robust lookup"""
        key = plant_name.lower().strip()
        self._cache[key] = plant_info
        self._timestamps[key] = datetime.now()
        
        # Also store under the actual plant name from the PlantInfo for robust lookup
        actual_key = plant_info.name.lower().strip()
        if actual_key != key:
            self._cache[actual_key] = plant_info
            self._timestamps[actual_key] = datetime.now()
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get number of cached plants"""
        return len(self._cache)

class PlantService:
    """
    3-Tier hybrid plant service:
    Tier 1: In-memory cache (fastest access for recent plants)
    Tier 2: PostgreSQL database (fast persistent storage for all plants)  
    Tier 3: LLM generation (unlimited variety, stores results in database)
    """
    
    def __init__(self):
        self.cache = PlantCache()
        # Initialize as None to indicate we haven't checked yet
        self._database_available = None
        self._database_check_attempted = False
        
        # Load legacy JSON as fallback (always available)
        self.static_plants = self._load_static_database()
        
        print("🌱 Plant service initialized - database status will be checked on first use")
    
    @property
    def database_available(self) -> bool:
        """
        Lazy property that checks database availability on first access.
        This allows the database to be initialized after the service is created.
        """
        if self._database_available is None:
            self._database_available = self._check_database_availability()
            
            if self._database_available:
                print("🗄️  Plant service detected PostgreSQL database is available")
            else:
                print(f"⚠️  Plant service using JSON fallback with {len(self.static_plants)} plants")
        
        return self._database_available
    
    def refresh_database_status(self) -> bool:
        """
        Force a re-check of database availability.
        Call this after the database has been initialized.
        
        Returns:
            bool: True if database is now available, False otherwise
        """
        print("🔄 Refreshing database availability status...")
        self._database_available = None  # Reset cached status
        self._database_check_attempted = False
        
        # Trigger the property check
        available = self.database_available
        
        if available:
            print("✅ Database is now available for plant service")
        else:
            print("❌ Database is still not available")
            
        return available
    
    def _check_database_availability(self) -> bool:
        """Check if database is properly configured and available"""
        if self._database_check_attempted:
            return self._database_available if self._database_available is not None else False
        
        self._database_check_attempted = True
        
        try:
            if not settings.validate_database_config():
                return False
            
            # Try to get database manager
            get_database_manager()
            return True
        except Exception as e:
            print(f"⚠️  Database not available: {e}")
            return False
    
    def _load_static_database(self) -> Dict[str, PlantInfo]:
        """
        Load plant data from JSON file into PlantInfo objects (fallback mode only)
        """
        try:
            with open(settings.plant_data_path, 'r') as f:
                data = json.load(f)
            
            plants = {}
            for plant_data in data:
                plant = PlantInfo(**plant_data)
                plants[plant.name.lower()] = plant
            
            return plants
            
        except FileNotFoundError:
            print(f"⚠️  Static plant database not found at {settings.plant_data_path}")
            return {}
        except Exception as e:
            print(f"❌ Error loading static plant database: {e}")
            return {}
    
    async def get_plant_info(self, plant_name: str) -> Optional[PlantInfo]:
        """
        Get plant information using 3-tier hybrid approach:
        1. Check in-memory cache first (fastest)
        2. Check PostgreSQL database (fast + persistent)
        3. Generate via LLM if not found (unlimited variety, store in DB)
        """
        plant_key = plant_name.lower().strip()
        
        # Tier 1: Check in-memory cache first
        cached_plant = self.cache.get(plant_name)
        if cached_plant:
            print(f"⚡ Found {plant_name} in memory cache")
            return cached_plant
        
        # Tier 2: Check PostgreSQL database
        if self.database_available:
            db_plant = await self._get_plant_from_database(plant_name)
            if db_plant:
                print(f"🗄️  Found {plant_name} in database")
                # Store in cache for faster future access
                self.cache.store(plant_name, db_plant)
                # Increment usage count
                await self._increment_usage_count(plant_name)
                return db_plant
        else:
            # Fallback to JSON if database unavailable
            if plant_key in self.static_plants:
                print(f"📖 Found {plant_name} in static JSON database")
                return self.static_plants[plant_key]
        
        # Tier 3: Generate via LLM and store in database
        print(f"🤖 Generating plant info for {plant_name} via LLM")
        try:
            generated_plant = await self._generate_plant_info_via_llm(plant_name)
            if generated_plant:
                # Store in database for future use
                if self.database_available:
                    await self._store_plant_in_database(generated_plant)
                
                # Store in cache for immediate reuse
                self.cache.store(plant_name, generated_plant)
                print(f"✅ Generated, stored, and cached plant info for {plant_name}")
                return generated_plant
            else:
                print(f"❌ Could not generate plant info for {plant_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating plant info for {plant_name}: {e}")
            return None
    
    async def _get_plant_from_database(self, plant_name: str) -> Optional[PlantInfo]:
        """
        Retrieve plant information from PostgreSQL database
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                # Try exact name match first
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name) == plant_name.lower().strip()
                )
                result = await session.execute(stmt)
                plant_model = result.scalar_one_or_none()
                
                if plant_model:
                    return self._model_to_plant_info(plant_model)
                
                # Try partial name match if exact match fails
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name).contains(plant_name.lower().strip())
                )
                result = await session.execute(stmt)
                plant_model = result.first()
                
                if plant_model:
                    return self._model_to_plant_info(plant_model[0])
                
                return None
                
        except SQLAlchemyError as e:
            print(f"❌ Database error retrieving plant {plant_name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error retrieving plant {plant_name}: {e}")
            return None
    
    async def _store_plant_in_database(self, plant_info: PlantInfo) -> bool:
        """
        Store plant information in PostgreSQL database
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                # Check if plant already exists
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name) == plant_info.name.lower().strip()
                )
                result = await session.execute(stmt)
                existing_plant = result.scalar_one_or_none()
                
                if existing_plant:
                    print(f"🔄 Plant {plant_info.name} already exists in database")
                    return True
                
                # Create new plant model
                plant_model = PlantModel(
                    name=plant_info.name,
                    scientific_name=plant_info.scientific_name,
                    plant_type=plant_info.plant_type,
                    days_to_harvest=plant_info.days_to_harvest,
                    spacing_inches=plant_info.spacing_inches,
                    planting_depth_inches=plant_info.planting_depth_inches,
                    sun_requirements=plant_info.sun_requirements,
                    water_requirements=plant_info.water_requirements,
                    soil_ph_range=plant_info.soil_ph_range,
                    source="llm",  # Mark as LLM-generated
                    llm_model=settings.llm_config.get("model", "unknown"),
                    usage_count=1
                )
                
                # Set companion plants and avoid lists
                plant_model.companion_plants_list = plant_info.companion_plants
                plant_model.avoid_planting_with_list = plant_info.avoid_planting_with
                
                # Add and commit
                session.add(plant_model)
                await session.commit()
                print(f"💾 Stored {plant_info.name} in database")
                return True
                
        except SQLAlchemyError as e:
            print(f"❌ Database error storing plant {plant_info.name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error storing plant {plant_info.name}: {e}")
            return False
    
    async def _increment_usage_count(self, plant_name: str):
        """
        Increment the usage count for a plant in the database
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name) == plant_name.lower().strip()
                )
                result = await session.execute(stmt)
                plant_model = result.scalar_one_or_none()
                
                if plant_model:
                    plant_model.usage_count += 1
                    await session.commit()
                    
        except Exception as e:
            # Non-critical error, don't propagate
            print(f"⚠️  Could not increment usage count for {plant_name}: {e}")
    
    def _model_to_plant_info(self, plant_model: PlantModel) -> PlantInfo:
        """
        Convert a PlantModel (SQLAlchemy) to a PlantInfo (Pydantic) object
        """
        return PlantInfo(
            name=plant_model.name,
            scientific_name=plant_model.scientific_name,
            plant_type=plant_model.plant_type,
            days_to_harvest=plant_model.days_to_harvest,
            spacing_inches=plant_model.spacing_inches,
            planting_depth_inches=plant_model.planting_depth_inches,
            sun_requirements=plant_model.sun_requirements,
            water_requirements=plant_model.water_requirements,
            soil_ph_range=plant_model.soil_ph_range,
            companion_plants=plant_model.companion_plants_list,
            avoid_planting_with=plant_model.avoid_planting_with_list
        )
    
    async def _generate_plant_info_via_llm(self, plant_name: str) -> Optional[PlantInfo]:
        """
        Generate plant information using LLM
        """
        prompt = f"""
        You are an expert gardener and botanist. Provide detailed growing information for the plant: "{plant_name}"

        Please respond with ONLY a valid JSON object that matches this exact structure:
        {{
            "name": "{plant_name}",
            "scientific_name": "Scientific name if known, or null",
            "plant_type": "vegetable, herb, fruit, or flower",
            "days_to_harvest": 60,
            "spacing_inches": 12,
            "planting_depth_inches": 0.5,
            "sun_requirements": "full sun, partial shade, or shade",
            "water_requirements": "low, moderate, or high",
            "soil_ph_range": "6.0-7.0",
            "companion_plants": ["plant1", "plant2", "plant3"],
            "avoid_planting_with": ["plant1", "plant2"]
        }}

        Requirements:
        - Use realistic growing data based on standard gardening practices
        - Include 3-5 companion plants that actually grow well together
        - Include plants to avoid if any (can be empty array)
        - Use only these sun_requirements values: "full sun", "partial shade", "shade"
        - Use only these water_requirements values: "low", "moderate", "high"
        - Provide soil pH as a range like "6.0-7.0"
        - If the plant doesn't exist or you're unsure, return null

        Plant to research: {plant_name}
        """
        
        try:
            response = await llm_service.generate_plant_info(prompt)
            
            if not response:
                return None
            
            # Parse the JSON response
            plant_data = json.loads(response.strip())
            
            # Validate that we got actual data (not null)
            if plant_data is None:
                return None
            
            # Create PlantInfo object
            plant_info = PlantInfo(**plant_data)
            return plant_info
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from LLM for {plant_name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error parsing LLM response for {plant_name}: {e}")
            return None
    
    async def get_multiple_plants(self, plant_names: List[str]) -> List[PlantInfo]:
        """
        Get information for multiple plants efficiently using 3-tier approach
        Optimizes by checking cache first, then batch database queries, then parallel LLM calls
        """
        print(f"🔍 Getting {len(plant_names)} plants: {plant_names}")
        plants = []
        remaining_plants = []
        
        # Tier 1: Check cache for all plants first
        for name in plant_names:
            cached_plant = self.cache.get(name)
            if cached_plant:
                plants.append(cached_plant)
                print(f"⚡ Found {name} in cache")
            else:
                remaining_plants.append(name)
        
        if not remaining_plants:
            print(f"✅ All {len(plants)} plants found in cache")
            return plants
        
        # Tier 2: Database lookup (batch query for efficiency)
        if self.database_available:
            db_plants = await self._get_multiple_plants_from_database(remaining_plants)
            for plant in db_plants:
                plants.append(plant)
                # Cache for future use
                self.cache.store(plant.name, plant)
                # Remove from remaining plants list
                remaining_plants = [name for name in remaining_plants 
                                  if name.lower().strip() != plant.name.lower().strip()]
        else:
            # Fallback to JSON static database
            json_plants = []
            for name in remaining_plants:
                if name.lower().strip() in self.static_plants:
                    plant = self.static_plants[name.lower().strip()]
                    plants.append(plant)
                    json_plants.append(name)
                    print(f"📖 Found {name} in JSON database")
            
            # Remove found plants from remaining list
            remaining_plants = [name for name in remaining_plants if name not in json_plants]
        
        # Tier 3: LLM generation for remaining plants (parallel)
        if remaining_plants:
            print(f"🤖 Generating {len(remaining_plants)} plants via LLM: {remaining_plants}")
            llm_tasks = [self.get_plant_info(name) for name in remaining_plants]
            llm_results = await asyncio.gather(*llm_tasks, return_exceptions=True)
            
            for i, result in enumerate(llm_results):
                if isinstance(result, PlantInfo):
                    plants.append(result)
                    print(f"✅ Generated plant: {result.name}")
                elif isinstance(result, Exception):
                    print(f"❌ Error generating plant {remaining_plants[i]}: {result}")
                else:
                    print(f"⚠️  No plant info generated for {remaining_plants[i]}")
        
        print(f"🏁 Returning {len(plants)} plants total")
        return plants
    
    async def _get_multiple_plants_from_database(self, plant_names: List[str]) -> List[PlantInfo]:
        """
        Efficiently retrieve multiple plants from database with a single query
        """
        if not plant_names:
            return []
        
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                # Batch query for all plant names
                lower_names = [name.lower().strip() for name in plant_names]
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name).in_(lower_names)
                )
                result = await session.execute(stmt)
                plant_models = result.scalars().all()
                
                # Convert to PlantInfo objects and increment usage counts
                plants = []
                for plant_model in plant_models:
                    plant_info = self._model_to_plant_info(plant_model)
                    plants.append(plant_info)
                    
                    # Increment usage count
                    plant_model.usage_count += 1
                
                # Commit usage count updates
                await session.commit()
                
                print(f"🗄️  Found {len(plants)} plants in database")
                return plants
                
        except SQLAlchemyError as e:
            print(f"❌ Database error retrieving multiple plants: {e}")
            return []
        except Exception as e:
            print(f"❌ Error retrieving multiple plants: {e}")
            return []

    async def get_plants_by_type(self, plant_type: str) -> List[PlantInfo]:
        """
        Get plants filtered by type from database or JSON fallback
        """
        if self.database_available:
            return await self._get_plants_by_type_from_database(plant_type)
        else:
            # JSON fallback
            return [plant for plant in self.static_plants.values() 
                    if plant.plant_type.lower() == plant_type.lower()]
    
    async def _get_plants_by_type_from_database(self, plant_type: str) -> List[PlantInfo]:
        """
        Get plants by type from PostgreSQL database
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.plant_type) == plant_type.lower().strip()
                )
                result = await session.execute(stmt)
                plant_models = result.scalars().all()
                
                plants = [self._model_to_plant_info(model) for model in plant_models]
                print(f"🗄️  Found {len(plants)} {plant_type} plants in database")
                return plants
                
        except SQLAlchemyError as e:
            print(f"❌ Database error getting plants by type {plant_type}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error getting plants by type {plant_type}: {e}")
            return []

    async def get_all_plants(self) -> List[PlantInfo]:
        """
        Get all plants from database or JSON fallback (for admin/UI purposes)
        """
        if self.database_available:
            return await self._get_all_plants_from_database()
        else:
            return list(self.static_plants.values())
    
    async def _get_all_plants_from_database(self) -> List[PlantInfo]:
        """
        Get all plants from PostgreSQL database
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                stmt = select(PlantModel).order_by(PlantModel.name)
                result = await session.execute(stmt)
                plant_models = result.scalars().all()
                
                plants = [self._model_to_plant_info(model) for model in plant_models]
                print(f"🗄️  Retrieved {len(plants)} total plants from database")
                return plants
                
        except SQLAlchemyError as e:
            print(f"❌ Database error getting all plants: {e}")
            return []
        except Exception as e:
            print(f"❌ Error getting all plants: {e}")
            return []
    
    async def search_plants(self, query: str) -> List[PlantInfo]:
        """
        Search plants by name (for autocomplete/suggestions) in database or JSON
        """
        if self.database_available:
            return await self._search_plants_in_database(query)
        else:
            # JSON fallback
            query_lower = query.lower()
            return [plant for plant in self.static_plants.values() 
                    if query_lower in plant.name.lower()]
    
    async def _search_plants_in_database(self, query: str) -> List[PlantInfo]:
        """
        Search plants in PostgreSQL database using LIKE query
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                query_pattern = f"%{query.lower().strip()}%"
                stmt = select(PlantModel).where(
                    func.lower(PlantModel.name).like(query_pattern)
                ).order_by(PlantModel.usage_count.desc(), PlantModel.name).limit(20)
                
                result = await session.execute(stmt)
                plant_models = result.scalars().all()
                
                plants = [self._model_to_plant_info(model) for model in plant_models]
                print(f"🔍 Found {len(plants)} plants matching '{query}'")
                return plants
                
        except SQLAlchemyError as e:
            print(f"❌ Database error searching plants: {e}")
            return []
        except Exception as e:
            print(f"❌ Error searching plants: {e}")
            return []
    
    def get_all_static_plants(self) -> List[PlantInfo]:
        """
        Get list of all plants in static JSON database (legacy method for compatibility)
        """
        return list(self.static_plants.values())
    
    def search_static_plants(self, query: str) -> List[PlantInfo]:
        """
        Search static JSON plants by name (legacy method for compatibility)
        """
        query = query.lower()
        return [plant for plant in self.static_plants.values() 
                if query in plant.name.lower()]
    
    def get_cache_stats(self) -> Dict[str, Union[int, List[str], bool]]:
        """
        Get comprehensive service statistics (useful for monitoring and debugging)
        """
        return {
            "database_available": self.database_available,
            "static_plants_count": len(self.static_plants),
            "cached_plants_count": self.cache.size(),
            "total_static_available": len(self.static_plants),
            "cached_plant_names": list(self.cache._cache.keys()) if hasattr(self.cache, '_cache') else [],
            "cache_duration_hours": self.cache.cache_duration.total_seconds() / 3600,
            "service_mode": "postgresql" if self.database_available else "json_fallback"
        }
    
    async def get_database_stats(self) -> Dict[str, Union[int, str]]:
        """
        Get database statistics (requires database connection)
        """
        if not self.database_available:
            return {"error": "Database not available"}
        
        try:
            db_manager = get_database_manager()
            async with db_manager.async_session_maker() as session:
                # Count total plants
                total_stmt = select(func.count(PlantModel.id))
                total_result = await session.execute(total_stmt)
                total_count = total_result.scalar()
                
                # Count by source
                static_stmt = select(func.count(PlantModel.id)).where(PlantModel.source == "static")
                static_result = await session.execute(static_stmt)
                static_count = static_result.scalar()
                
                llm_stmt = select(func.count(PlantModel.id)).where(PlantModel.source == "llm") 
                llm_result = await session.execute(llm_stmt)
                llm_count = llm_result.scalar()
                
                # Get most used plants
                popular_stmt = select(PlantModel.name, PlantModel.usage_count).order_by(
                    PlantModel.usage_count.desc()
                ).limit(5)
                popular_result = await session.execute(popular_stmt)
                popular_plants = popular_result.all()
                
                return {
                    "total_plants": total_count,
                    "static_plants": static_count,
                    "llm_generated_plants": llm_count,
                    "most_popular": [{"name": name, "usage_count": count} 
                                   for name, count in popular_plants]
                }
                
        except SQLAlchemyError as e:
            return {"error": f"Database error: {e}"}
        except Exception as e:
            return {"error": f"Error getting database stats: {e}"}

# Global instance for use throughout the application
plant_service = PlantService()
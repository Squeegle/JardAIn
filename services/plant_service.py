"""
Plant data service with hybrid approach.
Combines static database (fast) with LLM generation (unlimited variety).
"""

import json
import os
import asyncio
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from models.garden_plan import PlantInfo
from services.llm_service import llm_service
from config import settings

class PlantCache:
    """
    Simple in-memory cache for LLM-generated plant data
    In production, you might want to use Redis or persistent storage
    """
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self.cache_duration = timedelta(days=7)  # Cache for 1 week
    
    def get(self, plant_name: str) -> Optional[PlantInfo]:
        """Get cached plant info if it exists and isn't expired"""
        key = plant_name.lower()
        
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
            print(f"💾 Cached plant under both '{key}' and '{actual_key}'")
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get number of cached plants"""
        return len(self._cache)

class PlantService:
    """
    Hybrid plant service that combines static database with LLM generation
    """
    
    def __init__(self):
        self.static_plants = self._load_static_database()
        self.cache = PlantCache()
        print(f"🌱 Plant service initialized with {len(self.static_plants)} static plants")
    
    def _load_static_database(self) -> Dict[str, PlantInfo]:
        """
        Load plant data from JSON file into PlantInfo objects
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
        Get plant information using hybrid approach:
        1. Check static database first (fast)
        2. Check cache for LLM-generated plants
        3. Generate via LLM if not found (unlimited variety)
        """
        plant_key = plant_name.lower().strip()
        
        # Step 1: Check static database first
        if plant_key in self.static_plants:
            print(f"📖 Found {plant_name} in static database")
            return self.static_plants[plant_key]
        
        # Step 2: Check cache for previously generated plants
        cached_plant = self.cache.get(plant_name)
        if cached_plant:
            print(f"💾 Found {plant_name} in cache")
            return cached_plant
        
        # Step 2.5: Try alternative cache lookups for robustness
        for variant in [plant_name.title(), plant_name.capitalize(), plant_name.upper()]:
            cached_plant = self.cache.get(variant)
            if cached_plant:
                print(f"💾 Found {plant_name} in cache under variant '{variant}'")
                return cached_plant
        
        # Step 3: Generate via LLM
        print(f"🤖 Generating plant info for {plant_name} via LLM")
        try:
            generated_plant = await self._generate_plant_info_via_llm(plant_name)
            if generated_plant:
                # Cache the result with robust key storage
                self.cache.store(plant_name, generated_plant)
                print(f"✅ Generated and cached plant info for {plant_name}")
                return generated_plant
            else:
                print(f"❌ Could not generate plant info for {plant_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating plant info for {plant_name}: {e}")
            return None
    
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
        Get information for multiple plants efficiently
        Uses asyncio to parallelize LLM calls when needed
        """
        print(f"🔍 get_multiple_plants called with: {plant_names}")
        plants = []
        
        # Separate into static and potential LLM plants
        static_plants = []
        llm_plants = []
        
        for name in plant_names:
            if name.lower() in self.static_plants:
                static_plants.append(name)
                print(f"📖 {name} found in static database")
            else:
                llm_plants.append(name)
                print(f"🤖 {name} needs LLM lookup or cache check")
        
        print(f"Static plants: {static_plants}")
        print(f"LLM plants: {llm_plants}")
        
        # Get static plants immediately
        for name in static_plants:
            plant = self.static_plants[name.lower()]
            if plant:
                plants.append(plant)
                print(f"✅ Added static plant: {plant.name}")
        
        # Get LLM plants in parallel
        if llm_plants:
            print(f"🔍 Checking cache/LLM for: {llm_plants}")
            llm_tasks = [self.get_plant_info(name) for name in llm_plants]
            llm_results = await asyncio.gather(*llm_tasks, return_exceptions=True)
            
            for i, result in enumerate(llm_results):
                if isinstance(result, PlantInfo):
                    plants.append(result)
                    print(f"✅ Added LLM/cached plant: {result.name}")
                elif isinstance(result, Exception):
                    print(f"❌ Error getting plant info for {llm_plants[i]}: {result}")
                else:
                    print(f"❌ No plant info found for {llm_plants[i]}")
        
        print(f"🏁 Returning {len(plants)} plants: {[p.name for p in plants]}")
        return plants

    def get_plants_by_type(self, plant_type: str) -> List[PlantInfo]:
        """
        Get static plants filtered by type
        """
        return [plant for plant in self.static_plants.values() 
                if plant.plant_type.lower() == plant_type.lower()]

    def get_all_static_plants(self) -> List[PlantInfo]:
        """
        Get list of all plants in static database (for plant selection UI)
        """
        return list(self.static_plants.values())
    
    def search_static_plants(self, query: str) -> List[PlantInfo]:
        """
        Search static plants by name (for autocomplete/suggestions)
        """
        query = query.lower()
        matching_plants = []
        
        for plant in self.static_plants.values():
            if query in plant.name.lower():
                matching_plants.append(plant)
        
        return matching_plants
    
    def get_cache_stats(self) -> Dict[str, Union[int, List[str]]]:
        """
        Get cache statistics (useful for monitoring)
        """
        return {
            "static_plants_count": len(self.static_plants),
            "cached_plants_count": self.cache.size(),
            "total_available": len(self.static_plants) + self.cache.size(),
            "cached_plant_names": list(self.cache._cache.keys()) if hasattr(self.cache, '_cache') else []
        }

# Global instance
plant_service = PlantService()
"""
Plant API endpoints for the JardAIn Garden Planner.
Provides HTTP access to plant data and search functionality.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from models.garden_plan import PlantInfo
from services.plant_service import plant_service
from services.llm_service import llm_service
from config import settings

# Create the plants router
router = APIRouter()

# Response models for API documentation
class PlantResponse(BaseModel):
    """Response model for plant information"""
    name: str
    scientific_name: Optional[str]
    plant_type: str
    days_to_harvest: Optional[int]
    spacing_inches: Optional[int]
    planting_depth_inches: Optional[float]
    sun_requirements: Optional[str]
    water_requirements: Optional[str]
    soil_ph_range: Optional[str]
    companion_plants: List[str]
    avoid_planting_with: List[str]

class PlantListResponse(BaseModel):
    """Response model for plant lists"""
    plants: List[PlantResponse]
    total_count: int
    source: str  # "static", "cached", or "mixed"

class PlantSearchResponse(BaseModel):
    """Response model for plant search results"""
    query: str
    plants: List[PlantResponse]
    total_results: int
    search_time_ms: int

class PlantStatsResponse(BaseModel):
    """Response model for plant service statistics"""
    static_plants_count: int
    cached_plants_count: int
    total_available: int
    cached_plant_names: List[str]

# Helper function to convert PlantInfo to PlantResponse
def plant_info_to_response(plant: PlantInfo) -> PlantResponse:
    """Convert PlantInfo model to API response format"""
    return PlantResponse(
        name=plant.name,
        scientific_name=plant.scientific_name,
        plant_type=plant.plant_type,
        days_to_harvest=plant.days_to_harvest,
        spacing_inches=plant.spacing_inches,
        planting_depth_inches=plant.planting_depth_inches,
        sun_requirements=plant.sun_requirements,
        water_requirements=plant.water_requirements,
        soil_ph_range=plant.soil_ph_range,
        companion_plants=plant.companion_plants or [],
        avoid_planting_with=plant.avoid_planting_with or []
    )

# ========================
# Plant List Endpoints
# ========================

@router.get("", response_model=PlantListResponse)
async def get_all_plants(
    plant_type: Optional[str] = Query(None, description="Filter by plant type (vegetable, herb, fruit)")
):
    """
    Get list of all available plants from static database.
    
    **Parameters:**
    - **plant_type**: Optional filter by type (vegetable, herb, fruit, flower)
    
    **Returns:**
    - List of plants with complete growing information
    - Total count and data source information
    """
    try:
        if plant_type:
            # Filter by plant type
            plants = await plant_service.get_plants_by_type(plant_type)
        else:
            # Get all plants (database first, then JSON fallback)
            plants = await plant_service.get_all_plants()
        
        # Convert to response format
        plant_responses = [plant_info_to_response(plant) for plant in plants]
        
        return PlantListResponse(
            plants=plant_responses,
            total_count=len(plant_responses),
            source="database" if plant_service.database_available else "static"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plants: {str(e)}")

@router.get("/types", response_model=List[str])
async def get_plant_types():
    """
    Get list of available plant types.
    
    **Returns:**
    - List of unique plant types in the database
    """
    try:
        plants = await plant_service.get_all_plants()
        plant_types = list(set(plant.plant_type for plant in plants))
        return sorted(plant_types)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plant types: {str(e)}")

# ========================
# Plant Search Endpoints  
# ========================

@router.get("/search", response_model=PlantSearchResponse)
async def search_plants(
    q: str = Query(..., description="Search query for plant names"),
    include_generated: bool = Query(False, description="Include LLM-generated plants in search")
):
    """
    Search for plants by name.
    
    **Parameters:**
    - **q**: Search query (partial plant name matching)
    - **include_generated**: Whether to generate new plants via LLM if not found
    
    **Returns:**
    - Matching plants from static database
    - If include_generated=true and no results, attempts LLM generation
    """
    import time
    start_time = time.time()
    
    try:
        # Search database first (includes both static and LLM plants)
        search_results = await plant_service.search_plants(q)
        
        plants_found = [plant_info_to_response(plant) for plant in search_results]
        
        # If no results and include_generated is True, try LLM generation
        if not plants_found and include_generated:
            print(f"🤖 No static results for '{q}', attempting LLM generation...")
            generated_plant = await plant_service.get_plant_info(q)
            if generated_plant:
                plants_found = [plant_info_to_response(generated_plant)]
        
        search_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        return PlantSearchResponse(
            query=q,
            plants=plants_found,
            total_results=len(plants_found),
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# ========================
# Individual Plant Endpoints
# ========================

@router.get("/{plant_name}", response_model=PlantResponse)
async def get_plant_by_name(plant_name: str):
    """
    Get detailed information for a specific plant.
    
    **Parameters:**
    - **plant_name**: Name of the plant to retrieve
    
    **Returns:**
    - Complete plant information from static database or LLM generation
    
    **Behavior:**
    1. Checks static database first (fast)
    2. Checks cache for previously generated plants  
    3. Generates via LLM if not found (unlimited variety)
    """
    try:
        plant = await plant_service.get_plant_info(plant_name)
        
        if not plant:
            raise HTTPException(
                status_code=404, 
                detail=f"Plant '{plant_name}' not found in database and could not be generated"
            )
        
        return plant_info_to_response(plant)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plant: {str(e)}")

@router.get("/types/{plant_type}", response_model=PlantListResponse)
async def get_plants_by_type(plant_type: str):
    """
    Get all plants of a specific type.
    
    **Parameters:**
    - **plant_type**: Type of plants to retrieve (vegetable, herb, fruit, flower)
    
    **Returns:**
    - List of plants matching the specified type
    """
    try:
        plants = await plant_service.get_plants_by_type(plant_type)
        
        if not plants:
            raise HTTPException(
                status_code=404,
                detail=f"No plants found for type '{plant_type}'"
            )
        
        plant_responses = [plant_info_to_response(plant) for plant in plants]
        
        return PlantListResponse(
            plants=plant_responses,
            total_count=len(plant_responses),
            source="database" if plant_service.database_available else "static"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plants by type: {str(e)}")

# ========================
# Service Statistics Endpoints
# ========================

@router.get("/stats/cache", response_model=PlantStatsResponse)
async def get_plant_service_stats():
    """
    Get statistics about the plant service performance.
    
    **Returns:**
    - Count of static plants, cached plants, and total available
    - List of cached plant names
    
    **Use case:**
    - Monitoring and debugging
    - Understanding cache performance
    """
    try:
        stats = plant_service.get_cache_stats()
        
        return PlantStatsResponse(
            static_plants_count=stats["static_plants_count"],
            cached_plants_count=stats["cached_plants_count"], 
            total_available=stats["total_available"],
            cached_plant_names=stats["cached_plant_names"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

# ========================
# Batch Operations
# ========================

@router.post("/batch", response_model=PlantListResponse)
async def get_multiple_plants(plant_names: List[str]):
    """
    Get information for multiple plants in a single request.
    
    **Parameters:**
    - **plant_names**: List of plant names to retrieve
    
    **Returns:**
    - List of plant information for found plants
    - Uses hybrid approach (static + LLM) for each plant
    
    **Behavior:**
    - Processes requests in parallel for efficiency
    - Returns partial results if some plants aren't found
    """
    try:
        if not plant_names:
            raise HTTPException(status_code=400, detail="Plant names list cannot be empty")
        
        if len(plant_names) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 plants per batch request")
        
        # Use the plant service's efficient batch method
        plants = await plant_service.get_multiple_plants(plant_names)
        
        plant_responses = [plant_info_to_response(plant) for plant in plants]
        
        return PlantListResponse(
            plants=plant_responses,
            total_count=len(plant_responses),
            source="mixed"  # Could be static, cached, or generated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch request error: {str(e)}")

# ========================
# Diagnostic Endpoints
# ========================

@router.get("/debug/llm-test")
async def test_llm_service():
    """
    Test LLM service configuration and functionality.
    
    **Returns:**
    - LLM provider configuration status
    - Test generation attempt
    - Detailed error information if any
    
    **Use case:**
    - Debugging LLM integration issues
    - Verifying OpenAI API key configuration
    """
    try:
        # Check configuration
        config_status = {
            "provider": settings.llm_provider,
            "is_configured": llm_service.is_configured(),
            "is_production": settings.is_production,
            "openai_key_present": bool(settings.openai_api_key),
            "openai_key_length": len(settings.openai_api_key) if settings.openai_api_key else 0
        }
        
        # Test generation
        test_prompt = "Generate basic information about tomato plants in JSON format."
        generation_result = await llm_service.test_generation_quality(test_prompt)
        
        return {
            "config": config_status,
            "test_generation": generation_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "config": {
                "provider": settings.llm_provider,
                "is_configured": False,
                "error_details": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }

@router.get("/debug/plant-search-test")
async def test_plant_search_with_ai(plant_name: str = "pineapple"):
    """
    Test plant search with AI generation for debugging.
    
    **Parameters:**
    - **plant_name**: Plant name to test (defaults to "pineapple")
    
    **Returns:**
    - Step-by-step search process results
    - Detailed error information if any
    """
    import time
    
    start_time = time.time()
    
    try:
        # Step 1: Check static database
        static_results = await plant_service.search_plants(plant_name)
        
        # Step 2: Try direct plant lookup
        direct_lookup = await plant_service.get_plant_info(plant_name)
        
        # Step 3: Check LLM service status
        llm_status = llm_service.is_configured()
        
        search_time = int((time.time() - start_time) * 1000)
        
        return {
            "query": plant_name,
            "steps": {
                "static_search": {
                    "results_count": len(static_results),
                    "results": [plant.name for plant in static_results]
                },
                "direct_lookup": {
                    "found": bool(direct_lookup),
                    "plant_name": direct_lookup.name if direct_lookup else None,
                    "plant_type": direct_lookup.plant_type if direct_lookup else None
                },
                "llm_service": {
                    "configured": llm_status,
                    "provider": settings.llm_provider
                }
            },
            "search_time_ms": search_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": plant_name,
            "search_time_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.now().isoformat()
        }
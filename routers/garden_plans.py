"""
Garden Plan API endpoints for the JardAIn Garden Planner.
Core functionality for creating personalized garden plans using AI.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

from models.garden_plan import GardenPlan, PlanRequest, LocationInfo, PlantingSchedule, GrowingInstructions
from services.garden_plan_service import garden_plan_service
from services.location_service import location_service
from services.plant_service import plant_service

# Create the garden plans router
router = APIRouter()

# ========================
# Request/Response Models
# ========================

class CreatePlanRequest(BaseModel):
    """Request model for creating a garden plan"""
    zip_code: str = Field(..., description="US zip code or Canadian postal code")
    selected_plants: List[str] = Field(..., min_items=1, max_items=20, description="List of plants to include in garden plan")
    garden_size: Optional[str] = Field("medium", description="Garden size: small, medium, or large")
    experience_level: Optional[str] = Field("beginner", description="Gardening experience: beginner, intermediate, or advanced")

class PlanSummary(BaseModel):
    """Summary information for a garden plan"""
    plan_id: str
    created_date: datetime
    location_summary: str
    plant_count: int
    growing_season_days: Optional[int]
    climate_type: Optional[str]

class PlantingScheduleResponse(BaseModel):
    """Response model for planting schedules"""
    plant_name: str
    start_indoors_date: Optional[date]
    direct_sow_date: Optional[date]
    transplant_date: Optional[date]
    harvest_start_date: Optional[date]
    harvest_end_date: Optional[date]
    succession_planting_interval: Optional[int]

class GrowingInstructionsResponse(BaseModel):
    """Response model for growing instructions"""
    plant_name: str
    preparation_steps: List[str]
    planting_steps: List[str]
    care_instructions: List[str]
    pest_management: List[str]
    harvest_instructions: List[str]
    storage_tips: List[str]

class LocationResponse(BaseModel):
    """Response model for location information"""
    zip_code: str
    city: Optional[str]
    state: Optional[str]
    usda_zone: Optional[str]
    last_frost_date: Optional[date]
    first_frost_date: Optional[date]
    growing_season_days: Optional[int]
    climate_type: Optional[str]

class GardenPlanResponse(BaseModel):
    """Complete garden plan response"""
    plan_id: str
    created_date: datetime
    location: LocationResponse
    selected_plants: List[str]
    plant_information: List[Dict[str, Any]]  # Plant details
    planting_schedules: List[PlantingScheduleResponse]
    growing_instructions: List[GrowingInstructionsResponse]
    layout_recommendations: Dict[str, Any]
    general_tips: List[str]

# Helper functions
def location_to_response(location: LocationInfo) -> LocationResponse:
    """Convert LocationInfo to response format"""
    return LocationResponse(
        zip_code=location.zip_code,
        city=location.city,
        state=location.state,
        usda_zone=location.usda_zone,
        last_frost_date=location.last_frost_date,
        first_frost_date=location.first_frost_date,
        growing_season_days=location.growing_season_days,
        climate_type=location.climate_type
    )

def schedule_to_response(schedule: PlantingSchedule) -> PlantingScheduleResponse:
    """Convert PlantingSchedule to response format"""
    return PlantingScheduleResponse(
        plant_name=schedule.plant_name,
        start_indoors_date=schedule.start_indoors_date,
        direct_sow_date=schedule.direct_sow_date,
        transplant_date=schedule.transplant_date,
        harvest_start_date=schedule.harvest_start_date,
        harvest_end_date=schedule.harvest_end_date,
        succession_planting_interval=schedule.succession_planting_interval
    )

def instructions_to_response(instructions: GrowingInstructions) -> GrowingInstructionsResponse:
    """Convert GrowingInstructions to response format"""
    return GrowingInstructionsResponse(
        plant_name=instructions.plant_name,
        preparation_steps=instructions.preparation_steps,
        planting_steps=instructions.planting_steps,
        care_instructions=instructions.care_instructions,
        pest_management=instructions.pest_management,
        harvest_instructions=instructions.harvest_instructions,
        storage_tips=instructions.storage_tips
    )

# ========================
# Main Garden Plan Endpoints
# ========================

@router.post("", response_model=GardenPlanResponse)
async def create_garden_plan(request: CreatePlanRequest):
    """
    Create a personalized garden plan using AI.
    
    **The core feature of JardAIn!** This endpoint:
    1. Analyzes your location's climate and growing conditions
    2. Retrieves detailed information for your selected plants
    3. Generates AI-powered planting schedules based on your local frost dates
    4. Creates step-by-step growing instructions for each plant
    5. Provides companion planting and layout recommendations
    6. Offers personalized tips for your experience level
    
    **Parameters:**
    - **zip_code**: US zip code (12345) or Canadian postal code (K1A 0A6)
    - **selected_plants**: List of plants to grow (1-20 plants)
    - **garden_size**: Size of your garden space (small/medium/large)
    - **experience_level**: Your gardening experience (beginner/intermediate/advanced)
    
    **Returns:**
    - Complete personalized garden plan with planting schedules, instructions, and tips
    
    **Example Request:**
    ```json
    {
        "zip_code": "90210",
        "selected_plants": ["tomato", "basil", "lettuce"],
        "garden_size": "medium",
        "experience_level": "beginner"
    }
    ```
    """
    try:
        print(f"🌱 Creating garden plan for {request.zip_code} with {len(request.selected_plants)} plants")
        
        # Validate input
        if not request.selected_plants:
            raise HTTPException(status_code=400, detail="At least one plant must be selected")
        
        if len(request.selected_plants) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 plants allowed per garden plan")
        
        # Convert to internal request format
        plan_request = PlanRequest(
            zip_code=request.zip_code,
            selected_plants=request.selected_plants,
            garden_size=request.garden_size,
            experience_level=request.experience_level
        )
        
        # Generate the garden plan using our AI service
        garden_plan = await garden_plan_service.create_garden_plan(plan_request)
        
        # Convert to response format
        plant_info_dicts = []
        for plant in garden_plan.plant_information:
            plant_dict = {
                "name": plant.name,
                "scientific_name": plant.scientific_name,
                "plant_type": plant.plant_type,
                "days_to_harvest": plant.days_to_harvest,
                "spacing_inches": plant.spacing_inches,
                "planting_depth_inches": plant.planting_depth_inches,
                "sun_requirements": plant.sun_requirements,
                "water_requirements": plant.water_requirements,
                "soil_ph_range": plant.soil_ph_range,
                "companion_plants": plant.companion_plants or [],
                "avoid_planting_with": plant.avoid_planting_with or []
            }
            plant_info_dicts.append(plant_dict)
        
        response = GardenPlanResponse(
            plan_id=garden_plan.plan_id,
            created_date=garden_plan.created_date,
            location=location_to_response(garden_plan.location),
            selected_plants=garden_plan.selected_plants,
            plant_information=plant_info_dicts,
            planting_schedules=[schedule_to_response(s) for s in garden_plan.planting_schedules],
            growing_instructions=[instructions_to_response(i) for i in garden_plan.growing_instructions],
            layout_recommendations=garden_plan.layout_recommendations or {},
            general_tips=garden_plan.general_tips or []
        )
        
        print(f"✅ Garden plan {garden_plan.plan_id} created successfully!")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Error creating garden plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create garden plan: {str(e)}")

# ========================
# Utility Endpoints
# ========================

@router.get("/test-static", response_model=Dict[str, Any])
async def test_static_plants():
    """
    Test endpoint to verify static plant database is working.
    Returns a sample of available plants from the static database.
    """
    try:
        from services.plant_service import plant_service
        
        # Get a few sample plants from static database
        static_plants = plant_service.get_all_static_plants()
        sample_plants = static_plants[:5]  # First 5 plants
        
        return {
            "status": "success",
            "total_static_plants": len(static_plants),
            "sample_plants": [plant.name for plant in sample_plants],
            "database_available": plant_service.database_available,
            "message": "Static plant database is working correctly"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Static plant database test failed"
        }

@router.post("/validate", response_model=Dict[str, Any])
async def validate_garden_plan_request(request: CreatePlanRequest):
    """
    Validate a garden plan request without creating the full plan.
    
    **Use case:** Check if location is valid and plants are available before creating the full plan.
    
    **Returns:**
    - Location information
    - Available plants from the request
    - Estimated generation time
    - Any warnings or suggestions
    """
    try:
        # Validate location
        location_info = await location_service.get_location_info(request.zip_code)
        
        # Check plant availability
        available_plants = []
        unavailable_plants = []
        
        for plant_name in request.selected_plants:
            plant = await plant_service.get_plant_info(plant_name)
            if plant:
                available_plants.append(plant.name)
            else:
                unavailable_plants.append(plant_name)
        
        # Estimate generation time
        estimated_time_seconds = len(available_plants) * 3 + len(unavailable_plants) * 8  # LLM plants take longer
        
        # Generate warnings/suggestions
        warnings = []
        suggestions = []
        
        if not location_info.city:
            warnings.append(f"Could not validate location for {request.zip_code}")
        
        if location_info.growing_season_days and location_info.growing_season_days < 120:
            warnings.append(f"Short growing season ({location_info.growing_season_days} days) - consider cold-hardy varieties")
        
        if len(request.selected_plants) > 10:
            suggestions.append("Large plant selection - consider garden size and maintenance requirements")
        
        if request.experience_level == "beginner" and len(request.selected_plants) > 5:
            suggestions.append("Consider starting with fewer plants for your first garden")
        
        return {
            "valid": len(available_plants) > 0,
            "location": location_to_response(location_info) if location_info.city else None,
            "available_plants": available_plants,
            "unavailable_plants": unavailable_plants,
            "estimated_generation_time_seconds": estimated_time_seconds,
            "warnings": warnings,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/location/{postal_code}", response_model=LocationResponse)
async def get_location_info(postal_code: str):
    """
    Get climate and growing information for a specific location.
    
    **Parameters:**
    - **postal_code**: US zip code or Canadian postal code
    
    **Returns:**
    - Detailed location and climate information
    - USDA/Canadian hardiness zone
    - Frost dates and growing season length
    
    **Use case:** Preview location information before creating a garden plan
    """
    try:
        location_info = await location_service.get_location_info(postal_code)
        
        if not location_info.city:
            raise HTTPException(status_code=404, detail=f"Location information not found for {postal_code}")
        
        return location_to_response(location_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving location info: {str(e)}")

@router.get("/suggestions/{postal_code}", response_model=Dict[str, Any])
async def get_plant_suggestions(postal_code: str, experience_level: str = "beginner"):
    """
    Get plant suggestions based on location and experience level.
    
    **Parameters:**
    - **postal_code**: US zip code or Canadian postal code
    - **experience_level**: beginner, intermediate, or advanced
    
    **Returns:**
    - Recommended plants for the location and experience level
    - Plants to avoid for the climate
    - Seasonal planting suggestions
    """
    try:
        # Get location info
        location_info = await location_service.get_location_info(postal_code)
        
        if not location_info.city:
            raise HTTPException(status_code=404, detail=f"Location not found: {postal_code}")
        
        # Get all available plants
        all_plants = plant_service.get_all_static_plants()
        
        # Filter recommendations based on climate and experience
        recommendations = {
            "beginner_friendly": [],
            "climate_appropriate": [],
            "quick_growing": [],
            "avoid_for_climate": [],
            "seasonal_suggestions": {}
        }
        
        for plant in all_plants:
            # Beginner-friendly plants (quick, easy to grow)
            if (plant.days_to_harvest and plant.days_to_harvest <= 60 and 
                plant.plant_type in ["vegetable", "herb"]):
                recommendations["beginner_friendly"].append(plant.name)
            
            # Quick growing plants
            if plant.days_to_harvest and plant.days_to_harvest <= 45:
                recommendations["quick_growing"].append(plant.name)
            
            # Climate appropriate (based on growing season)
            if (location_info.growing_season_days and plant.days_to_harvest and
                plant.days_to_harvest <= location_info.growing_season_days - 30):
                recommendations["climate_appropriate"].append(plant.name)
        
        # Limit results to avoid overwhelming response
        for key in recommendations:
            if isinstance(recommendations[key], list):
                recommendations[key] = recommendations[key][:10]
        
        return {
            "location": location_to_response(location_info),
            "recommendations": recommendations,
            "experience_level": experience_level,
            "note": "Suggestions based on location climate and growing season"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

# ========================
# Plan Management (Future)
# ========================

@router.get("/{plan_id}", response_model=Dict[str, str])
async def get_garden_plan(plan_id: str):
    """
    Get an existing garden plan by ID.
    
    **Note:** This is a placeholder endpoint. In the current version, plans are not stored.
    In a future version, you could store plans in a database and retrieve them here.
    """
    # This would require implementing plan storage
    raise HTTPException(
        status_code=501, 
        detail="Plan storage not implemented yet. Plans are generated fresh each time."
    )

@router.get("", response_model=List[PlanSummary])
async def list_garden_plans():
    """
    List all saved garden plans.
    
    **Note:** This is a placeholder endpoint for future plan storage functionality.
    """
    # This would require implementing plan storage
    raise HTTPException(
        status_code=501,
        detail="Plan storage not implemented yet. Create new plans using POST /api/plans/"
    )
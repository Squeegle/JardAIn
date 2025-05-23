"""
Data models for garden planning.
Defines the structure of garden plans, plant information, and location data.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime

class PlantInfo(BaseModel):
    """
    Information about a specific plant/vegetable
    """
    name: str
    scientific_name: Optional[str] = None
    plant_type: str  # "vegetable", "herb", "fruit", etc.
    days_to_harvest: Optional[int] = None
    spacing_inches: Optional[int] = None
    planting_depth_inches: Optional[float] = None
    sun_requirements: Optional[str] = None  # "full sun", "partial shade", etc.
    water_requirements: Optional[str] = None
    soil_ph_range: Optional[str] = None
    companion_plants: Optional[List[str]] = []
    avoid_planting_with: Optional[List[str]] = []

class LocationInfo(BaseModel):
    """
    Climate and location information for garden planning
    """
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None
    usda_zone: Optional[str] = None
    last_frost_date: Optional[date] = None
    first_frost_date: Optional[date] = None
    growing_season_days: Optional[int] = None
    climate_type: Optional[str] = None

class PlantingSchedule(BaseModel):
    """
    Planting schedule for a specific plant
    """
    plant_name: str
    start_indoors_date: Optional[date] = None
    direct_sow_date: Optional[date] = None
    transplant_date: Optional[date] = None
    harvest_start_date: Optional[date] = None
    harvest_end_date: Optional[date] = None
    succession_planting_interval: Optional[int] = None  # days between plantings

class GrowingInstructions(BaseModel):
    """
    Detailed growing instructions for a plant
    """
    plant_name: str
    preparation_steps: List[str]
    planting_steps: List[str]
    care_instructions: List[str]
    pest_management: List[str]
    harvest_instructions: List[str]
    storage_tips: List[str]

class GardenPlan(BaseModel):
    """
    Complete garden plan for a user
    """
    plan_id: str
    created_date: datetime
    location: LocationInfo
    selected_plants: List[str]
    plant_information: List[PlantInfo]
    planting_schedules: List[PlantingSchedule]
    growing_instructions: List[GrowingInstructions]
    layout_recommendations: Optional[Dict[str, Any]] = None
    general_tips: Optional[List[str]] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

class PlanRequest(BaseModel):
    """
    Request model for creating a garden plan
    """
    zip_code: str
    selected_plants: List[str]
    garden_size: Optional[str] = "medium"  # small, medium, large
    experience_level: Optional[str] = "beginner"  # beginner, intermediate, advanced
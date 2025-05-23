"""
Garden plan generation service - the AI brain that creates personalized garden plans.
Combines location data, plant information, and LLM generation for comprehensive garden planning.
"""

import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from models.garden_plan import (
    GardenPlan, PlanRequest, LocationInfo, PlantInfo,
    PlantingSchedule, GrowingInstructions
)
from services.plant_service import plant_service
from services.location_service import location_service
from services.llm_service import llm_service
from config import settings

class GardenPlanService:
    """
    Service for generating comprehensive, personalized garden plans using AI
    """
    
    def __init__(self):
        print("🧠 Garden Plan Service initialized")
    
    async def create_garden_plan(self, request: PlanRequest) -> GardenPlan:
        """
        Create a complete personalized garden plan
        
        Process:
        1. Get location/climate information from zip code
        2. Retrieve plant information for selected plants
        3. Generate AI-powered planting schedules
        4. Create detailed growing instructions
        5. Provide layout recommendations
        6. Add general gardening tips
        """
        print(f"🌱 Creating garden plan for {len(request.selected_plants)} plants in {request.zip_code}")
        
        # Step 1: Get location information
        location_info = await location_service.get_location_info(request.zip_code)
        
        # Step 2: Get plant information (using our hybrid service)
        plant_information = await plant_service.get_multiple_plants(request.selected_plants)
        
        if not plant_information:
            raise ValueError("No plant information could be retrieved for the selected plants")
        
        # Step 3: Generate planting schedules using AI
        planting_schedules = await self._generate_planting_schedules(
            plant_information, location_info, request
        )
        
        # Step 4: Generate detailed growing instructions
        growing_instructions = await self._generate_growing_instructions(
            plant_information, location_info, request
        )
        
        # Step 5: Generate layout recommendations
        layout_recommendations = await self._generate_layout_recommendations(
            plant_information, request
        )
        
        # Step 6: Generate general tips
        general_tips = await self._generate_general_tips(
            plant_information, location_info, request
        )
        
        # Create the complete garden plan
        garden_plan = GardenPlan(
            plan_id=str(uuid.uuid4()),
            created_date=datetime.now(),
            location=location_info,
            selected_plants=[plant.name for plant in plant_information],
            plant_information=plant_information,
            planting_schedules=planting_schedules,
            growing_instructions=growing_instructions,
            layout_recommendations=layout_recommendations,
            general_tips=general_tips
        )
        
        print(f"✅ Garden plan created successfully with {len(plant_information)} plants")
        return garden_plan
    
    async def _generate_planting_schedules(
        self, 
        plants: List[PlantInfo], 
        location: LocationInfo, 
        request: PlanRequest
    ) -> List[PlantingSchedule]:
        """
        Generate AI-powered planting schedules based on location and climate
        """
        print("📅 Generating planting schedules...")
        
        # Create detailed prompt for LLM
        plants_info = []
        for plant in plants:
            plants_info.append({
                "name": plant.name,
                "type": plant.plant_type,
                "days_to_harvest": plant.days_to_harvest,
                "spacing": plant.spacing_inches
            })
        
        prompt = f"""
        You are an expert garden planner. Create precise planting schedules for the following plants based on the location and climate information.

        LOCATION INFORMATION:
        - Location: {location.city}, {location.state} ({location.zip_code})
        - USDA Zone: {location.usda_zone}
        - Last Frost Date: {location.last_frost_date}
        - First Frost Date: {location.first_frost_date}
        - Growing Season: {location.growing_season_days} days
        - Climate Type: {location.climate_type}

        PLANTS TO SCHEDULE:
        {json.dumps(plants_info, indent=2)}

        GARDENER PROFILE:
        - Experience Level: {request.experience_level}
        - Garden Size: {request.garden_size}

        Please provide a JSON array of planting schedules with this exact structure:
        [
            {{
                "plant_name": "Tomato",
                "start_indoors_date": "2024-03-15",
                "direct_sow_date": null,
                "transplant_date": "2024-05-15",
                "harvest_start_date": "2024-07-15",
                "harvest_end_date": "2024-10-01",
                "succession_planting_interval": 14
            }}
        ]

        REQUIREMENTS:
        - Use ISO date format (YYYY-MM-DD) 
        - Consider the last frost date for timing
        - Account for each plant's days to harvest
        - Provide either start_indoors_date OR direct_sow_date (not both for same plant)
        - Include succession planting intervals where appropriate
        - Ensure harvest dates are realistic for the growing season
        - Consider the experience level (beginners get simpler schedules)
        """
        
        try:
            response = await llm_service.generate_plant_info(prompt)
            
            if not response:
                return self._create_default_schedules(plants, location)
            
            # Parse the JSON response
            schedules_data = json.loads(response.strip())
            
            schedules = []
            for schedule_data in schedules_data:
                # Convert date strings to date objects
                schedule = PlantingSchedule(
                    plant_name=schedule_data["plant_name"],
                    start_indoors_date=self._parse_date(schedule_data.get("start_indoors_date")),
                    direct_sow_date=self._parse_date(schedule_data.get("direct_sow_date")),
                    transplant_date=self._parse_date(schedule_data.get("transplant_date")),
                    harvest_start_date=self._parse_date(schedule_data.get("harvest_start_date")),
                    harvest_end_date=self._parse_date(schedule_data.get("harvest_end_date")),
                    succession_planting_interval=schedule_data.get("succession_planting_interval")
                )
                schedules.append(schedule)
            
            return schedules
            
        except Exception as e:
            print(f"⚠️  Error generating planting schedules: {e}")
            return self._create_default_schedules(plants, location)
    
    async def _generate_growing_instructions(
        self,
        plants: List[PlantInfo],
        location: LocationInfo,
        request: PlanRequest
    ) -> List[GrowingInstructions]:
        """
        Generate detailed, step-by-step growing instructions for each plant
        """
        print("📋 Generating detailed growing instructions...")
        
        instructions_list = []
        
        # Generate instructions for each plant individually for better quality
        for plant in plants:
            prompt = f"""
            You are an expert master gardener with 30+ years of experience. Create DETAILED, SPECIFIC growing instructions for {plant.name} in {location.city}, {location.state}.

            PLANT INFORMATION:
            - Name: {plant.name} ({plant.scientific_name})
            - Type: {plant.plant_type}
            - Days to harvest: {plant.days_to_harvest}
            - Spacing: {plant.spacing_inches} inches
            - Sun requirements: {plant.sun_requirements}
            - Water requirements: {plant.water_requirements}
            - Soil pH: {plant.soil_ph_range}
            - Companion plants: {plant.companion_plants}

            LOCATION CONDITIONS:
            - Location: {location.city}, {location.state}
            - USDA Zone: {location.usda_zone}
            - Climate: {location.climate_type}
            - Last frost: {location.last_frost_date}
            - First frost: {location.first_frost_date}
            - Growing season: {location.growing_season_days} days

            GARDENER PROFILE:
            - Experience: {request.experience_level}
            - Garden size: {request.garden_size}

            REQUIREMENTS - BE VERY SPECIFIC AND DETAILED:
            - Give exact measurements, temperatures, timing
            - Include specific varieties good for this zone
            - Mention local climate considerations
            - Provide troubleshooting for common problems
            - Include seasonal care schedules
            - NO generic advice like "follow package directions"

            Provide instructions in this exact JSON format:
            {{
                "plant_name": "{plant.name}",
                "preparation_steps": [
                    "Test soil pH to 6.0-6.8 range using digital meter",
                    "Amend clay soil with 2-3 inches compost for drainage",
                    "Choose location with 6-8 hours direct sunlight"
                ],
                "planting_steps": [
                    "Start seeds indoors 6-8 weeks before {location.last_frost_date}",
                    "Sow seeds 1/4 inch deep in seed starting mix",
                    "Maintain soil temperature at 70-75°F for germination"
                ],
                "care_instructions": [
                    "Water deeply 1-2 times per week, providing 1-1.5 inches total",
                    "Apply balanced fertilizer (10-10-10) every 3-4 weeks",
                    "Mulch around plants with 2-3 inches organic matter"
                ],
                "pest_management": [
                    "Monitor for hornworms weekly from June-August",
                    "Use row covers in early season to prevent flea beetles",
                    "Spray neem oil every 2 weeks if aphids appear"
                ],
                "harvest_instructions": [
                    "Harvest when fruits are fully colored but still firm",
                    "Pick in early morning when temperatures are cool",
                    "Use clean, sharp shears to avoid damaging plant"
                ],
                "storage_tips": [
                    "Store ripe tomatoes at room temperature for best flavor",
                    "Green tomatoes can ripen indoors in paper bags",
                    "Preserve excess by canning, freezing, or dehydrating"
                ]
            }}

            Make ALL instructions specific to {request.experience_level} gardeners in {location.climate_type} climate zone {location.usda_zone}.
            Include exact timing based on {location.last_frost_date} and {location.first_frost_date}.
            """
            
            try:
                print(f"🤖 Generating detailed instructions for {plant.name}...")
                response = await llm_service.generate_plant_info(prompt)
                
                if response and len(response.strip()) > 100:  # Ensure we got substantial content
                    try:
                        instruction_data = json.loads(response.strip())
                        instructions = GrowingInstructions(**instruction_data)
                        instructions_list.append(instructions)
                        print(f"✅ Generated detailed instructions for {plant.name}")
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON parsing error for {plant.name}: {e}")
                        print(f"Raw response: {response[:200]}...")
                        instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
                else:
                    print(f"⚠️  Insufficient response for {plant.name}, using enhanced default")
                    instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
                    
            except Exception as e:
                print(f"❌ Error generating instructions for {plant.name}: {e}")
                instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
        
        return instructions_list
    
    def _create_enhanced_default_instructions(self, plant: PlantInfo, location: LocationInfo, request: PlanRequest) -> GrowingInstructions:
        """
        Create enhanced default instructions when AI generation fails
        """
        return GrowingInstructions(
            plant_name=plant.name,
            preparation_steps=[
                f"Choose a location with {plant.sun_requirements or 'appropriate sunlight'} for {plant.name}",
                f"Prepare soil with pH {plant.soil_ph_range or '6.0-7.0'} suitable for {plant.name}",
                f"Ensure good drainage as {plant.name} requires {plant.water_requirements or 'moderate'} watering"
            ],
            planting_steps=[
                f"Plant {plant.name} seeds at {plant.planting_depth_inches or 0.5} inch depth",
                f"Space plants {plant.spacing_inches or 12} inches apart for proper growth",
                f"Plant after last frost date ({location.last_frost_date}) in your zone {location.usda_zone}"
            ],
            care_instructions=[
                f"Water {plant.name} according to {plant.water_requirements or 'moderate'} water needs",
                f"Monitor growth and provide support if needed for {plant.name}",
                f"Fertilize appropriately for {plant.plant_type} during growing season"
            ],
            pest_management=[
                f"Monitor {plant.name} regularly for common {plant.plant_type} pests",
                f"Use integrated pest management appropriate for {location.climate_type} climate",
                f"Inspect weekly and treat organically when possible"
            ],
            harvest_instructions=[
                f"Harvest {plant.name} approximately {plant.days_to_harvest or 60} days after planting",
                f"Pick {plant.name} at optimal ripeness for best flavor",
                f"Harvest regularly to encourage continued production"
            ],
            storage_tips=[
                f"Store fresh {plant.name} properly to maintain quality",
                f"Consider preservation methods suitable for {plant.plant_type}",
                f"Use or preserve harvest promptly for best results"
            ]
        )
    
    async def _generate_layout_recommendations(
        self,
        plants: List[PlantInfo],
        request: PlanRequest
    ) -> Dict[str, Any]:
        """
        Generate garden layout and spacing recommendations
        """
        print("🗺️  Generating layout recommendations...")
        
        plants_info = []
        for plant in plants:
            plants_info.append({
                "name": plant.name,
                "spacing_inches": plant.spacing_inches,
                "companion_plants": plant.companion_plants,
                "avoid_planting_with": plant.avoid_planting_with
            })
        
        prompt = f"""
        Create garden layout recommendations for a {request.garden_size} garden with {request.experience_level} gardener.

        PLANTS TO ARRANGE:
        {json.dumps(plants_info, indent=2)}

        Provide recommendations in this JSON format:
        {{
            "garden_dimensions": "Suggested dimensions",
            "plant_groupings": [
                {{
                    "group_name": "Tomato Section", 
                    "plants": ["Tomato", "Basil"],
                    "reasoning": "Basil repels pests that affect tomatoes"
                }}
            ],
            "spacing_guide": {{
                "Tomato": "24 inches apart, 36 inches between rows"
            }},
            "companion_planting_tips": [
                "Plant basil near tomatoes for pest control"
            ],
            "layout_tips": [
                "Place taller plants on north side to avoid shading"
            ]
        }}

        Focus on companion planting benefits and efficient space usage.
        """
        
        try:
            response = await llm_service.generate_plant_info(prompt)
            if response:
                return json.loads(response.strip())
        except Exception as e:
            print(f"⚠️  Error generating layout recommendations: {e}")
        
        # Default layout recommendations
        return {
            "garden_dimensions": f"Recommended for {request.garden_size} garden",
            "plant_groupings": [{"group_name": "Mixed Garden", "plants": [p.name for p in plants]}],
            "spacing_guide": {p.name: f"{p.spacing_inches} inches apart" for p in plants if p.spacing_inches},
            "companion_planting_tips": ["Consider companion planting benefits"],
            "layout_tips": ["Place taller plants where they won't shade shorter ones"]
        }
    
    async def _generate_general_tips(
        self,
        plants: List[PlantInfo],
        location: LocationInfo,
        request: PlanRequest
    ) -> List[str]:
        """
        Generate general gardening tips specific to the location and plant selection
        """
        print("💡 Generating general tips...")
        
        prompt = f"""
        Provide 5-7 general gardening tips for a {request.experience_level} gardener in {location.city}, {location.state} growing these plants: {[p.name for p in plants]}.

        Consider:
        - USDA Zone: {location.usda_zone}
        - Climate: {location.climate_type}
        - Growing season: {location.growing_season_days} days

        Return as a simple JSON array of strings:
        ["Tip 1", "Tip 2", ...]

        Make tips specific and actionable for this location and plant selection.
        """
        
        try:
            response = await llm_service.generate_plant_info(prompt)
            if response:
                return json.loads(response.strip())
        except Exception as e:
            print(f"⚠️  Error generating general tips: {e}")
        
        # Default tips
        return [
            f"Consider your USDA zone ({location.usda_zone}) when planning planting dates",
            "Start with a soil test to understand your garden's needs",
            "Water deeply but less frequently to encourage strong root growth",
            "Keep a garden journal to track what works in your specific location"
        ]
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_string or date_string.lower() == "null":
            return None
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except:
            return None
    
    def _create_default_schedules(self, plants: List[PlantInfo], location: LocationInfo) -> List[PlantingSchedule]:
        """Create basic schedules if AI generation fails"""
        schedules = []
        base_date = location.last_frost_date or date.today()
        
        for plant in plants:
            schedule = PlantingSchedule(
                plant_name=plant.name,
                direct_sow_date=base_date + timedelta(days=14),
                harvest_start_date=base_date + timedelta(days=(plant.days_to_harvest or 60) + 14),
                harvest_end_date=base_date + timedelta(days=(plant.days_to_harvest or 60) + 60),
                succession_planting_interval=14 if plant.plant_type == "vegetable" else None
            )
            schedules.append(schedule)
        
        return schedules
    
    def _create_default_instructions(self, plant: PlantInfo) -> GrowingInstructions:
        """Create basic instructions if AI generation fails"""
        return GrowingInstructions(
            plant_name=plant.name,
            preparation_steps=[f"Prepare soil for {plant.name}"],
            planting_steps=[f"Plant {plant.name} according to package directions"],
            care_instructions=[f"Water and fertilize {plant.name} regularly"],
            pest_management=[f"Monitor {plant.name} for common pests"],
            harvest_instructions=[f"Harvest {plant.name} when ready"],
            storage_tips=[f"Store {plant.name} properly after harvest"]
        )

# Global instance
garden_plan_service = GardenPlanService()
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
You are a professional master gardener. You MUST respond with ONLY valid JSON - no extra text, explanations, or formatting.

PLANT: {plant.name} in {location.city}, {location.state} (Zone {location.usda_zone})
FROST DATES: Last {location.last_frost_date}, First {location.first_frost_date}

CRITICAL: Respond with ONLY the JSON below - no "Here's the JSON:" or explanations:

{{
    "plant_name": "{plant.name}",
    "preparation_steps": [
        "Test soil pH to {plant.soil_ph_range or '6.0-6.8'} using digital meter 2-3 weeks before planting",
        "Work 2-3 inches compost into top 8 inches soil when temperature reaches 50°F",
        "Choose location with {plant.sun_requirements or 'full sun'} receiving 6-8 hours direct sunlight daily"
    ],
    "planting_steps": [
        "Start {plant.name} seeds indoors 6-8 weeks before {location.last_frost_date} at 70-75°F soil temperature",
        "Sow seeds {plant.planting_depth_inches or 0.5} inches deep with {plant.spacing_inches or 12} inch spacing between plants",
        "Transplant outdoors 2 weeks after {location.last_frost_date} when nighttime temperatures stay above 50°F"
    ],
    "care_instructions": [
        "Water {plant.name} deeply 1-1.5 inches per week checking soil moisture 2 inches deep every 3 days",
        "Apply 10-10-10 fertilizer at 2 tablespoons per plant every 3 weeks starting 2 weeks after transplant",
        "Mulch with 2-3 inches organic matter keeping 6 inches away from plant stem"
    ],
    "pest_management": [
        "Inspect {plant.name} weekly for common zone {location.usda_zone} pests from May through September",
        "Apply neem oil spray at 2 tablespoons per gallon water every 14 days if pests detected",
        "Use floating row covers first 3 weeks after transplant to prevent early season pest damage"
    ],
    "harvest_instructions": [
        "Begin harvesting {plant.name} approximately {plant.days_to_harvest or 60} days after transplant when fruits reach full size",
        "Harvest in early morning 6-8 AM when temperatures below 75°F for best quality and flavor",
        "Cut stems with clean sharp shears 1/4 inch above leaf node to encourage continued production"
    ],
    "storage_tips": [
        "Store fresh {plant.name} at 55-60°F with 85% humidity for maximum 7-10 days after harvest",
        "Blanch and freeze within 24 hours of harvest - maintains quality for 8-12 months in freezer",
        "Preserve excess using canning or dehydrating methods appropriate for {plant.plant_type} type"
    ]
}}

RESPOND WITH ONLY THE JSON ABOVE - NO OTHER TEXT.
            """
            
            try:
                print(f"🤖 Generating ultra-detailed instructions for {plant.name}...")
                response = await llm_service.generate_plant_info(prompt)
                
                if response and len(response.strip()) > 200:  # Ensure substantial content
                    print(f"📝 Raw response length: {len(response)} characters")
                    
                    # Use improved JSON extraction
                    instruction_data = self._extract_and_clean_json(response)
                    
                    if instruction_data:
                        try:
                            # Validate that we got detailed content
                            is_detailed = self._validate_instruction_quality(instruction_data)
                            
                            if is_detailed:
                                instructions = GrowingInstructions(**instruction_data)
                                instructions_list.append(instructions)
                                print(f"✅ Generated detailed instructions for {plant.name}")
                            else:
                                print(f"⚠️  Instructions for {plant.name} not detailed enough, enhancing...")
                                enhanced_instructions = self._enhance_basic_instructions(instruction_data, plant, location, request)
                                instructions_list.append(enhanced_instructions)
                        
                        except Exception as e:
                            print(f"⚠️  Error creating GrowingInstructions for {plant.name}: {e}")
                            instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
                    else:
                        print(f"⚠️  Could not extract valid JSON for {plant.name}")
                        print(f"Response preview: {response[:300]}...")
                        instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
                else:
                    print(f"⚠️  Insufficient response for {plant.name}, using enhanced default")
                    instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
                    
            except Exception as e:
                print(f"❌ Error generating instructions for {plant.name}: {e}")
                instructions_list.append(self._create_enhanced_default_instructions(plant, location, request))
        
        return instructions_list
    
    def _validate_instruction_quality(self, instruction_data: Dict[str, Any]) -> bool:
        """
        Validate that instructions contain specific details, not generic advice
        """
        detailed_indicators = [
            'inches', 'feet', 'cm', 'temperature', '°f', '°c', 'degrees',
            'tablespoons', 'teaspoons', 'cups', 'gallons', 'liters',
            'weeks', 'days', 'hours', 'times per', 'every',
            'march', 'april', 'may', 'june', 'july', 'august', 'september',
            'ph', 'fertilizer', 'compost', 'mulch', 'soil moisture'
        ]
        
        # Check all instruction categories for specific details
        all_instructions = []
        for key in ['preparation_steps', 'planting_steps', 'care_instructions', 'pest_management', 'harvest_instructions', 'storage_tips']:
            all_instructions.extend(instruction_data.get(key, []))
        
        # Convert all instructions to lowercase for checking
        all_text = ' '.join(all_instructions).lower()
        
        # Count how many detailed indicators we found
        detail_count = sum(1 for indicator in detailed_indicators if indicator in all_text)
        
        # Consider it detailed if we have at least 5 specific indicators
        is_detailed = detail_count >= 5
        
        if not is_detailed:
            print(f"    Quality check: Found {detail_count} detail indicators, need at least 5")
            print(f"    Sample text: {all_text[:150]}...")
        
        return is_detailed
    
    def _enhance_basic_instructions(self, instruction_data: Dict[str, Any], plant: PlantInfo, location: LocationInfo, request: PlanRequest) -> GrowingInstructions:
        """
        Enhance basic instructions with specific details
        """
        from datetime import timedelta
        
        # Calculate specific dates
        if location.last_frost_date:
            indoor_start = location.last_frost_date - timedelta(weeks=6)
            transplant_date = location.last_frost_date + timedelta(weeks=2)
            harvest_date = transplant_date + timedelta(days=plant.days_to_harvest or 60)
        else:
            indoor_start = None
            transplant_date = None
            harvest_date = None
        
        enhanced_data = instruction_data.copy()
        
        # Enhance preparation steps
        enhanced_data['preparation_steps'] = [
            f"Test soil pH to achieve {plant.soil_ph_range or '6.0-6.8'} using digital pH meter",
            f"Amend soil with 2-3 inches of compost worked into top 8 inches",
            f"Select location with {plant.sun_requirements or 'full sun'} - minimum 6-8 hours daily"
        ]
        
        # Enhance planting steps
        enhanced_data['planting_steps'] = [
            f"Start seeds indoors on {indoor_start.strftime('%B %d') if indoor_start else 'early spring'} at 70-75°F",
            f"Plant seeds {plant.planting_depth_inches or 0.5} inches deep with {plant.spacing_inches or 12} inch spacing",
            f"Transplant outdoors on {transplant_date.strftime('%B %d') if transplant_date else 'after last frost'} when soil is 60°F+"
        ]
        
        # Enhance care instructions
        enhanced_data['care_instructions'] = [
            f"Water deeply 1-1.5 inches per week, checking soil moisture 2 inches deep",
            f"Apply balanced 10-10-10 fertilizer at 2 tablespoons per plant every 3 weeks",
            f"Mulch with 2-3 inches organic matter, keeping 6 inches from plant stem"
        ]
        
        # Enhance harvest instructions
        enhanced_data['harvest_instructions'] = [
            f"Begin harvest approximately {plant.days_to_harvest or 60} days after transplant - around {harvest_date.strftime('%B %d') if harvest_date else 'mid-summer'}",
            f"Harvest in early morning (6-8 AM) when temperatures are below 75°F",
            f"Use clean, sharp shears cutting 1/4 inch above leaf nodes"
        ]
        
        return GrowingInstructions(**enhanced_data)
    
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
    
    def _extract_and_clean_json(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract and clean JSON from LLM response that may contain extra text
        """
        if not response:
            return None
        
        # Remove common LLM prefixes/suffixes
        cleaned = response.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Here's the JSON:",
            "Here is the JSON:",
            "```json",
            "```",
            "JSON:",
            "Response:",
            "Here's the detailed information:",
            "Here are the instructions:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes_to_remove = ["```", "Let me know if you need more details!", "I hope this helps!"]
        for suffix in suffixes_to_remove:
            if cleaned.lower().endswith(suffix.lower()):
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Find JSON boundaries
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            print(f"⚠️  No valid JSON boundaries found in response")
            return None
        
        # Extract just the JSON part
        json_str = cleaned[start_idx:end_idx + 1]
        
        try:
            # Try to parse the extracted JSON
            data = json.loads(json_str)
            return data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Attempting to fix common JSON issues...")
            
            # Try to fix common JSON issues
            fixed_json = self._fix_common_json_issues(json_str)
            
            try:
                data = json.loads(fixed_json)
                print("✅ Fixed JSON successfully!")
                return data
            except json.JSONDecodeError:
                print(f"❌ Could not fix JSON. Raw content preview:")
                print(f"{json_str[:200]}...")
                return None
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """
        Fix common JSON formatting issues from LLM responses
        """
        import re
        
        # Fix unescaped quotes in strings
        # This is a basic fix - more complex cases might need better handling
        fixed = json_str
        
        # Fix trailing commas before closing brackets/braces
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix missing commas between array elements
        fixed = re.sub(r'"\s*\n\s*"', '",\n    "', fixed)
        
        # Fix missing quotes around keys (basic case)
        fixed = re.sub(r'(\w+):', r'"\1":', fixed)
        
        # Remove any control characters
        fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', fixed)
        
        return fixed

# Global instance
garden_plan_service = GardenPlanService()
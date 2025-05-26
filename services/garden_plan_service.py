"""
Garden plan generation service - the AI brain that creates personalized garden plans.
Combines location data, plant information, and LLM generation for comprehensive garden planning.
"""

import json
import uuid
import re
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
        try:
            plant_information = await plant_service.get_multiple_plants(request.selected_plants)
        except Exception as e:
            print(f"❌ Error retrieving plant information: {e}")
            # Try to get plants from static database as fallback
            plant_information = []
            for plant_name in request.selected_plants:
                try:
                    static_plant = plant_service.static_plants.get(plant_name.lower())
                    if static_plant:
                        plant_information.append(static_plant)
                        print(f"📖 Using static data for {plant_name}")
                except Exception as static_e:
                    print(f"⚠️  Could not get static data for {plant_name}: {static_e}")
        
        # Log detailed results for debugging
        found_plants = [p.name for p in plant_information]
        missing_plants = [name for name in request.selected_plants if name not in found_plants]
        
        if missing_plants:
            print(f"⚠️  Missing plants from selection: {missing_plants}")
            print(f"✅ Found plants: {found_plants}")
        
        if not plant_information:
            raise ValueError(f"No plant information could be retrieved for any of the selected plants: {request.selected_plants}. Please try with common plants like 'tomato', 'lettuce', or 'carrots'.")
        
        if len(plant_information) < len(request.selected_plants):
            print(f"⚠️  Only {len(plant_information)}/{len(request.selected_plants)} plants found, proceeding with available plants")
        
        # Step 3: Generate planting schedules using AI (with fallback)
        try:
            planting_schedules = await self._generate_planting_schedules(
                plant_information, location_info, request
            )
        except Exception as e:
            print(f"⚠️  Error generating planting schedules, using defaults: {e}")
            planting_schedules = self._create_default_schedules(plant_information, location_info)
        
        # Step 4: Generate detailed growing instructions (with fallback)
        try:
            growing_instructions = await self._generate_growing_instructions(
                plant_information, location_info, request
            )
        except Exception as e:
            print(f"⚠️  Error generating growing instructions, using defaults: {e}")
            growing_instructions = [self._create_default_instructions(plant) for plant in plant_information]
        
        # Step 5: Generate layout recommendations (with fallback)
        try:
            layout_recommendations = await self._generate_layout_recommendations(
                plant_information, request
            )
        except Exception as e:
            print(f"⚠️  Error generating layout recommendations, using defaults: {e}")
            layout_recommendations = self._create_default_layout(plant_information, request)
        
        # Step 6: Generate general tips (with fallback)
        try:
            general_tips = await self._generate_general_tips(
                plant_information, location_info, request
            )
        except Exception as e:
            print(f"⚠️  Error generating general tips, using defaults: {e}")
            general_tips = self._create_default_tips(plant_information, location_info, request)
        
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
        
        # SAVE THE GARDEN PLAN TO DISK
        await self._save_garden_plan(garden_plan)
        
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
            
            if not response or not response.strip():
                print("⚠️  Empty response from LLM for planting schedules")
                return self._create_default_schedules(plants, location)
            
            # Use universal JSON extraction method
            schedules_data = self._extract_and_clean_json_universal(response)
            
            if not schedules_data:
                print("⚠️  Could not extract valid JSON from planting schedules response")
                return self._create_default_schedules(plants, location)
            
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
        
        prompt = f"""
Create garden layout recommendations for: {[p.name for p in plants]}
Garden size: {request.garden_size}

Respond with ONLY valid JSON in this exact format:
{{
    "garden_dimensions": "Recommended dimensions and area for {request.garden_size} garden",
    "plant_groupings": [
        {{
            "group_name": "Main Garden Area",
            "plants": {[p.name for p in plants]},
            "spacing_notes": "spacing recommendations for this group"
        }}
    ],
    "spacing_guide": {{
        {', '.join([f'"{p.name}": "{p.spacing_inches or 12} inches apart"' for p in plants])}
    }},
    "companion_planting_tips": [
        "Specific companion planting advice for these plants"
    ],
    "layout_tips": [
        "Place taller plants on north side to avoid shading shorter plants",
        "Group plants with similar water needs together"
    ]
}}

Focus on practical layout advice for a {request.garden_size} {request.experience_level}-level garden.
"""
        
        try:
            response = await llm_service.generate_plant_info(prompt)
            if response and response.strip():
                # Use universal JSON extraction method
                layout_data = self._extract_and_clean_json_universal(response)
                if layout_data:
                    # Convert array format to dict format if needed
                    if isinstance(layout_data, list):
                        # Convert list of plant groupings to expected dict format
                        converted_layout = {
                            "garden_dimensions": f"Recommended for {request.garden_size} garden",
                            "plant_groupings": layout_data,  # Use the LLM's groupings
                            "spacing_guide": {},
                            "companion_planting_tips": [],
                            "layout_tips": []
                        }
                        
                        # Extract tips and spacing from the array if they exist
                        for group in layout_data:
                            if isinstance(group, dict):
                                # Look for spacing information
                                if "spacing" in group:
                                    for plant in group.get("plants", []):
                                        converted_layout["spacing_guide"][plant] = group["spacing"]
                                
                                # Look for tips in reasoning
                                if "reasoning" in group:
                                    converted_layout["companion_planting_tips"].append(group["reasoning"])
                        
                        return converted_layout
                    else:
                        # Already in dict format
                        return layout_data
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
            if response and response.strip():
                # Use universal JSON extraction method
                tips_data = self._extract_and_clean_json_universal(response)
                if tips_data and isinstance(tips_data, list):
                    return tips_data
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
        """Create default schedules when LLM fails"""
        schedules = []
        for plant in plants:
            # Calculate reasonable default dates based on location
            schedule = PlantingSchedule(
                plant_name=plant.name,
                start_indoors_date=self._calculate_indoor_start_date(plant, location),
                direct_sow_date=self._calculate_direct_sow_date(plant, location),
                transplant_date=self._calculate_transplant_date(plant, location),
                # ... etc
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
        
        fixed = json_str
        
        # Remove JavaScript-style comments (// comment text)
        fixed = re.sub(r'\s*//.*?(?=\n|$)', '', fixed, flags=re.MULTILINE)
        
        # Remove C-style comments (/* comment */)
        fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
        
        # Fix single quotes to double quotes (but be careful about apostrophes)
        # This regex looks for single quotes that are likely JSON string delimiters
        fixed = re.sub(r"'([^']*)'", r'"\1"', fixed)
        
        # Fix trailing commas before closing brackets/braces
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix missing commas between array elements
        fixed = re.sub(r'"\s*\n\s*"', '",\n    "', fixed)
        
        # Fix missing quotes around keys (basic case)
        fixed = re.sub(r'(\w+):', r'"\1":', fixed)
        
        # Remove any control characters
        fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', fixed)
        
        return fixed
    
    def _extract_and_clean_json_universal(self, response: str) -> Optional[Any]:
        """
        Extract and clean JSON from LLM response - handles both objects {} and arrays []
        """
        if not response:
            return None
        
        import re
        
        # Remove common LLM prefixes/suffixes
        cleaned = response.strip()
        
        # Remove common prefixes (more comprehensive)
        prefixes_to_remove = [
            "Here's the JSON:",
            "Here is the JSON:",
            "Here are three gardening tips for tomatoes:",
            "Here are",
            "```json",
            "```",
            "JSON:",
            "Response:",
            "Here's the detailed information:",
            "Here are the instructions:",
            "Here's your",
            "Based on",
            "For your garden"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove markdown code blocks more aggressively
        cleaned = re.sub(r'^```json\s*\n?', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Smart JSON extraction with proper bracket/brace counting
        json_str = self._extract_complete_json(cleaned)
        
        if not json_str:
            print(f"⚠️  No valid JSON found in response")
            print(f"Response preview: {cleaned[:200]}...")
            return None
        
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
            except json.JSONDecodeError as e2:
                print(f"❌ Could not fix JSON. Error: {e2}")
                print(f"Original JSON preview: {json_str[:200]}...")
                print(f"Fixed JSON preview: {fixed_json[:200]}...")
                return None

    def _extract_complete_json(self, text: str) -> Optional[str]:
        """
        Extract complete JSON by properly counting brackets/braces
        """
        # Try to find array first
        array_start = text.find('[')
        if array_start != -1:
            # Count brackets to find the complete array
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(text[array_start:], array_start):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            # Found the end of the complete array
                            return text[array_start:i+1]
        
        # Try to find object
        object_start = text.find('{')
        if object_start != -1:
            # Count braces to find the complete object
            brace_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(text[object_start:], object_start):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found the end of the complete object
                            return text[object_start:i+1]
        
        return None

    async def _save_garden_plan(self, garden_plan: GardenPlan):
        """Save garden plan to disk for PDF generation"""
        try:
            import json
            from pathlib import Path
            
            # Ensure directory exists
            plans_dir = Path("generated_plans")
            plans_dir.mkdir(exist_ok=True)
            
            # Convert garden plan to dict for JSON serialization
            plan_dict = {
                "plan_id": garden_plan.plan_id,
                "created_date": garden_plan.created_date.isoformat(),
                "location": {
                    "zip_code": garden_plan.location.zip_code,
                    "city": garden_plan.location.city,
                    "state": garden_plan.location.state,
                    "usda_zone": garden_plan.location.usda_zone,
                    "last_frost_date": garden_plan.location.last_frost_date.isoformat() if garden_plan.location.last_frost_date else None,
                    "first_frost_date": garden_plan.location.first_frost_date.isoformat() if garden_plan.location.first_frost_date else None,
                    "growing_season_days": garden_plan.location.growing_season_days,
                    "climate_type": garden_plan.location.climate_type
                },
                "selected_plants": garden_plan.selected_plants,
                "plant_information": [
                    {
                        "name": plant.name,
                        "scientific_name": plant.scientific_name,
                        "plant_type": plant.plant_type,
                        "days_to_harvest": plant.days_to_harvest,
                        "spacing_inches": plant.spacing_inches,
                        "planting_depth_inches": plant.planting_depth_inches,
                        "sun_requirements": plant.sun_requirements,
                        "water_requirements": plant.water_requirements,
                        "soil_ph_range": plant.soil_ph_range,
                        "companion_plants": plant.companion_plants,
                        "avoid_planting_with": plant.avoid_planting_with
                    } for plant in garden_plan.plant_information
                ],
                "planting_schedules": [
                    {
                        "plant_name": schedule.plant_name,
                        "start_indoors_date": schedule.start_indoors_date.isoformat() if schedule.start_indoors_date else None,
                        "direct_sow_date": schedule.direct_sow_date.isoformat() if schedule.direct_sow_date else None,
                        "transplant_date": schedule.transplant_date.isoformat() if schedule.transplant_date else None,
                        "harvest_start_date": schedule.harvest_start_date.isoformat() if schedule.harvest_start_date else None,
                        "harvest_end_date": schedule.harvest_end_date.isoformat() if schedule.harvest_end_date else None,
                        "succession_planting_interval": schedule.succession_planting_interval
                    } for schedule in garden_plan.planting_schedules
                ],
                "growing_instructions": [
                    {
                        "plant_name": instr.plant_name,
                        "preparation_steps": instr.preparation_steps,
                        "planting_steps": instr.planting_steps,
                        "care_instructions": instr.care_instructions,
                        "pest_management": instr.pest_management,
                        "harvest_instructions": instr.harvest_instructions,
                        "storage_tips": instr.storage_tips
                    } for instr in garden_plan.growing_instructions
                ],
                "layout_recommendations": garden_plan.layout_recommendations,
                "general_tips": garden_plan.general_tips
            }
            
            # Save to file
            filename = f"garden_plan_{garden_plan.plan_id}.json"
            filepath = plans_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(plan_dict, f, indent=2)
            
            print(f"💾 Garden plan saved to {filepath}")
            
        except Exception as e:
            print(f"⚠️  Error saving garden plan: {e}")
            # Don't fail the whole process if saving fails
    
    def _create_default_layout(self, plants: List[PlantInfo], request: PlanRequest) -> Dict[str, Any]:
        """Create default layout recommendations when LLM generation fails"""
        return {
            "garden_dimensions": f"Recommended for {request.garden_size} garden",
            "plant_groupings": [{"group_name": "Mixed Garden", "plants": [p.name for p in plants]}],
            "spacing_guide": {p.name: f"{p.spacing_inches} inches apart" for p in plants if p.spacing_inches},
            "companion_planting_tips": ["Consider companion planting benefits for better growth"],
            "layout_tips": ["Place taller plants where they won't shade shorter ones", "Group plants with similar water needs together"]
        }
    
    def _create_default_tips(self, plants: List[PlantInfo], location: LocationInfo, request: PlanRequest) -> List[str]:
        """Create default general tips when LLM generation fails"""
        tips = [
            f"Start with {len(plants)} plants for a manageable {request.garden_size} garden",
            f"Your USDA zone {location.usda_zone} has a {location.growing_season_days}-day growing season",
            "Water consistently and mulch around plants to retain moisture",
            "Test your soil pH and amend as needed for optimal plant growth"
        ]
        
        if request.experience_level == "beginner":
            tips.extend([
                "Start small and expand your garden as you gain experience",
                "Keep a garden journal to track what works best in your area"
            ])
        
        return tips

# Global instance
garden_plan_service = GardenPlanService()
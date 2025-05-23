"""
Test script for PDF generation functionality

This script tests the PDF service with sample garden plan data
to ensure all components work together correctly.
"""

import asyncio
import sys
import os
from datetime import datetime, date

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_service import PDFService
from models.garden_plan import GardenPlan, PlantInfo, LocationInfo, GrowingInstructions, PlantingSchedule

async def test_pdf_generation():
    """Test PDF generation with sample data"""
    
    print("🌱 Testing PDF Generation...")
    print("=" * 50)
    
    # Initialize PDF service
    try:
        pdf_service = PDFService()
        print("✅ PDF Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PDF Service: {e}")
        return
    
    # Create sample location info
    location_info = LocationInfo(
        zip_code="K1A 0A6",
        city="Ottawa", 
        state="ON",
        usda_zone="5a",
        last_frost_date=date(2024, 5, 15),
        first_frost_date=date(2024, 10, 1),
        growing_season_days=140,
        climate_type="Continental"
    )
    
    # Create sample plant information
    plant_info_list = [
        PlantInfo(
            name="Tomato",
            scientific_name="Solanum lycopersicum",
            plant_type="vegetable",
            days_to_harvest=75,
            spacing_inches=24,
            planting_depth_inches=0.25,
            sun_requirements="full sun",
            water_requirements="regular",
            soil_ph_range="6.0-6.8"
        ),
        PlantInfo(
            name="Lettuce",
            scientific_name="Lactuca sativa", 
            plant_type="vegetable",
            days_to_harvest=45,
            spacing_inches=6,
            planting_depth_inches=0.25,
            sun_requirements="partial shade",
            water_requirements="consistent moisture",
            soil_ph_range="6.0-7.0"
        ),
        PlantInfo(
            name="Carrots",
            scientific_name="Daucus carota",
            plant_type="vegetable", 
            days_to_harvest=70,
            spacing_inches=2,
            planting_depth_inches=0.25,
            sun_requirements="full sun",
            water_requirements="regular",
            soil_ph_range="6.0-6.8"
        )
    ]
    
    # Create sample growing instructions
    growing_instructions_list = [
        GrowingInstructions(
            plant_name="Tomato",
            preparation_steps=[
                "Prepare well-draining soil with compost",
                "Ensure pH is between 6.0-6.8", 
                "Choose a sunny location"
            ],
            planting_steps=[
                "Start seeds indoors 6-8 weeks before last frost",
                "Transplant when soil is warm and nights stay above 50°F",
                "Plant deep, burying 2/3 of the stem"
            ],
            care_instructions=[
                "Water deeply but infrequently",
                "Provide support with stakes or cages",
                "Mulch around plants to retain moisture",
                "Remove suckers for better fruit development"
            ],
            pest_management=[
                "Watch for hornworms and remove by hand",
                "Prevent blight with proper air circulation",
                "Use row covers early in season for protection"
            ],
            harvest_instructions=[
                "Harvest when fruits are fully colored but still firm",
                "Pick regularly to encourage continued production",
                "Harvest green tomatoes before first frost"
            ],
            storage_tips=[
                "Store ripe tomatoes at room temperature",
                "Refrigerate only fully ripe tomatoes",
                "Green tomatoes can ripen indoors"
            ]
        ),
        GrowingInstructions(
            plant_name="Lettuce",
            preparation_steps=[
                "Prepare loose, well-draining soil rich in organic matter",
                "Ensure pH is between 6.0-7.0",
                "Choose location with morning sun and afternoon shade"
            ],
            planting_steps=[
                "Direct sow seeds 1/4 inch deep",
                "Space rows 12 inches apart", 
                "Can succession plant every 2 weeks"
            ],
            care_instructions=[
                "Keep soil consistently moist",
                "Provide partial shade in hot weather",
                "Thin seedlings to proper spacing",
                "Use row covers for protection"
            ],
            pest_management=[
                "Watch for aphids and spray with water",
                "Use beer traps for slugs",
                "Row covers prevent most pest issues"
            ],
            harvest_instructions=[
                "Harvest outer leaves when 4-6 inches long",
                "Cut entire head at base when mature",
                "Harvest in cool morning hours"
            ],
            storage_tips=[
                "Wash and dry thoroughly before storing",
                "Store in refrigerator in plastic bag",
                "Use within 5-7 days for best quality"
            ]
        ),
        GrowingInstructions(
            plant_name="Carrots",
            preparation_steps=[
                "Prepare deep, loose, sandy soil free of stones",
                "Ensure pH is between 6.0-6.8",
                "Work soil to at least 12 inches deep"
            ],
            planting_steps=[
                "Direct sow seeds 1/4 inch deep",
                "Plant in rows 12 inches apart",
                "Thin to 2 inches apart when 2 inches tall"
            ],
            care_instructions=[
                "Keep soil consistently moist until germination",
                "Thin carefully to avoid disturbing remaining plants",
                "Mulch to retain moisture and suppress weeds"
            ],
            pest_management=[
                "Use row covers to prevent carrot fly",
                "Rotate crops to prevent soil-borne diseases",
                "Remove any cracked or damaged carrots promptly"
            ],
            harvest_instructions=[
                "Harvest when tops are 1/2 inch diameter",
                "Can leave in ground until needed",
                "Harvest before ground freezes"
            ],
            storage_tips=[
                "Remove tops before storing",
                "Store in cool, humid conditions",
                "Can store in ground with mulch protection"
            ]
        )
    ]
    
    # Create sample planting schedules
    planting_schedules = [
        PlantingSchedule(
            plant_name="Tomato",
            start_indoors_date=date(2024, 3, 15),
            transplant_date=date(2024, 5, 20),
            harvest_start_date=date(2024, 7, 15),
            harvest_end_date=date(2024, 9, 30)
        ),
        PlantingSchedule(
            plant_name="Lettuce",
            direct_sow_date=date(2024, 4, 1),
            harvest_start_date=date(2024, 5, 15),
            harvest_end_date=date(2024, 6, 30),
            succession_planting_interval=14
        ),
        PlantingSchedule(
            plant_name="Carrots", 
            direct_sow_date=date(2024, 4, 15),
            harvest_start_date=date(2024, 6, 30),
            harvest_end_date=date(2024, 8, 15)
        )
    ]
    
    # Create the complete garden plan
    sample_garden_plan = GardenPlan(
        plan_id="test_plan_001",
        created_date=datetime.now(),
        location=location_info,
        selected_plants=["Tomato", "Lettuce", "Carrots"],
        plant_information=plant_info_list,
        planting_schedules=planting_schedules,
        growing_instructions=growing_instructions_list,
        general_tips=[
            "Start a garden journal to track your progress",
            "Water early morning to reduce evaporation",
            "Companion plant to maximize garden space",
            "Compost kitchen scraps to improve soil"
        ]
    )
    
    print(f"📋 Created sample garden plan:")
    print(f"   Location: {sample_garden_plan.location}")
    print(f"   Plants: {len(sample_garden_plan.plant_information)}")
    print(f"   Generated: {sample_garden_plan.created_date}")
    print()
    
    # Test PDF generation
    try:
        print("🔄 Generating PDF...")
        
        result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=sample_garden_plan,
            custom_filename="test_garden_plan",
            include_images=True,
            include_calendar=True,
            include_layout=True
        )
        
        if result["success"]:
            print("✅ PDF Generated Successfully!")
            print(f"   📁 File: {result['filename']}")
            print(f"   📍 Path: {result['filepath']}")
            print(f"   📏 Size: {result['file_size_mb']} MB")
            print(f"   🌱 Plants: {result['plant_count']}")
            print(f"   📅 Generated: {result['generated_at']}")
        else:
            print("❌ PDF Generation Failed:")
            print(f"   Error: {result['error']}")
            print(f"   Type: {result.get('error_type', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Unexpected error during PDF generation: {e}")
        import traceback
        traceback.print_exc()
    
    # Test PDF listing
    try:
        print("\n📚 Testing PDF listing...")
        pdf_list = await pdf_service.list_generated_pdfs()
        
        if pdf_list:
            print(f"✅ Found {len(pdf_list)} PDF(s):")
            for pdf in pdf_list[:3]:  # Show first 3
                print(f"   📄 {pdf['filename']} ({pdf['size_mb']} MB)")
        else:
            print("📝 No PDFs found in generated_plans directory")
            
    except Exception as e:
        print(f"❌ Error listing PDFs: {e}")

if __name__ == "__main__":
    asyncio.run(test_pdf_generation()) 
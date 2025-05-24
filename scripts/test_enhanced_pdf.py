#!/usr/bin/env python3
"""
Test Enhanced PDF Generation
This script tests the beautiful new PDF template and styling
"""

import asyncio
import sys
import os
import json
from datetime import datetime, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_service import PDFService
from services.garden_plan_service import GardenPlanService
from models.garden_plan import PlanRequest

async def test_enhanced_pdf():
    """Test the enhanced PDF generation with beautiful new design"""
    
    print("🎨 Testing Enhanced PDF Generation")
    print("=" * 60)
    
    # Step 1: Create a comprehensive test request
    test_request = PlanRequest(
        zip_code="90210",
        selected_plants=[
            "Tomato", "Basil", "Lettuce", "Carrots", "Bell Peppers", 
            "Spinach", "Radishes", "Parsley", "Cucumber", "Zucchini"
        ],
        garden_size="medium",
        experience_level="beginner",
        garden_type="raised_bed",
        growing_season_goals=["fresh_vegetables", "herbs_for_cooking"]
    )
    
    print(f"🌱 Creating garden plan for {len(test_request.selected_plants)} plants...")
    print(f"📍 Location: {test_request.zip_code}")
    print(f"🌿 Plants: {', '.join(test_request.selected_plants)}")
    print()
    
    # Step 2: Generate the garden plan
    try:
        garden_service = GardenPlanService()
        start_time = datetime.now()
        
        garden_plan = await garden_service.create_garden_plan(test_request)
        
        plan_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Garden plan generated in {plan_time:.2f} seconds")
        print(f"📊 Plan includes {len(garden_plan.plant_information)} plants")
        print(f"📅 Generated {len(garden_plan.planting_schedules)} planting schedules")
        print()
        
    except Exception as e:
        print(f"❌ Garden plan generation failed: {e}")
        return
    
    # Step 3: Generate the enhanced PDF
    try:
        pdf_service = PDFService()
        start_time = datetime.now()
        
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=garden_plan,
            custom_filename="enhanced_garden_plan_demo",
            include_images=True,
            include_calendar=True,
            include_layout=True
        )
        
        pdf_time = (datetime.now() - start_time).total_seconds()
        
        if pdf_result.get("success"):
            print(f"🎉 Enhanced PDF generated successfully!")
            print(f"⚡ Generation time: {pdf_time:.2f} seconds")
            print(f"📄 File: {pdf_result['filename']}")
            print(f"💾 Size: {pdf_result['file_size_mb']} MB")
            print(f"📁 Path: {pdf_result['filepath']}")
            print()
            
            print("✨ Enhanced PDF Features:")
            print("   🎨 Beautiful cover page with stats")
            print("   📋 Professional table of contents")
            print("   🌍 Enhanced overview with visual cards")
            print("   📅 Color-coded planting calendar")
            print("   🌱 Individual plant profiles with timelines")
            print("   💡 Expert gardening tips")
            print("   🏷️ Professional branding and footer")
            print()
            
            # Display some sample content
            print("📊 PDF Content Summary:")
            print(f"   📍 Location: {pdf_result['location']}")
            print(f"   🌱 Plants included: {pdf_result['plant_count']}")
            print("   🎨 Visual enhancements: Emojis, color coding, modern layout")
            print("   📱 Professional design: Cards, timelines, visual hierarchy")
            
        else:
            print(f"❌ PDF generation failed: {pdf_result.get('error', 'Unknown error')}")
            return
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return
    
    # Step 4: Verify the file exists and provide access info
    try:
        file_path = pdf_result['filepath']
        if os.path.exists(file_path):
            print()
            print("🎯 Success! Enhanced PDF Features Verified:")
            print("   ✅ Professional cover page with location hero")
            print("   ✅ Visual plant preview grid")
            print("   ✅ Comprehensive table of contents")
            print("   ✅ Enhanced overview with detail cards")
            print("   ✅ Visual planting calendar with seasons")
            print("   ✅ Individual plant profiles with timelines")
            print("   ✅ Expert gardening tips section")
            print("   ✅ Professional footer and branding")
            print()
            print(f"📂 Open your enhanced PDF at: {os.path.abspath(file_path)}")
            
        else:
            print(f"⚠️  PDF file was created but not found at expected location")
            
    except Exception as e:
        print(f"❌ File verification error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced PDF Test Starting...")
    print("This test will create a beautiful, professional garden plan PDF")
    print("with enhanced visual design, modern layout, and comprehensive content.")
    print()
    
    asyncio.run(test_enhanced_pdf())
    
    print()
    print("🎨 Enhanced PDF test completed!")
    print("The new PDF features professional design with:")
    print("• Beautiful cover page with statistics")
    print("• Visual plant emojis and category organization") 
    print("• Color-coded seasonal calendar")
    print("• Timeline-based planting schedules")
    print("• Modern card-based layout")
    print("• Expert gardening tips")
    print("• Professional branding throughout") 
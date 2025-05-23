"""
Test PDF router imports and initialization
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pdf_router_imports():
    """Test all imports used by PDF router"""
    
    print("🔍 Testing PDF Router Imports...")
    print("=" * 50)
    
    try:
        print("1. Testing core imports...")
        from fastapi import APIRouter, HTTPException
        from typing import List, Optional, Dict, Any
        print("   ✅ FastAPI imports successful")
        
        print("2. Testing service imports...")
        from services.pdf_service import PDFService
        from services.garden_plan_service import garden_plan_service
        print("   ✅ Service imports successful")
        
        print("3. Testing model imports...")
        from models.garden_plan import GardenPlan, PlanRequest
        print("   ✅ Model imports successful")
        
        print("4. Testing service initialization...")
        pdf_service = PDFService()
        print(f"   ✅ PDF Service: {type(pdf_service)}")
        print(f"   ✅ Garden Plan Service: {type(garden_plan_service)}")
        
        print("5. Testing garden plan service method...")
        create_method = garden_plan_service.create_garden_plan
        print(f"   ✅ create_garden_plan method: {create_method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_router_imports()
    if success:
        print("\n🎉 All imports working correctly!")
    else:
        print("\n💥 Import issues detected") 
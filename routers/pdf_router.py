"""
PDF Router for Garden Plan PDF Generation

Provides endpoints for:
- Generating PDFs from garden plans
- Listing generated PDFs
- Downloading PDF files
- Deleting PDFs
- PDF management
"""

from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path
from pydantic import BaseModel

from services.pdf_service import PDFService
from services.garden_plan_service import garden_plan_service
from models.garden_plan import GardenPlan, LocationInfo, PlantInfo, GrowingInstructions, PlantingSchedule, PlanRequest

# Initialize router
router = APIRouter(prefix="/pdf", tags=["PDF Generation"])

# Initialize services
pdf_service = PDFService()

class PDFGenerationRequest(BaseModel):
    """Request model for PDF generation"""
    zip_code: str
    plant_names: List[str]  # We'll map this to selected_plants
    custom_filename: Optional[str] = None
    include_images: bool = True
    include_calendar: bool = True
    include_layout: bool = True
    # Garden plan specific fields
    garden_size: Optional[str] = "medium"  # small, medium, large
    experience_level: Optional[str] = "beginner"  # beginner, intermediate, advanced

class PDFFromPlanRequest(BaseModel):
    """Request model for PDF generation from existing plan"""
    garden_plan: GardenPlan
    custom_filename: Optional[str] = None
    include_images: bool = True
    include_calendar: bool = True
    include_layout: bool = True

@router.post("/generate")
async def generate_garden_plan_pdf(request: PDFGenerationRequest) -> Dict[str, Any]:
    """
    Generate a comprehensive garden plan PDF
    
    **Request Body:**
    ```json
    {
        "zip_code": "12345",
        "plant_names": ["Tomato", "Lettuce", "Carrots"],
        "custom_filename": "my_garden",
        "include_images": true,
        "include_calendar": true,
        "include_layout": true,
        "garden_size": "medium",
        "experience_level": "beginner"
    }
    ```
    
    **Returns:**
    - PDF generation result with file information
    """
    try:
        # Validate inputs
        if not request.zip_code or not request.zip_code.strip():
            raise HTTPException(status_code=400, detail="zip_code is required")
        
        if not request.plant_names or len(request.plant_names) == 0:
            raise HTTPException(status_code=400, detail="At least one plant must be selected")
        
        if len(request.plant_names) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 plants allowed per garden plan")
        
        print(f"🌱 Generating garden plan PDF for {request.zip_code} with {len(request.plant_names)} plants...")
        
        # Create PlanRequest object for the garden plan service
        plan_request = PlanRequest(
            zip_code=request.zip_code,
            selected_plants=request.plant_names,  # Map plant_names to selected_plants
            garden_size=request.garden_size,
            experience_level=request.experience_level
        )
        
        # Generate garden plan using the garden plan service
        garden_plan_result = await garden_plan_service.create_garden_plan(plan_request)
        
        # The result is the garden plan object directly, not a dict with success/error
        garden_plan = garden_plan_result
        
        # Generate PDF
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=garden_plan,
            custom_filename=request.custom_filename,
            include_images=request.include_images,
            include_calendar=request.include_calendar,
            include_layout=request.include_layout
        )
        
        if pdf_result["success"]:
            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_info": pdf_result,
                "download_url": f"/pdf/download/{pdf_result['filename']}",
                "view_url": f"/pdf/view/{pdf_result['filename']}",
                "garden_plan_summary": {
                    "location": garden_plan.location.zip_code,
                    "plant_count": len(garden_plan.plant_information),
                    "plants": [plant.name for plant in garden_plan.plant_information]
                }
            }
        else:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {pdf_result['error']}")
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/generate-from-plan")
async def generate_pdf_from_existing_plan(request: PDFFromPlanRequest) -> Dict[str, Any]:
    """
    Generate PDF from an existing garden plan object
    
    **Request Body:**
    ```json
    {
        "garden_plan": { /* complete garden plan object */ },
        "custom_filename": "my_garden",
        "include_images": true,
        "include_calendar": true,
        "include_layout": true
    }
    ```
    
    **Returns:**
    - PDF generation result with file information
    """
    try:
        print(f"📄 Generating PDF from existing garden plan...")
        
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=request.garden_plan,
            custom_filename=request.custom_filename,
            include_images=request.include_images,
            include_calendar=request.include_calendar,
            include_layout=request.include_layout
        )
        
        if pdf_result["success"]:
            return {
                "success": True,
                "message": "PDF generated successfully from existing plan",
                "pdf_info": pdf_result,
                "download_url": f"/pdf/download/{pdf_result['filename']}",
                "view_url": f"/pdf/view/{pdf_result['filename']}"
            }
        else:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {pdf_result['error']}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/list")
async def list_generated_pdfs() -> Dict[str, Any]:
    """
    List all generated PDF files
    
    **Returns:**
    - List of PDF files with metadata
    """
    try:
        pdf_list = await pdf_service.list_generated_pdfs()
        
        return {
            "success": True,
            "pdf_count": len(pdf_list),
            "pdfs": pdf_list,
            "total_size_mb": round(sum(pdf["size_mb"] for pdf in pdf_list), 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")

@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download a generated PDF file
    
    **Parameters:**
    - **filename**: Name of the PDF file to download
    
    **Returns:**
    - PDF file for download
    """
    try:
        # Validate filename
        if not filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
        
        # Construct file path
        file_path = Path(f"generated_plans/{filename}")
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF file '{filename}' not found")
        
        # Return file for download
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")

@router.get("/view/{filename}")
async def view_pdf(filename: str):
    """
    View a PDF file in the browser (inline)
    
    **Parameters:**
    - **filename**: Name of the PDF file to view
    
    **Returns:**
    - PDF file for inline viewing
    """
    try:
        # Validate filename
        if not filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
        
        # Construct file path
        file_path = Path(f"generated_plans/{filename}")
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF file '{filename}' not found")
        
        # Return file for inline viewing
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing PDF: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_pdf(filename: str) -> Dict[str, Any]:
    """
    Delete a generated PDF file
    
    **Parameters:**
    - **filename**: Name of the PDF file to delete
    
    **Returns:**
    - Deletion result
    """
    try:
        result = await pdf_service.delete_pdf(filename)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "deleted_file": filename
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting PDF: {str(e)}")

@router.get("/stats")
async def get_pdf_stats() -> Dict[str, Any]:
    """
    Get PDF generation statistics
    
    **Returns:**
    - Statistics about generated PDFs
    """
    try:
        pdf_list = await pdf_service.list_generated_pdfs()
        
        # Calculate statistics
        total_files = len(pdf_list)
        total_size_mb = sum(pdf["size_mb"] for pdf in pdf_list)
        
        # Find largest and smallest files
        largest_file = max(pdf_list, key=lambda x: x["size_mb"]) if pdf_list else None
        smallest_file = min(pdf_list, key=lambda x: x["size_mb"]) if pdf_list else None
        
        # Recent files (last 24 hours)
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_files = [
            pdf for pdf in pdf_list 
            if datetime.fromisoformat(pdf["created_at"].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff_time
        ]
        
        return {
            "success": True,
            "statistics": {
                "total_files": total_files,
                "total_size_mb": round(total_size_mb, 2),
                "average_size_mb": round(total_size_mb / total_files, 2) if total_files > 0 else 0,
                "largest_file": {
                    "filename": largest_file["filename"],
                    "size_mb": largest_file["size_mb"]
                } if largest_file else None,
                "smallest_file": {
                    "filename": smallest_file["filename"], 
                    "size_mb": smallest_file["size_mb"]
                } if smallest_file else None,
                "recent_files_24h": len(recent_files),
                "oldest_file": min(pdf_list, key=lambda x: x["created_at"])["created_at"] if pdf_list else None,
                "newest_file": max(pdf_list, key=lambda x: x["created_at"])["created_at"] if pdf_list else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PDF statistics: {str(e)}")

# Health check endpoint
@router.get("/health")
async def pdf_service_health() -> Dict[str, Any]:
    """
    Check PDF service health
    
    **Returns:**
    - Service health status
    """
    try:
        # Test basic PDF generation capability
        test_html = "<html><body><h1>Health Check</h1></body></html>"
        
        # Just test that we can create a PDF service instance
        test_service = PDFService()
        
        return {
            "success": True,
            "status": "healthy",
            "message": "PDF service is operational",
            "timestamp": datetime.now().isoformat(),
            "capabilities": {
                "pdf_generation": True,
                "file_management": True,
                "statistics": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy", 
            "message": f"PDF service error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/garden-plan/{plan_id}")
async def download_garden_plan_pdf(plan_id: str):
    """
    Generate and download PDF for an existing garden plan
    """
    try:
        print(f"📄 Generating PDF for garden plan: {plan_id}")
        
        # Check if the garden plan exists
        import json
        from datetime import datetime, date
        plan_file = f"generated_plans/garden_plan_{plan_id}.json"
        
        if not os.path.exists(plan_file):
            raise HTTPException(status_code=404, detail=f"Garden plan {plan_id} not found")
        
        # Load and convert the garden plan
        with open(plan_file, 'r') as f:
            plan_data = json.load(f)
        
        # Convert date strings back to date objects
        def parse_date_string(date_str):
            if date_str and isinstance(date_str, str):
                try:
                    return datetime.fromisoformat(date_str).date()
                except:
                    return None
            return date_str
        
        # Fix dates in planting_schedules
        if 'planting_schedules' in plan_data:
            for schedule in plan_data['planting_schedules']:
                schedule['start_indoors_date'] = parse_date_string(schedule.get('start_indoors_date'))
                schedule['direct_sow_date'] = parse_date_string(schedule.get('direct_sow_date'))
                schedule['transplant_date'] = parse_date_string(schedule.get('transplant_date'))
                schedule['harvest_start_date'] = parse_date_string(schedule.get('harvest_start_date'))
                schedule['harvest_end_date'] = parse_date_string(schedule.get('harvest_end_date'))
        
        # Fix dates in location
        if 'location' in plan_data:
            plan_data['location']['last_frost_date'] = parse_date_string(plan_data['location'].get('last_frost_date'))
            plan_data['location']['first_frost_date'] = parse_date_string(plan_data['location'].get('first_frost_date'))
        
        # Fix created_date
        if 'created_date' in plan_data:
            plan_data['created_date'] = datetime.fromisoformat(plan_data['created_date'])
        
        # Convert to GardenPlan object
        garden_plan = GardenPlan(**plan_data)
        
        # Generate PDF
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=garden_plan,
            custom_filename=f"garden_plan_{plan_id}",
            include_images=True,
            include_calendar=True,
            include_layout=True
        )
        
        if pdf_result["success"]:
            pdf_path = pdf_result["filepath"]
            return FileResponse(
                path=pdf_path,
                filename=pdf_result["filename"],
                media_type="application/pdf"
            )
        else:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {pdf_result['error']}")
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Garden plan {plan_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating PDF for plan {plan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}") 
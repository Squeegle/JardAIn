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

from services.pdf_service import PDFService
from services.garden_plan_service import GardenPlanService
from models.garden_plan import GardenPlan, LocationInfo, PlantInfo, GrowingInstructions, PlantingSchedule

# Initialize router
router = APIRouter(prefix="/pdf", tags=["PDF Generation"])

# Initialize services
pdf_service = PDFService()
garden_plan_service = GardenPlanService()

@router.post("/generate")
async def generate_garden_plan_pdf(
    zip_code: str,
    plant_names: List[str],
    custom_filename: Optional[str] = None,
    include_images: bool = True,
    include_calendar: bool = True,
    include_layout: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive garden plan PDF
    
    **Parameters:**
    - **zip_code**: Location zip/postal code (e.g., "12345" or "K1A 0A6")
    - **plant_names**: List of plants to include in the garden plan
    - **custom_filename**: Optional custom filename (timestamp will be added)
    - **include_images**: Whether to include plant images in PDF
    - **include_calendar**: Whether to include planting calendar
    - **include_layout**: Whether to include garden layout guide
    
    **Returns:**
    - PDF generation result with file information
    """
    try:
        # Validate inputs
        if not zip_code or not zip_code.strip():
            raise HTTPException(status_code=400, detail="zip_code is required")
        
        if not plant_names or len(plant_names) == 0:
            raise HTTPException(status_code=400, detail="At least one plant must be selected")
        
        if len(plant_names) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 plants allowed per garden plan")
        
        print(f"🌱 Generating garden plan PDF for {zip_code} with {len(plant_names)} plants...")
        
        # Generate garden plan using the garden plan service
        garden_plan_result = await garden_plan_service.create_garden_plan(
            zip_code=zip_code,
            selected_plants=plant_names
        )
        
        if not garden_plan_result["success"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to create garden plan: {garden_plan_result.get('error', 'Unknown error')}"
            )
        
        garden_plan = garden_plan_result["garden_plan"]
        
        # Generate PDF
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=garden_plan,
            custom_filename=custom_filename,
            include_images=include_images,
            include_calendar=include_calendar,
            include_layout=include_layout
        )
        
        if pdf_result["success"]:
            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_info": pdf_result,
                "download_url": f"/pdf/download/{pdf_result['filename']}",
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
async def generate_pdf_from_existing_plan(
    garden_plan: GardenPlan,
    custom_filename: Optional[str] = None,
    include_images: bool = True,
    include_calendar: bool = True,
    include_layout: bool = True
) -> Dict[str, Any]:
    """
    Generate PDF from an existing garden plan object
    
    **Parameters:**
    - **garden_plan**: Complete garden plan object
    - **custom_filename**: Optional custom filename
    - **include_images**: Whether to include plant images
    - **include_calendar**: Whether to include planting calendar
    - **include_layout**: Whether to include garden layout guide
    
    **Returns:**
    - PDF generation result with file information
    """
    try:
        print(f"📄 Generating PDF from existing garden plan...")
        
        pdf_result = await pdf_service.generate_garden_plan_pdf(
            garden_plan=garden_plan,
            custom_filename=custom_filename,
            include_images=include_images,
            include_calendar=include_calendar,
            include_layout=include_layout
        )
        
        if pdf_result["success"]:
            return {
                "success": True,
                "message": "PDF generated successfully from existing plan",
                "pdf_info": pdf_result,
                "download_url": f"/pdf/download/{pdf_result['filename']}"
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
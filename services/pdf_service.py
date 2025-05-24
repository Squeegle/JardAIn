"""
PDF Generation Service for Garden Plans

This service creates beautiful, professional PDFs with:
- Cover pages with location info
- Table of contents
- Individual plant sections with images
- Planting calendar and timeline
- Garden layout recommendations
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import weasyprint
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.garden_plan import GardenPlan, PlantInfo, LocationInfo, GrowingInstructions
from config import settings

class PDFService:
    """
    Comprehensive PDF generation service for garden plans
    
    Features:
    - Professional layout with cover page
    - Table of contents
    - Individual plant sections
    - Planting calendar
    - Garden spacing diagrams
    - Color styling with green gardening theme
    """
    
    def __init__(self):
        self.settings = settings
        
        # Setup Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader('templates/pdf'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories for PDF generation"""
        directories = [
            'generated_plans',
            'templates/pdf',
            'static/css',
            'static/images/plants',
            'static/icons'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def generate_garden_plan_pdf(
        self,
        garden_plan: GardenPlan,
        custom_filename: Optional[str] = None,
        include_images: bool = True,
        include_calendar: bool = True,
        include_layout: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive garden plan PDF
        
        Args:
            garden_plan: The garden plan data
            custom_filename: Optional custom filename
            include_images: Whether to include plant images
            include_calendar: Whether to include planting calendar
            include_layout: Whether to include garden layout diagrams
            
        Returns:
            Dict with PDF info (filepath, filename, size, etc.)
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            location_clean = f"{garden_plan.location.city}_{garden_plan.location.zip_code}".replace(" ", "_").replace(",", "")
            
            if custom_filename:
                filename = f"{custom_filename}_{timestamp}.pdf"
            else:
                filename = f"garden_plan_{location_clean}_{timestamp}.pdf"
            
            filepath = f"generated_plans/{filename}"
            
            # Prepare template data
            template_data = await self._prepare_template_data(
                garden_plan, include_images, include_calendar, include_layout
            )
            
            # Generate HTML from template
            html_content = await self._generate_html(template_data)
            
            # Generate PDF from HTML
            pdf_path = await self._generate_pdf_from_html(html_content, filepath)
            
            # Get file info
            file_stats = os.stat(pdf_path)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": pdf_path,
                "file_size_bytes": file_stats.st_size,
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "generated_at": datetime.now().isoformat(),
                "plant_count": len(garden_plan.plant_information),
                "location": f"{garden_plan.location.city}, {garden_plan.location.state} {garden_plan.location.zip_code}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _prepare_template_data(
        self,
        garden_plan: GardenPlan,
        include_images: bool,
        include_calendar: bool,
        include_layout: bool
    ) -> Dict[str, Any]:
        """Prepare all data needed for PDF template"""
        
        # For now, use basic location info from the garden plan
        location_info = {
            "zip_code": garden_plan.location.zip_code,
            "city": garden_plan.location.city,
            "state": garden_plan.location.state,
            "climate_zone": garden_plan.location.usda_zone,
            "frost_dates": {
                "last_spring_frost": garden_plan.location.last_frost_date.strftime("%B %d") if garden_plan.location.last_frost_date else "N/A",
                "first_fall_frost": garden_plan.location.first_frost_date.strftime("%B %d") if garden_plan.location.first_frost_date else "N/A"
            }
        }
        
        # Enhance plant data with additional info and visual elements
        enhanced_plants = []
        for plant_info in garden_plan.plant_information:
            plant_data = plant_info.dict()
            
            # Add visual emoji based on plant type
            plant_emoji_map = {
                'fruit': '🍅',
                'leafy_green': '🥬',
                'root_vegetable': '🥕',
                'herb': '🌿',
                'legume': '🌱',
                'vine': '🥒',
                'bulb': '🧅',
                'cruciferous': '🥦',
                'grain': '🌾',
                'flower': '🌻'
            }
            
            plant_data['emoji'] = plant_emoji_map.get(plant_info.plant_type.lower(), '🌱')
            
            # Add enhanced database info from the PlantInfo model itself
            plant_data['database_info'] = {
                'name': plant_info.name,
                'category': plant_info.plant_type.replace('_', ' ').title(),
                'sun_requirement': plant_info.sun_requirements or 'Full sun',
                'water_needs': plant_info.water_requirements or 'Regular watering',
                'days_to_maturity': f"{plant_info.days_to_harvest} days" if plant_info.days_to_harvest else 'See instructions',
                'spacing': f"{plant_info.spacing_inches} inches" if plant_info.spacing_inches else "See instructions",
                'planting_depth': f"{plant_info.planting_depth_inches} inches" if plant_info.planting_depth_inches else "See instructions"
            }
            plant_data['has_image'] = include_images
            plant_data['image_path'] = f"static/images/plants/{plant_info.name.lower().replace(' ', '_')}.jpg"
            
            # Add growing instructions if available
            growing_instructions = next(
                (gi for gi in garden_plan.growing_instructions if gi.plant_name == plant_info.name),
                None
            )
            if growing_instructions:
                plant_data['growing_instructions'] = {
                    'soil_preparation': ' '.join(growing_instructions.preparation_steps),
                    'planting_instructions': ' '.join(growing_instructions.planting_steps),
                    'care_instructions': ' '.join(growing_instructions.care_instructions),
                    'harvest_instructions': ' '.join(growing_instructions.harvest_instructions),
                    'common_problems': ' '.join(growing_instructions.pest_management)
                }
            
            # Add planting schedule if available
            schedule = next(
                (ps for ps in garden_plan.planting_schedules if ps.plant_name == plant_info.name),
                None
            )
            if schedule:
                plant_data['planting_schedule'] = {
                    'start_indoors': schedule.start_indoors_date.strftime("%B %d") if schedule.start_indoors_date else 'N/A',
                    'direct_sow': schedule.direct_sow_date.strftime("%B %d") if schedule.direct_sow_date else 'N/A',
                    'transplant': schedule.transplant_date.strftime("%B %d") if schedule.transplant_date else 'N/A',
                    'harvest': f"{schedule.harvest_start_date.strftime('%B %d')} to {schedule.harvest_end_date.strftime('%B %d')}" if schedule.harvest_start_date and schedule.harvest_end_date else 'See instructions'
                }
            
            enhanced_plants.append(plant_data)
        
        # Generate planting calendar if requested
        calendar_data = None
        if include_calendar:
            # Pass the garden plan's planting schedules to the calendar generator
            calendar_data = self._generate_planting_calendar_from_garden_plan(garden_plan, location_info)
        
        # Generate layout recommendations if requested
        layout_data = None
        if include_layout:
            layout_data = self._generate_layout_recommendations(enhanced_plants)
        
        # Add expert gardening tips for the tips page
        general_tips = [
            "💧 Water in the early morning to reduce evaporation and prevent disease",
            "🌱 Start with healthy soil - add compost regularly to improve structure and nutrients",
            "🐛 Encourage beneficial insects by planting flowers among your vegetables",
            "📏 Give plants proper spacing to ensure good air circulation and prevent disease",
            "🌱 Succession plant lettuce and radishes every 2-3 weeks for continuous harvest",
            "🔄 Rotate crops annually to prevent soil depletion and reduce pest problems",
            "🌡️ Use mulch to regulate soil temperature and retain moisture",
            "✂️ Regular harvesting encourages plants to produce more",
            "📝 Keep a garden journal to track what works in your specific location",
            "🌿 Harvest herbs in the morning after dew evaporates for best flavor"
        ]
        
        return {
            'garden_plan': garden_plan.dict(),
            'location_info': location_info,
            'enhanced_plants': enhanced_plants,
            'calendar_data': calendar_data,
            'layout_data': layout_data,
            'general_tips': general_tips,
            'generation_date': datetime.now().strftime("%B %d, %Y"),
            'generation_time': datetime.now().strftime("%I:%M %p"),
            'include_images': include_images,
            'include_calendar': include_calendar,
            'include_layout': include_layout,
            'total_plants': len(enhanced_plants),
            'app_name': "JardAIn - AI Garden Planner",
            'plan_id': getattr(garden_plan, 'plan_id', None)
        }
    
    def _generate_planting_calendar(self, plants: List[Dict], location_info: Dict) -> Dict[str, Any]:
        """Generate a monthly planting calendar using actual planting schedule data"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        calendar = {month: [] for month in months}
        
        for plant in plants:
            # Get the actual planting schedule data for this plant
            schedule_data = plant.get('planting_schedule', {})
            
            if schedule_data:
                plant_name = plant.get('name', 'Unknown Plant')
                
                # Add start indoors date
                if schedule_data.get('start_indoors') and schedule_data['start_indoors'] != 'N/A':
                    month_name = self._extract_month_from_date(schedule_data['start_indoors'])
                    if month_name and month_name in calendar:
                        calendar[month_name].append({
                            'plant': plant_name,
                            'action': 'Start Seeds Indoors',
                            'date': schedule_data['start_indoors']
                        })
                
                # Add direct sow date
                if schedule_data.get('direct_sow') and schedule_data['direct_sow'] != 'N/A':
                    month_name = self._extract_month_from_date(schedule_data['direct_sow'])
                    if month_name and month_name in calendar:
                        calendar[month_name].append({
                            'plant': plant_name,
                            'action': 'Direct Sow',
                            'date': schedule_data['direct_sow']
                        })
                
                # Add transplant date
                if schedule_data.get('transplant') and schedule_data['transplant'] != 'N/A':
                    month_name = self._extract_month_from_date(schedule_data['transplant'])
                    if month_name and month_name in calendar:
                        calendar[month_name].append({
                            'plant': plant_name,
                            'action': 'Transplant Outdoors',
                            'date': schedule_data['transplant']
                        })
                
                # Add harvest period
                if schedule_data.get('harvest') and schedule_data['harvest'] != 'See instructions':
                    # Extract start and end months from "June 15 to September 30" format
                    harvest_period = schedule_data['harvest']
                    if ' to ' in harvest_period:
                        start_harvest, end_harvest = harvest_period.split(' to ')
                        start_month = self._extract_month_from_date(start_harvest.strip())
                        end_month = self._extract_month_from_date(end_harvest.strip())
                        
                        if start_month and start_month in calendar:
                            calendar[start_month].append({
                                'plant': plant_name,
                                'action': 'Harvest Begins',
                                'date': start_harvest.strip()
                            })

        return {
            'calendar': calendar,
            'zone_info': location_info.get('climate_zone', 'Unknown'),
            'frost_dates': location_info.get('frost_dates', {})
        }
    
    def _extract_month_from_date(self, date_string: str) -> str:
        """Extract month name from date string like 'March 15' or 'June 15'"""
        if not date_string:
            return None
        
        # Handle formats like "March 15", "June 15", etc.
        try:
            # Split and get first word (should be month)
            parts = date_string.strip().split()
            if parts:
                month_name = parts[0]
                # Check if it's a valid month
                months = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
                if month_name in months:
                    return month_name
        except:
            pass
        
        return None
    
    def _generate_layout_recommendations(self, plants: List[Dict]) -> Dict[str, Any]:
        """Generate garden layout and spacing recommendations"""
        layout_sections = []
        
        # Group plants by categories
        categories = {}
        for plant in plants:
            category = plant.get('database_info', {}).get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(plant)
        
        # Generate spacing recommendations
        spacing_guide = []
        for plant in plants:
            db_info = plant.get('database_info', {})
            if db_info:
                spacing_guide.append({
                    'plant': plant['name'],
                    'spacing': db_info.get('spacing', 'See instructions'),
                    'depth': db_info.get('planting_depth', 'See instructions'),
                    'sun_requirement': db_info.get('sun_requirement', 'Full sun'),
                    'water_needs': db_info.get('water_needs', 'Regular')
                })
        
        return {
            'categories': categories,
            'spacing_guide': spacing_guide,
            'total_area_estimate': f"{len(plants) * 4} square feet (estimated)",
            'layout_tips': [
                "Plant tall crops on the north side to avoid shading shorter plants",
                "Group plants with similar water needs together",
                "Consider companion planting benefits",
                "Leave pathways for easy access and maintenance"
            ]
        }
    
    async def _generate_html(self, template_data: Dict[str, Any]) -> str:
        """Generate HTML content from template"""
        template = self.template_env.get_template('garden_plan.html')
        return template.render(**template_data)
    
    async def _generate_pdf_from_html(self, html_content: str, filepath: str) -> str:
        """Generate PDF from HTML using WeasyPrint"""
        
        try:
            # WeasyPrint HTML to PDF conversion
            # Create HTML document from string
            html_doc = weasyprint.HTML(string=html_content)
            
            # Generate PDF
            pdf_bytes = html_doc.write_pdf()
            
            # Save PDF file
            with open(filepath, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            
            return filepath
            
        except Exception as e:
            print(f"❌ WeasyPrint error: {e}")
            # Let's try a different approach if the first fails
            try:
                # Alternative: Write HTML to temp file first
                temp_html_path = filepath.replace('.pdf', '_temp.html')
                with open(temp_html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Generate PDF from file
                html_doc = weasyprint.HTML(filename=temp_html_path)
                pdf_bytes = html_doc.write_pdf()
                
                # Save PDF file
                with open(filepath, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)
                
                # Clean up temp file
                if os.path.exists(temp_html_path):
                    os.unlink(temp_html_path)
                
                return filepath
                
            except Exception as e2:
                raise Exception(f"WeasyPrint failed with both string and file methods: {e}, {e2}")
    
    async def list_generated_pdfs(self) -> List[Dict[str, Any]]:
        """List all generated PDF files"""
        pdf_files = []
        generated_dir = Path('generated_plans')
        
        if generated_dir.exists():
            for pdf_file in generated_dir.glob('*.pdf'):
                stats = pdf_file.stat()
                pdf_files.append({
                    'filename': pdf_file.name,
                    'filepath': str(pdf_file),
                    'size_bytes': stats.st_size,
                    'size_mb': round(stats.st_size / (1024 * 1024), 2),
                    'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
        
        return sorted(pdf_files, key=lambda x: x['created_at'], reverse=True)
    
    async def delete_pdf(self, filename: str) -> Dict[str, Any]:
        """Delete a generated PDF file"""
        try:
            filepath = Path(f'generated_plans/{filename}')
            if filepath.exists() and filepath.suffix == '.pdf':
                filepath.unlink()
                return {
                    "success": True,
                    "message": f"PDF {filename} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"PDF {filename} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_planting_calendar_from_garden_plan(self, garden_plan: GardenPlan, location_info: Dict) -> Dict[str, Any]:
        """Generate calendar directly from garden plan's planting schedules"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        calendar = {month: [] for month in months}
        
        # Use the actual planting schedules from the garden plan
        for schedule in garden_plan.planting_schedules:
            plant_name = schedule.plant_name
            
            # Add start indoors date
            if schedule.start_indoors_date:
                month_name = schedule.start_indoors_date.strftime("%B")
                calendar[month_name].append({
                    'plant': plant_name,
                    'action': 'Start Seeds Indoors',
                    'date': schedule.start_indoors_date.strftime("%B %d")
                })
            
            # Add direct sow date
            if schedule.direct_sow_date:
                month_name = schedule.direct_sow_date.strftime("%B")
                calendar[month_name].append({
                    'plant': plant_name,
                    'action': 'Direct Sow',
                    'date': schedule.direct_sow_date.strftime("%B %d")
                })
            
            # Add transplant date
            if schedule.transplant_date:
                month_name = schedule.transplant_date.strftime("%B")
                calendar[month_name].append({
                    'plant': plant_name,
                    'action': 'Transplant Outdoors',
                    'date': schedule.transplant_date.strftime("%B %d")
                })
            
            # Add harvest start
            if schedule.harvest_start_date:
                month_name = schedule.harvest_start_date.strftime("%B")
                calendar[month_name].append({
                    'plant': plant_name,
                    'action': 'Harvest Begins',
                    'date': schedule.harvest_start_date.strftime("%B %d")
                })

        return {
            'calendar': calendar,
            'zone_info': location_info.get('climate_zone', 'Unknown'),
            'frost_dates': location_info.get('frost_dates', {})
        } 
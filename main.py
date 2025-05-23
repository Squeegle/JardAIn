"""
JardAIn Garden Planner - FastAPI Application
Main entry point for the AI-powered garden planning application.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import uvicorn
from routers import plants, garden_plans

# Import our configuration
from config import settings

# Import routers
from routers import plants

# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.app_name,
    description="Generate personalized gardening plans using AI based on your location and plant preferences",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,  # Hide docs in production
    redoc_url="/redoc" if settings.debug else None
)

# ========================
# Middleware Configuration
# ========================

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ========================
# Static Files and Templates
# ========================

# Mount static files (CSS, JS, images)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
if os.path.exists("templates"):
    templates = Jinja2Templates(directory="templates")
else:
    templates = None

# ========================
# Include API Routers
# ========================

# Plant management APIs
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])

# Garden plan generation APIs
app.include_router(garden_plans.router, prefix="/api/plans", tags=["garden-plans"])

# TODO: Add these routers as we build them
# app.include_router(pdf_generator.router, prefix="/api/pdf", tags=["pdf"])

# ========================
# Core Routes
# ========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Homepage - Garden planner interface
    Renders the main application interface where users can:
    - Enter their zip code
    - Select vegetables to grow
    - Generate their garden plan
    """
    if templates:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                "app_name": settings.app_name,
                "debug": settings.debug
            }
        )
    else:
        # Fallback HTML if templates directory doesn't exist
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JardAIn Garden Planner</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                .header {{ text-align: center; color: #2e7d32; }}
                .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .api-section {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .endpoint {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #4caf50; }}
                .method {{ font-weight: bold; color: #2e7d32; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌱 JardAIn Garden Planner</h1>
                <p>AI-Powered Personalized Garden Planning</p>
            </div>
            <div class="status">
                <h3>✅ FastAPI Application Running Successfully!</h3>
                <p><strong>Configuration Status:</strong></p>
                <ul>
                    <li>LLM Provider: {settings.llm_provider.upper()}</li>
                    <li>Debug Mode: {settings.debug}</li>
                    <li>Server: {settings.host}:{settings.port}</li>
                </ul>
            </div>
            
            <div class="api-section">
                <h3>🌿 Available Plant APIs</h3>
                <div class="endpoint">
                    <span class="method">GET</span> /api/plants - List all plants
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/plants/search?q=tomato - Search plants
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/plants/tomato - Get specific plant
                </div>
                
                <h3>🧠 Garden Plan APIs</h3>
                <div class="endpoint">
                    <span class="method">POST</span> /api/plans - Create garden plan (THE MAIN FEATURE!)
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/plans/validate - Validate request
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/plans/location/90210 - Get location info
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/plans/suggestions/90210 - Get plant suggestions
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/docs" style="background: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    📚 View API Documentation
                </a>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment
    Returns application status and configuration info
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "llm_configured": settings.validate_llm_config(),
        "debug": settings.debug,
        "environment": "development" if settings.debug else "production",
        "available_endpoints": {
            "plants": "/api/plants",
            "plant_search": "/api/plants/search?q=tomato",
            "plant_details": "/api/plants/{name}",
            "plant_types": "/api/plants/types/{type}"
        }
    }

@app.get("/config")
async def get_config_info():
    """
    Configuration information endpoint (debug only)
    Shows current application configuration
    """
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "app_name": settings.app_name,
        "llm_provider": settings.llm_provider,
        "llm_config": {
            "provider": settings.llm_config["provider"],
            "model": settings.llm_config.get("model", "N/A"),
            "configured": settings.validate_llm_config()
        },
        "paths": {
            "plant_data": settings.plant_data_path,
            "generated_plans": settings.generated_plans_path,
            "plant_images": settings.plant_images_path
        },
        "server": {
            "host": settings.host,
            "port": settings.port,
            "debug": settings.debug
        }
    }

# ========================
# Startup and Shutdown Events
# ========================

@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    """
    print(f"🚀 Starting {settings.app_name}")
    print(f"🤖 LLM Provider: {settings.llm_provider.upper()}")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🌱 Plant API: http://{settings.host}:{settings.port}/api/plants")
    
    # Validate critical configuration
    if not settings.validate_llm_config():
        print("⚠️  Warning: LLM configuration incomplete")
    
    # Check if required directories exist
    required_dirs = [
        settings.generated_plans_path,
        settings.plant_images_path,
        settings.logs_path
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"📁 Created directory: {directory}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    """
    print(f"🛑 Shutting down {settings.app_name}")

# ========================
# Development Server
# ========================

if __name__ == "__main__":
    # Run the development server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # Auto-reload on file changes in debug mode
        log_level=settings.log_level.lower(),
        access_log=settings.debug
    )
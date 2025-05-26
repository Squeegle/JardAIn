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
from routers.pdf_router import router as pdf_router

# Import our configuration
from config import settings

# Import database functionality
from models.database import init_database, get_database_manager

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

# Add PDF router
app.include_router(pdf_router, prefix="/api")

# ========================
# Core Routes
# ========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Homepage - Garden planner user interface
    Serves the main user frontend for creating garden plans
    """
    try:
        # Serve the user frontend from static/index.html
        with open("static/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback if static file doesn't exist
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JardAIn Garden Planner</title>
            <style>body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}</style>
        </head>
        <body>
            <h1>🌱 JardAIn Garden Planner</h1>
            <p>Frontend files not found. Please check the static directory.</p>
            <a href="/docs">View API Documentation</a>
        </body>
        </html>
        """)

@app.get("/test", response_class=HTMLResponse)
async def frontend_test():
    """
    Frontend test page for debugging API issues
    """
    try:
        with open("static/test-frontend.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test page not found</h1><p>Please ensure static/test-frontend.html exists.</p>")

@app.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic health checks
    Returns immediately without any dependencies
    """
    return {"status": "ok", "service": "JardAIn Garden Planner"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment
    Returns application status and configuration info
    """
    # Always return healthy for basic health check
    # Database connectivity is optional for this application
    database_status = "not_configured"
    database_error = None
    
    try:
        if settings.validate_database_config():
            try:
                from sqlalchemy import text
                db_manager = get_database_manager()
                # Simple connection test with timeout
                async with db_manager.async_session_maker() as session:
                    await session.execute(text("SELECT 1"))
                database_status = "connected"
            except Exception as db_e:
                database_error = str(db_e)
                database_status = "error"
        else:
            database_status = "not_configured"
    except Exception as e:
        database_error = str(e)
        database_status = "error"
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "llm_configured": settings.validate_llm_config(),
        "database_status": database_status,
        "database_error": database_error,
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
    
    # Initialize database connection (non-blocking, graceful fallback)
    print("🗄️  Initializing database connection...")
    if settings.validate_database_config():
        try:
            db_manager = init_database(settings.database_url_computed, **settings.database_config)
            print(f"✅ Database manager initialized for: {settings.postgres_db}")
            
            # Create tables if they don't exist (with timeout)
            try:
                await db_manager.create_tables()
                print("🏗️  Database tables ready")
                
                # Notify plant service that database is now available
                from services.plant_service import plant_service
                plant_service.refresh_database_status()
                print("✅ Database fully connected and ready")
                
            except Exception as table_e:
                print(f"⚠️  Database table creation failed: {table_e}")
                print("⚠️  Application will continue with JSON fallback and LLM generation")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("⚠️  Application will continue with JSON fallback and LLM generation")
    else:
        print("⚠️  Database configuration incomplete - using JSON fallback and LLM generation")
    
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
    
    # Close database connections
    try:
        db_manager = get_database_manager()
        await db_manager.close()
        print("🗄️  Database connections closed")
    except Exception as e:
        print(f"⚠️  Error closing database: {e}")

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

# Mount static files for web frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main web app
@app.get("/", response_class=HTMLResponse)
async def serve_web_app():
    """Serve the main web application"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())
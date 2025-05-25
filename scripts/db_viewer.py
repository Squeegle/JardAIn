#!/usr/bin/env python3
"""
Database viewer for JardAIn - properly initializes database connection
"""
import os
import sys
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from config import settings
from models.database import get_database_manager, init_database
from services.plant_service import PlantService

async def initialize_database():
    """Initialize database connection"""
    print("🔗 Initializing database connection...")
    try:
        # Check config first
        if not settings.validate_database_config():
            print("❌ Database configuration invalid")
            return False
        
        # Initialize database (this returns the manager, doesn't need await)
        database_url = settings.database_url_computed
        print(f"Database URL: {database_url}")
        db_manager = init_database(database_url, **settings.database_config)
        print("✅ Database manager initialized")
        
        # Test connection
        async with db_manager.async_session_maker() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create tables
        await db_manager.create_tables()
        print("✅ Database tables created/verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

async def show_database_contents():
    """Display database contents"""
    print("\n🗄️  JardAIn Database Contents")
    print("=" * 50)
    
    try:
        # Initialize plant service (after database is ready)
        plant_service = PlantService()
        
        # Force refresh database status
        plant_service.refresh_database_status()
        
        print(f"Database available: {plant_service.database_available}")
        
        if plant_service.database_available:
            # Get database statistics
            stats = await plant_service.get_database_stats()
            
            if "error" not in stats:
                print(f"\n📊 Database Statistics:")
                print(f"  - Total plants: {stats['total_plants']}")
                print(f"  - Static plants: {stats['static_plants']}")
                print(f"  - LLM generated: {stats['llm_generated_plants']}")
                print(f"  - Most popular: {stats['most_popular']}")
            
            # Get all plants
            all_plants = await plant_service.get_all_plants()
            print(f"\n🌱 All Plants ({len(all_plants)} total):")
            
            # Group by type
            by_type = {}
            for plant in all_plants:
                if plant.plant_type not in by_type:
                    by_type[plant.plant_type] = []
                by_type[plant.plant_type].append(plant)
            
            print(f"\n🏷️  Plants by type:")
            for plant_type, plants in sorted(by_type.items()):
                print(f"  - {plant_type}: {len(plants)}")
            
            # Show sample plants from each type
            print(f"\n🌿 Sample plants by type:")
            for plant_type, plants in sorted(by_type.items()):
                print(f"\n  {plant_type.upper()}:")
                for plant in sorted(plants, key=lambda p: p.name)[:5]:  # Show first 5 of each type
                    print(f"    - {plant.name} ({plant.days_to_harvest} days)")
            
            # Test search functionality
            print(f"\n🔍 Search Examples:")
            
            search_terms = ["tom", "herb", "lettuce"]
            for term in search_terms:
                results = await plant_service.search_plants(term)
                print(f"  '{term}': {len(results)} results")
                for plant in results[:3]:  # Show first 3 results
                    print(f"    - {plant.name} ({plant.plant_type})")
                    
        else:
            print("❌ Database not available - showing static data")
            static_plants = plant_service.get_all_static_plants()
            print(f"📄 Static plants available: {len(static_plants)}")
            
            # Show first 10 static plants
            print(f"\n🌿 First 10 static plants:")
            for plant in static_plants[:10]:
                print(f"  - {plant.name} ({plant.plant_type}) - {plant.days_to_harvest} days")
                
    except Exception as e:
        print(f"❌ Error displaying database contents: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    print("🗄️  JardAIn Database Viewer")
    print("=" * 50)
    
    # First initialize database
    db_ready = await initialize_database()
    
    if db_ready:
        # Then show contents
        await show_database_contents()
    else:
        print("❌ Could not connect to database")
        print("💡 Try running: python3 scripts/setup_database_enhanced.py")

if __name__ == "__main__":
    asyncio.run(main()) 
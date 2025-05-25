#!/usr/bin/env python3
"""
Simple script to view the JardAIn database contents
"""
import asyncio
import sys
sys.path.append('.')
from models.database import get_database_manager
from sqlalchemy import text

async def show_database_contents():
    """Display database tables and plant data"""
    print("🗄️  JardAIn Database Viewer")
    print("=" * 50)
    
    try:
        # Initialize the database manager first
        from models.database import init_database
        await init_database()
        
        db_manager = get_database_manager()
        async with db_manager.async_session_maker() as session:
            # Get table info
            result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = result.fetchall()
            print('📊 Tables in database:')
            for table in tables:
                print(f'  - {table[0]}')
            
            # Get plant statistics
            result = await session.execute(text('SELECT COUNT(*) FROM plants;'))
            total_count = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM plants WHERE source = 'static';"))
            static_count = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM plants WHERE source = 'llm';"))
            llm_count = result.scalar()
            
            print(f'\n🌱 Plant Statistics:')
            print(f'  - Total plants: {total_count}')
            print(f'  - Static plants: {static_count}')
            print(f'  - LLM generated: {llm_count}')
            
            # Show plants by type
            result = await session.execute(text('SELECT plant_type, COUNT(*) FROM plants GROUP BY plant_type ORDER BY COUNT(*) DESC;'))
            types = result.fetchall()
            print(f'\n🏷️  Plants by type:')
            for plant_type, count in types:
                print(f'  - {plant_type}: {count}')
            
            # Show sample plants
            result = await session.execute(text('SELECT name, plant_type, days_to_harvest, source, usage_count FROM plants ORDER BY usage_count DESC, name LIMIT 15;'))
            plants = result.fetchall()
            print(f'\n🌿 Sample plants (top 15 by usage):')
            print(f'{"Name":<20} {"Type":<12} {"Days":<6} {"Source":<8} {"Usage":<6}')
            print("-" * 60)
            for name, plant_type, days, source, usage in plants:
                print(f'{name:<20} {plant_type:<12} {days:<6} {source:<8} {usage:<6}')
            
            # Show search example
            search_term = "tom"
            result = await session.execute(text(f"SELECT name, plant_type FROM plants WHERE LOWER(name) LIKE '%{search_term}%';"))
            search_results = result.fetchall()
            print(f'\n🔍 Search example for "{search_term}":')
            for name, plant_type in search_results:
                print(f'  - {name} ({plant_type})')
                
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure PostgreSQL is running and credentials are correct.")

if __name__ == "__main__":
    asyncio.run(show_database_contents()) 
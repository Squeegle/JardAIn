#!/usr/bin/env python3
"""
Migration script to transfer plant data from JSON to PostgreSQL database.
This script reads the existing common_vegetables.json file and populates the PostgreSQL plants table.

Usage:
    python scripts/migrate_plants_to_db.py [--backup] [--dry-run] [--force]

Options:
    --backup    Create a backup of the original JSON file
    --dry-run   Show what would be migrated without actually doing it
    --force     Overwrite existing plants in database
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from models.database import PlantModel, init_database, get_database_manager
from models.garden_plan import PlantInfo
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

class PlantMigrator:
    """
    Handles the migration of plant data from JSON to PostgreSQL
    """
    
    def __init__(self, source_file: str, backup: bool = False, dry_run: bool = False, force: bool = False):
        """
        Initialize the migrator
        
        Args:
            source_file: Path to the JSON file containing plant data
            backup: Whether to create a backup of the source file
            dry_run: Whether to simulate the migration without actually doing it
            force: Whether to overwrite existing plants in the database
        """
        self.source_file = source_file
        self.backup = backup
        self.dry_run = dry_run
        self.force = force
        self.migrated_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def load_json_plants(self) -> List[PlantInfo]:
        """
        Load plant data from the JSON file and convert to PlantInfo objects
        """
        print(f"📖 Loading plants from {self.source_file}...")
        
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
        
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            plants = []
            for plant_data in data:
                try:
                    plant = PlantInfo(**plant_data)
                    plants.append(plant)
                except Exception as e:
                    print(f"⚠️  Error parsing plant data {plant_data.get('name', 'unknown')}: {e}")
                    self.error_count += 1
            
            print(f"✅ Successfully loaded {len(plants)} plants from JSON")
            return plants
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in source file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading source file: {e}")
    
    def create_backup(self):
        """
        Create a backup of the original JSON file
        """
        if not self.backup:
            return
        
        backup_file = f"{self.source_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            import shutil
            shutil.copy2(self.source_file, backup_file)
            print(f"💾 Backup created: {backup_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
    
    def plant_info_to_model(self, plant_info: PlantInfo) -> PlantModel:
        """
        Convert a PlantInfo object to a PlantModel (SQLAlchemy) object
        """
        plant_model = PlantModel(
            name=plant_info.name,
            scientific_name=plant_info.scientific_name,
            plant_type=plant_info.plant_type,
            days_to_harvest=plant_info.days_to_harvest,
            spacing_inches=plant_info.spacing_inches,
            planting_depth_inches=plant_info.planting_depth_inches,
            sun_requirements=plant_info.sun_requirements,
            water_requirements=plant_info.water_requirements,
            soil_ph_range=plant_info.soil_ph_range,
            source="static",  # Mark as static since it comes from JSON
            llm_model=None,   # No LLM used for static plants
            usage_count=1     # Initialize usage count
        )
        
        # Set companion plants and avoid planting with as JSON
        plant_model.companion_plants_list = plant_info.companion_plants
        plant_model.avoid_planting_with_list = plant_info.avoid_planting_with
        
        return plant_model
    
    async def check_existing_plants(self, session, plant_names: List[str]) -> Dict[str, PlantModel]:
        """
        Check which plants already exist in the database
        """
        print("🔍 Checking for existing plants in database...")
        
        stmt = select(PlantModel).where(PlantModel.name.in_(plant_names))
        result = await session.execute(stmt)
        existing_plants = result.scalars().all()
        
        existing_dict = {plant.name: plant for plant in existing_plants}
        
        if existing_dict:
            print(f"📋 Found {len(existing_dict)} existing plants in database")
            if not self.force:
                print("💡 Use --force to overwrite existing plants")
        
        return existing_dict
    
    async def migrate_plants(self, plants: List[PlantInfo]):
        """
        Migrate plant data to the PostgreSQL database
        """
        print(f"🚀 Starting migration of {len(plants)} plants...")
        print(f"📊 Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        
        if self.dry_run:
            print("🔍 DRY RUN - No changes will be made to the database")
        
        # Initialize database connection
        db_manager = get_database_manager()
        
        async with db_manager.async_session_maker() as session:
            try:
                # Check for existing plants
                plant_names = [plant.name for plant in plants]
                existing_plants = await self.check_existing_plants(session, plant_names)
                
                for plant_info in plants:
                    try:
                        plant_name = plant_info.name
                        
                        # Check if plant already exists
                        if plant_name in existing_plants and not self.force:
                            print(f"⏭️  Skipping existing plant: {plant_name}")
                            self.skipped_count += 1
                            continue
                        
                        # Convert to database model
                        plant_model = self.plant_info_to_model(plant_info)
                        
                        if self.dry_run:
                            print(f"🔍 Would migrate: {plant_name} ({plant_info.plant_type})")
                            self.migrated_count += 1
                            continue
                        
                        # Handle existing plant (force mode)
                        if plant_name in existing_plants and self.force:
                            # Update existing plant
                            existing_plant = existing_plants[plant_name]
                            
                            # Update all fields except id, created_at, and usage_count
                            existing_plant.scientific_name = plant_model.scientific_name
                            existing_plant.plant_type = plant_model.plant_type
                            existing_plant.days_to_harvest = plant_model.days_to_harvest
                            existing_plant.spacing_inches = plant_model.spacing_inches
                            existing_plant.planting_depth_inches = plant_model.planting_depth_inches
                            existing_plant.sun_requirements = plant_model.sun_requirements
                            existing_plant.water_requirements = plant_model.water_requirements
                            existing_plant.soil_ph_range = plant_model.soil_ph_range
                            existing_plant.companion_plants = plant_model.companion_plants
                            existing_plant.avoid_planting_with = plant_model.avoid_planting_with
                            existing_plant.source = "static"  # Update source to static
                            
                            print(f"🔄 Updated existing plant: {plant_name}")
                        else:
                            # Add new plant
                            session.add(plant_model)
                            print(f"➕ Added new plant: {plant_name}")
                        
                        self.migrated_count += 1
                        
                    except IntegrityError as e:
                        print(f"❌ Integrity error for plant {plant_info.name}: {e}")
                        await session.rollback()
                        self.error_count += 1
                    except Exception as e:
                        print(f"❌ Error migrating plant {plant_info.name}: {e}")
                        self.error_count += 1
                
                # Commit all changes
                if not self.dry_run:
                    await session.commit()
                    print("✅ Migration committed to database")
                
            except Exception as e:
                if not self.dry_run:
                    await session.rollback()
                print(f"❌ Migration failed: {e}")
                raise
    
    def print_summary(self):
        """
        Print migration summary statistics
        """
        print("\n" + "="*50)
        print("📊 MIGRATION SUMMARY")
        print("="*50)
        print(f"✅ Successfully migrated: {self.migrated_count}")
        print(f"⏭️  Skipped (already exists): {self.skipped_count}")
        print(f"❌ Errors: {self.error_count}")
        print(f"📋 Total processed: {self.migrated_count + self.skipped_count + self.error_count}")
        
        if self.dry_run:
            print("\n🔍 This was a DRY RUN - no changes were made")
        else:
            print(f"\n🎉 Migration completed successfully!")
    
    async def run(self):
        """
        Run the complete migration process
        """
        try:
            print("🌱 JardAIn Plant Migration Tool")
            print("="*40)
            
            # Create backup if requested
            self.create_backup()
            
            # Load plants from JSON
            plants = self.load_json_plants()
            
            if not plants:
                print("⚠️  No plants found in JSON file. Nothing to migrate.")
                return
            
            # Migrate to database
            await self.migrate_plants(plants)
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            print(f"💥 Migration failed with error: {e}")
            sys.exit(1)

async def main():
    """
    Main entry point for the migration script
    """
    parser = argparse.ArgumentParser(description="Migrate plant data from JSON to PostgreSQL")
    parser.add_argument("--backup", action="store_true", help="Create backup of source JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without doing it")
    parser.add_argument("--force", action="store_true", help="Overwrite existing plants in database")
    parser.add_argument("--source", default="data/common_vegetables.json", help="Source JSON file path")
    
    args = parser.parse_args()
    
    print(f"🔧 Initializing database connection...")
    print(f"🔗 Database URL: {settings.database_url_computed}")
    
    # Validate database configuration
    if not settings.validate_database_config():
        print("❌ Database configuration is incomplete!")
        print("💡 Please set DATABASE_URL or individual postgres_* environment variables")
        sys.exit(1)
    
    # Initialize database
    try:
        db_manager = init_database(settings.database_url_computed, **settings.database_config)
        
        # Ensure tables exist
        print("🏗️  Creating database tables if they don't exist...")
        await db_manager.create_tables()
        
        # Run migration
        migrator = PlantMigrator(
            source_file=args.source,
            backup=args.backup,
            dry_run=args.dry_run,
            force=args.force
        )
        
        await migrator.run()
        
        # Close database connections
        await db_manager.close()
        
    except Exception as e:
        print(f"💥 Database initialization failed: {e}")
        print("💡 Make sure PostgreSQL is running and connection details are correct")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 
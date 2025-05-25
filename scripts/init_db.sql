-- JardAIn PostgreSQL Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main database (already created by POSTGRES_DB env var)
-- CREATE DATABASE jardain;

-- Connect to the jardain database
\c jardain;

-- Create extensions that might be useful for the application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- For fuzzy text search

-- Create a schema for application tables (optional, using public for simplicity)
-- CREATE SCHEMA IF NOT EXISTS jardain_app;

-- Grant necessary permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE jardain TO jardain_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO jardain_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jardain_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jardain_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jardain_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jardain_user;

-- Create indexes for better performance (these will be created by SQLAlchemy too)
-- Note: SQLAlchemy will create the actual tables, this is just for additional setup

-- Log the completion
\echo 'JardAIn database initialization completed successfully!' 
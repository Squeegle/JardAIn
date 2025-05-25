# 🗄️ Database Setup Guide for JardAIn

This guide will help you set up PostgreSQL for the JardAIn Garden Planner application. Choose the method that best fits your needs and environment.

## 🚀 Quick Start (Recommended)

**Use the automated setup script:**
```bash
python scripts/setup_database_enhanced.py
```

This interactive script will:
- ✅ Detect your system and provide appropriate options
- ✅ Install required dependencies automatically
- ✅ Set up PostgreSQL using your preferred method
- ✅ Create and configure the database
- ✅ Generate your `.env` file with correct settings
- ✅ Run database migrations
- ✅ Verify everything is working

---

## 📋 Manual Setup Options

If you prefer to set up the database manually, choose one of these options:

### Option 1: 🐳 Docker Setup (Easiest)

**Prerequisites:**
- Docker installed and running

**Using existing docker-compose.yml:**
```bash
# Start PostgreSQL container
docker-compose up -d postgres

# The database will be available at:
# Host: localhost
# Port: 5432
# Database: jardain
# Username: jardain_user
# Password: jardain_password
```

**Using standalone Docker container:**
```bash
# Create and start PostgreSQL container
docker run -d \
  --name jardain_postgres \
  -e POSTGRES_DB=jardain \
  -e POSTGRES_USER=jardain_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -v jardain_postgres_data:/var/lib/postgresql/data \
  postgres:15

# Wait for PostgreSQL to be ready
docker exec jardain_postgres pg_isready -U jardain_user -d jardain
```

### Option 2: 💻 Native Installation

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE USER jardain_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE jardain OWNER jardain_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jardain TO jardain_user;"
```

**macOS (Homebrew):**
```bash
# Install PostgreSQL
brew install postgresql
brew services start postgresql

# Create database and user
createuser -s jardain_user
createdb jardain -O jardain_user
psql -d jardain -c "ALTER USER jardain_user WITH PASSWORD 'your_secure_password';"
```

**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Use pgAdmin or psql to create the database and user:
   ```sql
   CREATE USER jardain_user WITH PASSWORD 'your_secure_password';
   CREATE DATABASE jardain OWNER jardain_user;
   GRANT ALL PRIVILEGES ON DATABASE jardain TO jardain_user;
   ```

### Option 3: ☁️ Cloud PostgreSQL

**Popular cloud providers:**
- **AWS RDS**: https://aws.amazon.com/rds/postgresql/
- **Google Cloud SQL**: https://cloud.google.com/sql/postgresql
- **Heroku Postgres**: https://www.heroku.com/postgres
- **DigitalOcean Managed Databases**: https://www.digitalocean.com/products/managed-databases/

**After setting up your cloud database:**
1. Note down the connection details (host, port, database name, username, password)
2. Ensure your application can connect (check firewall/security groups)
3. Use these details in your `.env` file

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root with your database settings:

```env
# Database Configuration (PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jardain
POSTGRES_USER=jardain_user
POSTGRES_PASSWORD=your_secure_password_here

# Alternative: Use complete DATABASE_URL
# DATABASE_URL=postgresql+asyncpg://jardain_user:your_password@localhost:5432/jardain

# Application Settings
APP_NAME=JardAIn Garden Planner
DEBUG=true
HOST=0.0.0.0
PORT=8000

# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Optional: OpenAI (for production)
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-3.5-turbo
```

---

## 🔧 Database Schema Setup

After configuring your database connection, set up the schema:

```bash
# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Verify setup
python scripts/setup_database.py
```

---

## 🧪 Testing Your Setup

**Quick health check:**
```bash
python scripts/quick_health_check.py
```

**Comprehensive database test:**
```bash
python scripts/test_db_integration.py
```

**Test the application:**
```bash
# Start the application
python main.py

# Visit in browser
open http://localhost:8000

# Check API docs
open http://localhost:8000/docs
```

---

## 🔍 Troubleshooting

### Common Issues

**❌ "Connection refused" or "could not connect to server"**
- **Docker**: Check if container is running: `docker ps`
- **Native**: Check if PostgreSQL service is running: `sudo systemctl status postgresql`
- **Network**: Verify host and port settings in `.env`

**❌ "authentication failed for user"**
- Verify username and password in `.env` file
- Check if user exists: `psql -U postgres -c "\du"`
- Reset password if needed: `ALTER USER jardain_user WITH PASSWORD 'new_password';`

**❌ "database does not exist"**
- Create database: `createdb jardain -O jardain_user`
- Or via SQL: `CREATE DATABASE jardain OWNER jardain_user;`

**❌ "permission denied for database"**
- Grant privileges: `GRANT ALL PRIVILEGES ON DATABASE jardain TO jardain_user;`
- For schema: `GRANT ALL PRIVILEGES ON SCHEMA public TO jardain_user;`

**❌ "Alembic migration failed"**
- Check database connection first
- Reset migrations: `alembic downgrade base && alembic upgrade head`
- Check for conflicting tables: `\dt` in psql

**❌ "psycopg2 not found" or "asyncpg not found"**
```bash
pip install psycopg2-binary asyncpg sqlalchemy alembic
```

### Docker-Specific Issues

**Container won't start:**
```bash
# Check logs
docker logs jardain_postgres

# Remove and recreate
docker stop jardain_postgres
docker rm jardain_postgres
# Then run the docker run command again
```

**Port already in use:**
```bash
# Find what's using port 5432
sudo lsof -i :5432

# Use different port
docker run -p 5433:5432 ...
# Update POSTGRES_PORT=5433 in .env
```

### Performance Optimization

**For development:**
```sql
-- Increase shared_buffers for better performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

**For production:**
- Use connection pooling (pgbouncer)
- Configure appropriate `DATABASE_POOL_SIZE` in `.env`
- Monitor with `pg_stat_activity`

---

## 📊 Database Management

### Useful Commands

**Connect to database:**
```bash
# Using psql
psql -h localhost -p 5432 -U jardain_user -d jardain

# Using Docker
docker exec -it jardain_postgres psql -U jardain_user -d jardain
```

**Backup database:**
```bash
# Create backup
pg_dump -h localhost -U jardain_user jardain > jardain_backup.sql

# Restore backup
psql -h localhost -U jardain_user jardain < jardain_backup.sql
```

**Monitor database:**
```sql
-- Check active connections
SELECT * FROM pg_stat_activity WHERE datname = 'jardain';

-- Check database size
SELECT pg_size_pretty(pg_database_size('jardain'));

-- Check table sizes
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Migration Management

**Create new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migrations:**
```bash
alembic downgrade -1  # Go back one migration
alembic downgrade base  # Go back to beginning
```

**Check migration status:**
```bash
alembic current
alembic history
```

---

## 🔒 Security Best Practices

### Development
- ✅ Use strong passwords (16+ characters)
- ✅ Don't commit `.env` file to version control
- ✅ Use `localhost` connections when possible
- ✅ Keep PostgreSQL updated

### Production
- ✅ Use SSL connections (`sslmode=require`)
- ✅ Restrict network access (firewall rules)
- ✅ Use managed database services when possible
- ✅ Regular backups and monitoring
- ✅ Use environment variables for secrets
- ✅ Enable PostgreSQL logging and monitoring

### Example production DATABASE_URL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database?sslmode=require
```

---

## 📞 Getting Help

**If you're still having issues:**

1. **Run the diagnostic script:**
   ```bash
   python scripts/quick_health_check.py
   ```

2. **Check the logs:**
   ```bash
   tail -f logs/jardain.log
   ```

3. **Test individual components:**
   ```bash
   python scripts/test_config.py
   python scripts/test_db_integration.py
   ```

4. **Check the troubleshooting guides:**
   - `scripts/README.md` - Testing and debugging
   - `scripts/TESTING.md` - Comprehensive testing guide

5. **Common solutions:**
   - Restart PostgreSQL service
   - Check firewall settings
   - Verify `.env` file configuration
   - Ensure all dependencies are installed

---

**Happy Gardening! 🌱🗄️**

For more help, check the main [README.md](README.md) or the [scripts documentation](scripts/README.md). 
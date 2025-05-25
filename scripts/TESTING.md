# Testing Guide for JardAIn Garden Planner

This document explains how to test the JardAIn Garden Planner application to ensure everything is working correctly.

## Quick Tests Available

### 1. Quick Health Check (Recommended)
**File:** `scripts/quick_health_check.py`

A simple, fast health check that verifies core functionality without requiring pytest.

```bash
python scripts/quick_health_check.py
```

**What it checks:**
- ✅ Application startup and imports
- ✅ Configuration (LLM, database, paths)
- ✅ Plant service functionality
- ✅ Static files availability
- ✅ Data files presence

**Output:** Clear pass/fail status with helpful next steps.

### 2. Comprehensive Test Suite
**File:** `scripts/test_quick_check.py`

A full pytest-based test suite that thoroughly tests all API endpoints and functionality.

```bash
python scripts/test_quick_check.py
```

Or run with pytest directly:
```bash
pytest scripts/test_quick_check.py -v
```

**What it tests:**
- 🏥 Health check endpoint
- 🏠 Home page loading
- ⚙️ Configuration endpoint
- 🔍 Plant search API
- 🌱 Plant types API
- 🗄️ Database connection (if configured)
- 🤖 LLM configuration
- 🌿 Plant service integration

### 3. Database Persistence Test
**File:** `test_persistence.py`

Tests database functionality and plant data persistence (existing file).

```bash
python test_persistence.py
```

**What it tests:**
- Database connection and table creation
- Plant data persistence across requests
- Cache vs database behavior
- LLM-generated plant storage

## Test Results Interpretation

### ✅ All Tests Pass
Your application is ready to use! You can:
- Start the server: `python -m uvicorn main:app --reload`
- Visit the app: http://localhost:8000
- Check API docs: http://localhost:8000/docs

### ⚠️ Some Tests Fail/Skip
Common issues and solutions:

**Database Tests Skipped:**
- Normal if database is not configured
- Application works with JSON fallback
- Configure PostgreSQL if you want database features

**LLM Tests Fail:**
- Check your `.env` file for LLM configuration
- Ensure Ollama is running (if using Ollama)
- Verify OpenAI API key (if using OpenAI)

**Static File Warnings:**
- Some CSS/JS files may be missing
- Core functionality still works
- Frontend may have limited styling

**Plant Service Errors:**
- Usually indicates LLM configuration issues
- Check that your LLM provider is accessible
- Verify network connectivity

## Running Tests in Development

### Before Making Changes
```bash
# Quick check that everything still works
python scripts/quick_health_check.py
```

### After Making Changes
```bash
# Full test suite
python scripts/test_quick_check.py

# If database-related changes
python test_persistence.py
```

### Continuous Testing
```bash
# Run tests automatically on file changes
pytest scripts/test_quick_check.py --watch
```

## Test Configuration

### Environment Variables
Tests respect the same environment variables as the main application:
- `LLM_PROVIDER` (ollama/openai)
- `OLLAMA_BASE_URL`
- `OPENAI_API_KEY`
- `DATABASE_URL`
- `DEBUG`

### Test Data
Tests use:
- Static plant data from `data/common_vegetables.json`
- Test queries like "tomato", "basil", "vegetable"
- Mock/real LLM calls depending on configuration

## Troubleshooting Tests

### Import Errors
```bash
# Ensure you're in the project directory
cd /path/to/JardAIn

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Permission Errors
```bash
# Make test files executable
chmod +x scripts/quick_health_check.py
chmod +x scripts/test_quick_check.py
chmod +x test_persistence.py
```

### Network/LLM Errors
- Check internet connectivity
- Verify Ollama is running: `ollama list`
- Test OpenAI API key: `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models`

## Adding New Tests

### For New Endpoints
Add tests to `scripts/test_quick_check.py`:
```python
def test_new_endpoint(client):
    """Test description"""
    response = client.get("/api/new-endpoint")
    assert response.status_code == 200
    # Add assertions
```

### For New Services
Add integration tests:
```python
@pytest.mark.asyncio
async def test_new_service():
    """Test new service functionality"""
    # Test service methods
```

### For Database Features
Add tests to `test_persistence.py` or create new database test files.

## Best Practices

1. **Run quick health check first** - fastest way to verify basic functionality
2. **Use comprehensive tests for CI/CD** - full coverage of all features
3. **Test after configuration changes** - ensure settings are correct
4. **Check database tests separately** - they require additional setup
5. **Monitor test output** - warnings often indicate configuration issues

## Test Coverage

Current test coverage includes:
- ✅ Core application startup
- ✅ Configuration validation
- ✅ Plant API endpoints
- ✅ Health monitoring
- ✅ Database connectivity
- ✅ LLM integration
- ✅ Static file serving
- ✅ Error handling

Missing coverage (future improvements):
- Garden plan generation endpoints
- PDF generation functionality
- User authentication (if added)
- Performance/load testing
- Frontend JavaScript testing 
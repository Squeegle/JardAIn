# Scripts Directory

This directory contains various testing, debugging, and utility scripts for the JardAIn Garden Planner application.

## 🧪 Main Testing Scripts

### Quick Health Check
**File:** `quick_health_check.py`
```bash
python scripts/quick_health_check.py
```
- **Purpose:** Fast verification that the application is working
- **Use case:** Quick check before starting development or after changes
- **Output:** Clear pass/fail status with helpful next steps

### Comprehensive Test Suite
**File:** `test_quick_check.py`
```bash
python scripts/test_quick_check.py
```
- **Purpose:** Full pytest-based test suite for all API endpoints
- **Use case:** Thorough testing for CI/CD or before releases
- **Coverage:** Health checks, plant APIs, configuration, LLM integration

### Database Persistence Test
**File:** `../test_persistence.py` (in root directory)
```bash
python test_persistence.py
```
- **Purpose:** Tests database functionality and plant data persistence
- **Use case:** Verify database operations and LLM-generated plant storage

## 🔧 Specialized Test Scripts

### Database Integration
- `test_db_integration.py` - Database connection and operations testing
- `migrate_plants_to_db.py` - Plant data migration utilities
- `test_plant_database.py` - Plant database functionality testing

### PDF Generation
- `test_enhanced_pdf.py` - Enhanced PDF generation testing
- `test_pdf_generation.py` - Comprehensive PDF testing
- `test_pdf_router.py` - PDF API endpoint testing
- `test_pdf_minimal.py` - Minimal PDF generation test
- `test_weasyprint_isolated.py` - WeasyPrint library testing

### Garden Plan Services
- `test_garden_plan_service.py` - Garden plan service testing
- `test_garden_plan_api.py` - Garden plan API testing
- `test_garden_plan_improvements.py` - Enhanced garden plan features
- `debug_garden_plan_methods.py` - Garden plan debugging utilities

### Plant Services
- `test_hybrid_plants.py` - Hybrid plant functionality testing
- `test_ai_plant_fix.py` - AI plant generation fixes
- `test_ai_quality.py` - AI response quality testing

### LLM Integration
- `test_ollama_setup.py` - Ollama LLM setup and testing
- `debug_llm_responses.py` - LLM response debugging
- `debug_llm_comparison.py` - LLM provider comparison
- `debug_llm_responses.py` - Detailed LLM response analysis

### Location Services
- `test_location_service.py` - Location and weather data testing

### User Experience
- `test_loading_animation.py` - Loading animation testing
- `test_loading_experience.py` - User loading experience testing

### Configuration & Setup
- `test_config.py` - Configuration validation testing
- `test_json_parsing.py` - JSON data parsing testing

### Debug Utilities
- `debug_pdf_conflict.py` - PDF generation conflict debugging
- Various debug scripts for troubleshooting specific issues

## 📋 Testing Documentation

**File:** `TESTING.md`
- Complete testing guide with troubleshooting
- Best practices for development testing
- Environment setup instructions
- Test result interpretation

## 🚀 Quick Start

### For New Developers
1. **Quick health check:** `python scripts/quick_health_check.py`
2. **Full test suite:** `python scripts/test_quick_check.py`
3. **Read the guide:** `scripts/TESTING.md`

### For Development Workflow
```bash
# Before making changes
python scripts/quick_health_check.py

# After making changes
python scripts/test_quick_check.py

# For specific features
python scripts/test_[feature_name].py
```

### For CI/CD Pipeline
```bash
# Run all critical tests
python scripts/test_quick_check.py
python test_persistence.py
python scripts/test_garden_plan_api.py
python scripts/test_pdf_generation.py
```

## 🔍 Finding the Right Test

| What you want to test | Use this script |
|----------------------|----------------|
| **Overall app health** | `quick_health_check.py` |
| **All API endpoints** | `test_quick_check.py` |
| **Database features** | `test_db_integration.py` |
| **Plant search/info** | `test_plant_database.py` |
| **Garden plan creation** | `test_garden_plan_api.py` |
| **PDF generation** | `test_pdf_generation.py` |
| **LLM integration** | `test_ollama_setup.py` |
| **Location services** | `test_location_service.py` |
| **Configuration** | `test_config.py` |

## 📝 Adding New Tests

1. **For new features:** Create `test_[feature_name].py`
2. **For debugging:** Create `debug_[issue_name].py`
3. **Update this README** with the new script description
4. **Add to TESTING.md** if it's a main testing script

## 🛠️ Script Conventions

- **test_*.py** - Automated test scripts (use pytest)
- **debug_*.py** - Debugging and troubleshooting utilities
- **setup_*.py** - Setup and configuration scripts
- **migrate_*.py** - Data migration utilities

## 📞 Getting Help

- Check `TESTING.md` for detailed testing guide
- Run `python scripts/quick_health_check.py` for quick diagnostics
- Look for similar test scripts in this directory
- Check the main README.md for overall project setup 
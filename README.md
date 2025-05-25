# 🌱 JardAIn - AI-Powered Garden Planner

**JardAIn** (Garden + AI) is an intelligent garden planning application that creates personalized garden plans using artificial intelligence. Input your location and plant preferences, and get detailed growing instructions, planting schedules, and professional PDF garden plans.

## ✨ Features

### 🤖 AI-Powered Planning
- **Hybrid Plant Database**: 50+ common garden vegetables with instant access
- **LLM Enhancement**: Uses Ollama (local) or OpenAI for detailed instructions
- **Location-Aware**: Considers your USDA zone, frost dates, and climate

### 📋 Comprehensive Garden Plans
- **Detailed Plant Information**: Growing requirements, spacing, harvest times
- **Planting Schedules**: When to start seeds, transplant, and harvest
- **Step-by-Step Instructions**: Soil prep, planting, care, and pest management
- **Layout Recommendations**: Plant spacing and garden organization tips

### 📄 Professional PDF Generation
- **Beautiful PDFs**: Professional garden plans with plant information
- **Printable Format**: Each plant on its own page for easy reference
- **Planting Calendar**: Month-by-month planting schedule
- **Layout Guide**: Spacing tables and garden tips

### 🌐 Web Interface
- **Plant Selection**: Easy multi-select interface with 50+ vegetables
- **Location Input**: Supports US ZIP codes and Canadian postal codes
- **Instant Generation**: Generate and download plans in seconds
- **Mobile Friendly**: Responsive design for all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd JardAIn
```

2. **Create virtual environment**
```bash
python -m venv jardain_env
source jardain_env/bin/activate  # On Windows: jardain_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL Database**

**Option A: Automated Setup (Recommended)**
```bash
python scripts/setup_database_enhanced.py
```
This interactive script will guide you through setting up PostgreSQL with your preferred method (Docker, native, or cloud).

**Option B: Quick Docker Setup**
```bash
# Start PostgreSQL with docker-compose (requires .env file with POSTGRES_PASSWORD)
docker-compose up -d postgres

# Or use standalone Docker container
docker run -d --name jardain_postgres \
  -e POSTGRES_DB=jardain \
  -e POSTGRES_USER=jardain_user \
  -e POSTGRES_PASSWORD=your_secure_password_here \
  -p 5432:5432 \
  postgres:15
```

**Option C: Manual Setup**
See the detailed [Database Setup Guide](DATABASE_SETUP.md) for native installation instructions.

5. **Set up environment variables**
Create a `.env` file in the root directory:
```env
# App Configuration
APP_NAME=JardAIn Garden Planner
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration (PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jardain
POSTGRES_USER=jardain_user
POSTGRES_PASSWORD=your_secure_password_here

# LLM Configuration - Choose one or both
LLM_PROVIDER=ollama                          # Use 'ollama' or 'openai'
OLLAMA_BASE_URL=http://localhost:11434       # For local development
OLLAMA_MODEL=llama3.1
OPENAI_API_KEY=your_openai_api_key_here      # For production
OPENAI_MODEL=gpt-3.5-turbo

# File Paths
PLANT_DATA_PATH=data/common_vegetables.json
GENERATED_PLANS_PATH=generated_plans/
LOGS_PATH=logs/
```

**Note:** If you used the automated database setup script, your `.env` file will be created automatically with the correct database settings.

**⚠️ Security Note:** Never commit your `.env` file to version control. It contains sensitive information like database passwords and API keys. See [SECURITY.md](SECURITY.md) for detailed security guidelines.

6. **Set up database schema**
```bash
# Run database migrations to create tables
alembic upgrade head

# Verify database setup
python scripts/setup_database.py
```

7. **Install Ollama (for local development)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.1 model
ollama pull llama3.1
```

### 🏃‍♂️ Running the Application

1. **Start the FastAPI server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the application**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 Usage

### Web Interface
1. Open http://localhost:8000 in your browser
2. Enter your ZIP/postal code
3. Select vegetables you want to grow
4. Click "Generate My Garden Plan"
5. Download your personalized PDF garden plan

### API Usage

#### Generate Garden Plan
```bash
curl -X POST "http://localhost:8000/api/plans" \
     -H "Content-Type: application/json" \
     -d '{
       "zip_code": "12345",
       "selected_plants": ["Tomato", "Spinach", "Radishes"],
       "garden_size": "medium",
       "experience_level": "beginner"
     }'
```

#### Download PDF
```bash
curl -X GET "http://localhost:8000/api/pdf/garden-plan/{plan_id}" \
     --output garden-plan.pdf
```

## 🏗️ Project Structure

```

## 🔧 Configuration

### LLM Providers

**Local Development (Ollama)**
- Free and private
- Requires ~8GB RAM
- Good for development and testing
- Set `OLLAMA_HOST=http://localhost:11434`

**Production (OpenAI)**
- Requires API key and credits
- Better quality responses
- Faster generation
- Set `OPENAI_API_KEY=your_key_here`

### Supported Locations
- **US ZIP Codes**: All US ZIP codes supported
- **Canadian Postal Codes**: All Canadian postal codes supported
- **Climate Zones**: USDA hardiness zones 3-11

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_plant_service.py
pytest tests/test_garden_plan.py

# Test with coverage
pytest --cov=services --cov-report=html
```

## 🛠️ Development

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy services/
```

### Adding New Plants
1. Edit `data/vegetables.json`
2. Add plant information following the existing schema
3. Restart the application

### API Development
- FastAPI automatic documentation: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## 📋 API Endpoints

### Plants API
- `GET /api/plants` - List all available plants
- `GET /api/plants/{plant_name}` - Get specific plant information
- `GET /api/plants/search?q={query}` - Search plants

### Garden Plans API  
- `POST /api/plans` - Generate garden plan
- `GET /api/plans/{plan_id}` - Get existing plan

### PDF API
- `GET /api/pdf/garden-plan/{plan_id}` - Download PDF
- `GET /api/pdf/health` - PDF service health check

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama3.1
```

**PDF Generation Error**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Install system dependencies (macOS)
brew install pango
```

**Plant Data Not Loading**
- Check `data/vegetables.json` exists and is valid JSON
- Verify file permissions
- Check application logs in `logs/`

**Database Connection Issues**
```bash
# Quick database health check
python scripts/quick_health_check.py

# Test database connection specifically
python scripts/test_db_integration.py

# Check if PostgreSQL is running (Docker)
docker ps | grep postgres

# Check if PostgreSQL is running (Native)
sudo systemctl status postgresql
```

**Database Setup Problems**
- Run the automated setup: `python scripts/setup_database_enhanced.py`
- Check the detailed guide: [Database Setup Guide](DATABASE_SETUP.md)
- Verify `.env` file has correct database settings
- Ensure database user has proper permissions

**Migration Errors**
```bash
# Reset and rerun migrations
alembic downgrade base
alembic upgrade head

# Check migration status
alembic current
alembic history
```

## 🚀 Deployment

### Production Deployment
1. Set environment variables for production
2. Use production WSGI server (Gunicorn recommended)
3. Configure reverse proxy (Nginx recommended)
4. Set up SSL certificate
5. Configure file permissions for PDF generation

```bash
# Production server with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format code (`black .`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Plant Data**: Compiled from various gardening resources and expert knowledge
- **LLM Integration**: Powered by Ollama and OpenAI
- **PDF Generation**: WeasyPrint for professional document creation
- **Web Framework**: FastAPI for high-performance API development

---

**Happy Gardening! 🌱🏡**

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/yourusername/JardAIn).

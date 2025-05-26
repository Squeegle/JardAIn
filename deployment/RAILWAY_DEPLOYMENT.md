# 🚀 JardAIn Garden Planner - Railway Deployment Guide

This guide walks you through deploying the JardAIn Garden Planner to Railway with OpenAI integration.

## 📋 Prerequisites

- [Railway CLI](https://docs.railway.app/develop/cli) installed
- OpenAI API key
- Git repository with your code

## 🛠️ Deployment Steps

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login and Initialize
```bash
railway login
railway init
```

### 3. Add Services
```bash
# Add PostgreSQL database
railway add --database postgres

# Add application service
railway add --service jardain-app

# Link to your application service
railway service jardain-app
```

### 4. Set Environment Variables
```bash
# Core application settings
railway variables --set "DEBUG=false"
railway variables --set "LLM_PROVIDER=openai"
railway variables --set "LOG_LEVEL=info"
railway variables --set "PYTHONPATH=/app"

# OpenAI configuration
railway variables --set "OPENAI_API_KEY=your_actual_openai_api_key_here"
railway variables --set "OPENAI_MODEL=gpt-3.5-turbo"
railway variables --set "OPENAI_MAX_TOKENS=2000"

# File paths (Railway-optimized)
railway variables --set "PLANT_DATA_PATH=/app/data/common_vegetables.json"
railway variables --set "GENERATED_PLANS_PATH=/tmp/generated_plans/"
railway variables --set "LOGS_PATH=/tmp/logs/"

# CORS origins (update after getting your Railway URL)
railway variables --set "ALLOWED_ORIGINS=[\"https://your-app.railway.app\"]"
```

### 5. Deploy
```bash
railway up
```

### 6. Get Your URL and Test
```bash
# Get deployment URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health

# Test API
curl https://your-app.railway.app/api/plants
```

## 🔧 Configuration Files

### Key Files for Railway Deployment

- **`railway.json`** - Railway configuration
- **`Dockerfile.railway`** - Production Docker container
- **`deployment/railway.env.template`** - Environment variables template
- **`deployment/railway_startup.sh`** - Production startup script

### WeasyPrint Dependencies

The `Dockerfile.railway` includes all necessary system dependencies for WeasyPrint:

- `libpango-1.0-0` - Text rendering
- `libcairo2` - Graphics rendering  
- `fontconfig` - Font management
- `fonts-dejavu-core` - Default fonts
- Additional graphics and XML libraries

## 🐛 Troubleshooting

### WeasyPrint Issues

If you see WeasyPrint errors:

1. **Check system dependencies** - The Dockerfile includes all required libraries
2. **Test PDF generation** - Run the WeasyPrint test:
   ```bash
   railway run python deployment/test_weasyprint.py
   ```
3. **Check logs** - View detailed error messages:
   ```bash
   railway logs --build
   ```

### Database Connection Issues

1. **Verify DATABASE_URL** - Railway automatically sets this
2. **Check database service** - Ensure PostgreSQL service is running
3. **Test connection**:
   ```bash
   railway connect postgres
   ```

### OpenAI API Issues

1. **Verify API key** - Check environment variables:
   ```bash
   railway variables
   ```
2. **Test API connection**:
   ```bash
   railway run python -c "
   import os
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('OpenAI client created successfully')
   "
   ```

### Build Failures

1. **Check build logs**:
   ```bash
   railway logs --build
   ```
2. **Verify Dockerfile** - Ensure all dependencies are correctly specified
3. **Check file permissions** - Ensure startup script is executable

## 📊 Monitoring and Maintenance

### View Logs
```bash
# Latest deployment logs
railway logs

# Build logs
railway logs --build

# Deployment logs
railway logs --deployment
```

### Check Status
```bash
# Project status
railway status

# Environment variables
railway variables

# Service information
railway service
```

### Redeploy
```bash
# Redeploy latest version
railway redeploy

# Deploy new changes
railway up
```

## 🔒 Security Considerations

1. **Environment Variables** - Never commit API keys to git
2. **Non-root User** - Dockerfile runs as non-root user `jardain`
3. **CORS Configuration** - Update `ALLOWED_ORIGINS` with your actual domain
4. **Health Checks** - Railway monitors `/health` endpoint

## 🌐 Custom Domains

To add a custom domain:

```bash
# Add custom domain
railway domain add yourdomain.com

# Update CORS origins
railway variables --set "ALLOWED_ORIGINS=[\"https://yourdomain.com\",\"https://your-app.railway.app\"]"
```

## 📈 Performance Optimization

### Production Settings

- **Debug Mode**: Disabled (`DEBUG=false`)
- **Workers**: Single worker for Railway's resource limits
- **Logging**: Info level for production
- **Health Checks**: 30-second intervals

### Resource Management

- **File Storage**: Uses `/tmp` for generated files
- **Database Pool**: Configured for Railway's connection limits
- **Memory**: Optimized for Railway's container limits

## 🆘 Support

If you encounter issues:

1. Check Railway's [documentation](https://docs.railway.app/)
2. Review deployment logs: `railway logs`
3. Test individual components using `railway run`
4. Check the health endpoint: `/health`

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `false` |
| `LLM_PROVIDER` | AI provider | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `DATABASE_URL` | PostgreSQL URL | Auto-set by Railway |
| `ALLOWED_ORIGINS` | CORS origins | `["https://app.railway.app"]` |
| `LOG_LEVEL` | Logging level | `info` |

## ✅ Deployment Checklist

- [ ] Railway CLI installed and logged in
- [ ] Project initialized with services
- [ ] Environment variables set
- [ ] OpenAI API key configured
- [ ] Application deployed (`railway up`)
- [ ] Health check passing
- [ ] API endpoints responding
- [ ] PDF generation working
- [ ] CORS origins updated
- [ ] Custom domain configured (optional)

---

🌱 **Happy Gardening with JardAIn!** 
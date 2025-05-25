# 🚀 JardAIn Production Deployment Guide

This guide covers multiple deployment options for the JardAIn Garden Planner application.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Domain name (for production)
- Database service (PostgreSQL)
- LLM API access (OpenAI or Ollama)

## 🎯 Deployment Options

### Option 1: Cloud Platform (Recommended)
**Best for**: Easy deployment, managed infrastructure, automatic scaling

**Supported Platforms**:
- [Railway](https://railway.app) - Simple, developer-friendly
- [Render](https://render.com) - Great free tier
- [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform) - Reliable, good pricing
- [Fly.io](https://fly.io) - Global edge deployment

### Option 2: VPS/Server
**Best for**: Full control, custom configurations, cost optimization

**Supported Providers**:
- DigitalOcean Droplets
- Linode
- AWS EC2
- Google Cloud Compute Engine

### Option 3: Local Docker
**Best for**: Development, testing, small-scale deployment

---

## 🐳 Quick Start with Docker

### 1. Clone and Setup
```bash
git clone <your-repo>
cd JardAIn

# Copy environment template
cp env.production .env
# Edit .env with your configuration
nano .env
```

### 2. Local Development
```bash
# Start development environment
./deploy.sh dev

# View logs
./deploy.sh logs

# Stop when done
./deploy.sh stop
```

### 3. Production Deployment
```bash
# Build and start production
./deploy.sh prod

# Check status
docker-compose ps

# View logs
./deploy.sh logs
```

---

## ☁️ Cloud Platform Deployment

### Railway Deployment

1. **Create Railway Account**: [railway.app](https://railway.app)

2. **Setup Database**:
   ```bash
   # In Railway dashboard
   # Add PostgreSQL service
   # Note the connection details
   ```

3. **Deploy Application**:
   ```bash
   # Connect GitHub repo to Railway
   # Set environment variables in Railway dashboard
   # Deploy automatically on push
   ```

4. **Environment Variables** (set in Railway dashboard):
   ```
   POSTGRES_HOST=<railway-postgres-host>
   POSTGRES_PORT=5432
   POSTGRES_DB=railway
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=<railway-postgres-password>
   OPENAI_API_KEY=<your-openai-key>
   LLM_PROVIDER=openai
   DEBUG=false
   ALLOWED_ORIGINS=https://your-app.railway.app
   ```

### Render Deployment

1. **Create Render Account**: [render.com](https://render.com)

2. **Setup Database**:
   ```yaml
   # Create PostgreSQL service in Render
   # Note the internal connection URL
   ```

3. **Create Web Service**:
   ```yaml
   # Connect GitHub repository
   # Build Command: docker build -t jardain .
   # Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables**:
   ```
   DATABASE_URL=<render-postgres-url>
   OPENAI_API_KEY=<your-openai-key>
   LLM_PROVIDER=openai
   DEBUG=false
   PORT=10000
   ```

### DigitalOcean App Platform

1. **Create DO Account**: [digitalocean.com](https://digitalocean.com)

2. **Setup Managed Database**:
   ```bash
   # Create PostgreSQL cluster
   # Note connection details
   ```

3. **Deploy App**:
   ```yaml
   # Create app from GitHub
   # Use Dockerfile for build
   # Set environment variables
   ```

---

## 🖥️ VPS/Server Deployment

### DigitalOcean Droplet Setup

1. **Create Droplet**:
   ```bash
   # Ubuntu 22.04 LTS
   # 2GB RAM minimum (4GB recommended)
   # Install Docker and Docker Compose
   ```

2. **Server Setup**:
   ```bash
   # SSH into server
   ssh root@your-server-ip

   # Update system
   apt update && apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   apt install docker-compose-plugin -y

   # Create app user
   useradd -m -s /bin/bash jardain
   usermod -aG docker jardain
   ```

3. **Deploy Application**:
   ```bash
   # Switch to app user
   su - jardain

   # Clone repository
   git clone <your-repo>
   cd JardAIn

   # Setup environment
   cp env.production .env
   nano .env  # Edit with your values

   # Deploy
   ./deploy.sh prod
   ```

4. **Setup Nginx (Optional)**:
   ```bash
   # Install Nginx on host
   sudo apt install nginx

   # Configure reverse proxy
   sudo nano /etc/nginx/sites-available/jardain

   # Enable site
   sudo ln -s /etc/nginx/sites-available/jardain /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **SSL Certificate**:
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx

   # Get certificate
   sudo certbot --nginx -d yourdomain.com
   ```

---

## 🗄️ Database Setup

### Managed Database Services

#### Neon (Recommended)
```bash
# 1. Create account at neon.tech
# 2. Create database
# 3. Get connection string
# 4. Add to .env:
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
```

#### Supabase
```bash
# 1. Create account at supabase.com
# 2. Create project
# 3. Get database URL from settings
# 4. Add to .env
```

#### Railway PostgreSQL
```bash
# 1. Add PostgreSQL service in Railway
# 2. Use provided connection details
# 3. Set individual variables or DATABASE_URL
```

### Self-Hosted Database
```bash
# Using Docker Compose (included in docker-compose.yml)
# Database will be created automatically
# Data persisted in Docker volume
```

---

## 🤖 LLM Configuration

### OpenAI Setup
```bash
# 1. Get API key from platform.openai.com
# 2. Add to .env:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### Ollama Setup (Self-hosted)
```bash
# 1. Install Ollama on server
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull model
ollama pull llama3.1

# 3. Configure in .env:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

---

## 🔧 Configuration

### Environment Variables

**Required**:
```bash
# Database
POSTGRES_HOST=your-db-host
POSTGRES_DB=jardain
POSTGRES_USER=jardain_user
POSTGRES_PASSWORD=secure-password

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key

# Security
ALLOWED_ORIGINS=https://yourdomain.com
```

**Optional**:
```bash
# Application
APP_NAME="JardAIn Garden Planner"
DEBUG=false
LOG_LEVEL=info

# Paths
PLANT_DATA_PATH=data/plants.json
GENERATED_PLANS_PATH=generated_plans
```

### Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **Database**: Use strong passwords, enable SSL
3. **API Keys**: Rotate regularly, use least privilege
4. **HTTPS**: Always use SSL in production
5. **Firewall**: Restrict access to necessary ports only

---

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://yourdomain.com/health

# Database connection
docker-compose exec postgres pg_isready

# View logs
./deploy.sh logs
```

### Backups
```bash
# Create backup
./deploy.sh backup

# Restore from backup
./deploy.sh restore backup_20240524_120000.sql
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy.sh stop
./deploy.sh prod
```

---

## 🚨 Troubleshooting

### Common Issues

**Database Connection Failed**:
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check environment variables
docker-compose exec app env | grep POSTGRES

# Check logs
docker-compose logs postgres
```

**Application Won't Start**:
```bash
# Check logs
./deploy.sh logs

# Check environment
docker-compose exec app env

# Rebuild image
./deploy.sh build --no-cache
```

**Out of Memory**:
```bash
# Check resource usage
docker stats

# Increase server resources
# Or optimize Docker memory limits
```

### Getting Help

1. Check application logs: `./deploy.sh logs`
2. Check health endpoint: `/health`
3. Verify environment variables
4. Check database connectivity
5. Review Docker container status: `docker-compose ps`

---

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 3
    # Add load balancer
```

### Vertical Scaling
```bash
# Increase server resources
# Update Docker memory limits
# Optimize database connections
```

### Performance Optimization
- Enable Redis caching
- Use CDN for static files
- Optimize database queries
- Implement connection pooling

---

## 🎉 Success!

Your JardAIn Garden Planner should now be running in production!

**Next Steps**:
1. Set up monitoring (Sentry, DataDog)
2. Configure automated backups
3. Set up CI/CD pipeline
4. Add custom domain and SSL
5. Monitor performance and scale as needed

**Useful URLs**:
- Application: `https://yourdomain.com`
- API Docs: `https://yourdomain.com/docs`
- Health Check: `https://yourdomain.com/health` 
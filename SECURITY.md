# 🔒 Security Guide for JardAIn

This document outlines security best practices and what information should be kept secure when setting up and running JardAIn.

## 🚨 Critical Security Information

### **Never Commit These to Version Control:**

1. **`.env` files** - Contains database passwords and API keys
2. **Database passwords** - Any real passwords used for PostgreSQL
3. **API keys** - OpenAI API keys, weather API keys, etc.
4. **SSL certificates and private keys**
5. **Production configuration files** with real credentials

### **Files That Are Safe to Commit:**

✅ `env.example` - Template with placeholder values  
✅ `env.docker.example` - Docker template with placeholders  
✅ `DATABASE_SETUP.md` - Documentation with example placeholders  
✅ `README.md` - Documentation with example placeholders  
✅ Configuration files with placeholder values  

## 🔐 Password and Secret Management

### **Database Passwords**

**✅ Secure Practices:**
- Use strong passwords (16+ characters)
- Include letters, numbers, and special characters
- Generate passwords programmatically when possible
- Use environment variables, never hardcode
- Rotate passwords regularly

**❌ Avoid:**
- Hardcoding passwords in files
- Using simple passwords like "password123"
- Reusing passwords across environments
- Committing passwords to version control

### **API Keys**

**✅ Secure Practices:**
- Store in environment variables only
- Use least-privilege access
- Rotate keys regularly
- Monitor usage and billing
- Use different keys for development/production

**❌ Avoid:**
- Hardcoding API keys in source code
- Sharing keys in documentation
- Using production keys in development
- Committing keys to version control

## 🛡️ Environment-Specific Security

### **Development Environment**

```bash
# ✅ Good - Use localhost and strong passwords
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=randomly_generated_secure_password

# ✅ Good - Use local LLM for development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# ❌ Avoid - Don't use production credentials in development
# OPENAI_API_KEY=production_key_here
```

### **Production Environment**

```bash
# ✅ Good - Use managed database services
POSTGRES_HOST=your-managed-db-host.com
POSTGRES_PASSWORD=very_strong_production_password

# ✅ Good - Use SSL connections
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require

# ✅ Good - Use production API keys
OPENAI_API_KEY=production_api_key_here
```

## 🔍 Security Checklist

### **Before Deployment:**

- [ ] All `.env` files are in `.gitignore`
- [ ] No hardcoded passwords in source code
- [ ] No real API keys in documentation
- [ ] Database uses strong passwords
- [ ] SSL/TLS enabled for database connections
- [ ] API keys have appropriate permissions
- [ ] Secrets are stored in environment variables
- [ ] Production and development environments are separate

### **Regular Maintenance:**

- [ ] Rotate database passwords quarterly
- [ ] Rotate API keys regularly
- [ ] Monitor API usage and costs
- [ ] Review access logs
- [ ] Update dependencies for security patches
- [ ] Backup database regularly
- [ ] Test disaster recovery procedures

## 🚀 Secure Setup Process

### **1. Initial Setup**

```bash
# Use the automated setup script (recommended)
python scripts/setup_database_enhanced.py

# This script will:
# ✅ Generate secure random passwords
# ✅ Create .env file with proper settings
# ✅ Never expose passwords in logs or output
```

### **2. Manual Setup**

```bash
# Generate secure password
openssl rand -base64 32

# Or use Python
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"

# Set in environment
export POSTGRES_PASSWORD="your_generated_password"
```

### **3. Docker Setup**

```bash
# Copy template and edit
cp env.docker.example .env

# Edit .env file and replace placeholders
# NEVER commit the .env file
echo ".env" >> .gitignore
```

## 🔧 Security Configuration

### **Database Security**

```bash
# ✅ Use SSL connections in production
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require

# ✅ Restrict database access
# Configure firewall rules to only allow application access
# Use database user with minimal required permissions
```

### **Application Security**

```bash
# ✅ Set secure origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ✅ Use HTTPS in production
# Configure SSL certificates
# Redirect HTTP to HTTPS
```

## 🚨 What to Do If Secrets Are Exposed

### **If you accidentally commit secrets:**

1. **Immediately rotate the exposed credentials**
2. **Remove from git history:**
   ```bash
   # Remove file from git history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/file' \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (be careful!)
   git push origin --force --all
   ```
3. **Update all environments with new credentials**
4. **Monitor for unauthorized usage**

### **If API keys are exposed:**

1. **Immediately revoke the exposed keys**
2. **Generate new API keys**
3. **Update all applications using the keys**
4. **Monitor billing and usage for anomalies**
5. **Review access logs**

## 📞 Security Resources

### **Password Generators:**
- [1Password Password Generator](https://1password.com/password-generator/)
- [Bitwarden Password Generator](https://bitwarden.com/password-generator/)
- Command line: `openssl rand -base64 32`

### **Secret Management Tools:**
- [HashiCorp Vault](https://www.vaultproject.io/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)

### **Security Scanning:**
- [GitGuardian](https://gitguardian.com/) - Scan for secrets in git repos
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Find secrets in git history
- [git-secrets](https://github.com/awslabs/git-secrets) - Prevent committing secrets

## 🎯 Quick Security Tips

1. **Use the automated setup script** - it generates secure passwords automatically
2. **Never commit `.env` files** - they contain sensitive information
3. **Use different credentials for development and production**
4. **Regularly rotate passwords and API keys**
5. **Monitor your API usage and billing**
6. **Use SSL/TLS for all database connections in production**
7. **Keep dependencies updated** for security patches
8. **Use managed database services** in production when possible

---

**Remember: Security is an ongoing process, not a one-time setup! 🔒**

For questions about security practices, consult your organization's security team or refer to industry best practices like [OWASP](https://owasp.org/). 
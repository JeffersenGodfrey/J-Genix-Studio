# 🚀 ProductAI Pro - Production Deployment Guide

## Phase 1: Streamlit Cloud Deployment (MVP)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- Domain name (optional)

### Step 1: Prepare Repository
```bash
# 1. Create GitHub repository
git init
git add .
git commit -m "Initial ProductAI Pro release"
git remote add origin https://github.com/yourusername/productai-pro.git
git push -u origin main

# 2. Create production requirements.txt
echo "streamlit>=1.32.0
requests>=2.31.0
python-dotenv>=1.0.1
Pillow>=10.2.0
streamlit-drawable-canvas>=0.9.3
numpy>=1.24.3
pandas>=2.0.0
aiohttp>=3.8.0" > requirements.txt
```

### Step 2: Environment Configuration
```bash
# Create .streamlit/config.toml
mkdir .streamlit
cat > .streamlit/config.toml << EOF
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#2c3e50"
font = "sans serif"
EOF

# Create .streamlit/secrets.toml (for production secrets)
cat > .streamlit/secrets.toml << EOF
# Add your production secrets here
BRIA_API_KEY = "your_production_api_key"
DATABASE_URL = "your_database_url"
ADMIN_PASSWORD = "your_admin_password"
EOF
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Connect your GitHub account
3. Select your repository
4. Set main file path: `app.py`
5. Add secrets in the Streamlit Cloud dashboard
6. Deploy!

### Step 4: Custom Domain Setup
```bash
# 1. Purchase domain (recommended: productaipro.com)
# 2. In Streamlit Cloud settings, add custom domain
# 3. Update DNS records:
#    CNAME: www.productaipro.com → your-app.streamlit.app
#    A: productaipro.com → Streamlit Cloud IP
```

## Phase 2: Railway Deployment (Scaling)

### Step 1: Railway Setup
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and create project
railway login
railway init
railway link
```

### Step 2: Create Production Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 3: Railway Configuration
```bash
# railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 4: Environment Variables
```bash
# Set production environment variables
railway variables set BRIA_API_KEY=your_production_key
railway variables set ENVIRONMENT=production
railway variables set DATABASE_URL=your_database_url
```

### Step 5: Deploy
```bash
railway up
```

## Phase 3: DigitalOcean App Platform (Enterprise)

### Step 1: App Specification
```yaml
# .do/app.yaml
name: j-genix-studio
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/j-genix-studio
    branch: main
  run_command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 8501
  health_check:
    http_path: /_stcore/health
  envs:
  - key: BRIA_API_KEY
    scope: RUN_TIME
    type: SECRET
  - key: ENVIRONMENT
    value: production
    scope: RUN_TIME
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET

databases:
- name: j-genix-db
  engine: PG
  version: "13"
  size: basic-xs

static_sites:
- name: j-genix-docs
  source_dir: /docs
  github:
    repo: yourusername/j-genix-studio-docs
    branch: main
```

### Step 2: Database Setup
```python
# database/init.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def init_database():
    """Initialize production database"""
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
    
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            subscription_tier VARCHAR(50) DEFAULT 'starter',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            prompt TEXT,
            image_url TEXT,
            generation_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_time FLOAT
        )
    ''')
    
    conn.commit()
    conn.close()
```

## Security & Production Considerations

### 1. API Key Management
```python
# utils/security.py
import os
import hashlib
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        if self.cipher:
            return self.cipher.encrypt(api_key.encode()).decode()
        return api_key
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        if self.cipher:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        return encrypted_key
```

### 2. Rate Limiting
```python
# utils/rate_limiting.py
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [req_time for req_time in user_requests 
                           if now - req_time < self.window_seconds]
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
```

### 3. Monitoring & Logging
```python
# utils/monitoring.py
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_generation(user_id: str, prompt: str, success: bool, processing_time: float):
    """Log image generation events"""
    logger.info(f"Generation - User: {user_id}, Success: {success}, Time: {processing_time}s")
    
    # Send to monitoring service (e.g., DataDog, New Relic)
    if os.getenv('MONITORING_ENABLED'):
        # Implementation for your monitoring service
        pass
```

## SSL Certificate & Domain Setup

### 1. Custom Domain Configuration
```bash
# 1. Purchase domain (e.g., productaipro.com)
# 2. Configure DNS records:
#    A record: @ → your_server_ip
#    CNAME: www → productaipro.com
#    CNAME: api → productaipro.com

# 3. SSL Certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d productaipro.com -d www.productaipro.com
```

### 2. Nginx Configuration
```nginx
# /etc/nginx/sites-available/productaipro
server {
    listen 80;
    server_name productaipro.com www.productaipro.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name productaipro.com www.productaipro.com;
    
    ssl_certificate /etc/letsencrypt/live/productaipro.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/productaipro.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Deployment Checklist

### Pre-Deployment
- [ ] Code review completed
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] SSL certificates ready
- [ ] Domain DNS configured

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] User acceptance testing
- [ ] Performance monitoring active
- [ ] Backup verification
- [ ] Documentation updated
- [ ] Team notified of deployment

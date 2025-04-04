# Advogada Parceira - Deployment Documentation

This document provides comprehensive instructions for deploying the Advogada Parceira application in a production environment.

## Architecture Overview

The application consists of two main components:

1. **Frontend**: React application (deployed at http://app.advogadaparceira.com.br)
2. **Backend**: FastAPI Python application (deployed at http://api.advogadaparceira.com.br)

## Server Requirements

- Ubuntu server (tested on Ubuntu 24.04 LTS)
- Nginx web server
- Node.js (for frontend)
- Python 3.10+ (for backend)
- Git

## Initial Server Setup

1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install Node.js and npm (if not already installed):
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   source ~/.nvm/nvm.sh
   nvm install --lts
   nvm use --lts
   ```

3. Install Python and dependencies:
   ```bash
   sudo apt install -y python3 python3-venv python3-pip python3-dev
   sudo apt install -y postgresql postgresql-contrib libpq-dev
   ```

4. Install Nginx:
   ```bash
   sudo apt install -y nginx
   ```

## Frontend Deployment

### Setup Nginx Configuration

Create a new Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/ap-frontend
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name app.advogadaparceira.com.br;
    
    root /home/ubuntu/ap-frontend-deploy;
    index index.html;
    
    # Serve static files directly and with proper cache headers
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
        access_log off;
        try_files $uri =404;
    }
    
    # For all other routes, serve index.html for client-side routing to handle
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Limit request size
    client_max_body_size 10M;
    
    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Logs
    access_log /var/log/nginx/ap-frontend-access.log;
    error_log /var/log/nginx/ap-frontend-error.log;
}
```

Enable the site:

```bash
sudo ln -sf /etc/nginx/sites-available/ap-frontend /etc/nginx/sites-enabled/
```

### Frontend Deployment Script

Create the frontend deployment script:

```bash
nano ~/frontend_deploy.sh
```

Add the following content:

```bash
#!/bin/bash
set -e
echo "FRONTEND DEPLOYMENT - HIGH QUALITY"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
DEPLOY_DIR="/home/ubuntu/ap-frontend-deploy"
REPO_DIR="/home/ubuntu/ap-frontend-repo"
mkdir -p $DEPLOY_DIR
if [ -d "$REPO_DIR/.git" ]; then
    cd $REPO_DIR
    git pull
else
    rm -rf $REPO_DIR
    git clone https://github.com/gregoryoliveiraa/ap-frontend.git $REPO_DIR
    cd $REPO_DIR
fi
cat > $REPO_DIR/.env << EOL
REACT_APP_API_URL=http://api.advogadaparceira.com.br
REACT_APP_ENV=production
EOL
npm install
npm run build
rm -rf $DEPLOY_DIR/*
cp -r build/* $DEPLOY_DIR/
sudo chown -R www-data:www-data $DEPLOY_DIR
sudo chmod -R 755 $DEPLOY_DIR
sudo ln -sf /etc/nginx/sites-available/ap-frontend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
echo "Frontend deployment completed successfully!"
echo "Website is now available at: http://app.advogadaparceira.com.br"
```

Make the script executable:

```bash
chmod +x ~/frontend_deploy.sh
```

## Backend Deployment

### Setup Nginx Configuration

Create a new Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/ap-backend.conf
```

Add the following configuration:

```nginx
server { 
    listen 80; 
    server_name api.advogadaparceira.com.br; 
    
    location / { 
        proxy_pass http://localhost:8080; 
        proxy_set_header Host $host; 
        proxy_set_header X-Real-IP $remote_addr; 
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
        proxy_set_header X-Forwarded-Proto $scheme; 
    } 
}
```

Enable the site:

```bash
sudo ln -sf /etc/nginx/sites-available/ap-backend.conf /etc/nginx/sites-enabled/
```

### Backend Deployment Script

Create the backend deployment script:

```bash
nano ~/backend_deploy.sh
```

Add the following content:

```bash
#!/bin/bash
set -e
echo "BACKEND DEPLOYMENT - HIGH QUALITY"
DEPLOY_DIR="/home/ubuntu/ap-backend-deploy"
REPO_DIR="/home/ubuntu/ap-backend-repo"
mkdir -p $DEPLOY_DIR
if [ -d "$REPO_DIR/.git" ]; then
    cd $REPO_DIR
    git pull
else
    rm -rf $REPO_DIR
    git clone https://github.com/gregoryoliveiraa/ap-backend.git $REPO_DIR
    cd $REPO_DIR
fi
rm -rf $DEPLOY_DIR/*
cp -r $REPO_DIR/* $DEPLOY_DIR/
cd $DEPLOY_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cat > .env << EOL
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=e2d0f9e5ae3e40988e6c75e5bdadba5e
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your_api_key_here
EOL
python -m alembic upgrade head || true
pkill -f "uvicorn app:app" || true
nohup python -m uvicorn app:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
echo "Backend deployment completed successfully!"
echo "API is now available at: http://api.advogadaparceira.com.br"
```

Make the script executable:

```bash
chmod +x ~/backend_deploy.sh
```

### Backend Health Check Script

Create a health check script to monitor and automatically restart the backend if needed:

```bash
nano ~/backend_health_check.sh
```

Add the following content:

```bash
#!/bin/bash
if ! curl -s http://localhost:8080/ > /dev/null; then
  cd /home/ubuntu/ap-backend-deploy
  source venv/bin/activate
  pkill -f "uvicorn app:app" || true
  nohup python -m uvicorn app:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
  echo "Backend service restarted at $(date)" >> /home/ubuntu/backend_restart.log
fi
```

Make the script executable:

```bash
chmod +x ~/backend_health_check.sh
```

Add to crontab to run every 5 minutes:

```bash
(crontab -l 2>/dev/null | grep -v "backend_health_check.sh" ; echo "*/5 * * * * /home/ubuntu/backend_health_check.sh > /dev/null 2>&1") | crontab -
```

## Running the Deployments

### Deploy Frontend

```bash
cd /home/ubuntu
./frontend_deploy.sh
```

### Deploy Backend

```bash
cd /home/ubuntu
./backend_deploy.sh
```

## Troubleshooting

### Common Issues

1. **Permission Denied in Nginx Logs**
   - Solution: Make sure the Nginx user has access to the deployment directories
   ```bash
   sudo chown -R www-data:www-data /home/ubuntu/ap-frontend-deploy
   sudo chmod -R 755 /home/ubuntu/ap-frontend-deploy
   sudo chmod 755 /home/ubuntu  # Allow Nginx to traverse the directory
   ```

2. **Backend Not Starting**
   - Check the app.log file:
   ```bash
   cat /home/ubuntu/ap-backend-deploy/app.log
   ```

3. **Frontend Not Loading**
   - Check the Nginx error logs:
   ```bash
   sudo tail -50 /var/log/nginx/ap-frontend-error.log
   ```

## Monitoring

Health check scripts run every 5 minutes to ensure both services are running:
- Backend: `/home/ubuntu/backend_health_check.sh`

## Logs

- Backend deployment log: `/home/ubuntu/backend_restart.log`
- Backend application log: `/home/ubuntu/ap-backend-deploy/app.log`
- Nginx access logs: `/var/log/nginx/ap-frontend-access.log` and `/var/log/nginx/ap-backend-access.log`
- Nginx error logs: `/var/log/nginx/ap-frontend-error.log` and `/var/log/nginx/ap-backend-error.log`

## Security Considerations

- This documentation uses some default/example keys and secrets. In a real production environment, replace these with secure, randomly generated values.
- Consider implementing HTTPS with Let's Encrypt for secure connections.
- Regularly update the server and dependencies to patch security vulnerabilities. 
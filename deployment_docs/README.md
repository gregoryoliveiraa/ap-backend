# Advogada Parceira Deployment Documentation

This directory contains all the documentation and scripts needed to deploy the Advogada Parceira application in a production environment.

## Files Included

- `DEPLOYMENT.md` - Complete deployment guide with step-by-step instructions
- `frontend_deploy.sh` - Script to deploy the frontend application
- `backend_deploy.sh` - Script to deploy the backend application  
- `backend_health_check.sh` - Health check script for the backend
- `nginx_ap-frontend` - Nginx configuration for the frontend
- `nginx_ap-backend.conf` - Nginx configuration for the backend API

## Quick Start

1. Set up your server with required dependencies (see DEPLOYMENT.md)
2. Copy the Nginx configuration files to `/etc/nginx/sites-available/`
3. Copy the deployment scripts to your home directory
4. Run the deployment scripts:
   ```bash
   ./frontend_deploy.sh
   ./backend_deploy.sh
   ```

See `DEPLOYMENT.md` for full instructions and troubleshooting information. 
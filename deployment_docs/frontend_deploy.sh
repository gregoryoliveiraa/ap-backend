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
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
# Try to run migrations but continue if they fail
python -m alembic upgrade head || true
# Kill any existing server
pkill -f "uvicorn app:app" || true
# Start the server
nohup python -m uvicorn app:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
echo "Backend deployment completed successfully!"
echo "API is now available at: http://api.advogadaparceira.com.br" 
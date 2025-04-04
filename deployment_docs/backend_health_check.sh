#!/bin/bash
if ! curl -s http://localhost:8080/ > /dev/null; then
  cd /home/ubuntu/ap-backend-deploy
  source venv/bin/activate
  pkill -f "uvicorn app:app" || true
  nohup python -m uvicorn app:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
  echo "Backend service restarted at $(date)" >> /home/ubuntu/backend_restart.log
fi 
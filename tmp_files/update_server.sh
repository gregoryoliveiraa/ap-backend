#!/bin/bash

# Substituir o modelo document.py
cp /home/ubuntu/updated_files/document.py /home/ubuntu/ap-backend/app/models/document.py

# Verificar se houve mudanças
diff /home/ubuntu/updated_files/document.py /home/ubuntu/ap-backend/app/models/document.py

# Reiniciar o servidor API
cd /home/ubuntu/ap-backend
source venv/bin/activate
pkill -f "uvicorn app.main:app" || echo "No uvicorn process running"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
echo "Server restarted!" 
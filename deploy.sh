#!/bin/bash

# Saindo em caso de erro
set -e

echo "=============================================="
echo "Iniciando deploy da API AP-Backend"
echo "=============================================="

# Configurações
APP_DIR=$(pwd)
LOG_FILE="$APP_DIR/api.log"
PORT=${API_PORT:-8080}
HOST=${API_HOST:-0.0.0.0}

# Verificar ambiente
echo "Verificando ambiente..."
if [ -z "$DATABASE_URL" ]; then
    echo "AVISO: Variável DATABASE_URL não definida. Usando sqlite local."
    export DATABASE_URL="sqlite:///./app.db"
fi

# Garantir que o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Ambiente virtual não encontrado. Executando setup..."
    bash setup.sh
else
    echo "Ambiente virtual encontrado."
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar dependências
echo "Atualizando dependências..."
pip install -r requirements.txt

# Inicializar banco de dados (se necessário)
if [ ! -f "app.db" ]; then
    echo "Inicializando banco de dados..."
    python init_db.py
else
    echo "Banco de dados já existe."
fi

# Executar migrações
echo "Executando migrações..."
alembic upgrade heads || echo "AVISO: Erro nas migrações. Verifique se o esquema do banco é compatível."

# Parar instâncias anteriores
echo "Parando instâncias anteriores..."
pkill -f "uvicorn app.main:app" || echo "Nenhuma instância anterior encontrada."

# Configurar Nginx
echo "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/ap-backend.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name api.advogadaparceira.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.advogadaparceira.com.br;
    
    ssl_certificate /etc/letsencrypt/live/api.advogadaparceira.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.advogadaparceira.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for long-running API requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://app.advogadaparceira.com.br' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://app.advogadaparceira.com.br' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
    
    # Logs
    access_log /var/log/nginx/ap-backend-access.log;
    error_log /var/log/nginx/ap-backend-error.log;
}
EOF

# Enable the site if not already enabled
if [ ! -f "/etc/nginx/sites-enabled/ap-backend.conf" ]; then
    echo "Habilitando site no Nginx..."
    sudo ln -s /etc/nginx/sites-available/ap-backend.conf /etc/nginx/sites-enabled/
fi

# Test nginx configuration
echo "Testando configuração do Nginx..."
sudo nginx -t

# Reload nginx
echo "Recarregando Nginx..."
sudo systemctl reload nginx

# Iniciar o servidor
echo "Iniciando o servidor API..."
nohup uvicorn app.main:app --host $HOST --port $PORT > $LOG_FILE 2>&1 &

# Verificar se o servidor iniciou
sleep 3
if curl -s http://$HOST:$PORT > /dev/null; then
    echo "=============================================="
    echo "API iniciada com sucesso!"
    echo "Executando em: http://$HOST:$PORT"
    echo "Logs em: $LOG_FILE"
    echo "=============================================="
else
    echo "ERRO: Falha ao iniciar a API. Verifique os logs em $LOG_FILE"
    exit 1
fi

# Adicionar verificação de saúde (health check)
echo "#!/bin/bash

API_STATUS=\$(curl -s -o /dev/null -w \"%{http_code}\" http://$HOST:$PORT)

if [ \"\$API_STATUS\" != \"200\" ]; then
    echo \"\$(date) - API não está respondendo. Reiniciando...\" >> $APP_DIR/api_restart.log
    pkill -f \"uvicorn app.main:app\"
    cd $APP_DIR
    source venv/bin/activate
    nohup uvicorn app.main:app --host $HOST --port $PORT > $LOG_FILE 2>&1 &
    echo \"\$(date) - API reiniciada.\" >> $APP_DIR/api_restart.log
fi" > health_check.sh

chmod +x health_check.sh

# Configurar cron para verificação de saúde
echo "Configurando verificação de saúde a cada 5 minutos..."
(crontab -l 2>/dev/null | grep -v "$APP_DIR/health_check.sh"; echo "*/5 * * * * $APP_DIR/health_check.sh") | crontab -

echo "Configuração da verificação de saúde concluída." 
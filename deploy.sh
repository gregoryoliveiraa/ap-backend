#!/bin/bash

# Saindo em caso de erro
set -e

echo "=============================================="
echo "Iniciando deploy da API AP-Backend"
echo "=============================================="

# Configurações
APP_DIR=$(pwd)
LOG_FILE="$APP_DIR/api.log"
PORT=${API_PORT:-8000}
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
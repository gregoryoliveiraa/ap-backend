#!/bin/bash

# Saindo em caso de erro
set -e

echo "=============================================="
echo "Configuração do ambiente para AP-Backend"
echo "=============================================="

# Verificar se o Python 3 está instalado
if ! command -v python3 &>/dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3."
    exit 1
fi

echo "Criando ambiente virtual..."
# Remover ambiente virtual existente, se houver
if [ -d "venv" ]; then
    echo "Removendo ambiente virtual existente..."
    rm -rf venv
fi

# Criar novo ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Criar arquivo .env a partir do exemplo, se necessário
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env com suas configurações."
else
    echo "Arquivo .env já existe. Mantendo configurações existentes."
fi

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python init_db.py

# Executar migrações
echo "Executando migrações..."
alembic upgrade heads || echo "AVISO: Erro nas migrações. Verifique se o esquema do banco é compatível."

echo "=============================================="
echo "Configuração concluída com sucesso!"
echo "Para iniciar o servidor, execute:"
echo "source venv/bin/activate && uvicorn app.main:app --reload"
echo "==============================================" 
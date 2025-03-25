#!/bin/bash

# Script para executar o backend da Advogada Parceira com SQLite

# Verifica se o ambiente virtual existe, se não, cria
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
fi

# Ativa o ambiente virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Não foi possível encontrar o script de ativação do ambiente virtual!"
    exit 1
fi

# Instala as dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Configura o banco de dados SQLite
echo "Configurando o banco de dados SQLite..."
python scripts/init_db_sqlite.py

# Exporta variável de ambiente para usar SQLite
export USE_SQLITE=True

# Inicia a aplicação
echo "Iniciando a aplicação com SQLite..."
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Desativa o ambiente virtual ao sair
deactivate
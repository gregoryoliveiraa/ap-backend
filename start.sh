#!/bin/bash
# Script melhorado para iniciar a aplicação Advogada Parceira

# Encontrar o Python instalado no sistema
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado! Por favor, instale o Python 3.9 ou superior."
    exit 1
fi

# Imprime a versão do Python que será usada
echo "🐍 Usando Python: $($PYTHON_CMD --version)"

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao criar o ambiente virtual. Verifique se o módulo venv está instalado."
        exit 1
    fi
fi

# Determina o caminho do ativador do ambiente virtual
if [ -f "venv/bin/activate" ]; then
    ACTIVATE_SCRIPT="venv/bin/activate"
elif [ -f "venv/Scripts/activate" ]; then
    ACTIVATE_SCRIPT="venv/Scripts/activate"
else
    echo "❌ Não foi possível encontrar o script de ativação do ambiente virtual!"
    exit 1
fi

echo "🔄 Ativando ambiente virtual: $ACTIVATE_SCRIPT"
source $ACTIVATE_SCRIPT

# Agora, com o ambiente virtual ativado, verifica os comandos
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado no ambiente virtual! Algo deu errado na criação do ambiente."
    exit 1
fi

echo "🔧 Instalando dependências..."
pip install -r requirements.txt

# Instala o validador de email (dependência específica identificada)
echo "🔧 Instalando o validador de email..."
pip install "pydantic[email]"

# Configura o banco de dados SQLite
echo "🗃️ Configurando o banco de dados SQLite..."
python scripts/init_db_sqlite.py

# Exporta variável de ambiente para usar SQLite
export USE_SQLITE=True

# Verifica se uvicorn está instalado
if ! command -v uvicorn &> /dev/null; then
    echo "🔧 Instalando uvicorn..."
    pip install uvicorn
fi

# Inicia a aplicação
echo "🚀 Iniciando a aplicação com SQLite..."
cd app || cd backend/app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Se chegou aqui, algo deu errado com o uvicorn
if [ $? -ne 0 ]; then
    echo "❌ Falha ao iniciar o servidor uvicorn. Tentando método alternativo..."
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi

# O script não deve chegar aqui normalmente, pois o uvicorn mantém o processo em execução
echo "⚠️ O servidor foi encerrado."

# Desativa o ambiente virtual ao sair
deactivate
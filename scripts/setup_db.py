#!/usr/bin/env python3
"""
Script para configurar e testar a conexão com PostgreSQL
"""
import psycopg2
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório pai ao path para importar a aplicação
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
print(f"Adicionando ao path: {parent_dir}")

# Carrega variáveis de ambiente
load_dotenv()

def setup_postgres():
    """Configura e testa a conexão com PostgreSQL"""
    # Use um usuário sem senha primeiro, que é comum em desenvolvimento local
    db_user = os.getenv("DB_USER", os.getenv("USER", "postgres"))
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = "advogada_parceira"
    
    # URL para conectar ao banco de dados postgres (padrão)
    postgres_url = f"postgresql://{db_user}@{db_host}:{db_port}/postgres"
    
    print(f"Tentando conectar ao PostgreSQL: {postgres_url}")
    
    try:
        # Conecta ao banco padrão 'postgres' primeiro
        conn = psycopg2.connect(postgres_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verifica se o banco de dados já existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Criando banco de dados '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Banco de dados '{db_name}' criado com sucesso!")
        else:
            print(f"Banco de dados '{db_name}' já existe.")
        
        # Fecha a conexão com 'postgres'
        cursor.close()
        conn.close()
        
        # Agora conecta ao banco de dados do projeto
        app_db_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
        print(f"Conectando ao banco de dados do projeto: {app_db_url}")
        
        # Escreve a URL no arquivo .env
        env_path = os.path.join(parent_dir, '.env')
        
        # Lê o arquivo .env existente
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Substitui ou adiciona a variável DATABASE_URL
        if "DATABASE_URL=" in env_content:
            # Substitui a linha existente
            lines = env_content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("DATABASE_URL="):
                    new_lines.append(f"DATABASE_URL={app_db_url}")
                else:
                    new_lines.append(line)
            env_content = '\n'.join(new_lines)
        else:
            # Adiciona a variável no final do arquivo
            env_content += f"\nDATABASE_URL={app_db_url}\n"
        
        # Escreve o arquivo atualizado
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"Arquivo .env atualizado com a URL do banco de dados: {app_db_url}")
        print("\nAgora você pode executar o script de inicialização do banco de dados:")
        print("python scripts/init_db.py")
        
        return True
        
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        print("\nVerifique se:")
        print("1. O PostgreSQL está instalado e em execução")
        print("2. As credenciais estão corretas")
        print("3. Você tem permissão para criar bancos de dados")
        
        return False

if __name__ == "__main__":
    print("Configurando conexão com PostgreSQL...")
    setup_postgres()
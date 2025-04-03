#!/usr/bin/env python3
"""
Script para importar os modelos de petições do arquivo CSV para o banco de dados.
Este script melhora a performance do sistema ao permitir acesso mais rápido aos templates.
"""

import os
import sys
import csv
import uuid
import json
import logging
import sqlite3
from datetime import datetime

# Adiciona o diretório raiz ao path para poder importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Aumenta o limite de tamanho do campo CSV
csv.field_size_limit(1024 * 1024)  # Aumenta para 1MB

# Caminho para o arquivo CSV
CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'peticoes.csv')

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')

def setup_database():
    """Configura a conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_existing_templates(conn):
    """Verifica se já existem templates no banco de dados e pergunta se o usuário quer limpar."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM templates")
    count = cursor.fetchone()[0]
    
    if count > 0:
        logging.info(f"Já existem {count} templates no banco de dados.")
        response = input("Deseja limpar os templates existentes? (s/N): ").strip().lower()
        if response == 's':
            cursor.execute("DELETE FROM templates")
            conn.commit()
            logging.info("Templates existentes foram removidos.")
            return True
    return False

def import_templates():
    """Importa os templates do arquivo CSV para o banco de dados."""
    if not os.path.exists(CSV_FILE):
        logging.error(f"Arquivo CSV não encontrado: {CSV_FILE}")
        return False
    
    conn = setup_database()
    check_existing_templates(conn)
    cursor = conn.cursor()
    
    count = 0
    errors = 0
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for i, row in enumerate(reader, start=1):
                try:
                    # Extrai os campos do CSV seguindo a estrutura vista
                    content = row.get('text', '') 
                    name = row.get('document_name', '')
                    category = row.get('subfolder_1', '')
                    doc_type = row.get('subfolder_2', '')
                    
                    # Verifica se tem conteúdo e nome
                    if not content or not name:
                        logging.warning(f"Linha {i}: Conteúdo ou nome vazio, pulando.")
                        continue
                    
                    # Garante que sejam strings
                    content = str(content) if content is not None else ""
                    name = str(name) if name is not None else ""
                    category = str(category) if category is not None else "Geral"
                    doc_type = str(doc_type) if doc_type is not None else "Outros"
                    
                    # Gera um ID único
                    template_id = str(uuid.uuid4())
                    
                    # Gera descrição
                    description = f"Template de {doc_type if doc_type else category}"
                    
                    # Inicializa as variáveis como um objeto vazio
                    variables = json.dumps({})
                    
                    # Timestamp atual
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Insere no banco de dados
                    cursor.execute(
                        """INSERT INTO templates 
                           (id, name, description, content, category, type, is_premium, variables, created_at, updated_at) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (template_id, name, description, content, category, doc_type, 0, variables, now, now)
                    )
                    
                    count += 1
                    if count % 100 == 0:
                        conn.commit()
                        logging.info(f"Importados {count} templates...")
                
                except Exception as e:
                    errors += 1
                    logging.error(f"Erro ao processar linha {i}: {str(e)}")
            
            conn.commit()
            logging.info(f"Importação concluída. Total de templates importados: {count}")
            if errors > 0:
                logging.warning(f"Ocorreram {errors} erros durante a importação.")
    
    except Exception as e:
        logging.error(f"Erro ao abrir ou processar o arquivo CSV: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    import_templates() 
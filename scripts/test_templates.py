#!/usr/bin/env python3
"""
Script para testar templates e variáveis no banco de dados.
"""

import os
import sys
import json
import sqlite3
import logging
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Adiciona o diretório raiz ao path para poder importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')

def setup_database():
    """Configura a conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def test_template_variables():
    """Testa a extração de variáveis dos templates."""
    conn = setup_database()
    cursor = conn.cursor()
    
    # Conta o total de templates no banco de dados
    cursor.execute("SELECT COUNT(*) FROM templates")
    total = cursor.fetchone()[0]
    logging.info(f"Total de templates no banco de dados: {total}")
    
    # Verifica quantos templates têm variáveis
    cursor.execute("SELECT COUNT(*) FROM templates WHERE variables IS NOT NULL AND variables != ''")
    with_vars = cursor.fetchone()[0]
    logging.info(f"Templates com variáveis: {with_vars}")
    
    # Seleciona alguns templates para análise
    cursor.execute("SELECT id, name, category, content, variables FROM templates LIMIT 5")
    templates = cursor.fetchall()
    
    for template in templates:
        template_id = template['id']
        name = template['name']
        content = template['content']
        variables_raw = template['variables']
        
        logging.info(f"\nAnalisando template: {name} (ID: {template_id})")
        
        # Extrai variáveis do conteúdo usando regex
        extracted_vars = []
        matches = re.findall(r'\[([^\]]+)\]', content)
        for var in matches:
            if var not in extracted_vars:
                extracted_vars.append(var)
        
        # Variáveis armazenadas no banco
        stored_vars = []
        if variables_raw and variables_raw.strip():
            try:
                stored_vars = json.loads(variables_raw)
            except json.JSONDecodeError:
                logging.error(f"Erro ao decodificar variáveis para o template {name}")
        
        logging.info(f"Variáveis extraídas do conteúdo: {extracted_vars}")
        logging.info(f"Variáveis armazenadas no banco: {stored_vars}")
        
        # Verifica se as variáveis armazenadas correspondem às extraídas
        missing_vars = [v for v in extracted_vars if v not in stored_vars]
        extra_vars = [v for v in stored_vars if v not in extracted_vars]
        
        if missing_vars:
            logging.warning(f"Variáveis no conteúdo mas não armazenadas: {missing_vars}")
        if extra_vars:
            logging.warning(f"Variáveis armazenadas mas não no conteúdo: {extra_vars}")
    
    conn.close()

if __name__ == "__main__":
    test_template_variables() 
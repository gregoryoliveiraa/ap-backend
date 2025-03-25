#!/usr/bin/env python3
"""
Script para verificar a estrutura de diretórios do projeto
"""
import os
import sys
from pathlib import Path

# Obtém o diretório raiz do projeto
project_root = Path(__file__).resolve().parent
print(f"Diretório raiz do projeto: {project_root}")

# Verifica caminhos importantes
paths_to_check = [
    "app",
    "app/models",
    "app/core",
    "app/api",
    "app/services",
    "app/schemas",
    "scripts"
]

for path in paths_to_check:
    full_path = project_root / path
    exists = full_path.exists()
    print(f"Verificando {path}: {'✅ Existe' if exists else '❌ Não existe'}")
    
    if exists and full_path.is_dir():
        print(f"  Arquivos em {path}:")
        for file in full_path.iterdir():
            if file.is_file():
                print(f"    - {file.name}")

# Verifica especificamente os modelos SQLite
sqlite_models = [
    "app/models/user_sqlite.py",
    "app/models/document_sqlite.py", 
    "app/models/chat_sqlite.py"
]

print("\nVerificando modelos SQLite:")
for model in sqlite_models:
    full_path = project_root / model
    exists = full_path.exists()
    print(f"Verificando {model}: {'✅ Existe' if exists else '❌ Não existe'}")
    
    if exists:
        # Verifica o conteúdo do arquivo
        print(f"  Primeiras linhas de {model}:")
        with open(full_path, 'r') as f:
            lines = f.readlines()[:5]  # Primeiras 5 linhas
            for line in lines:
                print(f"    {line.strip()}")

print("\nCaminhos no Python path:")
for path in sys.path:
    print(f"  - {path}")
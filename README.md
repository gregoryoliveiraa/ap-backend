# AP-Backend

**Versão atual:** 2.1.8

Backend API service for the Advogada Parceira platform. This service provides endpoints for managing legal documents, templates, and user authentication.

## Features

* User authentication using JWT tokens
* Document management (creation, retrieval, updating)
* Template management with variable extraction
* AI-powered assistants for legal document generation
* User management and permissions

## Requisitos

* Python 3.9+
* SQLite (desenvolvimento local) ou PostgreSQL (produção)
* Ambiente virtual Python (venv)

## Instalação Rápida

Para configurar o ambiente de desenvolvimento rapidamente, use o script de setup:

```bash
# Clone o repositório
git clone https://github.com/gregoryoliveiraa/ap-backend.git
cd ap-backend

# Execute o script de setup (cria ambiente virtual e instala dependências)
chmod +x setup.sh
./setup.sh
```

O script `setup.sh` automatiza:
- Criação do ambiente virtual
- Instalação de dependências
- Criação do arquivo .env a partir do template
- Inicialização do banco de dados
- Execução de migrações

## Configuração Manual

Se preferir fazer a configuração manualmente:

```bash
# Clone o repositório
git clone https://github.com/gregoryoliveiraa/ap-backend.git
cd ap-backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Inicializar banco de dados
python init_db.py

# Executar migrações
alembic upgrade heads
```

## Iniciar o Servidor

Para iniciar o servidor localmente:

```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Iniciar servidor com recarregamento automático
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`. A documentação da API está em `http://localhost:8000/docs`.

## Criar Usuário Administrador

Para criar um usuário administrador:

```bash
python create_admin.py --email admin@example.com --password senha123 --nome "Administrador"
```

## Verificar Usuários

Para listar os usuários cadastrados:

```bash
python list_users.py
```

## Deploy e Operações

### Guia Detalhado

Para detalhes completos sobre deploy, operações e manutenção em ambiente de produção, consulte o arquivo [DEPLOY.md](DEPLOY.md).

Este guia contém instruções detalhadas sobre:
- Configuração do servidor
- Instalação e configuração da aplicação
- Gerenciamento do serviço systemd
- Configuração do Nginx como proxy reverso
- Monitoramento e logs
- Backups e manutenção
- Solução de problemas comuns

### Comandos Rápidos

Para uma referência rápida com os comandos mais comuns para gerenciar o serviço em produção, consulte [OPERATIONS_CHEATSHEET.md](OPERATIONS_CHEATSHEET.md).

### Deploy Rápido

Para um deploy rápido, você pode usar:

```bash
# Clone o repositório
git clone https://github.com/gregoryoliveiraa/ap-backend.git
cd ap-backend

# Configurar variáveis de ambiente para produção
cp .env.example .env
# Edite o arquivo .env com as configurações de produção
# Importante: ajuste DATABASE_URL para o banco PostgreSQL

# Execute o script de deploy
chmod +x deploy.sh
./deploy.sh
```

Para verificação de saúde, o script de deploy configura automaticamente um serviço de monitoramento que verifica a API a cada 5 minutos.

## Estrutura do Projeto

```
ap-backend/
├── alembic/                # Migrações de banco de dados
├── app/
│   ├── api/                # Rotas e endpoints da API
│   ├── core/               # Configurações e funcionalidades centrais
│   ├── db/                 # Configuração do banco de dados
│   ├── models/             # Modelos SQLAlchemy
│   ├── schemas/            # Esquemas Pydantic
│   ├── services/           # Serviços e lógica de negócios
│   └── utils/              # Utilitários gerais
├── scripts/                # Scripts de utilidade
├── .env.example            # Template de variáveis de ambiente
├── create_admin.py         # Script para criar usuário administrador
├── deploy.sh               # Script de deploy
├── init_db.py              # Inicialização do banco de dados
├── list_users.py           # Listar usuários cadastrados
├── requirements.txt        # Dependências do projeto
└── setup.sh                # Script de configuração do ambiente
```

## Solução de Problemas

Se encontrar problemas com migrações do banco de dados:

1. Verifique se a estrutura do banco está correta: `alembic current`
2. Se necessário, reinicie as migrações: `alembic revision --autogenerate -m "reset migrations"`
3. Aplique migrações: `alembic upgrade heads`

Para problemas com o pandas (se estiver usando SQLite):
```bash
pip install --no-cache-dir pandas
```

## Licença

MIT License

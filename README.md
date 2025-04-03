# AP-Backend

Backend API para o sistema de assistência jurídica com IA.

## Descrição

O AP-Backend é uma API REST desenvolvida em Python com FastAPI que fornece serviços para o aplicativo de assistência jurídica. Esta API gerencia documentos jurídicos, templates, autenticação de usuários e integração com modelos de IA para geração de conteúdo jurídico.

## Principais Funcionalidades

- Autenticação e gerenciamento de usuários
- CRUD de documentos jurídicos
- Gerenciamento de templates de documentos
- Integração com modelos de IA para assistência na geração de textos jurídicos
- Pesquisa avançada de documentos e jurisprudência

## Tecnologias Utilizadas

- Python 3.9+
- FastAPI
- SQLAlchemy
- SQLite (desenvolvimento)
- PyJWT para autenticação
- OpenAI API para integração com modelos de IA

## Instalação e Execução

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone este repositório:
```bash
git clone https://github.com/gregoryoliveiraa/ap-backend.git
cd ap-backend
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### Execução

Para iniciar o servidor de desenvolvimento:

```bash
python -m uvicorn app.main:app --reload --port 8080
```

O servidor estará disponível em `http://localhost:8080`.

## Estrutura do Projeto

```
ap-backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── main.py
├── scripts/
├── requirements.txt
└── README.md
```

## Documentação da API

A documentação interativa da API está disponível em:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Licença

Este projeto está licenciado sob a licença MIT. 
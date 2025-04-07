# Advogada Parceira

Este repositório contém o código fonte do sistema Advogada Parceira.

## Estrutura do Projeto

O projeto é composto por dois repositórios principais:

- `ap-frontend`: Frontend da aplicação em React
- `ap-backend`: Backend da aplicação em FastAPI (Python)

## Estratégia de Branches

O projeto adota o modelo Git Flow para gerenciamento de branches. Confira o arquivo [branch_strategy.md](branch_strategy.md) para mais detalhes.

### Branches Principais
- **main**: Branch de produção. Contém código estável e testado pronto para deploy.
- **develop**: Branch de desenvolvimento onde novas funcionalidades são integradas.

### Branches Temporárias
- **feature/nome-da-feature**: Para desenvolvimento de novas funcionalidades.
- **bugfix/nome-do-bug**: Para correção de bugs.
- **hotfix/nome-do-hotfix**: Para correções urgentes em produção.
- **release/versão**: Para preparação de novas versões.

## Scripts de Gerenciamento

O projeto possui um conjunto de scripts para facilitar o gerenciamento do código e das versões:

### Gerenciamento de Branches e Versões
- `create_feature_branch.sh`: Cria uma nova branch de feature a partir da develop
- `create_release.sh`: Prepara uma nova versão para lançamento
- `finalize_release.sh`: Finaliza o processo de release, mesclando na main e develop
- `create_hotfix.sh`: Cria uma branch de hotfix para correções urgentes em produção
- `finalize_hotfix.sh`: Finaliza um hotfix, aplicando as correções em main e develop
- `implement_branch_strategy.sh`: Script usado para implementar inicialmente a estratégia de branches

### Exemplos de Uso

#### Criar uma Feature
```bash
./create_feature_branch.sh frontend nova-funcionalidade
```

#### Criar uma Release
```bash
./create_release.sh both 1.1.0
```

#### Finalizar uma Release
```bash
./finalize_release.sh both 1.1.0
```

#### Criar um Hotfix
```bash
./create_hotfix.sh backend correcao-urgente 1.0.1
```

#### Finalizar um Hotfix
```bash
./finalize_hotfix.sh backend correcao-urgente 1.0.1
```

## Convenções de Versionamento

O projeto segue o padrão Semantic Versioning (SemVer):

- **X.Y.Z** onde:
  - **X**: Versão principal (major) - Mudanças incompatíveis com versões anteriores
  - **Y**: Versão secundária (minor) - Adições de funcionalidades compatíveis
  - **Z**: Versão de patch - Correções de bugs compatíveis

## Deployment

O sistema está atualmente configurado para ser implantado em:
- Frontend: http://advogadaparceira.com.br
- API: http://api.advogadaparceira.com.br

## Informações Adicionais

- Para detalhes sobre a estratégia de branches, consulte [branch_strategy.md](branch_strategy.md)
- Documentação adicional pode ser encontrada na pasta `deployment_docs/`

## Visão Geral

A Advogada Parceira é uma plataforma que permite a profissionais do direito gerenciar, criar e gerar documentos jurídicos com assistência de IA. O sistema é composto por:

- **Frontend**: Aplicação React (http://app.advogadaparceira.com.br)
- **Backend**: API FastAPI Python (http://api.advogadaparceira.com.br)

## Tecnologias Utilizadas

### Frontend
- React
- TypeScript
- Material UI
- Axios para requisições HTTP
- React Router para navegação

### Backend
- FastAPI (Python)
- SQLite/PostgreSQL
- JWT para autenticação
- Integração com APIs de IA (OpenAI, Anthropic, DeepSeek)

## Estrutura do Projeto

```
advogada-parceira/
├── ap-frontend/         # Aplicação React
├── ap-backend/          # API FastAPI
└── deployment_docs/     # Documentação de implantação
```

## Implantação

### Requisitos do Servidor
- Ubuntu Server 22.04 LTS ou superior
- Nginx
- Node.js (para o frontend)
- Python 3.10+ (para o backend)
- Git

### Scripts de Implantação

Para implantar o frontend:
```bash
./deploy_frontend.sh
```

Para implantar o backend:
```bash
./backend_deploy.sh
```

## Desenvolvimento Local

### Frontend
```bash
cd ap-frontend
npm install
npm start
```

### Backend
```bash
cd ap-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuração de Ambiente

### Frontend (.env)
```
REACT_APP_API_URL=http://api.advogadaparceira.com.br
REACT_APP_ENV=development
```

### Backend (.env)
```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Licença

Este projeto é proprietário e não está licenciado para uso público sem permissão explícita.

## Contato

Para questões ou suporte, entre em contato com a equipe de desenvolvimento em gregory.oliveira.it@gmail.com. 
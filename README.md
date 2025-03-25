# Advogada Parceira

Uma assistente de IA especializada em textos jurídicos para o sistema legal brasileiro.

## Visão Geral

A Advogada Parceira é uma aplicação que combina uma interface elegante com funcionalidades avançadas de IA para auxiliar profissionais do direito. O sistema inclui:

1. **Chat com IA** integrado à API do ChatGPT
2. **Geração e automação de documentos jurídicos**
3. **Pesquisa de jurisprudência** assistida por IA
4. **Sistema de gerenciamento de consumo/créditos** de IA
5. **Sistema de autenticação** para advogados (com verificação da OAB)

## Arquitetura

O projeto utiliza uma arquitetura moderna:

* **Frontend**: React.js com TypeScript e TailwindCSS
* **Backend**: Python com FastAPI
* **Banco de dados**: PostgreSQL
* **Integração com IA**: API da OpenAI (ChatGPT)

## Pré-requisitos

Para executar o projeto localmente, você precisará ter instalado:

1. Python 3.9+
2. Node.js 16+ e npm
3. PostgreSQL
4. Chave de API da OpenAI

## Configuração

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/advogada-parceira.git
   cd advogada-parceira
   ```

2. Configure o arquivo `.env` na raiz do projeto backend:
   ```
   cp backend/.env.example backend/.env
   ```
   
   Edite o arquivo `.env` com suas configurações, especialmente:
   - `DATABASE_URL`: URL de conexão com o PostgreSQL
   - `OPENAI_API_KEY`: Sua chave de API da OpenAI
   - `SECRET_KEY`: Uma chave secreta para assinatura de tokens JWT

3. Configure o banco de dados PostgreSQL:
   ```
   # Crie um banco de dados chamado 'advogada_parceira'
   createdb advogada_parceira
   ```

## Inicialização

### Backend

1. Navegue até o diretório backend:
   ```
   cd backend
   ```

2. Torne o script de execução executável:
   ```
   chmod +x ./run_backend.sh
   ```

3. Execute o script:
   ```
   ./run_backend.sh
   ```

O script irá:
- Criar um ambiente virtual Python
- Instalar as dependências
- Inicializar o banco de dados
- Iniciar o servidor FastAPI

O backend estará disponível em: http://localhost:8000

A documentação da API estará disponível em: http://localhost:8000/api/docs

### Frontend

1. Navegue até o diretório frontend:
   ```
   cd frontend
   ```

2. Torne o script de execução executável:
   ```
   chmod +x ./run_frontend.sh
   ```

3. Execute o script:
   ```
   ./run_frontend.sh
   ```

O script irá:
- Instalar as dependências do Node.js
- Configurar as variáveis de ambiente
- Iniciar o servidor de desenvolvimento do React

O frontend estará disponível em: http://localhost:3000

## Usuário Inicial

Após a inicialização do banco de dados, um usuário administrador será criado automaticamente:

- **Email**: admin@advogadaparceira.com.br
- **Senha**: admin123

## Funcionalidades Principais

1. **Autenticação**
   - Registro
   - Login
   - Verificação de OAB

2. **Chat com IA**
   - Conversa em tempo real com a IA
   - Histórico de conversas
   - Sistema de créditos

3. **Documentos**
   - Criação de documentos
   - Geração automática a partir de templates
   - Análise de documentos existentes
   - Gerenciamento de documentos

4. **Jurisprudência**
   - Pesquisa de jurisprudência assistida por IA
   - Filtros avançados

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
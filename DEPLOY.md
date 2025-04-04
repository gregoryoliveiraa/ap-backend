# Guia de Deploy e Operações - Advogada Parceira Backend

**Versão atual:** 2.1.8

Este documento descreve os procedimentos para deploy, monitoramento e operações do backend da API Advogada Parceira em ambiente de produção.

## Arquitetura do Sistema

O backend é composto por:
- **API FastAPI**: Serviço principal que atende requisições HTTP
- **Banco de dados SQLite/PostgreSQL**: Armazenamento de dados
- **Nginx**: Proxy reverso para roteamento de requisições
- **Systemd**: Gerenciamento do serviço

## Requisitos de Infraestrutura

- Ubuntu Server 22.04 LTS ou superior
- Python 3.9+
- Nginx
- Certificados SSL (para produção)
- Portas liberadas: 80 (HTTP), 443 (HTTPS), 8000 (API)

## Procedimento de Deploy

### 1. Preparação do Servidor

```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Instale dependências
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

### 2. Configuração do Aplicativo

```bash
# Clone o repositório em um diretório específico para produção
git clone https://github.com/gregoryoliveiraa/ap-backend.git /home/ubuntu/ap-backend-new
cd /home/ubuntu/ap-backend-new

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Copie o arquivo .env de exemplo e configure-o
cp .env.example .env
# Edite o arquivo .env conforme necessário para produção
```

### 3. Configuração do Banco de Dados

```bash
# Inicialize o banco de dados
python init_db.py

# Execute as migrações
venv/bin/alembic upgrade head
```

### 4. Configuração do Serviço Systemd

Crie um arquivo de serviço systemd:

```bash
sudo nano /etc/systemd/system/ap-backend.service
```

Conteúdo do arquivo:

```ini
[Unit]
Description=Advogada Parceira Backend API
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ap-backend-new
ExecStart=/home/ubuntu/ap-backend-new/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=ap-backend
Environment="PATH=/home/ubuntu/ap-backend-new/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
```

Habilite e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ap-backend.service
sudo systemctl start ap-backend.service
```

### 5. Configuração do Nginx

Crie um arquivo de configuração Nginx:

```bash
sudo nano /etc/nginx/sites-available/ap-backend.conf
```

Conteúdo do arquivo:

```nginx
server {
    listen 80;
    server_name api.advogadaparceira.com.br;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Configurações para WebSockets (se necessário)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Configuração para documentação Swagger/ReDoc
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /redoc {
        proxy_pass http://localhost:8000/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Habilite o site e reinicie o Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/ap-backend.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Configuração SSL (Opcional, mas recomendado para produção)

```bash
sudo certbot --nginx -d api.advogadaparceira.com.br
```

## Gerenciamento do Serviço

### Iniciar o Serviço

```bash
sudo systemctl start ap-backend.service
```

### Parar o Serviço

```bash
sudo systemctl stop ap-backend.service
```

### Reiniciar o Serviço

```bash
sudo systemctl restart ap-backend.service
```

### Verificar Status do Serviço

```bash
sudo systemctl status ap-backend.service
```

### Visualizar Logs do Serviço

```bash
# Ver logs recentes
sudo journalctl -u ap-backend.service -n 100

# Acompanhar logs em tempo real
sudo journalctl -u ap-backend.service -f
```

## Atualizações e Manutenção

### Atualização do Código

```bash
cd /home/ubuntu/ap-backend-new
git pull origin main

# Ative o ambiente virtual
source venv/bin/activate

# Atualize dependências
pip install -r requirements.txt

# Execute migrações do banco de dados (se necessário)
venv/bin/alembic upgrade head

# Reinicie o serviço
sudo systemctl restart ap-backend.service
```

### Backup do Banco de Dados

```bash
# Para SQLite
cp /home/ubuntu/ap-backend-new/app.db /home/ubuntu/backups/app_$(date +%Y%m%d).db
```

## Monitoramento

### Verificação de Saúde

A API possui um endpoint de saúde na raiz:

```bash
curl http://localhost:8000
# Ou com domínio
curl http://api.advogadaparceira.com.br
```

A resposta deve ser similar a:
```json
{
  "message": "Advogada Parceira API is running",
  "status": "ok",
  "version": "2.1.8"
}
```

### Monitoramento com Cron

Configure uma verificação periódica de saúde:

```bash
crontab -e
```

Adicione a linha:
```
*/5 * * * * curl -s http://localhost:8000 > /dev/null || sudo systemctl restart ap-backend.service
```

Isso verificará o serviço a cada 5 minutos e o reiniciará caso não esteja respondendo.

## Solução de Problemas

### Serviço não inicia

Verifique erros nos logs:
```bash
sudo journalctl -u ap-backend.service -n 50
```

Problemas comuns incluem:
- Permissões incorretas
- Variáveis de ambiente faltando
- Banco de dados inacessível
- Porta 8000 já em uso

### Erro "502 Bad Gateway"

Isso geralmente ocorre quando:
- A API não está em execução
- Nginx não consegue se comunicar com a API
- Configuração incorreta do proxy

Verificações:
```bash
# Verificar se a API está em execução
sudo systemctl status ap-backend.service

# Verificar logs do Nginx
sudo tail -n 100 /var/log/nginx/error.log
```

### Migrações de banco de dados

Caso encontre problemas com migrações:

```bash
cd /home/ubuntu/ap-backend-new
source venv/bin/activate

# Verificar estado atual das migrações
venv/bin/alembic current

# Se houver problemas, pode-se fazer um downgrade
venv/bin/alembic downgrade -1

# Ou criar uma nova revisão para corrigir problemas
venv/bin/alembic revision --autogenerate -m "fix_schema"
venv/bin/alembic upgrade head
```

## Contatos e Responsáveis

Para problemas críticos, entrar em contato com:

- Administrador de Sistemas: [Nome e contato]
- Desenvolvedor Backend: [Nome e contato] 
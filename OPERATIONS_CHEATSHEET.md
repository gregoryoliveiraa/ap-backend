# Guia Rápido de Operações - Advogada Parceira Backend

**Versão atual:** 2.1.8

Este é um guia rápido com os comandos mais importantes para operar o backend da API Advogada Parceira. Para instruções mais detalhadas, consulte o [DEPLOY.md](DEPLOY.md).

## Comandos Essenciais

### Gerenciamento do Serviço

```bash
# Iniciar o serviço
sudo systemctl start ap-backend.service

# Parar o serviço
sudo systemctl stop ap-backend.service

# Reiniciar o serviço
sudo systemctl restart ap-backend.service

# Verificar status
sudo systemctl status ap-backend.service
```

### Logs

```bash
# Ver os últimos 50 logs
sudo journalctl -u ap-backend.service -n 50

# Ver logs em tempo real (Ctrl+C para sair)
sudo journalctl -u ap-backend.service -f
```

### Verificações de Saúde

```bash
# Verificar se a API está respondendo
curl http://localhost:8000
# ou
curl http://api.advogadaparceira.com.br

# Verificar documentação da API
curl -I http://api.advogadaparceira.com.br/docs

# Verificar conectividade do banco de dados (requer sqlite3)
sqlite3 /home/ubuntu/ap-backend-new/app.db "SELECT COUNT(*) FROM users;"
```

### Atualizações

```bash
# Atualizar o código
cd /home/ubuntu/ap-backend-new
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar o serviço após atualizações
sudo systemctl restart ap-backend.service
```

### Banco de Dados

```bash
# Backup rápido do banco de dados
cp /home/ubuntu/ap-backend-new/app.db /home/ubuntu/backups/app_$(date +%Y%m%d).db

# Aplicar migrações
cd /home/ubuntu/ap-backend-new
source venv/bin/activate
venv/bin/alembic upgrade head
```

### Nginx

```bash
# Testar configuração do Nginx
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status do Nginx
sudo systemctl status nginx

# Ver logs de erro do Nginx
sudo tail -n 100 /var/log/nginx/error.log
```

## Solução Rápida de Problemas

| Problema | Solução |
|----------|---------|
| API não responde | `sudo systemctl restart ap-backend.service` |
| Erro 502 Bad Gateway | Verificar logs: `sudo journalctl -u ap-backend.service -n 50` |
| Banco de dados corrompido | Restaurar o backup mais recente: `cp /home/ubuntu/backups/app_YYYYMMDD.db /home/ubuntu/ap-backend-new/app.db` |
| Conexões pendentes | Reiniciar: `sudo systemctl restart ap-backend.service` |
| Erro de permissão | Verificar permissões: `sudo chown -R ubuntu:ubuntu /home/ubuntu/ap-backend-new` |

## Contatos para Suporte

- Problemas técnicos: [Nome e contato técnico]
- Emergências: [Nome e contato emergência] 
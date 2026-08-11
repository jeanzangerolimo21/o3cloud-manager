# O3Cloud Manager

# Arquitetura Beta

Status: Planejada

---

# Objetivo

Definir a arquitetura operacional recomendada para a release Beta do O3Cloud Manager, preservando dados reais, simplificando manutenção e preparando crescimento futuro.

---

# Topologia Recomendada

## Opção preferencial

```text
Servidor App
- Ubuntu Server
- Nginx
- Gunicorn/systemd
- Código em /opt/o3cloud-manager
- Storage em volume dedicado

Servidor Banco
- MariaDB/MySQL
- Disco dedicado para dados
- Backups SQL recebidos/armazenados conforme política
```

Benefícios:

- Isola carga da aplicação e banco.
- Facilita backup e restore.
- Reduz risco operacional em atualizações do ERP.
- Permite crescimento futuro do banco sem mover aplicação.

## Opção mínima aceitável para Beta

```text
Servidor único
- Aplicação
- Banco
- Storage em disco/volume separado
```

Mesmo em servidor único, `/opt/o3cloud-manager/storage` deve ficar em volume separado sempre que possível.

---

# Layout de Diretórios

```text
/opt/o3cloud-manager/
  app/
  database/
  deployment/
  docs/
  storage/
  logs/
  venv/
```

Recomendação:

```text
/opt/o3cloud-manager          código e venv
/opt/o3cloud-manager/storage  volume persistente separado
/opt/o3cloud-manager/logs     logs locais rotacionados
```

---

# Serviço da Aplicação

A aplicação deve rodar por `systemd` com `gunicorn`, conforme:

```text
docs/38-SERVICO-SYSTEMD.md
deployment/o3cloud-manager.service
```

Não usar `python app.py` em produção/Beta.

---

# Banco de Dados

Recomendações:

- Banco dedicado para Beta.
- Usuário SQL específico para a aplicação.
- Acesso remoto restrito ao servidor da aplicação.
- Backup com `mysqldump --single-transaction --routines --triggers --events`.
- Restore testado antes da homologação.

---

# Storage

Conteúdo esperado:

- Contratos e PDFs assinados.
- Anexos comerciais e operacionais.
- Relatórios gerados.
- Imagens de e-mail marketing.
- Backups locais temporários.

Regras:

- Não versionar no Git.
- Backup separado do dump SQL.
- Permissão operacional para usuário `o3cloud`.
- Destino externo obrigatório para retenção real.

---

# Variáveis de Ambiente Relevantes

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
PUBLIC_BASE_URL
O3_LOG_DIR
EMAIL_MARKETING_LOGO_URL
EMAIL_MARKETING_PUBLIC_BASE_URL
```

Novas variáveis poderão ser definidas para backup e GitHub na Sprint 21.

---

# Migração para Beta

Fluxo planejado:

```text
1. congelar janela de migração
2. gerar dump SQL do ambiente atual
3. compactar storage atual
4. provisionar servidor Beta
5. restaurar banco
6. restaurar storage
7. aplicar migrations
8. iniciar systemd
9. validar módulos críticos
10. liberar homologação
```

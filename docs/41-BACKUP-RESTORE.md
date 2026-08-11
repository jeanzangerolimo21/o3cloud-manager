# O3Cloud Manager

# Backup e Restore

Status: Planejado

---

# Objetivo

Criar uma estratégia de backup e restore para banco de dados e storage, com operação pela interface administrativa e suporte futuro a destinos externos.

---

# Tipos de Backup

## Banco de dados

Formato inicial:

```text
.sql.gz
```

Comando base planejado:

```bash
mysqldump --single-transaction --routines --triggers --events \
  --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --password="$DB_PASSWORD" "$DB_NAME" \
  | gzip > backup.sql.gz
```

## Storage

Formato inicial:

```text
storage.tar.gz
```

Conteúdo:

```text
/opt/o3cloud-manager/storage
```

---

# Destinos Planejados

## Local

Uso inicial para Beta:

```text
/opt/o3cloud-manager/storage/backups/database
/opt/o3cloud-manager/storage/backups/storage
```

Observação: backup local não substitui destino externo.

## SFTP/SSH

- Host.
- Porta.
- Usuário.
- Chave privada ou senha criptografada.
- Diretório remoto.
- Teste de conexão.

## S3 compatível

- Endpoint.
- Bucket.
- Região.
- Access key.
- Secret key criptografada.
- Prefixo.

## NAS/TrueNAS ou caminho montado

- Caminho local montado.
- Verificação de escrita.
- Política de retenção.

---

# Tela Configurações > Backups

Funcionalidades planejadas:

- Gerar backup agora.
- Agendar periodicidade.
- Definir retenção.
- Escolher destino.
- Testar destino.
- Consultar histórico.
- Baixar arquivo local quando permitido.
- Exibir status, tamanho e duração.

Acesso:

- Apenas Administrador.

---

# Histórico de Backup

Campos esperados:

```text
id
tipo
destino
status
arquivo
tamanho_bytes
iniciado_em
finalizado_em
executado_por
mensagem
checksum
```

---

# Restore

Restore deve ser documentado e inicialmente executado por script operacional, não automaticamente pela tela.

Fluxo:

```text
1. parar aplicação
2. validar arquivo SQL
3. criar snapshot/backup do estado atual
4. restaurar dump
5. restaurar storage se aplicável
6. rodar migrations
7. iniciar aplicação
8. validar saúde
```

---

# Segurança

- Credenciais externas devem ser criptografadas.
- Segredos não devem aparecer em logs.
- Download de backup apenas para Administrador.
- Histórico deve registrar usuário e status.
- Backup antes de atualização deve ser obrigatório.

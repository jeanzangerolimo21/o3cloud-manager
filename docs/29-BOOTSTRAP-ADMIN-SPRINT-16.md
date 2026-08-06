# Bootstrap Seguro do Primeiro Administrador - Sprint 16

Versao: 3.0 Alpha

Data: 04/08/2026

Status: Implementado

---

# Objetivo

Garantir uma forma controlada de criar ou promover o primeiro usuario administrador local sem gravar senha em migration, seed ou codigo fonte.

---

# Comando

```bash
O3_BOOTSTRAP_ADMIN_EMAIL=admin@empresa.com \
O3_BOOTSTRAP_ADMIN_PASSWORD='senha-forte-com-12-ou-mais' \
venv/bin/flask --app 'app:create_app' bootstrap-admin
```

Opcionalmente:

```bash
venv/bin/flask --app 'app:create_app' bootstrap-admin \
  --email admin@empresa.com \
  --name 'Administrador' \
  --login admin
```

Se `--password`/`O3_BOOTSTRAP_ADMIN_PASSWORD` nao for informado, o comando solicita a senha no terminal com confirmacao.

---

# Regras de Seguranca

- Senha inicial deve ter no minimo 12 caracteres.
- O comando exige e-mail valido.
- A senha e armazenada apenas como hash seguro via Werkzeug.
- O comando cria usuario local ativo com perfil ADMIN quando nao houver administrador ativo.
- Se ja existir ADMIN ativo, o comando bloqueia a execucao por padrao.
- `--force` permite promover/atualizar apenas o usuario informado, registrando auditoria.
- Nenhuma senha e registrada em auditoria, logs ou migration.

---

# Auditoria

O bootstrap registra evento em `auth_auditoria`:

- `ADMIN_BOOTSTRAP_CRIADO`
- `ADMIN_BOOTSTRAP_ATUALIZADO`

Entidade: `auth_usuarios`.

---

# Encaminhamento

A etapa 4 da Sprint 16 fica atendida. FreeIPA, LDAP e Active Directory permanecem para validacao pos-Beta, quando houver ambiente externo disponivel.

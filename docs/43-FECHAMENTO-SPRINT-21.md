# O3Cloud Manager v3.0

# Fechamento Sprint 21

Release Beta, Backup e Atualizações

Data de fechamento técnico: 12/08/2026

Status: Concluída tecnicamente

---

# Entregas Consolidadas

- Arquitetura Beta documentada para operação segura do O3Cloud Manager.
- Estratégia de branches, tags e releases definida para `develop`, `beta`, `main` e versões `v0.9.x-beta.x`.
- Tag `v0.9.0-beta.1` criada e publicada no remoto a partir do commit `6f78d62`.
- Tag `v0.9.0-beta.2` criada e publicada no remoto a partir do commit `55fb2ee`.
- Serviço systemd/gunicorn documentado e preparado para operação sem `python app.py` em debug.
- Tela `Configurações > Backups do Sistema` criada para Administrador.
- Histórico de backups persistido.
- Serviço de backup local para banco, storage ou completo criado.
- Comando CLI `flask backups-processar-agendados` criado.
- Cron operacional atualizado para processar backups pendentes.
- Script `deployment/restore-db.sh` criado para restaurar dump `.sql`, `.sql.gz` ou artefato completo com `database.sql.gz`.
- Script `deployment/healthcheck.sh` criado para validar serviço systemd, conexão MySQL e HTTP local.
- Tela `Configurações > Atualizações do Sistema` criada em modo somente leitura.
- Verificação de branch, commit, tag, remoto, upstream, divergência e alterações locais disponibilizada.
- Consulta de tags/releases remotas preparada para GitHub Releases.
- Histórico de verificações de atualização persistido.

---

# Migrations

- `083_create_config_backups.sql`
- `084_permissao_atualizacoes_sistema.sql`
- `085_create_config_atualizacoes_verificacoes.sql`
- `086_expandir_verificacoes_github_releases.sql`

---

# Documentação Atualizada

- `docs/38-SERVICO-SYSTEMD.md`
- `docs/39-SPRINT-21-RELEASE-BETA.md`
- `docs/40-ARQUITETURA-BETA.md`
- `docs/41-BACKUP-RESTORE.md`
- `docs/42-ATUALIZACOES-SISTEMA.md`
- `docs/CHANGELOG.md`

---

# Pendências para Homologação Beta

- Publicar GitHub Release formal vinculada às tags Beta.
- Validar backup completo com dados reais controlados.
- Validar restore em ambiente Beta separado.
- Validar permissões do usuário `o3cloud` no servidor Beta.
- Validar destino externo de backup quando o caminho NAS/MOUNT estiver criado.
- Definir credenciais protegidas para SFTP/SSH ou S3 compatível, se esses destinos forem ativados.
- Validar healthcheck após restore e após atualização assistida.
- Manter execução de atualização pela tela bloqueada até o fluxo com backup obrigatório ser homologado.

---

# Decisão de Fechamento

O Sprint 21 está concluído tecnicamente em 12/08/2026.

A entrega prepara a operação Beta com backup, restore, versionamento, serviço systemd e tela de atualizações em modo controlado. As validações com dados reais e destinos externos permanecem como pendências de homologação Beta.

Com o fechamento técnico do Sprint 21, o desenvolvimento retorna ao Sprint 17 para concluir a frente de Comissões de Executivos e expansão da sincronização financeira OMIE.

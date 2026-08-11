# O3Cloud Manager v3.0

# Sprint 21 - Release Beta, Backup e Atualizações

Status: Em desenvolvimento

Data de abertura: 11/08/2026

---

# Objetivo

Preparar o O3Cloud Manager para a release Beta com arquitetura operacional de deploy, backup, restore, versionamento, atualização controlada e migração segura dos dados reais já existentes.

A Sprint 21 deve transformar a aplicação de um ambiente de desenvolvimento assistido em um ambiente Beta operável, com procedimentos repetíveis e trilhas de auditoria técnica.

---

# Diretrizes

- Preservar os dados reais atuais do banco e do `storage`.
- Separar claramente desenvolvimento, Beta e versão oficial.
- Automatizar backup antes de operações críticas.
- Evitar atualização sem backup recente válido.
- Manter atualização do ERP controlada por Administrador.
- Preparar destinos externos de backup desde o desenho inicial.
- Documentar instalação e operação antes de desenvolver telas administrativas.

---

# Escopo Planejado

## 1. Arquitetura Beta

- Definir arquitetura recomendada para ambiente Beta.
- Avaliar separação entre servidor da aplicação e servidor de banco de dados.
- Definir volume dedicado para `/opt/o3cloud-manager/storage`.
- Definir política de logs, storage, backup e restore.
- Documentar variáveis de ambiente obrigatórias.

Referência: `docs/40-ARQUITETURA-BETA.md`

## 2. Estratégia de Branches e Releases

Modelo recomendado:

```text
develop  -> desenvolvimento contínuo
beta     -> versão homologada Beta
main     -> versão oficial/produção
tags     -> releases instaláveis
```

Tags planejadas:

```text
v0.9.0-beta.1
v0.9.0-beta.2
v1.0.0
v1.0.1
```

Status inicial de release:

- Tag `v0.9.0-beta.1` criada e publicada no remoto em 11/08/2026 a partir do commit `6f78d62`.
- Verificação pela tela encontrou 1 tag remota após publicação.

Regras:

- Ambiente Beta deve acompanhar branch `beta` ou tags `v0.9.x-beta.x`.
- Ambiente oficial deve acompanhar branch `main` ou tags estáveis `v1.x.x`.
- `develop` não deve ser instalado diretamente em produção oficial.

## 3. Backup e Restore

- Criar scripts de dump SQL com `mysqldump`.
- Criar script de restore SQL.
- Criar backup compactado do `storage`.
- Criar histórico de backups.
- Criar política de retenção.
- Preparar destinos externos.

Destinos planejados:

- Local.
- SFTP/SSH.
- S3 compatível.
- NAS/TrueNAS ou caminho montado.

Referência: `docs/41-BACKUP-RESTORE.md`

## 4. Tela Configurações > Backups

Status da implementação inicial:

- Criada migration 083_create_config_backups.sql para agendamento, histórico de execuções e permissão backups_sistema para ADMIN.
- Criado serviço administrativo para backup do banco, storage ou completo.
- Criada tela Configurações > Backups do Sistema para salvar periodicidade, retenção, destino local/MOUNT, executar backup manual e baixar artefato local permitido.
- Criado comando CLI flask backups-processar-agendados --limite 1.
- Adicionada rotina ao cron operacional para processar backups pendentes a cada 15 minutos.

Funcionalidades planejadas:

- Gerar backup agora.
- Configurar periodicidade.
- Configurar retenção.
- Selecionar destino.
- Testar destino externo.
- Consultar histórico.
- Baixar backup local quando permitido.
- Exibir status, tamanho, duração e erro resumido.

Acesso:

- Apenas Administrador.

Pendências da próxima etapa:

- Teste explícito de escrita do destino antes de salvar, mantido para a versão Beta porque o diretório NAS/MOUNT ainda não foi criado.
- Destinos SFTP/SSH e S3 compatível com credenciais protegidas.
- Script formal de restore e healthcheck operacional criados em `deployment/restore-db.sh` e `deployment/healthcheck.sh`.

## 5. Atualizações do Sistema

Status da implementação inicial:

- Criada tela `Configurações > Atualizações do Sistema` em modo somente leitura.
- Exibidos branch, commit, tag atual, última tag local, remoto, upstream, divergência com upstream e alterações locais.
- Criada permissão `atualizacoes_sistema` para ADMIN pela migration `084_permissao_atualizacoes_sistema.sql`.
- Criado botão `Verificar atualizações`, ainda sem instalação, consultando tags remotas e registrando histórico pela migration `085_create_config_atualizacoes_verificacoes.sql`.
- Execução de atualização pela tela permanece bloqueada para fase posterior, dependente de backup obrigatório e rotina operacional assistida.

Funcionalidades planejadas:

- Exibir versão atual instalada.
- Exibir branch, commit e tag atuais.
- Consultar releases disponíveis no GitHub.
- Mostrar changelog da release.
- Preparar atualização com backup obrigatório.
- Executar atualização controlada em fase posterior.
- Registrar histórico de atualização.

Acesso:

- Apenas Administrador.

Referência: `docs/42-ATUALIZACOES-SISTEMA.md`

## 6. Scripts de Deploy e Atualização

Scripts planejados:

```text
deployment/backup-db.sh
deployment/restore-db.sh
deployment/backup-storage.sh
deployment/update.sh
deployment/healthcheck.sh
```

Status inicial:

- `deployment/restore-db.sh` criado para restaurar dump `.sql`, `.sql.gz` ou artefato `o3cloud-backup-*.tar.gz` contendo `database.sql.gz`.
- `deployment/healthcheck.sh` criado para validar serviço systemd, conexão MySQL e HTTP local.
- Runner formal de migrations segue pendente; restore orienta revisão/aplicação de migrations quando o dump vier de outra versão.

Fluxo mínimo de atualização:

```text
1. verificar versão atual
2. gerar backup SQL
3. validar backup
4. git fetch
5. checkout da tag/release
6. pip install -r requirements.txt
7. rodar migrations
8. reiniciar systemd
9. executar healthcheck
10. registrar histórico
```

## 7. Migração dos Dados Atuais para Beta

- Gerar dump SQL completo do ambiente atual.
- Restaurar no servidor Beta.
- Migrar conteúdo de `/opt/o3cloud-manager/storage`.
- Validar permissões.
- Rodar migrations pendentes.
- Validar módulos críticos com dados reais.

---

# Fora do Escopo Inicial

- Rollback totalmente automatizado pela interface.
- Replicação de banco em tempo real.
- Alta disponibilidade.
- CI/CD completo com deploy automático em produção.
- Backup imutável/WORM.
- Criptografia externa gerenciada por KMS.

Esses itens podem ser planejados após estabilização da Beta.

---

# Critérios de Aceite

- Documentação da arquitetura Beta aprovada.
- Estratégia de branches e tags definida.
- Scripts de backup/restore definidos e testados.
- Tela de Backups disponível para Administrador.
- Histórico de backups persistido.
- Estrutura preparada para destino externo.
- Tela/base de Atualizações disponível para Administrador.
- Consulta de releases GitHub definida com credencial segura.
- Processo de migração para Beta documentado.
- Checklist de homologação Beta definido.

---

# Documentos Relacionados

- `docs/40-ARQUITETURA-BETA.md`
- `docs/41-BACKUP-RESTORE.md`
- `docs/42-ATUALIZACOES-SISTEMA.md`
- `docs/38-SERVICO-SYSTEMD.md`
- `docs/36-LOGS-BACKEND.md`
- `docs/37-FECHAMENTO-SPRINT-20.md`

# O3Cloud Manager

# Atualizações do Sistema

Status: Implementação inicial em andamento

---

# Objetivo

Definir a estratégia para atualização controlada do ERP O3Cloud Manager a partir de releases do GitHub, com backup obrigatório, histórico e acesso restrito a Administradores.

---

# Estratégia de Branches

```text
develop  desenvolvimento contínuo
beta     homologação Beta
main     versão oficial
tags     releases instaláveis
```

Ambientes:

```text
Desenvolvimento -> develop
Beta             -> beta ou v0.9.x-beta.x
Produção oficial -> main ou v1.x.x
```

---

# Releases

Usar tags e GitHub Releases para publicar versões instaláveis.

Exemplos:

```text
v0.9.0-beta.1
v0.9.0-beta.2
v1.0.0
v1.0.1
```

Cada release deve possuir changelog resumido, migrations relevantes e instruções específicas quando necessário.

---

# Tela Configurações > Atualizações do Sistema

Implementação inicial:

- Tela administrativa `Configurações > Atualizações do Sistema`.
- Exibição de branch, commit, data, mensagem, tag atual, última tag local, remoto e upstream.
- Exibição de divergência local versus upstream quando configurado.
- Exibição de alterações locais para bloquear atualização futura com worktree suja.
- Permissão `atualizacoes_sistema` restrita a Administrador.

Funcionalidades planejadas:

- Exibir versão atual.
- Exibir branch atual.
- Exibir commit atual.
- Exibir tag atual, se houver.
- Verificar releases disponíveis no GitHub.
- Mostrar changelog da release.
- Preparar atualização.
- Exigir backup recente válido.
- Registrar histórico.

Acesso:

- Apenas Administrador.

---

# GitHub

Autenticação recomendada:

- Deploy key somente leitura para `git fetch`.
- Fine-grained token somente leitura para consultar releases, se necessário.

Não usar senha de usuário.

---

# Fases de Implementação

## Fase 1 - Consulta e planejamento

- Tela mostra versão atual.
- Tela consulta releases disponíveis.
- Tela gera plano de atualização.
- Atualização executada por script operacional.

## Fase 2 - Execução assistida

- Tela executa backup obrigatório.
- Tela dispara script de atualização.
- Tela acompanha status e histórico.

## Fase 3 - Automação com rollback

- Rollback documentado e parcialmente automatizado.
- Healthcheck bloqueia conclusão em caso de falha.
- Histórico detalhado de cada etapa.

---

# Fluxo de Atualização Planejado

```text
1. obter versão atual
2. consultar GitHub Releases
3. selecionar release
4. gerar backup SQL
5. validar backup
6. git fetch
7. checkout da tag
8. pip install -r requirements.txt
9. rodar migrations
10. reiniciar o3cloud-manager.service
11. executar healthcheck
12. registrar resultado
```

---

# Histórico de Atualizações

Campos esperados:

```text
id
versao_anterior
versao_nova
commit_anterior
commit_novo
status
iniciado_em
finalizado_em
executado_por
backup_id
mensagem
log_resumido
```

---

# Regras de Segurança

- Apenas Administrador pode acessar.
- Atualização exige backup válido.
- Apenas releases/tags permitidas podem ser instaladas.
- Não instalar diretamente `develop` em produção oficial.
- Registrar toda tentativa, sucesso ou falha.

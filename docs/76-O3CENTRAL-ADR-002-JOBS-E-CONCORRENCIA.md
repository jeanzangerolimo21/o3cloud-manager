# ADR-002 - Jobs, locks e concorrencia do O3Central

Status: ACEITO em 2026-10-30.

## Contexto

Gunicorn executa multiplos workers. Um loop iniciado na criacao da aplicacao
seria duplicado em cada worker, provocando processamento concorrente e efeitos
repetidos. O prototipo FastAPI possui monitor em background, mas esse desenho
nao deve ser copiado para o Manager.

## Decisao

- Requests curtos permanecem no Flask/Gunicorn.
- Tarefas periodicas usam comandos Flask/CLI chamados por cron ou systemd timer.
- Cada job adquire lock nomeado no MariaDB com timeout curto.
- Jobs sao idempotentes, processam lotes limitados e podem ser repetidos.
- Execucao e resultado aparecem em `o3central_jobs_execucoes` e logs.

## Jobs iniciais

| Job | Frequencia inicial | Funcao |
|---|---:|---|
| o3central-presenca | 1 minuto | marcar gateway/terminal offline |
| o3central-tickets | 5 minutos | expirar tickets e idempotencias |
| o3central-reconciliar-vms | 15 minutos | detectar divergencia de VM/IP |
| o3central-retencao | diario | remover payload temporario conforme politica |
| o3central-alertas | 5 minutos | gerar alertas operacionais sem duplicar |

Frequencias sao configuraveis; nao devem vir de request do usuario.

## Lock

Nome definido: `o3central-job:<job_key>`. Adquirir com `GET_LOCK`, registrar
owner e sempre executar `RELEASE_LOCK` em `finally`. Se lock estiver ocupado, a
execucao termina com status `IGNORADO`, nao como erro.

## Idempotencia

- Atualizacoes usam estado esperado e timestamps.
- Alertas possuem chave natural de deduplicacao.
- Expiracao usa `WHERE status='ATIVO' AND expires_at <= NOW()`.
- Lotes usam ordem estavel e limite.
- Falha no meio preserva itens ja transacionados e permite reexecucao.

## Timeouts e observabilidade

Cada job define tempo maximo, contadores lidos/alterados/erros, request/correlation
ID e mensagem sanitizada. Zabbix deve alertar por ultima execucao, duracao e
falhas consecutivas. Logs nunca incluem tokens ou politicas completas.

## Implantacao

Usar systemd timers chamando comandos Flask/CLI. O instalador/atualizador deve
instalar unidades e timers idempotentemente e validar o comando em modo dry-run.

## Alternativas rejeitadas

- thread em cada worker Gunicorn;
- job disparado por acesso a pagina;
- lock apenas em arquivo `/tmp` sem consciencia entre hosts;
- fila distribuida antes de existir demanda que justifique sua operacao.

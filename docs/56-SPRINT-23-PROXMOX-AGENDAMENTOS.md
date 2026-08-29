# Sprint 23 - Agendamento de Upgrade CPU/Memória Proxmox

## Entregue

- Menu/permissão `proxmox_agendamentos` em Infraestrutura.
- Rotas em `/infraestrutura/agendamentos` para listar, filtrar, criar, visualizar e cancelar agendamentos.
- Primeira versão limitada a VM QEMU, CPU e memória.
- Persistência em `proxmox_agendamentos` e timeline em `proxmox_agendamentos_eventos`.
- Conflito bloqueado para dois agendamentos ativos da mesma VM.
- Cancelamento permitido apenas enquanto o status estiver `AGENDADO`.
- Execução fora da request web via comando `flask proxmox-agendamentos-processar` ou script `python -m scripts.processar_agendamentos_proxmox`.
- Worker com claim atômico, revalidação no Proxmox, shutdown gracioso, aplicação de `cores`/`memory`, validação final e start automático quando configurado.
- E-mail para o usuário criador ao cadastrar o agendamento, quando o worker inicia a execução e ao finalizar com sucesso ou falha.

## Operação

Executar a cada minuto no cron/systemd timer:

```bash
cd /opt/o3cloud-manager
venv/bin/flask proxmox-agendamentos-processar --limite 5
```

O arquivo `deployment/o3cloud-manager.cron` inclui a chamada a cada minuto para processar agendamentos vencidos.

Também disponível:

```bash
cd /opt/o3cloud-manager
venv/bin/python -m scripts.processar_agendamentos_proxmox
```

## Limites desta versão

- Não altera disco, storage, rede, snapshots, migração ou LXC.
- Não remove locks do Proxmox; se a VM possuir lock, o agendamento entra em `ERRO`.
- Se a VM for localizada em outro node no momento da execução, o agendamento entra em `ERRO` para evitar alteração no destino errado.
- Redução de CPU/memória é bloqueada nesta primeira versão; apenas upgrade.

## Validações locais realizadas

- `py_compile` dos módulos novos e arquivos alterados.
- `git diff --check` nos arquivos da Sprint 23.
- Migration `120_create_proxmox_agendamentos.sql` aplicada localmente.
- Rotas Flask carregadas:
  - `/infraestrutura/agendamentos`
  - `/infraestrutura/agendamentos/novo`
  - `/infraestrutura/agendamentos/<id>`
  - `/infraestrutura/agendamentos/<id>/cancelar`
- Comando `venv/bin/flask proxmox-agendamentos-processar --limite 1` executado sem pendências.

## Teste que depende de ambiente real

A execução completa contra Proxmox real precisa ser validada em uma VM de teste, porque envolve shutdown/start e `PUT /nodes/{node}/qemu/{vmid}/config`.

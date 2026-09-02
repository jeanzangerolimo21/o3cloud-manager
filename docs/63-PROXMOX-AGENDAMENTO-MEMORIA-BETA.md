# Proxmox: agendamento de upgrade de memoria no Beta

Data: 2026-09-02

## Contexto

A tela `Novo Agendamento Proxmox` ja possuia campo para CPU total desejada e memoria total desejada, e o executor ja aplicava `memory` no Proxmox. A validacao de criacao, porem, ainda possuia mensagens antigas da primeira versao e podia confundir upgrade de memoria com restricao de CPU.

## Ajuste implementado

- O agendamento aceita upgrade apenas de memoria, apenas de CPU, ou CPU e memoria juntos.
- CPU em branco continua significando `sem alteracao`.
- Memoria em branco continua significando `sem alteracao`.
- Downgrade segue bloqueado por seguranca operacional.
- As mensagens antigas `Esta primeira versao permite apenas upgrade de CPU/memoria` foram substituidas por mensagens explicitas de downgrade:
  - `CPU total desejada é menor que a CPU atual...`
  - `Memória total desejada é menor que a memória atual...`
- Adicionado teste automatizado para agendamento com CPU em branco e memoria maior que a atual.
- A tela passa a ajustar os valores minimos dos campos desejados conforme a CPU/memoria atuais da VM selecionada, reduzindo envio acidental de downgrade.

## Atualizacao do Beta

1. Atualizar o codigo da branch `beta`.
2. Recarregar o Gunicorn do O3Cloud Manager.
3. Abrir `Infraestrutura > Agendamentos > Novo Agendamento Proxmox`.
4. Selecionar a VM QEMU.
5. Deixar `CPU total desejada` em branco.
6. Informar `Memória total desejada (GB)` maior que a memoria atual.
7. Salvar o agendamento.

## Validacao

Executar:

```bash
venv/bin/python -B -m pytest tests/test_proxmox_agendamento_service.py
```

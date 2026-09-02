# Proxmox: cron dos agendamentos no Beta

Data: 2026-09-02

## Contexto

O agendamento Proxmox estava sendo criado corretamente e o comando manual abaixo processava a fila com sucesso:

```bash
cd /opt/o3cloud-manager
O3_LOG_DIR=/tmp/o3cloud-manager-logs venv/bin/flask --app app:create_app proxmox-agendamentos-processar --limite 5
```

No Beta, o arquivo instalado em `/etc/cron.d/o3cloud-manager` estava desatualizado e nao continha a linha do worker `proxmox-agendamentos-processar`. Por isso agendamentos vencidos permaneciam como `AGENDADO` ate execucao manual.

## Ajuste implementado

- `deployment/update-beta.sh` passa a reinstalar `deployment/o3cloud-manager.cron` em `/etc/cron.d/o3cloud-manager` durante a atualizacao do Beta.
- A instalacao usa owner `root:root` e permissao `0644`, formato esperado para arquivos em `/etc/cron.d`.
- Apos copiar o arquivo, o script tenta recarregar o servico `cron` e, se necessario, reinicia o servico.
- O arquivo versionado `deployment/o3cloud-manager.cron` ja contem a rotina a cada minuto:

```cron
* * * * * o3cloud cd /opt/o3cloud-manager && mkdir -p /tmp/o3cloud-manager-logs && O3_LOG_DIR=/tmp/o3cloud-manager-logs /opt/o3cloud-manager/venv/bin/flask --app app:create_app proxmox-agendamentos-processar --limite 5 >> /tmp/o3cloud-manager-logs/proxmox-agendamentos-cron.log 2>&1
```

## Correcao imediata no Beta atual

Depois de atualizar o codigo, reinstalar o runner e executar a atualizacao normal:

```bash
sudo /opt/o3cloud-manager/deployment/install-update-runner.sh
sudo /usr/local/sbin/o3cloud-update-beta
```

Se precisar corrigir o cron imediatamente, sem aguardar novo fluxo de update:

```bash
cd /opt/o3cloud-manager
sudo install -o root -g root -m 0644 deployment/o3cloud-manager.cron /etc/cron.d/o3cloud-manager
sudo systemctl reload cron || sudo systemctl restart cron
tail -n 3 /etc/cron.d/o3cloud-manager
```

## Validacao

1. Confirmar que `/etc/cron.d/o3cloud-manager` contem a linha `proxmox-agendamentos-processar`.
2. Criar um agendamento Proxmox para poucos minutos a frente.
3. Aguardar a virada do minuto seguinte ao horario agendado.
4. Verificar o log:

```bash
tail -120 /tmp/o3cloud-manager-logs/proxmox-agendamentos-cron.log
```

5. Confirmar que o agendamento saiu de `AGENDADO` para `CONCLUIDO` ou `FALHOU`, com evento gravado na tela de detalhe.

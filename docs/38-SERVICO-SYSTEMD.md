# O3Cloud Manager

# Serviço systemd

## Objetivo

Executar o O3Cloud Manager como daemon Linux gerenciado pelo `systemd`, sem depender de terminal aberto e sem usar `python app.py` em modo debug.

O serviço oficial utiliza `gunicorn`, já declarado em `requirements.txt`, e roda com o usuário de aplicação `o3cloud`.

## Arquivos

```text
wsgi.py
deployment/o3cloud-manager.service
deployment/install-systemd-service.sh
```

## Instalação

A instalação deve ser feita como `root`, porque grava o unit file em `/etc/systemd/system` e gerencia o serviço.

```bash
cd /opt/o3cloud-manager
deployment/install-systemd-service.sh
```

Mesmo executado por `root`, o processo da aplicação roda como `o3cloud`, definido no unit file:

```ini
User=o3cloud
Group=o3cloud
```

## Comando de produção

O unit file inicia a aplicação com:

```bash
/opt/o3cloud-manager/venv/bin/gunicorn --workers 3 --timeout 300 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - wsgi:app
```

## Habilitação no boot

O script de instalação já executa:

```bash
systemctl daemon-reload
systemctl enable o3cloud-manager.service
systemctl restart o3cloud-manager.service
```

Validação manual:

```bash
systemctl is-enabled o3cloud-manager.service
systemctl status o3cloud-manager.service --no-pager
ps -ef | grep gunicorn
ss -ltnp | grep ':5000'
```

O esperado é que os processos `gunicorn` apareçam com usuário `o3cloud`.

## Encerramento de processos manuais

Antes de iniciar o daemon, encerre processos manuais antigos que estejam ocupando a porta `5000`, especialmente `python app.py` iniciado como `root` ou em modo debug.

Exemplo:

```bash
ps -ef | grep 'python app.py'
kill <pid>
```

## Logs e permissões

O serviço usa:

```ini
Environment=O3_LOG_DIR=/opt/o3cloud-manager/logs
```

O script corrige permissões antes de reiniciar:

```bash
chown -R o3cloud:o3cloud /opt/o3cloud-manager/logs
chmod 0750 /opt/o3cloud-manager/logs
find /opt/o3cloud-manager/logs -type f -name "*.log" -exec chown o3cloud:o3cloud {} + -exec chmod 0640 {} +
```

Regra operacional: não iniciar a aplicação com `sudo python app.py`, pois arquivos de log criados ou rotacionados por esse processo passam a pertencer a `root`.

## Requisitos

`gunicorn` deve permanecer declarado em `requirements.txt`. Atualmente:

```text
gunicorn==26.0.0
```

# Email de Faturamento da Implantacao - Beta

Data: 01/09/2026

## Objetivo

Atualizar o destinatario da notificacao financeira enviada ao finalizar uma implantacao, alinhando o fluxo operacional ao novo e-mail de faturamento.

## Fluxos impactados

A alteracao se aplica a dois pontos do modulo `Implantacao`:

- Envio automatico quando a implantacao e movida para a coluna `Finalizado` no Kanban.
- Reenvio manual pelo botao `Notificar financeiro`, exibido na tela da implantacao quando a etapa esta como `Finalizado`.

## Ajuste realizado

O destinatario fixo da notificacao financeira foi alterado de:

```text
contas@o3cloud.com.br
```

para:

```text
faturamento@o3cloud.com.br
```

O endereco passou a ficar centralizado em `EMAIL_FINANCEIRO_IMPLANTACAO`, usado pelo envio, historico, logs, flash de sucesso e confirmacao do botao manual.

## Arquivos alterados

- `app/implantacao/service.py`
- `app/implantacao/routes.py`
- `app/templates/implantacao/view.html`

## Banco de dados

Esta entrega nao cria migration nova.

## Validacao tecnica

Executado em 01/09/2026:

```bash
python3 -B -m py_compile app/implantacao/service.py app/implantacao/routes.py
venv/bin/python -B -m pytest tests/test_implantacao_comentario_anexos_email.py tests/test_implantacao_checklist_lote.py tests/test_implantacao_sync_dedup.py
```

Resultado: 9 testes passaram.

## Validacao pos-atualizacao

1. Atualizar o Beta com `git pull origin beta`.
2. Reiniciar o servico da aplicacao.
3. Abrir uma implantacao em etapa `Finalizado`.
4. Acionar `Notificar financeiro` e confirmar que a mensagem visual referencia `faturamento@o3cloud.com.br`.
5. Mover uma implantacao para `Finalizado` no Kanban e confirmar o disparo automatico para `faturamento@o3cloud.com.br`.

## Atualizacao Beta

```bash
cd /opt/o3cloud-manager
git pull origin beta
sudo systemctl restart o3cloud-manager.service
deployment/healthcheck.sh
```

# Reajustes Contratuais - Email Consolidado Beta

Data: 01/09/2026

## Objetivo

Evitar timeout no Flask e excesso de mensagens ao executar `Verificar agora` em `Financeiro > Reajustes Contratuais`.

## Problema

A rotina de verificacao enviava um e-mail para cada contrato alertavel. Em uma execucao com muitos contratos vencidos ou proximos do aniversario, a requisicao web permanecia aberta enquanto varios envios SMTP eram feitos, aumentando o risco de timeout e gerando muitos e-mails para os mesmos destinatarios.

## Ajuste realizado

A rotina passou a consolidar os alertas da execucao em um unico e-mail com um arquivo CSV anexo.

O CSV separa os contratos por grupo:

- `Vencidos`
- `Proximos 30 dias`

O arquivo inclui contrato, cliente, inicio da vigencia, proximo aniversario, dias restantes, situacao, valor atual, valor INPC estimado, prejuizo estimado, vendedor e link do contrato.

A deduplicacao operacional foi preservada: cada contrato continua registrando seu alerta em `contratos_reajustes_alertas`, mas o campo `email_enviado_em` passa a ser marcado depois do envio consolidado bem-sucedido.

## Arquivos alterados

- `app/financeiro/reajuste_service.py`
- `tests/test_reajuste_contrato_service.py`

## Banco de dados

Esta entrega nao cria migration nova.

## Validacao tecnica

Executado em 01/09/2026:

```bash
python3 -B -m py_compile app/financeiro/reajuste_service.py app/financeiro/routes.py app/cli.py
venv/bin/python -B -m pytest tests/test_reajuste_contrato_service.py
```

Resultado: 16 testes passaram.

## Validacao pos-atualizacao

1. Atualizar o Beta com `git pull origin beta`.
2. Reiniciar o servico da aplicacao.
3. Abrir `Financeiro > Reajustes Contratuais`.
4. Clicar em `Verificar agora`.
5. Confirmar que os destinatarios configurados recebem apenas um e-mail da execucao.
6. Confirmar que o anexo CSV contem os contratos vencidos e os contratos a vencer nos proximos 30 dias.

## Atualizacao Beta

```bash
cd /opt/o3cloud-manager
git pull origin beta
sudo systemctl restart o3cloud-manager.service
deployment/healthcheck.sh
```

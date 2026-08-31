# Melhorias Beta - 31/08/2026

## Objetivo

Registrar o pacote de ajustes liberado para atualizacao do Beta em 31/08/2026, cobrindo sincronismo Proxmox, navegacao de retorno nas telas operacionais e envio de e-mails em Pagamento Campanhas.

## 1. Proxmox - Sincronismo de Inventario

### Problema

O sincronismo do inventario Proxmox falhava no Beta com a mensagem:

```text
Falha ao sincronizar inventario Proxmox: Not all parameters were used in the SQL statement
```

### Ajuste

O `INSERT` em `proxmox_vm_inventory` foi corrigido para ter placeholder correspondente ao campo `raw_payload`, mantendo `ativo=1` e `ultimo_sync_em=NOW()` como valores fixos.

### Validacao

Execucao real contra a integracao Proxmox `2` retornou:

```text
Sincronismo Proxmox read-only concluido. Recursos lidos: 235.
```

A tabela `proxmox_vm_sync_execucoes` registrou a execucao `OK`, com 235 recursos lidos e 235 atualizados.

## 2. Navegacao - Retorno Inteligente

### Problema

Botoes de retorno baseados no historico do navegador podiam voltar para etapas intermediarias, como `novo` ou `editar`, em vez de voltar para a ultima listagem operacional atualizada.

### Ajuste

Foi adicionada navegacao inteligente no JavaScript global:

- Listagens e telas operacionais gravam a URL atual no `sessionStorage`.
- Telas transitórias como `novo`, `editar`, `importar` e detalhes com ID nao sobrescrevem o destino salvo.
- O botao global `Voltar Inicio` usa a ultima URL operacional salva e preserva filtros/query string.
- Botoes locais `Voltar` passam a usar a mesma regra, mantendo o `href` original como fallback.

### Exemplo

```text
Cofre de Senhas ?pasta_id=10
-> Nova Credencial
-> Editar Credencial apos salvar
-> Voltar Inicio
-> Cofre de Senhas ?pasta_id=10 atualizado
```

## 3. Parceiros - Executivos

### Ajuste

A tela `Parceiros > Executivos` recebeu botao secundario no cabecalho para voltar para a listagem geral de parceiros.

- Quando acessada por `/parceiros/<id>/executivos`, o botao exibido e `Voltar Parceiros`.
- Quando acessada por `/parceiros/executivos`, o botao exibido e `Parceiros`.
- Ambos direcionam para `/parceiros/`.

## 4. Pagamento Campanhas - Destinatarios Extras

### Problema

O formulario de e-mail exibia os destinatarios vindos do cadastro/Omie, mas o campo estava bloqueado e nao permitia adicionar outros e-mails antes do envio.

### Ajuste

Em `Financeiro > Premiacoes > Pagamento Campanhas`, o campo `Destinatarios` passou a ser editavel:

- Mantem preenchidos os e-mails ja encontrados no parceiro/Omie.
- Permite adicionar destinatarios extras separados por virgula, ponto e virgula ou espaco.
- Permite envio mesmo quando o parceiro nao possui e-mail cadastrado, desde que o usuario informe manualmente um destinatario valido.
- O backend mescla destinatarios cadastrados e manuais, normaliza para minusculas, remove duplicados e valida formato.

## Validacao Tecnica

Executado em 31/08/2026:

```bash
python3 -B -m py_compile app/financeiro/service.py app/financeiro/routes.py app/parceiros/routes.py app/__init__.py
venv/bin/python -B -c "from app.financeiro.service import FinanceiroService; print(FinanceiroService._destinatarios_pagamento_campanha(['base@dominio.com'], 'extra@dominio.com; base@dominio.com outro@dominio.com'))"
deployment/healthcheck.sh
```

Resultados:

- Compilacao Python sem erros.
- Template `financeiro/pagamento_campanhas.html` carregado pela aplicacao Flask sem erro.
- Mesclagem de destinatarios validada com remocao de duplicidade.
- E-mail invalido retorna `ValueError` antes do envio.
- Healthcheck local OK: servico ativo, banco respondendo e HTTP 200 em `/login`.

## Atualizacao Beta

Apos o `git pull` no servidor Beta, reiniciar o servico para carregar JavaScript, templates e services atualizados:

```bash
cd /opt/o3cloud-manager
git pull origin beta
sudo systemctl restart o3cloud-manager.service
deployment/healthcheck.sh
```

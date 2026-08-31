# Pagamento Campanhas - Premiacoes Beta

Data: 30/08/2026

## Objetivo

Criar uma tela de apoio ao Contas a Pagar para conferir, simular, gerar recibos e enviar e-mails de pagamento de premiacoes por campanha, parceiro e executivo.

## Tela

A nova tela fica em:

```text
Financeiro > Premiações > Pagamento Campanhas
/financeiro/pagamento-campanhas
```

Tambem foi adicionado um botao no topo de `Financeiro > Premiações`, ao lado de `Faturamento` e `Regras Campanhas`.

## Regra de cálculo

- Entram no contas a pagar padrao somente premiacoes com status manual `Lançado`.
- Premiacoes com status `Aberto` nao entram no calculo de pagamento.
- Premiacoes com status `Pago` sao tratadas como ja pagas e ficam disponiveis apenas para conferencia pelo filtro de status.
- Contratos entram somente quando o primeiro titulo/parcela do Omie esta conciliado como recebido, pago ou liquidado e sem categoria excluida.
- Adendos entram pela premiacao manual ja lancada, respeitando o status manual informado.

## Filtros

A tela permite simular antes do envio por:

- Busca por cliente, contrato, parceiro, executivo ou campanha.
- Campanha.
- Parceiro.
- Periodo de recebimento.
- Status da premiacao.
- Inclusao ou exclusao de adendos.


## Vinculo de executivo

A comparação entre `Projeto OMIE` e o cadastro de executivo ignora diferença de maiúsculas/minúsculas. Exemplo: `LUIZ PAULO BONFIM DE SOUZA` no Omie casa com `Luiz Paulo Bonfim de Souza` no cadastro do O3Cloud Manager.

Quando o `Projeto OMIE` estiver preenchido mas nao localizar executivo ativo com premiacao habilitada, o sistema usa o executivo vinculado manualmente ao contrato, se existir.

## Agrupamento

Os resultados sao agrupados por campanha e parceiro. Dentro de cada grupo a tela exibe os contratos/adendos e os executivos vinculados com valores de premiacao.

## Relatorios e recibos

Os botoes de relatorio geral do cabecalho ignoram os filtros de campanha, parceiro, executivo e busca, consolidando todos os parceiros em um unico CSV ou PDF. Os botoes dentro de cada grupo continuam separados por campanha e parceiro.

Os PDFs exibem o logo institucional da O3 Cloud e, quando cadastrado, o logo do parceiro. O email em HTML tambem embute os dois logos quando os arquivos estiverem disponiveis. O CSV permanece em formato tabular para importacao e conferencia.


Foram adicionadas as opcoes:

- Relatorio CSV geral.
- Relatorio PDF geral.
- Recibo PDF por parceiro.
- Recibo PDF por executivo.

Os recibos incluem:

- Campanha.
- Parceiro.
- Executivo, quando for recibo de executivo.
- Contrato.
- Cliente.
- Data de recebimento no Omie, quando houver.
- Data de ativacao do contrato.
- Valor base.
- Valor de premiacao do parceiro.
- Valor de premiacao do executivo.

## E-mail

A tela permite abrir um formulario de envio por parceiro, com:

- Assunto editavel.
- Campo `Destinatarios` editavel, preenchido inicialmente com os e-mails cadastrados do parceiro/Omie.
- Inclusao manual de destinatarios extras separados por virgula, ponto e virgula ou espaco.
- Mesclagem no backend entre destinatarios cadastrados e extras, com normalizacao, remocao de duplicados e validacao de formato.
- Corpo de e-mail editavel.
- Variaveis aceitas: `{parceiro}`, `{campanha}`, `{periodo}`, `{total}`, `{total_parceiro}`, `{total_executivo}`.
- Anexo automatico do recibo do parceiro.
- Anexos automaticos dos recibos dos executivos vinculados ao parceiro na campanha filtrada.

O envio usa a finalidade de e-mail:

```text
PAGAMENTO_CAMPANHAS
```

O cadastro de `Serviços de Email` passou a exibir a finalidade `Pagamento de campanhas`. Pela tela de pagamento ha um atalho para novo SMTP com remetente sugerido:

```text
contas@o3cloud.com.br
```

## Banco de dados

Nao houve nova tabela nesta entrega. A tela reaproveita:

- `financeiro_recebimentos`
- `financeiro_premiacoes_pagamento`
- `financeiro_premiacoes_adendos`
- `regras_campanhas_comissao`
- `config_email_servicos`

## Validacao tecnica

Executado em 30/08/2026:

```bash
venv/bin/python -B -m pytest tests/test_financeiro_premiacoes_service.py tests/test_contrato_dashboard_repository.py tests/test_contrato_service_omie_sync.py tests/test_proposta_instalacao_recursos.py -q
python3 -B -m py_compile app/financeiro/routes.py app/financeiro/service.py app/financeiro/repository.py app/configuracoes/email_service.py app/configuracoes/routes.py app/core/access_control.py
```

Resultado: 26 testes passaram.

Tambem foi validada consulta real local da nova tela, com 2 itens lançados para pagamento e total de R$ 653,94, alem da geracao real de PDF iniciando com `%PDF`.

## Validacao pos-atualizacao

1. Cadastrar ou ativar um SMTP em `Configurações > Serviços de Email` com finalidade `Pagamento de campanhas` e remetente `contas@o3cloud.com.br`.
2. Abrir `Financeiro > Premiações` e marcar uma premiacao recebida como `Lançado`.
3. Abrir `Pagamento Campanhas`.
4. Confirmar que a premiacao marcada como `Lançado` aparece no contas a pagar.
5. Confirmar que itens `Aberto` nao aparecem no filtro padrao.
6. Usar o filtro `Pago` apenas para conferencia de itens ja pagos.
7. Gerar relatorio CSV/PDF.
8. Gerar recibo de parceiro e recibo de executivo.
9. Editar destinatarios e corpo do e-mail, mantendo os e-mails cadastrados e adicionando um destinatario extra de teste.
10. Enviar para o parceiro com anexos e confirmar que a mensagem de sucesso lista todos os destinatarios enviados.

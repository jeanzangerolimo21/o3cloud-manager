# Melhorias Beta - 27/08/2026

Status: Documentado

Branch: `beta`

---

# Objetivo

Registrar o pacote de melhorias operacionais liberado para atualizacao do Beta em 27/08/2026, cobrindo Cofre de Senhas, Ambientes, Premiacoes, Reajustes Contratuais e comentarios de Implantacao.

---

# 1. Cofre de Senhas

## Pesquisa em campos vinculados

O formulario de nova/edicao de credencial passou a usar o mesmo padrao pesquisavel do campo Cliente tambem para:

- Ambiente do cliente
- Implantador
- Faixa de rede
- Licenca O3Web

Os campos continuam gravando os identificadores originais esperados pelo backend e preservam os comportamentos de preenchimento automatico ja existentes, como URL da licenca e implantador sugerido pelo ambiente.

## Anexos da credencial

A edicao da credencial passou a permitir excluir arquivos vinculados quando forem anexados incorretamente.

A tela principal do Cofre passou a listar os arquivos vinculados como links clicaveis para download diretamente abaixo do titulo da credencial.

---

# 2. Ambientes

A opcao `Implantacao` foi removida da lista padrao de `Situacao`, pois esse conceito ja existe em `Tipo`.

Para compatibilidade, ambientes antigos que ja estiverem salvos com situacao `IMPLANTACAO` continuam exibindo essa opcao selecionada ao editar, evitando alteracao involuntaria de dados historicos.

---

# 3. Premiacoes

## Checagem manual de pagamento

A tela `Financeiro > Premiacoes` recebeu controle manual de pagamento da premiacao com as opcoes:

- Aberto
- Lancado
- Pago

A selecao aparece somente para contratos com status financeiro `Recebido` pelo sistema. Contratos atrasados ou nao localizados nao exibem o controle.

A alteracao e salva automaticamente por AJAX, sem botao Salvar.

## Filtro por campanha vigente

A listagem de Premiacoes passou a exibir somente contratos cuja data de inicio de vigencia se encaixa em uma campanha ativa. Contratos fora de qualquer campanha deixam de aparecer nessa tela, reduzindo ruido operacional.

## Persistencia

Criada a migration:

- `database/migrations/114_create_financeiro_premiacoes_pagamento.sql`

A tabela `financeiro_premiacoes_pagamento` persiste o status manual por `contrato_id + campanha_id`.

---

# 4. Reajustes Contratuais

A tela `Financeiro > Reajustes Contratuais` recebeu botao manual para sincronizar Faturamento e Previsoes do Omie.

O sincronismo usa o tipo `OMIE_FATURAMENTO_PREVISOES`, reaproveitando a infraestrutura de sincronismos agendados, e importa contas a receber recebidas ou previstas sem exigir nota fiscal para esse fluxo especifico.

## Regra de corte

O calculo de reajustes considera faturamentos a partir de `01/03/2026`, conforme a constante `DATA_CORTE_CALCULO = date(2026, 3, 1)` em `ReajusteContratoService`.

Faturamentos anteriores a essa data sao ignorados na analise de ciclos e prejuizo estimado, preservando a regra operacional definida para esta frente.

## Analise operacional

A tela passou a separar contratos ativos de contratos inativos, suspensos, encerrados ou cancelados.

Para contratos ativos, a analise exibe tempo sem reajuste, valor estimado por INPC, prejuizo estimado, proximo aniversario e situacao. Para contratos inativos, o historico fica separado para consulta, sem misturar com a carteira ativa.

---

# 5. Comentarios de Implantacao

Na visualizacao do Card de Implantacao, o comentario agora permite escolher se os arquivos anexados tambem devem ser enviados no e-mail.

O fluxo ficou assim:

1. O comentario e registrado no historico.
2. Os anexos sao salvos no historico do comentario.
3. Se `Enviar comentario por e-mail` estiver marcado, o e-mail e enviado.
4. Se `Enviar arquivos anexados junto no e-mail` tambem estiver marcado, os arquivos salvos seguem como anexos do e-mail.
5. O resultado do envio e atualizado no historico apos o envio.

A opcao de enviar anexos fica desabilitada enquanto o envio de e-mail nao estiver marcado.

---

# 6. Validacoes executadas

- `python3 -B -m compileall app/financeiro app/implantacao app/repositories app/core`
- Parse Jinja de `app/templates/financeiro/comissoes.html`
- Parse Jinja de `app/templates/financeiro/reajustes_contratuais.html`
- Parse Jinja de `app/templates/implantacao/view.html`
- Parse Jinja de `app/templates/implantacao/cofre_senhas/form.html`
- Parse Jinja de `app/templates/implantacao/cofre_senhas/index.html`
- Parse Jinja de `app/templates/ambientes/form.html`
- `venv/bin/python -B -m pytest tests/test_financeiro_premiacoes_service.py`
- `venv/bin/python -B -m pytest tests/test_implantacao_comentario_anexos_email.py`
- `venv/bin/python -B -m pytest tests/test_cofre_senhas_service.py`
- `venv/bin/python -B -m pytest tests/test_reajuste_contrato_service.py`

---

# 7. Atualizacao do Beta

No servidor Beta, executar o fluxo oficial de atualizacao da branch `beta`.

A migration `114_create_financeiro_premiacoes_pagamento.sql` deve ser aplicada para liberar a checagem manual de pagamento das premiacoes.

Observacao operacional: no ambiente local de desenvolvimento, o runner geral de migrations encontrou migrations antigas ja aplicadas fisicamente no banco mas nao registradas em `schema_migrations`. Por isso a migration `114` foi aplicada e registrada manualmente neste ambiente.

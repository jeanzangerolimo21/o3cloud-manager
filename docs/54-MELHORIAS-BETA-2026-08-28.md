# Melhorias Beta - 28/08/2026

Status: Documentado

Branch: `beta`

Observacao: alteracoes mantidas apenas no workspace local. Nao houve commit nem push para o GitHub nesta etapa.

---

# Objetivo

Registrar as melhorias operacionais realizadas em 28/08/2026 para a versao Beta, com foco em remover referencias internas de Sprints das telas, corrigir exclusao de anexos no Cofre de Senhas e padronizar vinculos de Cliente/Empresa no CRM Comercial.

---

# 1. Remocao de Referencias de Sprint nas Telas

## Problema tratado

Algumas telas ainda exibiam referencias internas de desenvolvimento, como `Sprint 14` ou `Nesta sprint`, o que nao deve aparecer na versao Beta usada pela operacao.

## Mudancas implementadas

- `Clientes > Detalhe`: badge `Sprint 14` substituido por `Beta`.
- `Implantacao > Detalhe`: badge `Sprint 14` substituido por `Beta`.
- `Produtos por Cliente`: texto `Sprint 14 - leitura pre-Beta` substituido por `Leitura pre-Beta`.
- `Integracoes Tecnicas`: texto `Nesta sprint` substituido por `Nesta fase Beta`.

## Resultado operacional

As telas deixam de expor a organizacao interna de desenvolvimento e passam a usar linguagem adequada para homologacao Beta.

---

# 2. Cofre de Senhas - Exclusao de Anexos

## Problema tratado

Ao anexar um arquivo em uma credencial do Cofre de Senhas e tentar exclui-lo em seguida, a tela voltava para o menu principal/edicao da credencial, mas o arquivo permanecia vinculado.

## Causa identificada

O botao de exclusao do anexo estava dentro do formulario principal de edicao da credencial, criando formulario aninhado. Esse HTML invalido fazia o navegador submeter o formulario de edicao em vez da rota especifica de exclusao do anexo.

## Mudancas implementadas

- O botao de exclusao do anexo passou a usar o atributo `form` apontando para um formulario externo proprio.
- Os formularios de exclusao de anexos ficam fora do formulario principal da credencial.
- A rota `implantacao.excluir_anexo_senha_cofre` passa a receber corretamente o POST do botao de exclusao.

## Resultado operacional

Arquivos vinculados a credenciais podem ser removidos corretamente pela tela de edicao da credencial.

---

# 3. CRM Comercial - Vinculo de Contatos com Clientes

## Problema tratado

Em `CRM > Contatos > Novo Contato`, o campo `Empresa` era apenas texto livre. Isso impedia associar formalmente o contato ao cadastro de Clientes, fosse ele manual ou vindo do Omie.

## Mudancas implementadas

- Adicionado `cliente_id` em `crm_contatos`.
- Contatos passam a gravar vinculo direto com a tabela `clientes`.
- O service de Contatos valida se o cliente vinculado existe.
- Ao salvar contato com cliente selecionado, o campo textual `empresa` e atualizado como snapshot do nome fantasia/razao social.
- Listagem e detalhe de Contatos priorizam `cliente_exibicao` quando houver vinculo.
- O dropdown de contatos em Oportunidades passa a exibir o cliente vinculado ao contato quando existir.

## Migration adicionada

```text
database/migrations/115_add_cliente_id_crm_contatos.sql
```

Estrutura adicionada:

```text
crm_contatos.cliente_id BIGINT NULL
idx_crm_contatos_cliente_id
fk_crm_contatos_cliente -> clientes(id)
```

A migration tambem tenta vincular contatos existentes por correspondencia exata entre `crm_contatos.empresa` e `clientes.nome_fantasia` ou `clientes.razao_social`.

## Resultado operacional

O executivo pode cadastrar primeiro o cliente em `Cadastro Clientes` e depois associar esse cliente ao contato, preservando o relacionamento mesmo se o cliente manual for posteriormente sincronizado pelo Omie.

---

# 4. CRM Comercial - Empresa/Cliente em Oportunidades

## Problema tratado

Em `Oportunidades > Nova Oportunidade`, havia separacao entre campo textual `Empresa` e campo `Cliente Vinculado`, gerando duplicidade visual e risco de preenchimento inconsistente.

## Mudancas implementadas

- O campo principal passou a ser `Empresa / Cliente` baseado na tabela `clientes`.
- O seletor duplicado de `Cliente Vinculado` foi removido do bloco de relacionamento.
- Ao salvar oportunidade com `cliente_id`, o campo textual `empresa` e atualizado como snapshot do cliente selecionado.
- A validacao existente de `cliente_id` foi preservada.

## Resultado operacional

A oportunidade fica associada ao cadastro oficial do cliente, seja manual ou Omie, mantendo a compatibilidade com o campo textual legado.

---

# 5. Picker Reutilizavel de Cliente/Contrato

## Problema tratado

O padrao de selecao pesquisavel usado em `Ambientes > Novo Ambiente > Vinculos comerciais` precisava ser adotado em outras telas para evitar seletores longos ou campos texto soltos.

## Mudancas implementadas

- Criado componente reutilizavel:

```text
app/templates/components/search_picker_script.html
```

- `Ambientes > Formulario` passou a usar esse componente compartilhado em vez de manter o script inline.
- `Contatos > Novo/Editar` passou a usar o picker pesquisavel para `Empresa / Cliente`.
- `Oportunidades > Nova/Editar` passou a usar o picker pesquisavel para `Empresa / Cliente`.
- O picker suporta `data-picker-max="1"` para selecao unica.
- O picker suporta `data-picker-create-url` para direcionar o botao `+` a uma tela de novo cadastro.

## Comportamento do botao `+`

Nas telas de Contatos e Oportunidades, o botao `+` do campo `Empresa / Cliente` redireciona para:

```text
/clientes/novo
```

A selecao de cliente continua sendo feita ao digitar e clicar no resultado da busca, ou usando Enter no resultado selecionado.

## Resultado operacional

O padrao de vinculo por busca usado em Ambientes foi reaproveitado no CRM, e ficou preparado para ser expandido gradualmente para outras telas que vinculam clientes e contratos.

---

# 6. Sincronizacao Omie x Cadastro Manual

O comportamento existente de `ClienteRepository.upsert_omie()` foi revisado durante a melhoria.

Quando um cliente vindo do Omie chega com CNPJ ja existente em cadastro manual, o sistema atualiza o mesmo registro de `clientes`, altera os dados sincronizados e passa a origem para `OMIE`, mantendo o mesmo `id`.

Com os novos vinculos por `cliente_id`, contatos e oportunidades continuam apontando para o mesmo cliente, evitando duplicidade operacional.

---

# 7. Aplicacao no Banco Local

A migration `115_add_cliente_id_crm_contatos.sql` foi aplicada manualmente no banco local, pois o runner geral de migrations parou em uma migration antiga ja aplicada fisicamente no banco mas nao registrada em `schema_migrations`.

Confirmacoes realizadas no banco local:

```text
schema_migrations contem 115_add_cliente_id_crm_contatos.sql
crm_contatos.cliente_id criado
idx_crm_contatos_cliente_id criado
fk_crm_contatos_cliente criado
3 de 4 contatos existentes vinculados automaticamente por nome de empresa
388 clientes ativos disponiveis para os pickers
```

A aplicacao Gunicorn na porta `5000` foi recarregada com `HUP` para carregar os templates atualizados.

---

# 8. Validacoes Executadas

Validacoes com sucesso:

```text
venv/bin/python -B -m py_compile app/contatos/routes.py app/contatos/service.py app/repositories/contato_repository.py app/oportunidades/routes.py app/oportunidades/service.py app/repositories/oportunidade_repository.py
```

```text
Parse Jinja:
- app/templates/components/search_picker_script.html
- app/templates/ambientes/form.html
- app/templates/contatos/form.html
- app/templates/oportunidades/form.html
- app/templates/contatos/index.html
- app/templates/contatos/view.html
- app/templates/oportunidades/index.html
- app/templates/oportunidades/view.html
```

```text
venv/bin/python -B -m pytest tests/test_contrato_service_omie_sync.py tests/test_cofre_senhas_service.py
Resultado: 11 passed
```

Renderizacao com banco real:

```text
Contatos > Novo: 388 opcoes de cliente no HTML
Oportunidades > Nova: 388 opcoes de cliente no HTML
Botao + com destino /clientes/novo nas duas telas
```

Checagem de diff:

```text
git diff --check
Resultado: sem problemas de whitespace
```

## Observacao sobre suite completa

A suite completa foi executada e retornou:

```text
74 passed, 15 failed
```

As falhas ocorreram em areas fora deste pacote de CRM/Cofre/UI:

- `tests/test_atualizacao_service.py::test_github_release_recomendada_ignora_tag_atual`
- multiplos testes em `tests/test_reajuste_contrato_service.py` relacionados a `ReajusteContratoService`

Essas falhas nao passam pelos arquivos alterados neste pacote, mas permanecem como pendencia tecnica separada.

---

# 9. Proximos Pontos de Padronizacao

A auditoria de templates ainda encontrou telas com vinculo simples de cliente ou contrato que podem receber o mesmo picker em uma etapa futura, conforme necessidade operacional:

- `Contratos > Formulario`
- `Implantacao > Formulario`
- `Faixas de Rede`
- `Cofre de Senhas > Pastas`
- `Administrativo > ASO`
- filtros administrativos que usam seletores simples

O componente reutilizavel ja esta disponivel para essa evolucao.

# O3Cloud Manager v3.0

# Descoberta OMIE - Sprint 17

Data: 12/08/2026

Status: Evidência técnica inicial

---

# Fontes

- API real OMIE com credenciais configuradas no ambiente.
- Documentação oficial OMIE:
  - `https://developer.omie.com.br/service-list/`
  - `https://app.omie.com.br/api/v1/servicos/contrato/`
  - `https://app.omie.com.br/api/v1/financas/contareceber/`

---

# Contratos de Serviço

Endpoint:

```text
https://app.omie.com.br/api/v1/servicos/contrato/
```

Método:

```text
ListarContratos
```

Campos confirmados:

```text
cabecalho.nCodCtr      -> código externo do contrato
cabecalho.cNumCtr      -> número do contrato
cabecalho.cCodSit      -> status OMIE
cabecalho.dVigInicial  -> início de vigência
cabecalho.dVigFinal    -> fim de vigência
cabecalho.nValTotMes   -> valor mensal
infAdic.nCodVend       -> código do vendedor
infAdic.nCodProj       -> código do projeto
infAdic.nCodCC         -> centro de custo
infAdic.cDadosAdicNF   -> Dados Adicionais para a Nota Fiscal
observacoes.cObsContrato -> Observações de contrato que não serão exibidas na Nota Fiscal
```

Observação atualizada em 12/08/2026:

A documentação oficial do OMIE informa que `ListarContratos` aceita `cExibeObs` para retornar "Observação / Dados Adicionais" na listagem. Sem esse parâmetro, a API pode devolver `observacoes.cObsContrato` vazio mesmo quando a aba de observações do contrato possui conteúdo.

Validação real no contrato `2026/00199` do cliente `SUPERMERCADO CASTANHEIRA`:

```text
observacoes.cObsContrato -> Observações de contrato (não exibidas na Nota Fiscal)
infAdic.cDadosAdicNF     -> Dados Adicionais para a Nota Fiscal
```

Decisão: sincronizar somente `observacoes.cObsContrato` em `contratos.observacao_contrato`. Não misturar com `infAdic.cDadosAdicNF`.

---

# Itens do Contrato

Campos confirmados:

```text
itemCabecalho.quant          -> quantidade
itemCabecalho.valorUnit      -> valor unitário
itemCabecalho.valorTotal     -> valor total do item
itemCabecalho.valorDesconto  -> desconto do item
itemCabecalho.aliqDesconto   -> percentual de desconto
itemCabecalho.cTpDesconto    -> tipo de desconto
itemCabecalho.valorAcrescimo -> acréscimo do item
itemCabecalho.cCodCategItem  -> categoria do item
```

Decisão inicial:

- `valor_servicos_bruto` será calculado por `quant * valorUnit`.
- `valor_descontos` será calculado pela soma de `valorDesconto`.
- `valor_servicos_liquido` será calculado por `valor_servicos_bruto - valor_descontos`.
- O campo existente `valor_mensal` permanece preservado.

---

# Vendedores

Endpoint:

```text
https://app.omie.com.br/api/v1/geral/vendedores/
```

Método:

```text
ListarVendedores
```

Campos confirmados:

```text
cadastro[].codigo -> código do vendedor
cadastro[].nome   -> nome do vendedor
```

Decisão:

Durante sincronização de contratos, carregar vendedores em cache por execução para resolver `codigo_vendedor -> vendedor_nome`.

---

# Projetos

Endpoint:

```text
https://app.omie.com.br/api/v1/geral/projetos/
```

Método:

```text
ListarProjetos
```

Campos confirmados:

```text
cadastro[].codigo -> código do projeto
cadastro[].nome   -> nome do projeto
```

Decisão:

Durante sincronização de contratos, carregar projetos em cache por execução para resolver `codigo_projeto -> projeto_nome`.

---

# Contas a Receber

Endpoint:

```text
https://app.omie.com.br/api/v1/financas/contareceber/
```

Métodos:

```text
ListarContasReceber
ConsultarContaReceber
```

Campos confirmados:

```text
codigo_lancamento_omie      -> identificador único do título
codigo_cliente_fornecedor   -> código OMIE do cliente
cNumeroContrato             -> número do contrato do cliente
codigo_vendedor             -> código do vendedor
codigo_projeto              -> código do projeto
codigo_categoria            -> categoria principal
categorias[]                -> rateio de categorias
valor_documento             -> valor do título
status_titulo               -> status retornado
data_vencimento             -> vencimento
data_previsao               -> previsão
data_emissao                -> emissão
numero_documento            -> documento
numero_documento_fiscal     -> documento fiscal
numero_parcela              -> parcela
```

Resultado importante:

- A API não aceita `filtrar_por_status = RECEBIDO`.
- Filtros aceitos para títulos recebidos/liquidados: `PAGO` e `LIQUIDADO`.
- Mesmo usando `PAGO` ou `LIQUIDADO`, o campo retornado em `status_titulo` veio como `RECEBIDO`.

Vínculo técnico com contrato:

```text
conta_receber_cadastro[].cNumeroContrato -> contratos.numero
conta_receber_cadastro[].codigo_cliente_fornecedor -> clientes.codigo_externo
```

Decisão inicial:

Relacionar recebimento com contrato usando `cNumeroContrato` + cliente OMIE. Não relacionar apenas por descrição textual.


---

# Categorias

Endpoint:

```text
https://app.omie.com.br/api/v1/geral/categorias/
```

Método:

```text
ListarCategorias
```

Campos confirmados:

```text
categoria_cadastro[].codigo
categoria_cadastro[].descricao
categoria_cadastro[].descricao_padrao
```

Decisão:

Resolver `categoria_codigo -> categoria_nome` com cache por execução e aplicar normalização sem acento para excluir categorias contendo `SETUP` ou `IMPLANTACAO`.

---

# Resultado da Carga Inicial

Data da carga: 12/08/2026

Contratos:

```text
210 contratos OMIE atualizados
163 com vendedor_nome resolvido
39 com projeto_nome resolvido
210 com valor_servicos_bruto, valor_descontos e valor_servicos_liquido
```

Recebimentos:

```text
Filtro OMIE usado: filtrar_por_status=PAGO
Status retornado: status_titulo=RECEBIDO
Janela local aplicada: 14/05/2026 a 12/08/2026
Títulos persistidos na janela: 595
Títulos vinculados a contratos: 505
Categorias excluídas da comissão: 89
```

Observação sobre data:

A API documenta `filtrar_por_data_de` e `filtrar_por_data_ate` como filtros de inclusão/alteração, não como baixa financeira. Na amostra consultada, `recebimento.data` veio nulo para títulos recebidos. Por isso, a primeira implementação usa `data_previsao` como fallback de `data_recebimento` e filtra localmente a janela de 90 dias. Esse ponto deve permanecer visível para homologação financeira.

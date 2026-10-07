# Implantação Opcional por Adendo

## Objetivo

Permitir que um adendo de contrato ativo origine, por ação manual, uma nova implantação no Kanban. O fluxo atende expansões excepcionais, como novo servidor, novo ambiente, migração ou serviço adicional com setup, sem alterar o status do contrato principal no Omie.

## Fluxo funcional

1. O usuário cadastra o adendo no contrato e informa o valor de setup, quando aplicável.
2. Na linha do adendo, a ação `Criar implantação` abre os campos de planejamento.
3. A confirmação cria um card na etapa `Fila`, identificado como `Implantação de adendo`.
4. O card mantém vínculo com cliente, contrato principal e adendo.
5. Depois da criação, a ação é substituída por `Ver implantação`.
6. Uma implantação ativa por adendo é permitida. Repetições retornam a implantação existente.

## Dados iniciais

- Título sugerido a partir do adendo e cliente.
- Prioridade normal por padrão.
- Datas previstas opcionais.
- Observações e escopo herdados do adendo quando não informados.
- Valor de setup registrado no adendo e exibido na implantação.

## Regras

- O contrato principal permanece ativo e não muda para `ENCAMINHADO_PROJETO`.
- Nenhuma atualização é enviada ao Omie.
- A regra de uma implantação principal por contrato permanece no serviço.
- Implantações de adendo podem coexistir com implantação anterior ou ativa do cliente.
- A sincronização automática de contratos encaminhados ignora cards de adendo.
- Adendo com implantação vinculada não pode ser inativado.
- Todas as criações são registradas na auditoria.

## Modelo técnico

- `contratos_adendos.valor_setup`: setup específico do adendo.
- `implantacoes.adendo_id`: vínculo opcional com o adendo.
- `implantacoes.origem`: `CONTRATO` ou `ADENDO`.
- Índice único em `adendo_id` impede a criação de mais de uma implantação para o mesmo adendo; a regra da implantação principal permanece protegida pelo serviço.
- A migration é compatível com MariaDB sem suporte à expressão originalmente proposta em coluna gerada e pode ser retomada após execução parcial.

## Critérios de aceite

- Criar implantação a partir de adendo de contrato ativo.
- Card aparecer imediatamente na coluna `Fila`.
- Card e detalhe exibirem identificação, número, título e setup do adendo.
- Segunda tentativa abrir a implantação existente.
- Fluxos normais originados por contrato continuarem inalterados.

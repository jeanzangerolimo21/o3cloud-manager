# Melhorias Beta - 21/08/2026

Status: Documentado

Branch: `beta`

Commit de referencia: `1256ee3 Adiciona CS e agrupamento de implantacoes`

---

# Objetivo

Registrar as melhorias liberadas para a validacao Beta em 21/08/2026, cobrindo ajustes de propostas, licencas O3Web, Sucesso do Cliente e agrupamento de cards de implantacao.

---

# 1. Propostas Comerciais - Servidores em Blocos

## Problema tratado

Ao criar uma nova proposta, as acoes `Novo servidor` e `Servidor basico` adicionavam recursos junto ao servidor anterior, dificultando a separacao correta dos itens por servidor.

## Mudancas implementadas

- `Novo servidor` cria um novo bloco independente e deixa esse bloco selecionado.
- `Servidor basico` cria um bloco separado com os recursos padrao quando ja existe servidor cadastrado.
- Recursos deixam de ser adicionados implicitamente ao ultimo servidor sem selecao clara.
- O botao de inclusao de recurso foi renomeado de `Adicionar Servidor` para `Adicionar ao Servidor`.
- A tela passou a exigir uma selecao explicita do servidor de destino para incluir novos itens.

## Resultado operacional

A proposta passa a refletir corretamente varios servidores, cada um com seus proprios recursos, evitando mistura de itens entre servidores diferentes.

---

# 2. Licencas O3Web - Expiracao Automatica para Trial

## Problema tratado

A data de expiracao de licencas Trial precisava ser calculada manualmente a partir da data de ativacao e da quantidade de dias.

## Mudancas implementadas

- Ao selecionar `Trial`, informar `Data ativacao` e preencher `Dias`, a tela calcula `Data expiracao` automaticamente.
- O backend tambem calcula a expiracao ao salvar quando o campo estiver vazio.
- A data permanece editavel para ajustes manuais.
- O marcador `-` continua preservado para licencas permanentes ou casos sem expiracao controlada.

## Regra de calculo

```text
Data expiracao = Data ativacao + Dias
```

Exemplo validado:

```text
Data ativacao: 21/08/2026
Dias: 45
Data expiracao: 05/10/2026
```

---

# 3. CRM Comercial - Sucesso do Cliente

## Objetivo

Criar uma tela de Customer Success dentro do CRM Comercial para acompanhamento dos contratos ativos e do relacionamento com clientes.

## Dados exibidos

- Razao Social
- Nome Fantasia
- CNPJ
- Usuarios
- Vendedor OMIE
- Projeto OMIE
- Valor Bruto
- Observacoes do Contrato OMIE
- Contato vinculado do CRM Comercial

## Regras de curva

- Curva A: contratos com valor bruto maior ou igual a R$ 2.999,99.
- Curva B: contratos entre R$ 1.000,00 e abaixo de R$ 2.999,99.
- Curva C: contratos abaixo de R$ 1.000,00.

## Padrao visual das curvas

- Curva A: badge amarela.
- Curva B: badge cinza.
- Curva C: badge azul.

## Relacionamento CS

A tela permite registrar historico de relacionamento com os seguintes status:

- Otimo
- Bom
- Regular
- Critico

Contratos marcados como `Critico` ficam destacados em vermelho na listagem/dashboard. Tambem foi adicionada acao rapida para marcar o contrato como critico sem abrir a tela de comentario.

## Contatos e anexos

- Permite vincular um contato existente do CRM Comercial.
- Exibe atalho para cadastrar contato quando ainda nao existir.
- Permite anexar arquivos em cada comentario do relacionamento.
- Grava data, hora, usuario autor e auditoria das inclusoes.

---

# 4. Implantacao - Agrupamento de Cards

## Problema tratado

Clientes com mais de uma unidade de negocio podem ter mais de um contrato OMIE, o que gera mais de um card na fila de implantacao. Em alguns casos, todas as unidades usam o mesmo ambiente e os mesmos servidores, entao processos separados causariam duplicidade operacional.

## Mudancas implementadas

- Criado vinculo entre cards de implantacao por meio de um card principal.
- Um card secundario pode ser vinculado a outro card principal.
- Cards vinculados continuam existindo para rastreabilidade do contrato.
- Cards vinculados deixam de aparecer na lista principal e no Kanban por padrao.
- A tela de implantacao recebeu filtro de agrupamento:
  - `Cards principais`
  - `Cards vinculados`
  - `Todos`
- A listagem permite vincular e desvincular cards rapidamente.
- A tela de detalhe mostra os cards vinculados ao card principal.
- Cada vinculo/desvinculo grava historico operacional e auditoria.

## Regra operacional

O card principal deve representar o processo unico de implantacao do ambiente. Cards vinculados representam contratos/unidades adicionais que usam o mesmo processo e nao devem gerar novo fluxo operacional no Kanban.

---

# 5. Banco de Dados

## Migrations adicionadas

```text
database/migrations/104_create_sucesso_cliente.sql
database/migrations/105_vincular_cards_implantacao.sql
```

## Estruturas principais

`104_create_sucesso_cliente.sql` cria as estruturas de acompanhamento CS, historico e anexos.

`105_vincular_cards_implantacao.sql` adiciona em `implantacoes`:

```text
implantacao_principal_id BIGINT NULL
idx_implantacoes_principal
fk_implantacoes_principal
```

---

# 6. Validacoes Tecnicas Realizadas

- Compilacao Python dos modulos alterados.
- Carga dos templates Jinja de implantacao e CS.
- Validacao das rotas Flask novas.
- Validacao de listagem de cards principais e vinculados.
- Validacao de Kanban exibindo apenas cards principais.
- Confirmacao local da migration `105_vincular_cards_implantacao.sql`.

---

# 7. Procedimento para Atualizar o Beta

1. Fazer backup do banco e do storage antes da atualizacao.
2. Atualizar a branch `beta` para o commit `1256ee3` ou superior.
3. Aplicar as migrations `104` e `105` caso ainda nao estejam registradas.
4. Instalar dependencias se o ambiente exigir.
5. Reiniciar o servico da aplicacao.
6. Validar as telas:
   - `CRM Comercial > Propostas`
   - `Implantacao > Licencas O3Web`
   - `CRM Comercial > Sucesso do Cliente`
   - `Implantacao`
   - `Implantacao > Kanban`

---

# 8. Pontos de Homologacao

## Propostas

- Criar proposta com dois servidores.
- Adicionar recursos em servidores diferentes.
- Confirmar que cada recurso permanece no bloco selecionado.
- Usar `Servidor basico` e confirmar que ele cria novo bloco separado.

## Licencas O3Web

- Criar Trial com ativacao e 30/45 dias.
- Confirmar calculo automatico da expiracao.
- Editar manualmente a expiracao e confirmar que o valor manual e preservado.

## Sucesso do Cliente

- Abrir a tela no CRM Comercial.
- Validar curva A/B/C por valor bruto.
- Vincular contato CRM.
- Registrar relacionamento com anexo.
- Marcar contrato como critico pela acao rapida.

## Implantacao

- Localizar dois cards de implantacao do mesmo cliente/grupo operacional.
- Vincular um card secundario a um card principal.
- Confirmar que o secundario sai da lista principal e do Kanban.
- Usar filtro `Cards vinculados` para encontrar o card secundario.
- Desvincular e confirmar retorno do card ao fluxo principal.

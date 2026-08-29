# O3Cloud Manager v3.0

# 17 - SPRINTS

Versão: 3.0 Beta

Última atualização: 14/08/2026

Status: Oficial

---

# Visão Geral

Este documento consolida a evolução das Sprints do projeto.

A referência oficial de planejamento continua sendo o `ROADMAP.md`.

---

# Sprints Concluídas

## Sprint 1

Entregas:

- Estrutura inicial do projeto
- Flask
- MariaDB
- Layout Base

Status:

✅ Concluído

---

## Sprint 2

Entregas:

- Módulo Ambientes
- CRUD completo
- Repository
- Service
- Routes
- Templates

Status:

✅ Concluído

---

## Sprint 3

Entregas:

- Estrutura administrativa
- Evolução da arquitetura
- Organização inicial dos domínios

Status:

✅ Concluído

---

## Sprint 4

Entregas:

- Módulo Clientes
- CRUD
- Integração OMIE
- Sincronização
- Bloqueios de edição
- Implantação

Status:

✅ Concluído

---

## Sprint 5

Entregas:

- Módulo Contratos
- CRUD
- Integração OMIE
- Contratos
- Itens de Contrato

Status:

✅ Concluído

---

## Sprint 6.1

Entregas:

- Fundação do Catálogo Técnico
- Estrutura inicial do módulo

Status:

✅ Concluído

---

## Sprint 6.2

Entregas:

- Estrutura do Catálogo Técnico
- Organização da base do módulo

Status:

✅ Concluído

---

## Sprint 6.3

Entregas:

- CRUD Categorias
- CRUD Produtos
- Repository padronizado
- Service padronizado
- Routes padronizadas
- Templates padronizados
- Componentes homologados
- BaseRepository atualizado

Status:

✅ Concluído

---

## Sprint 6.4

Entregas:

- CRUD Modelos
- CRUD Faixas
- Home do Catálogo Comercial ajustada
- Atalhos de acesso para Modelos e Faixas
- Contabilização de Categorias, Modelos e Faixas na visão geral
- Documentação da sprint atualizada

Status:

✅ Concluído

---

# Última Sprint Concluída

## Sprint 8

Objetivos:

- Consolidação comercial pós-assinatura
- Dashboard executivo/comercial
- Indicadores por parceiro e executivo
- Rastreabilidade proposta -> ClickSign -> contrato -> Omie
- Evolução de permissões e auditoria

Entregas:

- Dashboard Comercial inicial em `/propostas/dashboard`
- Agrupamentos por executivo, parceiro, status comercial e status ClickSign
- Atalhos no menu lateral e na tela de Propostas

Status:

✅ Concluída na primeira entrega

---

# Última Sprint Concluída

## Sprint 9

Implantação e Provisionamento

Objetivos:

- Módulo próprio de Implantação
- Workflow pós-contrato assinado
- Checklist técnico rastreável
- Acompanhamento por status, responsável e prazo
- Preparação de provisionamento
- Base para integração Proxmox, PBS e Zabbix segura e auditável

Escopo entregue:

- ✅ Fundação do domínio `implantacao` com migrations, repository, service, routes e templates
- ✅ Listagem, criação, visualização, edição e dashboard de implantações
- ✅ Kanban operacional com movimentação, histórico e notificação tolerante a SMTP ausente
- ✅ Administração de colunas do Kanban
- ✅ Checklist técnico rastreável com modelos, inclusão e remoção manual de itens
- ✅ Licenças O3Web, Faixas de Rede e Cofre de Senhas como telas operacionais da Implantação
- ✅ Cofre com senha criptografada, auditoria e navegação por parceiro -> cliente -> credenciais
- ✅ Rastreabilidade proposta -> contrato -> implantação nas telas operacionais
- ✅ Base de configuração para integrações Proxmox, PBS e Zabbix sem automação destrutiva

Documento de fechamento:

- `docs/19-FECHAMENTO-SPRINT-9.md`

Status:

✅ Concluída em 27/07/2026

---

# Última Sprint Concluída

## Sprint 10

Dashboard Executivo

Objetivos:

- Indicadores executivos
- Visão comercial e contratos
- Acompanhamento de implantação
- Base para rentabilidade e custos
- Drill-down para telas operacionais existentes

Escopo entregue:

- ✅ Dashboard Executivo dedicado em `/dashboard/executivo`
- ✅ Filtros executivos por periodo, parceiro, executivo e status
- ✅ Drill-down filtrado para Propostas, Contratos e Implantacao
- ✅ Evolucao mensal de propostas, receita ativa e volume operacional
- ✅ Base inicial para rentabilidade e custos, sem calculo definitivo de margem
- ✅ Carga por responsavel/implantador
- ✅ Rastreabilidade executiva proposta -> contrato -> implantacao

Documento de fechamento:

- `docs/20-FECHAMENTO-SPRINT-10.md`

Status:

✅ Concluída em 28/07/2026

---

# Ultima Sprint Encerrada

## Sprint 11

Integracoes e Melhorias Operacionais

Entregas:

- Menu Financeiro criado no sidebar com Dashboard Executivo, Produtos por Cliente, Faturamento e Contratos
- Tela `/dashboard/produtos-clientes` criada para diagnostico cliente -> contrato -> item contratado
- Vinculos Omie de maior impacto cadastrados no catalogo por seed idempotente
- Tela `/catalogo/produtos/custos` criada para exportar/importar custos por CSV
- Tela `/financeiro/faturamentos` criada para exportar modelo e importar faturamentos por competencia
- Pendencias de custos, faturamentos, parametros financeiros e rastreabilidade historica documentadas

Documento de fechamento:

- `docs/21-FECHAMENTO-SPRINT-11.md`

Status:

⚠️ Parcialmente concluida em 29/07/2026

---

## Sprint 12

Pendencias Operacionais e Preparacao da Versao Final

Entregas:

- `proposta_id` definido como vinculo opcional no fluxo operacional
- Contratos diretos/parceiros definidos como origem valida para implantacao
- Dashboard Executivo ajustado para exibir contratos sem proposta como contratos diretos
- Integracoes separadas em Negocio e Tecnicas
- OMIE e ClickSign exibidos a partir de variaveis de ambiente com segredos mascarados
- Comentarios de implantacao passaram a aceitar anexos

Documento de fechamento:

- `docs/22-FECHAMENTO-SPRINT-12.md`

Status:

✅ Concluida em 29/07/2026

---

## Sprint 13

Decisao, Preparacao Operacional e Validacoes Nao Destrutivas

Entregas:

- Decidido que dados reais oficiais ficam para a fase Beta com a equipe, sem carga prematura na Sprint 13
- Custos, faturamentos e parametros financeiros nao serao carregados antes do saneamento dos cadastros
- Comercial devera completar informacoes pendentes antes das validacoes oficiais
- Sprint 14 passa a focar consolidacao pre-Beta, diagnosticos, campos/telas pendentes e checklist de validacao

Documento de fechamento:

- `docs/23-FECHAMENTO-SPRINT-13.md`

Status:

✅ Concluida em 29/07/2026

---

# Sprint Encerrada

## Sprint 14

Consolidacao Pre-Beta e Preparacao de Validacao com a Equipe

Entregas consolidadas em 30/07/2026:

- Dashboard Executivo com diagnostico pre-Beta para cadastro comercial, fluxo operacional e dados financeiros
- Checklist inicial de validacao Beta por area: Comercial, Operacoes, Financeiro e Engenharia
- Indicacao explicita de que dados financeiros ausentes aguardam carga oficial da Beta
- Integracoes Tecnicas preparadas para Proxmox, PBS, Zabbix, FreeIPA e TrueNAS em modo diagnostico/nao destrutivo
- Infraestrutura recebeu itens para Backups PBS, Monitoramento Zabbix e Backup NAS
- Cadastros finais e revisao assistida com a equipe foram encaminhados para a fase Beta

Documento de fechamento:

- `docs/24-FECHAMENTO-SPRINT-14.md`

Status:

✅ Concluida em 30/07/2026

---

# Ultima Sprint Encerrada

## Sprint 15

Infraestrutura Operacional e Sincronismo Read-Only

Inicio registrado em 30/07/2026. Encerrada em 03/08/2026.

Entregas consolidadas:

- Sincronismo Proxmox VE em modo somente leitura.
- Telas operacionais de Clusters, Nodes, Maquinas Virtuais e Containers.
- Inventario Proxmox de recursos e nodes com dashboards operacionais.
- Backups PBS com escopos, namespaces, snapshots e sincronismo manual.
- Monitoramento Zabbix com cache, sincronismo manual, ordenacao por criticidade e filtros por status/criticidade.
- Backup NAS/TrueNAS com cache, sincronismo manual, alertas por pasta sem alteracao recente e aba de Backups OK.
- Atalhos para Integracoes Tecnicas removidos das telas operacionais e do menu lateral.
- Seguranca preservada: sem start, stop, reboot, migrate, delete ou alteracoes destrutivas.

Documento de revisao de fechamento:

- `docs/25-FECHAMENTO-SPRINT-15.md`

Pendencias encaminhadas:

- Validacao assistida com a operacao.
- Decisao futura sobre historico centralizado de sincronismos Zabbix/TrueNAS.
- Controle formal de acesso/perfis encaminhado para sprint futura.

Status:

✅ Concluida em 03/08/2026

---

# Melhorias Pre-Sprint 16

Registro:

- `docs/26-MELHORIAS-PRE-SPRINT-16.md`

Entregas consolidadas:

- Selecionar Representante Legal na proposta para ClickSign.
- Exigir nome completo e CPF do Representante Legal antes do envio.
- Bloquear reenvio duplicado para ClickSign quando ja existe envelope.
- Cancelar envelope pendente na ClickSign ao cancelar/rejeitar/expirar proposta.
- Exibir Gerar documento e Enviar na listagem de propostas aprovadas, respeitando status do documento.
- Bloquear nova geracao de documento para fluxo assinado/concluido.
- Refinar PDF, pipeline comercial, cofre de senhas e rastreabilidade operacional.

Status:

✅ Registrado em 03/08/2026 antes da abertura da Sprint 16

---


# Sprints Concluídas

## Sprint 16

Governanca, Acessos e Operacao Assistida

Inicio registrado em 03/08/2026.

Documento de abertura:

- `docs/27-ABERTURA-SPRINT-16.md`
- `docs/28-AUTENTICACAO-USUARIOS-SPRINT-16.md`
- `docs/29-BOOTSTRAP-ADMIN-SPRINT-16.md`
- `docs/30-ENTREGAS-OPERACIONAIS-SPRINT-16.md`
- `docs/31-ENTREGAS-GOVERNANCA-INTEGRACOES-SPRINT-16.md`

Objetivos iniciais:

- Definir controle de acesso e perfis por area operacional.
- Criar Configuracoes > Usuarios e Acessos.
- Prever usuarios locais convidados por e-mail.
- Prever sincronismo FreeIPA, configuracao LDAP e autenticacao Active Directory.
- Mapear telas administrativas e integracoes tecnicas para restricao por permissao.
- Priorizar auditoria operacional para acoes sensiveis.
- Criar roteiro de validacao assistida da Beta por area.
- Enderecar refinamentos operacionais priorizados pela equipe.
- Eventos CRM e importação de participantes implementados.
- Base de Conhecimento com pastas, artigos e arquivos implementada.
- Login global, sessao e matriz de permissoes por menu implementados para validacao assistida.
- Auditoria operacional centralizada implementada com sanitizacao de campos sensiveis.
- Comentarios internos em propostas, regras de campanhas/comissao e compartilhamento temporario do cofre implementados.
- Brevo, disparos de e-mail de eventos CRM e dimensionamento de hardware por parceiro implementados.

Documento de fechamento:

- `docs/33-FECHAMENTO-SPRINT-16.md`

Pendencias de validacao Beta:

- `docs/32-PENDENCIAS-TESTES-BETA-SPRINT-16.md`

Status:

✅ Concluida tecnicamente em 06/08/2026

---

# SPRINT 17
# MÓDULO FINANCEIRO
# COMISSÕES DE EXECUTIVOS


# Sprint 17 – Comissões de Executivos e Expansão da Sincronização Financeira OMIE

Status: Concluida tecnicamente em 14/08/2026; Sprint Final de homologacao Beta como proxima etapa.

Decisão de retomada:

* reaproveitar a tela existente de `Regras Campanhas`;
* não criar um cadastro paralelo de campanhas de comissão nesta etapa;
* adaptar a campanha para exibir os contratos ativos cuja data de início de vigência esteja dentro do intervalo da campanha;
* facilitar a visualização de qual contrato pertence a qual campanha quando existir campanha cadastrada;
* quando não houver campanha criada, não aplicar filtro por campanha na visualização de contratos/comissões.

Atualização 12/08/2026:

* descoberta OMIE inicial documentada em `docs/44-DESCOBERTA-OMIE-SPRINT-17.md`;
* migration `087_expandir_contratos_comissoes_sprint17.sql` aplicada no banco local;
* contratos OMIE expandidos com vendedor, projeto, observação do contrato, valor bruto, descontos e valor líquido;
* sincronização de contratos OMIE passou a enviar `cExibeObs=S` para retornar `observacoes.cObsContrato`;
* sincronização completa atualizou 210 contratos OMIE com os novos campos comerciais;
* detalhe de Contratos passou a exibir a seção `Informações Comerciais`;
* migration `088_create_financeiro_recebimentos_sprint17.sql` aplicada no banco local;
* recebimentos OMIE sincronizados com idempotência por `codigo_lancamento_omie`;
* janela local de 90 dias foi refinada para manter 505 recebimentos com contrato, cliente e nota fiscal vinculados;
* migration `090_limpar_recebimentos_omie_sem_vinculo_sprint17.sql` removeu 90 recebimentos sem vínculo operacional do cache;
* tela `Financeiro > Faturamentos` passou a exibir os recebimentos OMIE sincronizados para consulta operacional;
* recebimentos OMIE ficaram em cache local, com atualização manual pela tela de Faturamentos;
* criado sincronismo separado `OMIE_RECEBIMENTOS`, inativo por padrão, para execução manual ou automação agendada em Configurações.
* `Regras Campanhas` passou a exibir os contratos ativos com `inicio_vigencia` dentro do intervalo da campanha.
* tela de Faturamentos passou a paginar Recebimentos OMIE e destacar títulos `ATRASADO` em vermelho.

Atualização 13/08/2026:

* ASO passou a criar agendamento a partir do cadastro do colaborador, com agenda do Gestor Administrativo, compartilhamento com outro usuario habilitado e lembretes por e-mail de 7, 15 ou 30 dias.
* Campo `Exames realizados` passou a evidenciar anexos multiplos e listar os arquivos selecionados abaixo do campo.
* Implantacoes e Kanban de Implantacao passaram a exibir CNPJ do cliente diretamente na lista/card.
* Parceiros receberam `premiacao_ativa`, permitindo campanha com premiacao para Parceiro, Executivo ou ambos.
* Tela `Financeiro > Premiações` passou a exibir somente contratos com Parceiro ou Executivo habilitado e a considerar apenas o primeiro titulo/parcela ativo.
* Executivos passaram a ter exclusao operacional para Administrador e Diretoria, com inativacao e remocao do vinculo com parceiro.
* Lista de Executivos passou a permitir mudar rapidamente o status de premiacao sem abrir edicao.
* Criada tela `Financeiro > Receitas por Servidor`, com receita mensal por node Proxmox baseada em ambientes e contratos ativos vinculados.
* Acompanhamento detalhado das etapas de 13/08/2026 registrado em `docs/45-ACOMPANHAMENTO-SPRINT-17-2026-08-13.md`, incluindo entregas consolidadas e frente ainda pendente no workspace.

Atualização 14/08/2026 - 2FA e TOTP:

* 2FA por e-mail revisado e aprovado para homologacao assistida.
* TOTP implementado para autenticacao remota e perfis administrativos.
* Usuario configura TOTP em `Minha Conta`, confirmando o primeiro codigo antes da ativacao.
* Login `/login/2fa` passou a validar EMAIL ou TOTP conforme `two_factor_metodo`.
* Segredo TOTP fica protegido pelo mecanismo de criptografia do Cofre de Senhas.
* Testes automatizados de 2FA/TOTP, backup e atualizacoes passaram com `23 passed`.

Atualização 14/08/2026 - Fechamento tecnico:

* Usuario confirmou a validacao funcional assistida das 8 etapas solicitadas para o Sprint 17.
* Ajustado controle de acesso para permitir perfil Infraestrutura em `Retencao de Cache`, `Automacoes de Sincronismo` e `Backups do Sistema` conforme permissoes do perfil.
* Validacao tecnica final executada com `venv/bin/python -B -m pytest`, resultado `34 passed`.
* Compilacao Python dos arquivos alterados executada sem erro.
* Migrations `096`, `097`, `098` e `099` aplicadas/conferidas e registradas em `schema_migrations` em 14/08/2026; ausencia de CPFs duplicados confirmada antes da constraint da `096`.

## 1. Objetivo

Evoluir a integração financeira do O3Cloud Manager com o OMIE para disponibilizar todas as informações necessárias ao cálculo e auditoria de comissões dos executivos comerciais.

O Sprint deverá:

1. ampliar a sincronização dos Contratos OMIE;
2. importar informações adicionais necessárias ao cálculo de comissão;
3. sincronizar recebimentos dos últimos 90 dias através de Contas a Receber;
4. criar a tela **Financeiro → Comissões**;
5. adaptar a tela existente de **Regras/Campanhas de Comissão**;
6. selecionar automaticamente os contratos elegíveis conforme a vigência da campanha;
7. considerar somente contratos ATIVOS;
8. permitir valor manual complementar utilizado pelas regras da campanha;
9. deixar a arquitetura preparada para cálculo e auditoria das comissões.

---

# 2. Princípio Arquitetural

Manter o padrão atual do O3Cloud Manager:

Repository
↓
Service
↓
Routes
↓
Templates
↓
Testes

Integrações OMIE:

Client
↓
Mapper
↓
Service
↓
Repository
↓
MariaDB

Não colocar regras de comissão:

* no Mapper;
* no Repository;
* nas Routes;
* diretamente nos templates.

As regras deverão permanecer na camada de Service.

---

# 3. Escopo 17.1 – Expansão da Sincronização de Contratos

A sincronização atual de contratos deverá ser ampliada.

## 3.1 Observações do Contrato

Sincronizar o campo existente no OMIE identificado na interface como:

**“Observações do contrato (elas não serão exibidas Nota Fiscal)”**

Esse conteúdo deverá ser armazenado no O3Cloud Manager e exibido como observação do contrato.

### Regra importante

Antes de implementar o Mapper:

1. consultar um contrato real pela API OMIE;
2. localizar no JSON exatamente qual propriedade corresponde ao campo exibido na interface do OMIE;
3. documentar o caminho JSON encontrado;
4. somente depois implementar o mapeamento.

Não presumir que seja o mesmo campo de observação atualmente utilizado.

Caso existam:

* observação interna;
* observação da NF;
* observação do contrato;

mantê-las separadas.

Não sobrescrever campos diferentes com o mesmo conteúdo.

---

# 4. Vendedor

Na aba **Informações Adicionais** do contrato OMIE existe o Vendedor.

Atualmente o O3Cloud Manager já possui suporte ao código do vendedor.

Deverá passar a sincronizar também:

* código do vendedor;
* nome do vendedor.

Exemplo conceitual:

```text
codigo_vendedor = 11586524905
vendedor_nome = João da Silva
```

O nome deverá ser exibido no detalhe do contrato.

### Regra

Se a API de contratos retornar apenas o código:

1. utilizar endpoint oficial do OMIE apropriado para vendedores;
2. resolver `codigo_vendedor → nome`;
3. evitar consultar o mesmo vendedor repetidamente dentro do loop de contratos;
4. utilizar cache em memória durante a execução ou sincronização prévia quando adequado.

Não realizar centenas de chamadas iguais para o mesmo vendedor.

---

# 5. Projeto

Na aba **Informações Adicionais** do OMIE também pode existir Projeto.

Sincronizar:

* código do projeto;
* nome do projeto.

Exemplo:

```text
codigo_projeto = 12345
projeto_nome = Projeto Migração ABC
```

Quando o contrato não possuir projeto:

```text
codigo_projeto = NULL ou 0
projeto_nome = NULL
```

Não tratar ausência de Projeto como erro de sincronização.

---

# 6. Valores dos Serviços

Separar no contrato os valores comerciais necessários para comissão.

Sincronizar/calcular:

## valor_servicos_bruto

Soma dos serviços do contrato antes dos descontos aplicáveis.

## valor_descontos

Soma total dos descontos existentes nos itens/contrato.

## valor_servicos_liquido

Resultado após descontos.

Conceitualmente:

```text
valor_servicos_liquido =
valor_servicos_bruto - valor_descontos
```

O campo atual:

```text
valor_mensal
```

deve permanecer.

Não remover nem alterar o significado do campo atual sem migration e análise de impacto.

---

# 7. Desconto para Comissão

O desconto precisa ser armazenado de forma explícita porque será utilizado no cálculo da comissão.

Manter distinção entre:

* desconto de item;
* desconto total do contrato;
* valor líquido.

Nos itens do contrato já existem informações relacionadas a desconto.

Revisar o payload real do OMIE e garantir que sejam corretamente sincronizados:

```text
valor_desconto
percentual_desconto, se disponível
tipo_desconto, se necessário
```

No contrato, consolidar:

```text
valor_descontos
```

Não calcular comissão utilizando valor bruto quando a regra exigir valor após desconto.

---

# 8. Revisão da Tabela `contratos`

Criar migration para incluir somente os campos ausentes necessários.

Sugestão conceitual:

```text
observacao_contrato
vendedor_nome
projeto_nome
valor_servicos_bruto
valor_descontos
valor_servicos_liquido
```

Campos existentes que deverão ser preservados:

```text
codigo_vendedor
codigo_projeto
valor_mensal
```

Antes da migration:

```sql
SHOW CREATE TABLE contratos\G
```

e validar os nomes existentes para evitar duplicidade.

---

# 9. Revisão de `contratos_itens`

Validar se a tabela atual já possui:

```text
quantidade
valor_unitario
valor_total
desconto
acrescimo
```

Caso já possua, reutilizar.

Não duplicar informações.

Revisar o Mapper de itens para garantir que o desconto real retornado pelo OMIE esteja persistido corretamente.

---

# 10. Validação Financeira pelo Contas a Receber

Para o cálculo de comissão, o contrato não deve ser considerado pago apenas por existir no OMIE.

O O3Cloud Manager deverá sincronizar informações do módulo:

**OMIE → Contas a Receber**

Período:

**últimos 90 dias**

---

# 11. Regra de Recebimentos

Sincronizar registros de Contas a Receber cuja situação seja equivalente a:

**Recebido**

A implementação deverá primeiro validar no payload real do OMIE qual campo/código representa a situação `Recebido`.

Não assumir texto ou código sem teste da API.

---

# 12. Exclusões de Categoria

Não considerar para comissão registros cuja categoria contenha, de forma case-insensitive:

```text
SETUP
```

ou

```text
IMPLANTACAO
```

Também tratar variações de acentuação:

```text
IMPLANTAÇÃO
Implantação
implantacao
```

A normalização deve ser feita de forma segura.

Exemplos que devem ser excluídos:

```text
SETUP O3 CLOUD
SERVIÇO DE SETUP
IMPLANTACAO
IMPLANTAÇÃO CLOUD
TAXA DE IMPLANTAÇÃO
```

Não utilizar comparação apenas por igualdade.

Utilizar regra equivalente a:

`categoria contém termo proibido`.

---

# 13. Janela de Sincronização

Ao executar a sincronização de recebimentos:

```text
hoje - 90 dias
até
hoje
```

A data utilizada para esse filtro deverá ser documentada:

* data de recebimento;
* data de pagamento;
* data de baixa;

conforme o campo correto disponibilizado pela API OMIE.

Para comissão, priorizar a data que represente efetivamente o recebimento/baixa financeira.

---

# 14. Nova Tabela de Recebimentos

Criar tabela específica.

Nome sugerido:

```text
financeiro_recebimentos
```

Campos conceituais:

```text
id
uuid

codigo_externo
cliente_id
contrato_id

numero_documento
numero_parcela

categoria_codigo
categoria_nome

valor_original
valor_recebido
valor_desconto
valor_juros

data_vencimento
data_recebimento

situacao

codigo_cliente_omie
codigo_contrato_omie

origem
synced_at

created_at
updated_at
```

Adaptar aos dados realmente disponibilizados pela API.

---

# 15. Vínculo Recebimento ↔ Contrato

Esse ponto é crítico.

O Codex deverá descobrir, através do payload real do OMIE, qual identificador permite associar de maneira confiável:

```text
Conta a Receber
       ↓
Contrato OMIE
```

Prioridade:

1. código do contrato;
2. identificador/documento explicitamente relacionado;
3. outro relacionamento oficial da API.

Não relacionar contratos por descrição textual se houver identificador técnico disponível.

Se não existir vínculo inequívoco no endpoint utilizado:

* documentar;
* não inventar correspondência;
* propor regra segura antes de implementar.

---

# 16. Idempotência dos Recebimentos

Uma nova sincronização dos mesmos 90 dias não poderá duplicar registros.

Criar identificação única baseada no identificador oficial do OMIE.

Fluxo:

```text
Recebimento existe?
    ↓
SIM → UPDATE
NÃO → INSERT
```

Executar o sincronismo repetidamente deve produzir:

```text
Novos: 0
Atualizados: N
```

e nunca registros duplicados.

---

# 17. Histórico de Sincronização

Registrar no mecanismo atual de:

```text
sync_execucoes
```

Nova operação lógica:

```text
OMIE_RECEBIMENTOS
```

Se o ENUM atual não suportar esse valor, avaliar:

* expandir corretamente; ou
* continuar utilizando integração `OMIE` e identificar o tipo da rotina em outro campo/log.

Não repetir o problema anterior de gravar valor não permitido pelo ENUM.

---

# 18. Nova Tela – Financeiro → Comissões

Adicionar item:

```text
Financeiro
├── ...
├── Inadimplentes
└── Comissões
```

Rota sugerida:

```text
/financeiro/comissoes
```

---

# 19. Tela Principal de Comissões

Listar inicialmente apenas contratos:

```text
status = ATIVO
```

Exibir:

* número do contrato;
* cliente;
* vendedor;
* projeto;
* vigência inicial;
* valor mensal;
* valor bruto dos serviços;
* descontos;
* valor líquido;
* situação de recebimento;
* campanha/regra associada;
* comissão calculada, quando existir.

Filtros:

* período;
* vendedor;
* cliente;
* contrato;
* projeto;
* status de recebimento;
* campanha.

---

# 20. Campo de Valor Manual

Na tela de Comissões deverá existir um campo livre numérico para lançamento manual.

Esse valor será utilizado pelas regras de campanha.

Nome conceitual:

```text
valor_manual_comissao
```

ou:

```text
base_manual
```

O valor:

* deve aceitar decimal;
* deve possuir formatação monetária;
* deve registrar usuário;
* deve registrar data da alteração;
* não deve sobrescrever valores sincronizados do OMIE.

Esse campo é complementar.

Nunca utilizar o mesmo campo de `valor_mensal` ou `valor_servicos`.

---

# 21. Auditoria do Valor Manual

Guardar:

```text
valor
usuario
data_hora
```

Preferencialmente preservar histórico de alterações se o sistema já possuir mecanismo de auditoria.

O valor manual pode impactar comissão, portanto não deve ser alterado sem rastreabilidade.

---

# 22. Campanhas / Regras de Comissão

Evoluir a tela existente:

```text
Regras Campanhas
```

A campanha deverá possuir:

* nome;
* descrição;
* data inicial;
* data final;
* status;
* regras de cálculo;
* observações;
* criado por;
* data de criação.

Regra de implementação:

* não duplicar cadastro de campanhas em outro módulo;
* manter a campanha atual como fonte operacional;
* adicionar a visualização de contratos elegíveis dentro do detalhe/edição da campanha;
* quando nenhuma campanha existir, a listagem geral não deverá filtrar contratos por campanha.

---

# 23. Seleção Automática de Contratos da Campanha

Ao abrir ou salvar uma campanha:

Selecionar automaticamente os contratos cuja:

```text
inicio_vigencia
```

esteja dentro do intervalo:

```text
campanha.data_inicio
até
campanha.data_fim
```

Regra:

```text
inicio_vigencia >= data_inicio
AND
inicio_vigencia <= data_fim
AND
status = ATIVO
```

Esses contratos deverão ficar visíveis dentro da campanha.

---

# 24. Contratos Dentro da Campanha

Exibir tabela:

```text
Contrato
Cliente
Vendedor
Projeto
Início da Vigência
Valor Mensal
Valor Bruto
Desconto
Valor Líquido
Valor Manual
Recebido?
Comissão
```

A lista deverá ser recalculável.

Não duplicar contratos a cada abertura da campanha.

---

# 25. Snapshot da Campanha

Existe uma diferença importante entre:

**contratos atualmente elegíveis**

e

**contratos efetivamente considerados no fechamento da campanha**.

A arquitetura deverá preparar suporte para snapshot.

Enquanto a campanha estiver:

```text
RASCUNHO
```

pode recalcular automaticamente os contratos elegíveis.

Após:

```text
FECHADA
```

os contratos e valores utilizados devem permanecer registrados para auditoria.

Uma alteração posterior no contrato não deverá modificar silenciosamente uma comissão já fechada.

---

# 26. Status de Campanha

Sugestão:

```text
RASCUNHO
EM_APURACAO
FECHADA
CANCELADA
```

Regras:

### RASCUNHO

Pode alterar regras e intervalo.

### EM_APURACAO

Contratos selecionados e cálculo em conferência.

### FECHADA

Não recalcular automaticamente.

### CANCELADA

Mantém histórico, mas não produz comissão.

---

# 27. Regras de Comissão

A arquitetura deve permitir regras configuráveis.

Não colocar percentuais fixos em Python.

Exemplo conceitual:

```text
Campanha Agosto/2026

Período:
01/08/2026 a 31/08/2026

Regra:
X% sobre base elegível

Condições:
Contrato ativo
Recebimento confirmado
Categoria permitida
```

Os detalhes definitivos das fórmulas poderão ser expandidos posteriormente, mas a modelagem deve nascer parametrizável.

---

# 28. Base Elegível para Comissão

Separar claramente:

```text
valor bruto
desconto
valor líquido
valor manual
valor recebido
base da comissão
```

Nunca utilizar apenas:

```text
valor_mensal
```

sem identificar qual regra está sendo aplicada.

Criar no Service um cálculo explícito:

```text
base_comissao
```

A origem dessa base deve ser rastreável.

---

# 29. Confirmação de Pagamento

A tela de Comissões deverá indicar claramente:

```text
RECEBIDO
NÃO RECEBIDO
NÃO LOCALIZADO
```

Nunca considerar `NÃO LOCALIZADO` como pago.

A confirmação deverá utilizar os dados sincronizados de Contas a Receber.

---

# 30. Categorias Excluídas

Mesmo quando o recebimento estiver `RECEBIDO`, não considerá-lo como base elegível quando a categoria possuir:

```text
SETUP
```

ou

```text
IMPLANTACAO / IMPLANTAÇÃO
```

Exibir o motivo:

```text
Recebimento desconsiderado:
Categoria excluída da comissão.
```

Isso facilita auditoria pelo Financeiro.

---

# 31. Modelagem de Campanhas

Reaproveitar e evoluir a tabela existente:

```text
regras_campanhas_comissao
```

Campos existentes devem ser preservados, especialmente:

```text
id
uuid
nome
percentual_parceiro
percentual_executivo
percentual_comissao
vigencia_inicio
vigencia_fim
descricao
ativo
created_by
updated_by
created_at
updated_at
```

Campos adicionais somente devem ser criados se forem necessários para a visualização dos contratos da campanha, apuração ou fechamento. Não criar uma nova tabela principal de campanhas nesta etapa.

---

# 32. Relação Campanha ↔ Contratos

Criar tabela auxiliar de vínculo e snapshot:

```text
regras_campanhas_contratos
```

Campos sugeridos:

```text
id
uuid

campanha_id
contrato_id

vendedor_codigo
vendedor_nome

valor_mensal
valor_servicos_bruto
valor_descontos
valor_servicos_liquido

valor_manual

valor_recebido_elegivel

base_comissao
percentual_comissao
valor_comissao

status_recebimento

incluido_automaticamente

created_at
updated_at
```

Essa tabela também servirá como snapshot durante o fechamento.

---

# 33. Regras de Integridade

Não permitir o mesmo:

```text
campanha_id + contrato_id
```

duplicado.

Criar índice/constraint apropriado.

---

# 34. Repository de Comissão

Implementação inicial em 12/08/2026 seguindo o padrão atual do módulo Financeiro, sem criar submódulo separado nesta etapa:

```text
app/financeiro/repository.py
app/financeiro/service.py
app/financeiro/routes.py
app/templates/financeiro/comissoes.html
```

Métodos implementados para consulta operacional:

```python
listar_campanhas_comissao()
buscar_campanha_comissao()
listar_comissoes_contratos()
resumo_comissoes_contratos()
filtros_comissoes()
status_comissoes()
```

A consulta usa contratos ativos, regras de campanha existentes e o cache local `financeiro_recebimentos`. Snapshot persistido e fechamento de campanha permanecem reservados para a etapa de apuração definitiva.

---

# 35. ComissãoService

Toda regra deverá estar na camada:

```text
ComissaoService
```

Responsabilidades:

* determinar contratos elegíveis;
* verificar recebimentos;
* excluir categorias;
* calcular base;
* considerar descontos;
* considerar valor manual;
* executar regra da campanha;
* fechar campanha;
* preservar snapshot.

---

# 36. Permissões

O módulo respeita o sistema atual de usuários/perfis.

Implementado em 12/08/2026:

```text
menu_key: comissoes
endpoint: financeiro.comissoes
migration: 091_permissao_comissoes_sprint17.sql
```

A permissão inicial foi herdada dos perfis que já possuíam acesso a `faturamento`, mantendo a tela restrita aos perfis financeiros já autorizados. Permissões granulares de fechamento/edição ficam para a etapa de apuração definitiva.

---

# 37. Interface – Comissões

Tela:

```text
Financeiro → Comissões
```

Cards sugeridos:

```text
Contratos Ativos
Recebidos Elegíveis
Pendentes
Comissão Apurada
```

Tabela principal abaixo.

Não transformar a primeira versão em dashboard complexo.

Priorizar auditoria e clareza.

Implementado em 12/08/2026:

* menu `Financeiro > Comissões`;
* filtros por busca, campanha e status financeiro;
* cards de contratos, recebidos, atrasados, não localizados, base de comissão e comissão prevista;
* tabela com contrato, cliente, campanha, vendedor/projeto, vigência, status, base, recebido, atraso e comissão;
* botão de cálculo na linha do contrato direcionando para `Financeiro > Comissões > Cálculo`;
* destaque vermelho para contratos com recebimentos `ATRASADO`/`VENCIDO`;
* paginação no rodapé;
* quando campanha é selecionada, filtra contratos com `inicio_vigencia` dentro do intervalo da campanha;
* quando não há campanha selecionada, exibe contratos ativos sem filtrar por campanha.

---

# 38. Detalhe do Contrato na Comissão

Ao clicar no contrato, mostrar:

```text
Contrato
Cliente
Vendedor
Projeto

Vigência

Valor bruto
Desconto
Valor líquido

Valor manual

Recebimentos localizados
Categorias

Base elegível

Regra aplicada

Comissão calculada
```

Isso permitirá ao Financeiro auditar exatamente de onde veio o cálculo.

Implementado em 12/08/2026:

* tela `financeiro/comissao_calculo.html`;
* rota `financeiro.calcular_comissao`;
* campo livre `valor_manual_base` para o Financeiro informar a base manual;
* cálculo usando `valor_manual_base` quando maior que zero, ou a base do contrato quando vazio;
* aplicação do percentual executivo da campanha vinculada pela vigência;
* conferência de base do contrato, recebido elegível, atraso, status financeiro, vendedor, projeto e vigência.

O cálculo permanece como conferência operacional sem fechamento/snapshot persistido nesta etapa.

---

# 39. Alterações na Tela de Contratos

A tela existente de contratos deverá passar a mostrar também:

* Vendedor;
* Projeto;
* Valor dos Serviços;
* Descontos;
* Valor Líquido.

No detalhe:

Adicionar seção:

```text
Informações Comerciais
```

com:

```text
Vendedor
Projeto
Valor Bruto dos Serviços
Descontos
Valor Líquido
```

E:

```text
Observações do Contrato
```

utilizando o novo campo correto sincronizado do OMIE.

---

# 40. Compatibilidade

Não quebrar:

* sincronização atual de Clientes;
* sincronização de Contratos;
* sincronização de Itens;
* tela atual de Contratos;
* paginação;
* pesquisa;
* relacionamento Cliente → Contrato;
* funcionalidades existentes do Financeiro.

---

# 41. Ordem de Implementação

Executar nesta ordem.

## 17.1 – Descoberta da API

Antes de migrations:

* inspecionar contrato real;
* localizar observação correta;
* localizar vendedor;
* localizar projeto;
* localizar descontos;
* testar endpoint de vendedor/projeto;
* testar Contas a Receber;
* identificar chave de relacionamento Recebimento ↔ Contrato;
* documentar payloads.

Não programar por suposição.

## 17.2 – Migration de Contratos

Adicionar campos necessários.

## 17.3 – Mapper / Repository / Service de Contratos

Atualizar sincronização.

## 17.4 – Recebimentos OMIE

Implementado:

* client OMIE para Contas a Receber e categorias;
* mapper de recebimentos com identificação de status recebido;
* repository e service com persistência idempotente em cache local;
* sync dos últimos 90 dias com exclusão de categorias SETUP/IMPLANTACAO;
* sincronismo separado `OMIE_RECEBIMENTOS` para execução manual ou agendada;
* botão manual na tela `Financeiro > Faturamentos` para atualizar o cache sob demanda.

## 17.5 – Testar últimos 90 dias

Validar recebimentos e categorias excluídas.

## 17.6 – Tela Comissões

Criar listagem dos contratos ativos.

## 17.7 – Valor Manual

Adicionar edição e auditoria.

## 17.8 – Campanhas

Adaptar o cadastro existente de Regras Campanhas e preservar o intervalo de datas.

## 17.9 – Seleção Automática

Relacionar e exibir contratos ativos pela vigência inicial dentro do intervalo da campanha.

## 17.10 – Cálculo

Aplicar regra configurada.

## 17.11 – Fechamento

Preservar snapshot.

## 17.12 – Testes e Documentação

Finalizar Sprint.

---

# 42. Testes Obrigatórios – Contratos

Testar contrato:

1. sem observação;
2. com observação interna;
3. com vendedor;
4. sem vendedor;
5. com projeto;
6. sem projeto;
7. sem desconto;
8. com desconto;
9. com vários itens;
10. com descontos em itens diferentes;
11. sincronização repetida;
12. alteração posterior no OMIE.

---

# 43. Testes Obrigatórios – Recebimentos

Testar:

1. últimos 90 dias;
2. registro RECEBIDO;
3. registro não recebido;
4. categoria normal;
5. categoria contendo SETUP;
6. categoria contendo setup;
7. categoria contendo IMPLANTACAO;
8. categoria contendo IMPLANTAÇÃO;
9. recebimento sem contrato identificável;
10. execução repetida;
11. duplicidade;
12. alteração de valor;
13. alteração da situação;
14. paginação da API.

---

# 44. Testes Obrigatórios – Campanhas

Testar:

1. campanha sem contratos;
2. contrato com vigência antes do período;
3. dentro do período;
4. depois do período;
5. contrato CANCELADO;
6. contrato SUSPENSO;
7. contrato ATIVO;
8. contrato recebido;
9. contrato não recebido;
10. categoria excluída;
11. desconto;
12. valor manual;
13. vendedor;
14. projeto;
15. fechamento;
16. tentativa de recalcular campanha fechada;
17. duplicidade de contrato;
18. auditoria;
19. ausencia de campanhas nao filtrando a listagem geral.

---

# 45. Critérios de Aceite

Sprint 17 estará concluído quando:

* observação correta do contrato estiver sincronizada;
* vendedor estiver sincronizado por código e nome;
* projeto estiver sincronizado por código e nome;
* valores brutos de serviços estiverem disponíveis;
* descontos estiverem separados;
* valor líquido estiver calculado;
* tela de Contratos exibir essas informações;
* recebimentos dos últimos 90 dias forem sincronizados;
* situação RECEBIDO puder ser identificada;
* categorias SETUP e IMPLANTAÇÃO forem excluídas;
* recebimentos não forem duplicados;
* recebimentos forem consultados por cache local, com sincronização manual e agendada separada;
* cache de recebimentos considerar somente registros com contrato, cliente e nota fiscal vinculados;
* Financeiro possuir tela Comissões;
* somente contratos ATIVOS forem listados;
* valor manual puder ser informado;
* alterações manuais forem auditáveis;
* campanhas possuírem intervalo na tela existente de Regras Campanhas;
* contratos forem selecionados automaticamente pela vigência inicial;
* contratos selecionados ficarem visíveis dentro da campanha;
* ausência de campanha não filtrar a visualização geral;
* recebimento puder ser auditado;
* comissão puder utilizar desconto;
* campanha fechada preservar snapshot;
* nenhum módulo existente for quebrado;
* documentação, DER, modelo físico e CHANGELOG forem atualizados;
* parceiros e executivos tiverem habilitacao independente para premiacao;
* tela de premiacoes listar apenas contratos elegiveis e somente a primeira parcela/titulo;
* Receita por Servidor mostrar receita mensal por node Proxmox a partir de ambientes e contratos ativos vinculados.

Status final Sprint 17:

* Concluido tecnicamente em 14/08/2026.
* Validacao funcional assistida concluida pelo usuario nas 8 etapas solicitadas.
* Testes automatizados finais: `34 passed`.
* Sprint Final segue como etapa de homologacao Beta, evidencias, commit/tag/release e plano de rollback; migrations `096`, `097`, `098` e `099` ja foram aplicadas/conferidas no banco local/alvo em 14/08/2026.

---

# 46. Fora do Escopo

Não implementar neste Sprint:

* pagamento automático da comissão;
* integração bancária para pagar executivo;
* folha de pagamento;
* emissão de recibo;
* alteração automática do OMIE;
* edição de contrato OMIE pelo O3Cloud Manager;
* regras arbitrárias executando Python/SQL;
* dashboards avançados de BI;
* previsão futura de comissão.

O foco é:

**sincronização correta → recebimento → campanha → base → cálculo → auditoria.**

---

# 47. Regra Final de Desenvolvimento para o Codex

Antes de alterar qualquer arquivo:

1. ler a documentação atual;
2. revisar `ContratoMapper`;
3. revisar `ContratoRepository`;
4. revisar `ContratoService`;
5. revisar `OmieClient`;
6. revisar `OmieSync`;
7. executar `SHOW CREATE TABLE contratos`;
8. executar `SHOW CREATE TABLE contratos_itens`;
9. testar payload real do OMIE;
10. somente depois propor migrations.

Seguir a sequência padrão do projeto:

**Repository → Service → Routes → Templates → Testes**

Implementar e homologar uma etapa por vez.

Não realizar refatorações fora do Sprint 17.

------------------------------------------------

# SPRINT 18
# MÓDULO ADMINISTRATIVO

---

## Status

Concluida tecnicamente em 06/08/2026. Atualizacao final registrada em 07/08/2026.

---

## Atualizacao Final - 07/08/2026

- Remocao de usuarios de acesso restrita a Administradores, com auditoria e protecoes operacionais.
- Logs backend estruturados e documentados para operacao por SSH.
- Validacao de CNPJ unico em Clientes, melhorias de Propostas, pesquisa no Cofre de Senhas, vinculo de ambientes no Cofre/Base de Conhecimento e ajustes de navegacao/template incorporados ao pacote final.
- Validacoes dessas entregas foram adicionadas a `docs/34-PENDENCIAS-TESTES-BETA-SPRINT-18.md`.

---

## Objetivo

Desenvolver o Módulo Administrativo do O3Cloud Manager responsável pelo gerenciamento das atividades internas da empresa, agendas corporativas, demandas administrativas, produtividade dos colaboradores e acompanhamento operacional pelos gestores.

Este módulo deverá centralizar todas as tarefas administrativas internas da empresa, permitindo que gestores distribuam atividades aos colaboradores, acompanhem a execução das demandas e monitorem a produtividade da equipe.

---

# Escopo

Esta Sprint contempla:

- Dashboard Administrativo
- Cadastro de Demandas
- Agenda Corporativa
- Agenda por Colaborador
- Comentários
- Histórico
- Notificações
- Alertas
- Auditoria
- Relatórios

---

# Estrutura do módulo

Administrativo

├── Dashboard

├── Demandas

├── Agenda Corporativa

├── Colaboradores

├── Relatórios

└── Configurações

---

# Arquitetura

Seguir integralmente:

- AGENTS.md
- DOMAIN_RULES.md
- Definition Of Done
- Architecture Freeze

Não alterar arquitetura existente.

---

# Banco de Dados

Criar migrations seguindo padrão do projeto.

Sugestão de entidades:

administrativo_demandas

administrativo_agendas

administrativo_tarefas

administrativo_comentarios

administrativo_historico

---

# Cadastro de Demandas

CRUD Completo

Campos

- UUID
- Título
- Descrição
- Categoria
- Prioridade
- Responsável
- Departamento
- Data Inicial
- Data Limite
- Hora
- Status
- Observações
- Permitir Comentários
- Possui Anexos
- Criado Por
- Data Criação
- Última Alteração

---

# Categorias

Administrativo

Financeiro

Comercial

Implantação

Suporte

Infraestrutura

RH

Diretoria

Outros

---

# Prioridades

Baixa

Normal

Alta

Urgente

---

# Status

Pendente

Em andamento

Concluída

Cancelada

Atrasada

---

# Fluxo

Gestor

↓

Cria Demanda

↓

Seleciona Colaborador

↓

Sistema cria tarefa

↓

Agenda atualizada

↓

Colaborador recebe notificação

↓

Executa atividade

↓

Conclui

↓

Gestor acompanha

---

# Agenda Corporativa

Cada colaborador poderá possuir uma agenda própria.

A agenda somente poderá ser criada por um Gestor.

---

# Cadastro do Colaborador

Adicionar campo:

Possui Agenda

SIM

NÃO

Caso:

NÃO

não exibir menu Agenda.

Caso:

SIM

criar automaticamente agenda vinculada ao usuário.

---

# Visualizações

Hoje

Semana

Mês

Lista

---

# Cada tarefa possuirá

Título

Descrição

Categoria

Prioridade

Status

Responsável

Data

Hora

Comentários

Histórico

Anexos

---

# Comentários

Cada tarefa poderá possuir comentários.

Campos

Usuário

Data

Hora

Comentário

Histórico completo.

---

# Tela do Colaborador

Visualiza apenas:

Sua Agenda

Suas Demandas

Seus Comentários

Seu Histórico

Jamais poderá visualizar agendas de terceiros.

---

# Tela do Gestor

Visualiza:

Agenda Geral

Agenda Individual

Agenda por Departamento

Agenda por Equipe

Agenda por Período

Pode:

Criar

Editar

Excluir

Cancelar

Reagendar

Transferir Responsável

Alterar Prioridade

Concluir

Duplicar

---

# Dashboard Administrativo

Widgets

Demandas Abertas

Demandas Concluídas

Demandas Atrasadas

Demandas Urgentes

Agenda Hoje

Agenda Semana

Pendências

Produtividade

Tempo Médio

Ranking Colaboradores

---

# Dashboard Colaborador

Minha Agenda

Próximas Atividades

Pendências

Comentários Recentes

Concluídas Hoje

---

# Alertas

Sempre que o colaborador realizar login.

Verificar:

Existem tarefas pendentes com data inferior ao dia atual?

Caso positivo:

Exibir alerta amarelo.

Mensagem

⚠ Existem tarefas pendentes de dias anteriores.

---

# Menu

Exemplo

Agenda (3)

onde

3 = quantidade pendente.

---

# Notificações

Nova Demanda

Demanda Concluída

Demanda Cancelada

Demanda Reagendada

Demanda Atrasada

Comentário Novo

---

# Relatórios

Demandas por Colaborador

Demandas por Departamento

Demandas por Período

Agenda Geral

Agenda Individual

Produtividade

Pendências

Tempo Médio

---

# Auditoria

Registrar:

Usuário

Data

Hora

IP

Operação

Tabela

Registro

Valores anteriores

Valores novos

---

# Permissões

Gestor

Administrador

Colaborador

Cada perfil deverá utilizar o sistema de permissões do O3Cloud Manager.

---

# Critérios de Aceite

CRUD funcionando.

Agenda funcionando.

Comentários funcionando.

Alertas funcionando.

Notificações funcionando.

Dashboards implementados.

Relatórios implementados.

Permissões funcionando.

Auditoria implementada.

---

# Definition Of Done

Repository

Service

Routes

Templates

Testes

Documentação

Changelog atualizado

Sprint atualizada

Roadmap atualizado

Architecture Freeze preservado.

---

# Observação

Este módulo deverá ser implementado totalmente desacoplado de integrações externas.

Na versão 2.0 as notificações, workflows e automações poderão ser migradas para o O3Cloud Infrastructure (O3Infra), preservando os contratos internos do sistema.



Documento de testes Beta:

- `docs/34-PENDENCIAS-TESTES-BETA-SPRINT-18.md`

Documento de fechamento:

- `docs/35-FECHAMENTO-SPRINT-18.md`

---

# Sprint 19 – Gestão de Clientes Inadimplentes

## 1. Objetivo

Criar dentro do módulo **Financeiro** do O3Cloud Manager uma funcionalidade para controle de inadimplência por contrato.

A funcionalidade deve permitir que a equipe Financeira:

* selecione um contrato;
* registre que o contrato possui pendência financeira;
* bloqueie operacionalmente o cliente no O3Cloud Manager;
* notifique a equipe de Suporte;
* notifique o cliente;
* destaque visualmente o cliente em todo o sistema;
* impeça novas propostas e novas implantações enquanto houver pendência ativa;
* posteriormente libere o cliente após:

  * quitação da pendência; ou
  * realização de acordo.

A funcionalidade não deve apagar histórico. Toda inclusão e liberação de inadimplência deve permanecer registrada para auditoria.

---

# 2. Localização no Sistema

Adicionar ao módulo:

Financeiro

novo item de menu:

Financeiro
├── Dashboard
├── Contratos
├── Faturamento
└── Inadimplentes

Nome da tela:

**Inadimplentes**

---

# 3. Regra Principal

A inadimplência será registrada por **Contrato**.

Entretanto:

> Se um cliente possuir pelo menos um contrato com inadimplência ATIVA, o Cliente deve ser considerado com pendência financeira em todo o O3Cloud Manager.

Portanto:

Contrato com pendência
↓
Cliente com restrição financeira
↓
Bloqueios operacionais

Quando não existir mais nenhuma inadimplência ativa vinculada aos contratos daquele cliente:

Cliente
↓
Restrição removida
↓
Operações liberadas

---

# 4. Nova Tela – Inadimplentes

URL sugerida:

`/financeiro/inadimplentes`

A tela deverá possuir:

* contratos atualmente inadimplentes;
* cliente;
* número do contrato;
* valor mensal;
* data do bloqueio;
* responsável pelo bloqueio;
* status;
* observação;
* ações.

Filtros:

* cliente;
* número do contrato;
* status;
* período;
* responsável.

Status principais:

* PENDENTE
* LIBERADO

Na interface:

PENDENTE → vermelho

LIBERADO → verde ou cinza

---

# 5. Nova Inadimplência

Adicionar botão:

`+ Nova Inadimplência`

A experiência deve seguir o padrão existente de:

Ambientes → Novo Ambiente

Fluxo:

1. Usuário acessa Financeiro → Inadimplentes.
2. Seleciona Nova Inadimplência.
3. Pesquisa e seleciona um contrato por número, cliente, razão social ou CNPJ.
4. O sistema carrega automaticamente:

   * cliente;
   * número do contrato;
   * status;
   * valor mensal;
   * e-mail do cliente.
5. Financeiro informa:

   * motivo;
   * observações;
   * data da ocorrência, se necessário.
6. Confirma a inclusão.
7. Sistema registra a inadimplência.
8. Sistema coloca o cliente em restrição financeira.
9. Sistema envia as notificações.
10. Sistema passa a destacar esse cliente nas demais telas.

Não permitir registrar uma segunda inadimplência ATIVA para o mesmo contrato.

---

# 6. Notificação ao Suporte

Após a confirmação da inadimplência, enviar automaticamente e-mail para:

`sac@o3cloud.com.br` e `plantao@o3ti.com.br`


Assunto sugerido:

`[O3Cloud Manager] Bloqueio por pendência financeira – {cliente}`

Conteúdo mínimo:

Cliente:
{cliente}

Razão Social:
{razao_social}

CNPJ:
{cnpj}

Contrato:
{numero_contrato}

Status:
Pendência financeira registrada

Solicitação:
Realizar o bloqueio do ambiente do cliente devido a pendência financeira.

Registrado por:
{usuario}

Data:
{data_hora}

Observações:
{observacao}

IMPORTANTE:

O O3Cloud Manager não deve bloquear diretamente VM ou ambiente nesta primeira implementação.

O sistema apenas:

* registra a restrição;
* sinaliza o cliente;
* notifica o Suporte para executar o procedimento operacional.

A automação direta de bloqueio de ambiente poderá ser avaliada em sprint futuro.

---

# 7. Notificação ao Cliente

Após a inclusão da inadimplência, enviar também um e-mail para o endereço cadastrado na tela de Clientes.

Utilizar:

`clientes.email`

Se não existir e-mail:

* não impedir o cadastro da inadimplência;
* registrar que a notificação ao cliente não pôde ser enviada;
* exibir aviso para o Financeiro.

O conteúdo deve ser profissional e neutro.

Não expor informações técnicas internas.

Exemplo conceitual:

Assunto:

`Pendência financeira – O3Cloud`

Mensagem:

Informar que foi identificada uma pendência financeira relacionada ao contrato, incluindo razão social e CNPJ do contrato bloqueado.

Incluir os canais de regularização:

* telefone: 19 3142-0232 opção 3;
* telefone/WhatsApp: 19 99912-4028;
* e-mail: contas@o3cloud.com.br.

Os textos finais devem ficar centralizados no Service, evitando conteúdo fixo dentro da Route.

---

# 8. Destaque Visual do Cliente

Enquanto existir inadimplência ativa:

Todas as telas relevantes que apresentem referência ao cliente deverão deixar clara a restrição.

Adicionar destaque visual vermelho.

Exemplos:

## Tela Cliente

Exibir no topo:

`PENDÊNCIA FINANCEIRA`

com:

* fundo vermelho;
* ícone de alerta;
* data da restrição;
* contrato relacionado.

## Listagens

Onde o cliente aparecer, utilizar:

* badge vermelho;
* ícone de alerta; ou
* linha com indicação visual.

Texto sugerido:

`Pendência Financeira`

Evitar pintar telas inteiras de vermelho.

Utilizar destaque consistente e visível sem prejudicar a leitura.

---

# 9. Regra Transversal de Bloqueio

Enquanto o cliente possuir pendência financeira ativa:

## PROIBIR

* criação de novas propostas;
* criação de novas implantações.

A proteção deve existir na camada de **Service**, e não somente na interface.

Isso é obrigatório.

Mesmo que alguém tente chamar diretamente uma rota POST, a operação deve ser recusada.

Retorno funcional sugerido:

`Não é possível realizar esta operação. O cliente possui pendências financeiras ativas.`

---

# 10. Propostas

Ao tentar criar uma proposta para cliente inadimplente:

Bloquear a ação.

Exibir:

`Cliente com pendência financeira. Regularize a situação financeira antes de criar uma nova proposta.`

Se existir tela de seleção de cliente:

O cliente pode continuar aparecendo na pesquisa, porém deve estar identificado:

`⚠ PENDÊNCIA FINANCEIRA`

Não permitir concluir o cadastro.

---

# 11. Implantações

Aplicar exatamente a mesma regra.

Ao tentar criar nova implantação:

Verificar se o cliente possui inadimplência ativa.

Se possuir:

* impedir criação;
* mostrar mensagem;
* não gravar registro parcial.

Clientes já em implantação não devem ser apagados ou alterados automaticamente.

O bloqueio é para **novas implantações**.

---

# 12. Liberação Financeira

Na própria tela Financeiro → Inadimplentes, uma pendência PENDENTE deve possuir ação:

`Liberar`

Ao clicar:

Abrir modal ou formulário de liberação.

O Financeiro deverá obrigatoriamente selecionar uma das opções:

### QUITOU PENDÊNCIA

Cliente efetuou o pagamento integral da pendência.

Código sugerido:

`QUITACAO`

### REALIZOU ACORDO

Foi firmado acordo financeiro e o cliente está autorizado a continuar utilizando/contratando os serviços.

Código sugerido:

`ACORDO`

Também permitir:

* observação da liberação;
* data;
* responsável.

---

# 13. Regra de Liberação do Cliente

Após liberar uma inadimplência:

Verificar:

`Existe outra inadimplência ATIVA em outro contrato deste cliente?`

### Se SIM

Manter cliente:

`COM PENDÊNCIA FINANCEIRA`

Não liberar:

* propostas;
* implantações.

### Se NÃO

Remover restrição financeira do cliente.

Liberar novamente:

* novas propostas;
* novas implantações.

Remover os avisos vermelhos.

Isso é extremamente importante para clientes que possuem vários contratos.

Enviar e-mail para o contato de e-mail do cadastro do cliente, e também para `sac@o3cloud.com.br` e `plantao@o3ti.com.br`, informando a liberação do sistema.

Os e-mails de liberação enviados ao cliente e ao time técnico devem incluir:

* cliente;
* razão social;
* CNPJ no padrão `00.000.000/0000-00`;
* número do contrato;
* tipo de liberação;
* responsável e data quando aplicável.

---

# 14. Histórico

Não executar exclusão física de registros de inadimplência no fluxo operacional.

Para ciclos de teste e saneamento controlado, o perfil `ADMIN` pode remover um histórico da lista por exclusão lógica (`ativo=0`). Essa ação deve retirar o registro das consultas operacionais e do bloqueio financeiro, mas preservar o registro no banco.

O sistema deve preservar:

* contrato;
* cliente;
* data da inclusão;
* usuário que incluiu;
* motivo;
* observação;
* data da liberação;
* usuário que liberou;
* tipo de liberação;
* observação da liberação;
* ativo/inativo para remoção lógica administrativa.

Exemplo:

Cliente ABC

Contrato 2026/00125

Bloqueado:
01/08/2026

Liberado:
07/08/2026

Motivo da liberação:
ACORDO

---

# 15. Modelagem Sugerida

Criar tabela:

`financeiro_inadimplencias`

Campos sugeridos:

```sql
id BIGINT AUTO_INCREMENT PRIMARY KEY,
uuid CHAR(36) NOT NULL,

contrato_id BIGINT NOT NULL,

status ENUM(
    'PENDENTE',
    'LIBERADO'
) NOT NULL DEFAULT 'PENDENTE',

motivo VARCHAR(255) NULL,

observacoes TEXT NULL,

bloqueado_em DATETIME NOT NULL,

bloqueado_por BIGINT NULL,

tipo_liberacao ENUM(
    'QUITACAO',
    'ACORDO'
) NULL,

observacao_liberacao TEXT NULL,

liberado_em DATETIME NULL,

liberado_por BIGINT NULL,

email_suporte_enviado TINYINT(1) DEFAULT 0,

email_cliente_enviado TINYINT(1) DEFAULT 0,

erro_email_suporte TEXT NULL,

erro_email_cliente TEXT NULL,

ativo TINYINT(1) NOT NULL DEFAULT 1,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
```

FK:

`contrato_id → contratos.id`

Não é obrigatório armazenar `cliente_id`.

O cliente deve ser obtido através:

inadimplência
→ contrato
→ cliente

Isso evita duplicidade desnecessária de relacionamento.

---

# 16. Índices

Criar:

```sql
INDEX idx_inadimplencia_contrato (contrato_id)

INDEX idx_inadimplencia_status (status)

INDEX idx_inadimplencia_bloqueado_em (bloqueado_em)
```

Também criar mecanismo para impedir duas inadimplências simultaneamente ativas para o mesmo contrato.

A implementação deve combinar regra no Service e validação transacional. Para MariaDB, evitar `UNIQUE(contrato_id, status)` simples, pois isso bloquearia múltiplos históricos `LIBERADO`. A regra inicial da Sprint 19 deve usar leitura transacional do contrato antes de inserir e índice de apoio em `contrato_id`, `status` e `ativo`.

Migration prevista:

`database/migrations/076_create_financeiro_inadimplencias.sql`

---

# 17. Arquitetura Python

Seguir obrigatoriamente o padrão atual do O3Cloud Manager:

Repository
↓
Service
↓
Routes
↓
Templates
↓
Testes

Criar ou adaptar ao padrão atual do módulo Financeiro:

```text
app/financeiro/inadimplencias_repository.py
app/financeiro/inadimplencias_service.py
app/financeiro/routes.py
```

O módulo Financeiro atual ainda utiliza `routes.py`, `service.py` e `repository.py` em estrutura plana. A Sprint 19 pode isolar a persistência e regra em arquivos próprios de inadimplência, mantendo as rotas no blueprint financeiro existente para reduzir impacto de registro de blueprint.

Adicionar nova chave de permissão:

`inadimplentes`

Essa chave deve entrar em `MENU_PERMISSOES`, `ENDPOINT_PERMISSOES` e no menu lateral do grupo Financeiro.

Templates:

```text
app/templates/financeiro/inadimplencias/
├── index.html
├── form.html
└── view.html
```

---

# 18. Repository

Métodos mínimos:

```python
listar()
total()
buscar_por_id()
buscar_ativa_por_contrato()
listar_ativas_por_cliente()
cliente_possui_pendencia()
criar()
liberar()
```

Repository não deve:

* enviar e-mail;
* bloquear proposta;
* bloquear implantação;
* decidir regra de liberação;
* decidir permissão de exclusão administrativa.

Repository apenas persiste dados.

---

# 19. Service

Criar:

`InadimplenciaService`

Responsável por:

```python
registrar()
liberar()
excluir_historico()
cliente_possui_pendencia()
validar_operacao_cliente()
```

Fluxo de `registrar()`:

1. validar contrato;
2. validar se não existe pendência ativa;
3. criar registro;
4. confirmar transação;
5. disparar notificações;
6. retornar resultado.

Fluxo de `liberar()`:

1. localizar inadimplência;
2. validar status;
3. exigir QUITACAO ou ACORDO;
4. registrar liberação;
5. verificar outras pendências do cliente;
6. recalcular situação financeira;
7. liberar operações apenas se nenhuma outra pendência permanecer ativa.

---

# 20. Serviço Central de Validação Financeira

Não duplicar a regra em Propostas e Implantação.

Criar uma função reutilizável:

```python
InadimplenciaService.validar_operacao_cliente(cliente_id)
```

Exemplo:

```python
if InadimplenciaService.cliente_possui_pendencia(cliente_id):
    raise RegraNegocioError(
        "Cliente possui pendências financeiras ativas."
    )
```

Utilizar essa validação no:

* Service de Propostas;
* Service de Implantação.

No futuro poderá ser reutilizada em outros módulos.

---

# 21. E-mails

Utilizar o serviço de e-mail existente no O3Cloud Manager.

Não colocar SMTP diretamente no módulo de inadimplência.

Criar métodos de alto nível, por exemplo:

```python
notificar_bloqueio_suporte()
notificar_pendencia_cliente()
```

Se já existir provider de comunicação, reutilizá-lo.

Configurar o destinatário do suporte no `.env` ou tabela de configurações:

```env
FINANCEIRO_EMAIL_SUPORTE=sac@o3cloud.com.br,plantao@o3ti.com.br
```

Evitar endereço fixo espalhado pelo código.

---

# 22. Falha de E-mail

A falha no envio de um e-mail NÃO deve desfazer o registro da inadimplência.

Exemplo:

Pendência registrada com sucesso
+
Falha ao enviar e-mail

Resultado:

* inadimplência continua ativa;
* cliente continua bloqueado;
* sistema registra erro;
* interface avisa Financeiro.

Nunca executar rollback da inadimplência porque SMTP/API ficou indisponível.

---

# 23. Notificação na Liberação

Recomendação:

Quando a pendência for liberada, enviar também e-mail para:

`sac@o3cloud.com.br` e `plantao@o3ti.com.br`

informando:

`Cliente liberado financeiramente`

para que o Suporte possa retirar eventual bloqueio aplicado ao ambiente.

Dados:

* cliente;
* razão social;
* CNPJ;
* contrato;
* tipo da liberação;
* responsável;
* data;
* observação.

Essa notificação é altamente recomendada porque o bloqueio operacional do ambiente foi solicitado anteriormente ao Suporte.

O envio para o cliente na liberação deve ocorrer pelo serviço de e-mail existente e incluir razão social e CNPJ do contrato liberado.

---

# 24. Segurança

Apenas usuários autorizados do Financeiro devem poder:

* registrar inadimplência;
* liberar inadimplência.

Apenas o perfil `ADMIN` deve poder:

* remover histórico de inadimplência da lista por inativação lógica (`ativo=0`).

Outros usuários poderão visualizar o aviso financeiro conforme permissão, mas não alterar o status.

Registrar obrigatoriamente:

* usuário;
* data;
* ação.

---

# 25. Interface – Listagem

Exemplo:

```text
INADIMPLENTES

[ + Nova Inadimplência ]

Cliente          Contrato       Desde       Status       Ações
----------------------------------------------------------------
Cliente ABC      2026/00125     05/08       PENDENTE     Ver | Liberar | Excluir histórico (ADMIN)
Cliente XYZ      2026/00190     07/08       LIBERADO     Ver | Excluir histórico (ADMIN)
```

Usar badge vermelho:

`PENDENTE`

Para histórico:

`LIBERADO`

---

# 26. Interface – Cliente

Adicionar alerta no topo das telas relacionadas ao cliente:

```text
⚠ PENDÊNCIA FINANCEIRA

Este cliente possui pendências financeiras ativas.

Contrato: 2026/00125
Desde: 05/08/2026
```

Não exibir detalhes financeiros sensíveis desnecessariamente para perfis sem autorização.

---

# 27. Critérios de Aceite

A Sprint estará concluída quando:

1. Financeiro conseguir abrir tela Inadimplentes.
2. Conseguir selecionar contrato.
3. Sistema identificar automaticamente o cliente.
4. Não permitir pendência ativa duplicada para o mesmo contrato.
5. Registrar inadimplência.
6. Enviar notificação para `sac@o3cloud.com.br`.
7. Enviar notificação para `clientes.email`.
8. Falha de e-mail não cancelar o bloqueio.
9. Cliente aparecer com destaque vermelho.
10. Nova proposta para cliente inadimplente ser bloqueada.
11. Nova implantação para cliente inadimplente ser bloqueada.
12. Bloqueio existir também no Service e não apenas na interface.
13. Financeiro conseguir liberar pendência.
14. Liberação exigir:

    * QUITACAO; ou
    * ACORDO.
15. Histórico permanecer salvo.
16. Cliente continuar bloqueado caso outro contrato ainda possua pendência ativa.
17. Cliente ser liberado quando não houver mais pendências ativas.
18. Alertas visuais desaparecerem após liberação.
19. Novas propostas voltarem a ser permitidas.
20. Novas implantações voltarem a ser permitidas.
21. Testes existentes continuarem passando.
22. Documentação, DER, modelo físico e CHANGELOG serem atualizados.
23. Busca e visualização de CNPJ usarem o padrão `00.000.000/0000-00`, aceitando CNPJ com ou sem máscara.
24. E-mails de bloqueio e liberação incluírem razão social e CNPJ para cliente e time técnico.
25. ADMIN conseguir remover histórico por inativação lógica, enquanto outros perfis não veem a ação e são bloqueados no backend.

---

# 28. Testes Obrigatórios

Testar:

* cliente com 1 contrato;
* cliente com vários contratos;
* inadimplência em apenas um dos contratos;
* inadimplência em dois contratos simultaneamente;
* liberação de apenas um contrato;
* liberação do último contrato pendente;
* quitação;
* acordo;
* cliente sem e-mail;
* erro no envio para suporte;
* tentativa de criar proposta;
* tentativa de criar implantação;
* tentativa direta por POST;
* duplicidade de inadimplência;
* usuário sem permissão;
* histórico após liberação.

---

# 29. Fora do Escopo

Não implementar nesta Sprint:

* bloqueio automático no Proxmox;
* shutdown de VM;
* bloqueio de rede;
* suspensão automática de VPS;
* integração automática com cobrança do OMIE;
* baixa automática por boleto;
* liberação automática por API bancária.

Esses itens poderão ser evoluções futuras.

Nesta Sprint, o Financeiro controla a restrição no O3Cloud Manager e o Suporte recebe a solicitação operacional por e-mail.

---

# 30. Resultado Esperado

O fluxo final deverá ser:

```text
Financeiro
    ↓
Seleciona Contrato
    ↓
Registra Pendência
    ↓
O3Cloud Manager
    ├── registra histórico
    ├── marca cliente com restrição
    ├── bloqueia novas propostas
    ├── bloqueia novas implantações
    ├── envia e-mail ao Suporte
    └── envia e-mail ao Cliente

Após regularização:

Financeiro
    ↓
Liberar
    ↓
[Quitação] ou [Acordo]
    ↓
Verificar outras pendências
    ↓
Se nenhuma:
    ├── retirar restrição
    ├── liberar propostas
    ├── liberar implantações
    ├── remover alertas vermelhos
    └── notificar liberação
```

A arquitetura deve preservar histórico completo e permitir futuras automações sem necessidade de remodelar o módulo.
 _____

# Sprint 20 – Módulo de Relatórios Customizáveis

## 1. Objetivo

Criar no O3Cloud Manager um módulo central de **Relatórios Customizáveis**, permitindo que usuários autorizados construam relatórios de acordo com a necessidade de cada departamento.

O sistema possui vários módulos e diferentes necessidades operacionais. Portanto, não criar apenas relatórios fixos.

A solução deve permitir:

* selecionar a fonte de dados;
* escolher os campos que serão exibidos;
* aplicar filtros;
* filtrar por período;
* ordenar;
* agrupar;
* realizar cálculos quando existirem campos numéricos;
* salvar modelos de relatórios;
* executar novamente modelos salvos;
* exportar resultados;
* imprimir diretamente.

Formatos obrigatórios:

* PDF;
* CSV;
* XLSX;
* DOCX;
* impressão direta pelo navegador.

---

# 2. Controle de Acesso

Somente usuários cujo perfil possuir permissão explícita para acessar o módulo de Relatórios poderão abrir a tela.

Criar permissão funcional equivalente a:

`RELATORIOS_ACESSAR`

O controle deve existir no backend e não apenas no menu.

Usuários sem permissão:

* não visualizam o item Relatórios;
* não acessam diretamente as rotas;
* recebem resposta de acesso negado quando tentarem acessar por URL.

---

# 3. Perfis com Poder de Criação

Os seguintes perfis poderão criar e customizar relatórios:

* Administrador;
* Diretoria;
* Administrativo_Gestor.

Criar permissão específica equivalente a:

`RELATORIOS_CRIAR`

Não depender somente do nome textual do perfil.

Utilizar o sistema de permissões atual.

Outros perfis poderão futuramente possuir:

`RELATORIOS_VISUALIZAR`

permitindo executar relatórios previamente disponibilizados sem modificar sua definição.

---

# 4. Princípio de Segurança

O construtor de relatórios NÃO deve permitir SQL livre digitado pelo usuário.

Não criar campo:

`Digite sua consulta SQL`

A aplicação deverá trabalhar com **fontes de dados previamente cadastradas e autorizadas**.

Isso evita:

* SQL Injection;
* exposição de dados sensíveis;
* consultas destrutivas;
* acesso indevido entre departamentos;
* travamento do banco por queries arbitrárias.

---

# 5. Conceito de Fonte de Dados

Criar conceito:

`Fonte de Relatório`

Exemplos:

* Clientes;
* Contratos;
* Inadimplências;
* Faturamentos;
* Leads;
* Eventos;
* Participantes de Eventos;
* Contatos;
* Oportunidades;
* Propostas;
* Parceiros;
* Implantações;
* Ambientes;
* Recursos;
* Licenças;
* Demandas Administrativas;
* Comissões;
* Histórico de Sincronizações.

Cada fonte deverá disponibilizar somente campos explicitamente autorizados.

---

# 6. Catálogo de Campos

Cada fonte deverá possuir definição de campos disponíveis.

Exemplo conceitual:

Fonte:

`Contratos`

Campos:

* número;
* cliente;
* origem;
* status;
* início da vigência;
* fim da vigência;
* valor mensal;
* dia de faturamento;
* vendedor;
* projeto.

Cada campo deverá possuir metadados:

* código interno;
* nome exibido;
* tipo;
* se pode ser filtrado;
* se pode ser agrupado;
* se pode ser ordenado;
* se pode receber agregação;
* formato de saída;
* nível de sensibilidade.

Tipos previstos:

* TEXTO;
* INTEIRO;
* DECIMAL;
* MOEDA;
* DATA;
* DATETIME;
* BOOLEAN;
* STATUS;
* PERCENTUAL.

---

# 7. Construtor de Relatório

Criar tela:

`Relatórios → Novo Relatório`

Fluxo:

1. Usuário informa nome do relatório.
2. Seleciona uma fonte de dados.
3. Sistema apresenta campos disponíveis.
4. Usuário seleciona os campos desejados.
5. Define a ordem das colunas.
6. Configura filtros.
7. Configura ordenação.
8. Configura agrupamentos, quando aplicável.
9. Configura cálculos.
10. Visualiza uma prévia.
11. Executa.
12. Opcionalmente salva como modelo.

---

# 8. Seleção de Campos

A interface deverá permitir adicionar e remover campos.

Preferencialmente utilizar:

* seleção múltipla; ou
* lista de campos disponíveis versus selecionados;
* drag-and-drop apenas se já houver infraestrutura JS segura no projeto.

Não tornar drag-and-drop obrigatório para a primeira versão.

Exemplo:

Disponíveis:

* Cliente
* Contrato
* Status
* Valor mensal
* Início
* Fim
* Origem

Selecionados:

1. Cliente
2. Contrato
3. Status
4. Valor mensal

---

# 9. Filtros

Suportar filtros de acordo com o tipo do campo.

## Texto

* igual;
* diferente;
* contém;
* começa com.

## Número / Moeda

* igual;
* maior que;
* maior ou igual;
* menor que;
* menor ou igual;
* entre.

## Data

* igual;
* antes;
* depois;
* entre.

## Status / Enum

* igual;
* diferente;
* em uma lista.

## Boolean

* sim;
* não.

---

# 10. Filtro por Período

Para campos DATA e DATETIME permitir:

`Data inicial`

`Data final`

Exemplo:

01/07/2026 a 31/07/2026

O usuário deve poder escolher qual campo de data será utilizado quando a fonte possuir mais de uma data.

Exemplo:

Contratos:

* início da vigência;
* fim da vigência;
* data de criação;
* última sincronização.

---

# 11. Cálculos

Para campos numéricos permitir cálculos.

Agregações previstas:

* SOMA;
* MÉDIA;
* MÍNIMO;
* MÁXIMO;
* CONTAGEM;
* CONTAGEM DISTINTA.

Exemplo:

Relatório de contratos:

Campo:

`valor_mensal`

Agregação:

`SOMA`

Resultado:

`Total mensal: R$ 185.320,00`

---

# 12. Agrupamentos

Permitir agrupamento por campos compatíveis.

Exemplos:

## Comercial

Agrupar oportunidades por:

* executivo;
* status;
* parceiro;
* mês.

Depois calcular:

* total de oportunidades;
* valor estimado;
* valor médio;
* taxa de ganho.

## Financeiro

Agrupar contratos por:

* cliente;
* status;
* vendedor;
* mês;
* origem.

Calcular:

* quantidade;
* soma do valor mensal;
* média.

---

# 13. Campos Calculados

Na primeira versão NÃO permitir fórmulas arbitrárias escritas pelo usuário.

Permitir apenas cálculos predefinidos e seguros.

No futuro poderá existir recurso de:

`Campo calculado`

mas deve ser implementado com parser seguro e nunca com execução direta de Python, SQL ou JavaScript.

---

# 14. Relatórios Salvos

Permitir salvar uma configuração como modelo.

Exemplo:

`Contratos Ativos por Cliente`

Salvar:

* fonte;
* campos;
* filtros;
* agrupamentos;
* ordenação;
* agregações;
* nome;
* descrição;
* criador.

Posteriormente o usuário poderá:

* executar;
* duplicar;
* editar;
* excluir, conforme permissão.

---

# 15. Visibilidade dos Modelos

Cada relatório salvo deverá possuir visibilidade:

* PRIVADO;
* PERFIL;
* GLOBAL.

## PRIVADO

Somente o criador.

## PERFIL

Disponível para perfis autorizados escolhidos.

## GLOBAL

Disponível para usuários que tenham permissão de visualizar relatórios.

Somente Administrador, Diretoria e Administrativo_Gestor poderão publicar modelos GLOBAL.

---

# 16. Exportação

Todos os relatórios gerados ou exibidos devem possuir cabeçalho padrão com o logo da O3Cloud no topo.

Usar preferencialmente o ativo existente:

`app/static/img/logo.png`

O cabeçalho deve aparecer em:

* prévia/resultado HTML;
* impressão direta;
* PDF;
* DOCX;
* XLSX, quando tecnicamente suportado pela biblioteca;
* capa ou primeira linha identificadora nos formatos em que imagem não for adequada.

Na tela do resultado disponibilizar:

`Exportar`

Opções:

* PDF;
* CSV;
* XLSX;
* DOCX;
* Imprimir.

---

# 17. CSV

Gerar arquivo:

* UTF-8;
* cabeçalho textual com identificação `O3Cloud Manager`, já que CSV não suporta imagem de logo de forma nativa;
* cabeçalho de colunas;
* dados já filtrados;
* somente colunas selecionadas.

Evitar conversões desnecessárias.

---

# 18. XLSX

Utilizar biblioteca Python compatível com a arquitetura atual.

Preferencialmente:

`openpyxl`

Gerar planilha profissional contendo:

* logo da O3Cloud no cabeçalho;
* título;
* data de geração;
* usuário;
* filtros aplicados;
* cabeçalhos;
* dados;
* totais;
* formatação de datas;
* formatação monetária;
* auto filtro;
* congelamento do cabeçalho quando aplicável.

Não utilizar LibreOffice como mecanismo principal para XLSX.

---

# 18.1. Dependências de Exportação

Dependências esperadas para implementação:

* `openpyxl` para XLSX;
* `python-docx` para DOCX;
* `reportlab` para PDF.

As dependências confirmadas devem permanecer registradas em `requirements.txt`.

---

# 19. PDF

O PDF deve possuir:

* logo da O3Cloud no cabeçalho;
* nome do relatório;
* data/hora da geração;
* usuário que gerou;
* período/filtros;
* tabela;
* totais;
* paginação;
* rodapé.

Para relatórios muito largos:

* utilizar orientação paisagem;
* ajustar largura das colunas;
* se necessário informar que determinado conjunto de colunas é mais adequado para XLSX.

---

# 20. DOCX

Gerar documento contendo:

* logo da O3Cloud no cabeçalho;
* título;
* data de geração;
* filtros;
* tabela;
* totalizadores;
* rodapé.

Utilizar biblioteca Python apropriada, preferencialmente:

`python-docx`

---

# 21. Impressão Direta

Criar versão HTML específica para impressão.

Utilizar:

`window.print()`

com CSS:

`@media print`

Ocultar:

* navbar;
* sidebar;
* botões;
* filtros;
* elementos de navegação.

Manter:

* logo da O3Cloud no cabeçalho;
* título;
* filtros;
* dados;
* totais;
* data da geração.

---

# 22. Paginação

Na tela:

utilizar paginação.

Não carregar centenas de milhares de registros no browser.

Exemplo:

50 ou 100 registros por página.

Exportações deverão executar a consulta completa filtrada, respeitando limite máximo de segurança.

---

# 23. Limite de Exportação

Criar configuração:

`RELATORIOS_MAX_EXPORT_ROWS`

Exemplo inicial:

50000

Se ultrapassar:

* impedir exportação síncrona;
* informar ao usuário;
* futuramente permitir geração assíncrona.

Não permitir que uma consulta gigantesca trave a aplicação.

---

# 24. Timeout

Consultas de relatórios deverão possuir limite operacional.

Registrar:

* tempo de execução;
* quantidade de registros;
* usuário;
* fonte.

Relatórios muito pesados deverão ser identificáveis para futura otimização.

---

# 25. Auditoria

Registrar toda geração de relatório.

Criar tabela conceitual:

`relatorios_execucoes`

Campos:

* id;
* uuid;
* relatorio_id, se salvo;
* usuario_id;
* fonte;
* filtros_snapshot;
* colunas_snapshot;
* formato;
* registros;
* iniciado_em;
* finalizado_em;
* duracao_ms;
* status;
* erro.

Não armazenar necessariamente todos os dados retornados.

Guardar configuração utilizada.

---

# 26. Modelagem Sugerida

Criar tabelas:

## relatorios

* id;
* uuid;
* nome;
* descricao;
* fonte_codigo;
* configuracao_json;
* visibilidade;
* criado_por;
* ativo;
* created_at;
* updated_at.

## relatorios_perfis

* id;
* relatorio_id;
* perfil_id.

## relatorios_execucoes

* id;
* uuid;
* relatorio_id;
* usuario_id;
* fonte_codigo;
* formato;
* filtros_json;
* campos_json;
* registros;
* duracao_ms;
* status;
* mensagem_erro;
* created_at;
* finalizado_em.

Os nomes devem ser adaptados ao padrão real do banco.

---

# 27. Configuração JSON

A definição do relatório pode ser armazenada em JSON.

Exemplo conceitual:

```json
{
  "fonte": "contratos",
  "campos": [
    "cliente",
    "numero",
    "status",
    "valor_mensal"
  ],
  "filtros": [
    {
      "campo": "status",
      "operador": "IGUAL",
      "valor": "ATIVO"
    }
  ],
  "ordenacao": [
    {
      "campo": "cliente",
      "direcao": "ASC"
    }
  ],
  "agrupamentos": [],
  "agregacoes": [
    {
      "campo": "valor_mensal",
      "funcao": "SOMA"
    }
  ]
}
```

Nunca converter esse JSON diretamente em SQL sem validação.

---

# 28. Engine de Relatórios

Criar camada central:

`ReportEngine`

Responsabilidades:

* carregar fonte autorizada;
* validar campos;
* validar filtros;
* validar operadores;
* gerar SQL seguro;
* construir parâmetros;
* executar consulta;
* montar agregações;
* aplicar paginação;
* retornar resultado estruturado.

Nunca concatenar valores fornecidos pelo usuário diretamente no SQL.

Todos os valores devem utilizar parâmetros `%s`.

Campos e nomes de tabelas somente podem vir de catálogo interno previamente cadastrado.

---

# 29. Fontes como Código

Na primeira versão, recomendo definir fontes no backend, e não permitir cadastro livre pela interface.

Exemplo conceitual:

```python
REPORT_SOURCES = {
    "contratos": {
        "nome": "Contratos",
        "from": "...",
        "campos": {...}
    }
}
```

ou classes:

```python
ContratoReportSource
ClienteReportSource
OportunidadeReportSource
```

Isso torna a solução muito mais segura.

No futuro, o catálogo poderá migrar para banco se houver necessidade.

---

# 30. Arquitetura Python

Sugestão:

```text
app/relatorios/
├── __init__.py
├── routes.py
├── service.py
├── repository.py
├── engine.py
├── permissions.py
├── sources/
│   ├── __init__.py
│   ├── clientes.py
│   ├── contratos.py
│   ├── financeiro.py
│   ├── comercial.py
│   └── administrativo.py
└── exporters/
    ├── __init__.py
    ├── csv_exporter.py
    ├── xlsx_exporter.py
    ├── pdf_exporter.py
    └── docx_exporter.py
```

Templates:

```text
templates/relatorios/
├── index.html
├── builder.html
├── resultado.html
├── view.html
└── print.html
```

---

# 31. Separação de Responsabilidades

Routes:

* receber request;
* validar permissão;
* chamar Service;
* renderizar.

Service:

* regras de negócio;
* salvar modelos;
* validar visibilidade;
* chamar Engine;
* exportar.

Engine:

* consulta dinâmica segura.

Repository:

* persistência de relatórios e histórico.

Exporters:

* transformação do resultado nos formatos solicitados.

---

# 32. Permissões por Fonte

A permissão Relatórios não deverá automaticamente conceder acesso a todos os dados.

Exemplo:

Um usuário pode ter:

`RELATORIOS_ACESSAR`

mas não possuir:

`FINANCEIRO_VISUALIZAR`

Nesse caso:

a fonte Financeiro NÃO deve aparecer.

A disponibilidade das fontes deve considerar as permissões funcionais dos módulos.

Exemplo:

* Financeiro → exige permissão financeira;
* CRM → exige permissão comercial;
* Administrativo → exige permissão administrativa.

Administrador e Diretoria podem seguir regras específicas conforme sistema atual.

---

# 33. Dados Sensíveis

Campos sensíveis não devem ficar automaticamente disponíveis.

Exemplos possíveis:

* dados bancários;
* credenciais;
* tokens;
* API Keys;
* senhas;
* documentos sigilosos.

Nunca disponibilizar segredos em fonte de relatório.

---

# 34. Cálculos Comerciais

Fontes do CRM poderão disponibilizar métricas como:

* quantidade de leads;
* oportunidades por executivo;
* oportunidades ganhas;
* oportunidades perdidas;
* valor estimado;
* valor ganho;
* ticket médio;
* taxa de conversão.

Essas métricas deverão utilizar regras centrais previamente definidas.

---

# 35. Cálculos Financeiros

Fontes Financeiras poderão disponibilizar:

* soma de contratos;
* receita mensal;
* quantidade de contratos;
* inadimplências;
* valores por cliente;
* valores por período.

Não reinventar cálculos já existentes nos Services do módulo Financeiro quando houver regra de negócio específica.

---

# 36. Exemplos de Relatórios

## Diretoria

`Receita mensal por cliente`

Campos:

* Cliente;
* Contratos;
* Valor Mensal.

Agrupar:

Cliente.

Calcular:

SOMA(valor_mensal).

---

## Comercial

`Oportunidades por Executivo`

Campos:

* Executivo;
* Status;
* Valor;
* Probabilidade.

Período:

01/07/2026 → 31/07/2026.

Agrupar:

Executivo.

Calcular:

CONTAGEM;

SOMA(valor).

---

## Administrativo

`Demandas administrativas por colaborador`

Campos:

* Colaborador;
* Tipo;
* Data;
* Status;
* Prazo.

Filtrar:

Status = PENDENTE.

---

## Financeiro

`Contratos inadimplentes`

Campos:

* Cliente;
* Contrato;
* Data da pendência;
* Status;
* Tipo de regularização.

---

# 37. UX do Builder

Organizar a tela em etapas:

1. Fonte
2. Campos
3. Filtros
4. Agrupamento e cálculos
5. Ordenação
6. Prévia
7. Salvar / Exportar

Não apresentar todas as configurações ao mesmo tempo se isso tornar a interface confusa.

---

# 38. Prévia

Antes de executar relatório completo:

permitir `Pré-visualizar`.

Limitar a prévia, por exemplo:

100 registros.

A prévia deve mostrar:

* colunas;
* filtros;
* agregações;
* amostra dos dados.

---

# 39. Tratamento de Erros

Mensagens funcionais:

* fonte não autorizada;
* campo inválido;
* filtro inválido;
* período inválido;
* nenhum resultado;
* limite de exportação excedido;
* erro de geração;
* consulta excedeu tempo permitido.

Nunca exibir SQL bruto ao usuário.

---

# 40. Testes Obrigatórios

Testar:

1. usuário sem RELATORIOS_ACESSAR;
2. usuário autorizado;
3. Administrador criando relatório;
4. Diretoria criando relatório;
5. Administrativo_Gestor criando relatório;
6. perfil somente visualização;
7. fonte sem permissão;
8. seleção de campos;
9. filtros texto;
10. filtros numéricos;
11. filtros data;
12. múltiplos filtros;
13. agrupamento;
14. soma;
15. média;
16. contagem;
17. ordenação;
18. paginação;
19. relatório sem resultados;
20. salvar;
21. editar;
22. duplicar;
23. excluir;
24. visibilidade privada;
25. visibilidade por perfil;
26. global;
27. CSV;
28. XLSX;
29. PDF;
30. DOCX;
31. impressão;
32. caracteres especiais/acentuação;
33. valores monetários;
34. datas brasileiras;
35. tentativa de manipular nome de campo;
36. tentativa de SQL Injection;
37. tentativa de acessar fonte sem permissão;
38. limite máximo de exportação;
39. registro de auditoria;
40. regressão dos módulos existentes.

---

# 41. Critérios de Aceite

A Sprint será considerada concluída quando:

* somente usuários autorizados acessarem Relatórios;
* Administrador, Diretoria e Administrativo_Gestor puderem criar modelos;
* fontes forem disponibilizadas conforme permissão;
* usuário puder selecionar campos;
* aplicar filtros;
* selecionar período;
* ordenar;
* agrupar;
* realizar cálculos numéricos;
* visualizar prévia;
* salvar modelo;
* executar modelo salvo;
* exportar CSV;
* exportar XLSX;
* exportar PDF;
* exportar DOCX;
* imprimir;
* cabeçalho dos relatórios exibir o logo da O3Cloud;
* auditoria registrar execução;
* nenhuma query arbitrária for permitida;
* SQL usar parâmetros;
* dados sensíveis não forem expostos;
* nenhum módulo existente for quebrado;
* documentação e CHANGELOG forem atualizados.

---

# 42. Fora do Escopo da Primeira Versão

Não implementar agora:

* BI visual completo;
* dashboards drag-and-drop;
* gráficos customizáveis complexos;
* linguagem própria de fórmulas;
* SQL livre;
* relatórios agendados por e-mail;
* execução assíncrona de milhões de registros;
* integração direta com Power BI;
* criação de views pelo usuário;
* pivot table avançada.

Essas funcionalidades podem ser evoluções futuras.

---

# 43. Evoluções Futuras

A arquitetura deve permitir posteriormente:

* gráficos;
* dashboards;
* relatórios favoritos;
* agendamento;
* envio por e-mail;
* relatórios recorrentes;
* exportação assíncrona;
* compartilhamento por link interno;
* API de relatórios;
* integração com BI;
* comparativos de períodos;
* indicadores calculados;
* tabelas dinâmicas.

---

# 44. Sequência de Implementação Recomendada

Implementar nesta ordem:

### Etapa 1

Permissões e módulo base.

### Etapa 2

Catálogo de fontes e campos.

### Etapa 3

Engine de filtros e consulta segura.

### Etapa 4

Builder.

### Etapa 5

Resultados, paginação e cálculos.

### Etapa 6

Salvar modelos.

### Etapa 7

CSV e XLSX.

### Etapa 8

PDF, DOCX e impressão.

### Etapa 9

Auditoria.

### Etapa 10

Testes e documentação.

Não iniciar exportadores antes de a Engine estar homologada.

---

# 45. Regra de Desenvolvimento

Antes de implementar:

1. Ler arquitetura atual.
2. Ler sistema de usuários, perfis e permissões.
3. Identificar todas as permissões já existentes.
4. Mapear módulos disponíveis.
5. Identificar Services/Repositories que já oferecem consultas úteis.
6. Mapear convenções de UUID, soft delete, auditoria e paginação.
7. Apresentar proposta de migration.
8. Implementar um arquivo por vez.
9. Executar testes a cada etapa.
10. Não refatorar módulos existentes sem necessidade.

O módulo de Relatórios deve se integrar à arquitetura atual, e não exigir reestruturação do ERP.

___________________________________________________________________________________________________

# Sprint 22 - Monitoramento de Reajustes Contratuais

Status: Concluido tecnicamente em 14/08/2026 para liberacao da versao Beta.

Implementacao entregue:

* Tela `Financeiro > Reajustes Contratuais` com filtros, cards e situacao por contrato.
* Calculo de idade contratual, proximo aniversario e dias para reajuste usando `contratos.inicio_vigencia`.
* Historico `contratos_valores_historico` para preservar alteracoes de valores.
* Comparacao prioritaria entre primeiro faturamento sincronizado em `financeiro_recebimentos` e valor atual do contrato.
* Configuracao de alertas 30/15/7 dias e usuarios destinatarios selecionados.
* Controle de duplicidade em `contratos_reajustes_alertas`.
* Botao `Verificar agora`, comando CLI `reajustes-processar-alertas` e cron diario.
* Secao `Reajuste Contratual` no detalhe do contrato.
* Permissao `reajustes_contratuais` no grupo Financeiro.
* Testes automatizados finais do projeto: `48 passed`.

Retrato operacional validado em 14/08/2026:

* 204 contratos monitorados.
* 177 contratos com base pelo primeiro faturamento sincronizado.
* 56 contratos com alteracao detectada entre base inicial e valor atual.
* 70 contratos sem reajuste detectado.
* 2 contratos ainda sem base de comparacao.

## 1. Objetivo

Criar no O3Cloud Manager um recurso para acompanhar automaticamente a data inicial dos contratos sincronizados do OMIE, identificar contratos com mais de 12 meses de vigência e verificar se houve reajuste de valor.

Também deverá existir uma rotina preventiva para contratos que ainda não completaram 12 meses, permitindo configurar alertas com antecedência de:

* 7 dias;
* 15 dias;
* 30 dias.

Os alertas deverão ser exibidos no sistema e poderão, opcionalmente, ser enviados por e-mail para usuários selecionados.

---

## 2. Fonte dos Dados

Utilizar os contratos já sincronizados do OMIE.

Campo principal:

`inicio_vigencia`

O cálculo de aniversário contratual deverá partir desse campo.

Não criar outra data manual quando a informação já existir no contrato sincronizado.

---

## 3. Conceito de Aniversário Contratual

Para cada contrato:

`data_proximo_reajuste = inicio_vigencia + N anos`

Onde N representa o próximo aniversário ainda não ultrapassado.

Exemplo:

Início:

`15/09/2025`

Primeiro aniversário:

`15/09/2026`

Segundo aniversário:

`15/09/2027`

O cálculo não deve se limitar apenas ao primeiro período de 12 meses.

Contratos com vários anos de existência deverão continuar sendo monitorados a cada aniversário.

---

## 4. Tela Financeiro → Reajustes Contratuais

Adicionar nova opção no módulo Financeiro:

`Reajustes Contratuais`

A tela deverá apresentar inicialmente:

* número do contrato;
* cliente;
* vendedor, quando disponível;
* data inicial;
* idade do contrato;
* último valor conhecido;
* valor atual;
* percentual de variação;
* próximo aniversário;
* dias restantes;
* situação do reajuste;
* status do contrato.

Filtros:

* cliente;
* contrato;
* vendedor;
* status;
* ano de aniversário;
* situação do reajuste;
* contratos vencidos para reajuste;
* contratos próximos do reajuste.

---

## 5. Situações do Reajuste

Sugestão:

* `A_VENCER`
* `REAJUSTE_PROXIMO`
* `REAJUSTE_VENCIDO`
* `REAJUSTADO`
* `SEM_BASE_COMPARACAO`
* `IGNORADO`

### A_VENCER

Contrato ainda fora das janelas configuradas.

### REAJUSTE_PROXIMO

Contrato dentro de 7, 15 ou 30 dias do próximo aniversário.

### REAJUSTE_VENCIDO

Contrato atingiu ou ultrapassou a data de aniversário sem evidência de reajuste.

### REAJUSTADO

Sistema encontrou alteracao entre o primeiro faturamento sincronizado do contrato e o valor atual. A variacao pode ser positiva ou negativa e deve ser conferida pelo Financeiro.

### SEM_REAJUSTE_DETECTADO

Contrato possui primeiro faturamento sincronizado, ja tem 12 meses ou mais de vigencia e o valor atual permanece igual ao valor base. Deve ser investigado pelo Financeiro para confirmar se o reajuste deveria ter ocorrido.

### SEM_BASE_COMPARACAO

Nao existe primeiro faturamento sincronizado nem historico suficiente para confirmar se houve reajuste.

---

## 6. Histórico de Valores do Contrato

Para verificar se houve reajuste, nao basta utilizar apenas o valor atual.

A regra operacional final usa, quando disponivel, o primeiro faturamento sincronizado em `financeiro_recebimentos` como valor fechado inicial do contrato e compara esse valor com o valor atual do contrato. O historico proprio continua existindo para auditar alteracoes detectadas depois da implantacao do monitoramento.

O sistema deverá preservar histórico dos valores sincronizados.

Criar tabela conceitual:

`contratos_valores_historico`

Campos sugeridos:

* id;
* uuid;
* contrato_id;
* valor_mensal;
* valor_servicos_bruto;
* valor_descontos;
* valor_servicos_liquido;
* vigencia_referencia;
* detectado_em;
* origem;
* created_at.

Sempre que a sincronização detectar alteração relevante no valor do contrato:

1. comparar com o último valor conhecido;
2. registrar um novo histórico;
3. não sobrescrever o histórico anterior.

Não criar registros duplicados se os valores não mudaram.

---

## 7. Identificação de Reajuste

Para contratos que já completaram 12 meses ou mais:

1. localizar o aniversário contratual correspondente;
2. consultar histórico de valores anterior ao aniversário;
3. consultar valor após o aniversário;
4. comparar.

Exemplo:

Valor antes do aniversário:

`R$ 1.000,00`

Valor após:

`R$ 1.050,00`

Variação:

`5%`

Resultado:

`REAJUSTADO`

Fórmula:

`percentual = ((valor_novo - valor_anterior) / valor_anterior) * 100`

Utilizar Decimal.

Nunca utilizar float para cálculos monetários.

---

## 8. O que é considerado valor para comparação

A arquitetura deverá permitir definir qual campo é a referência principal.

Sugestão inicial:

`valor_mensal`

Se o módulo de contratos possuir valores mais específicos, como:

* valor_servicos_bruto;
* valor_descontos;
* valor_servicos_liquido;

eles também poderão ser exibidos para auditoria.

O sistema não deve presumir que todo aumento de valor seja necessariamente um reajuste contratual.

Ele deve indicar:

`Alteração de valor detectada`

e permitir auditoria.

---

## 9. Contratos com mais de 12 meses

Criar visão específica:

`Contratos com reajuste a validar`

Critério:

* contrato ATIVO;
* idade >= 12 meses.

Para cada contrato indicar:

* aniversário anterior;
* valor antes;
* valor depois;
* diferença;
* percentual;
* situação.

---

## 10. Contratos ainda não vencidos

Para contratos que ainda não chegaram ao próximo aniversário:

Calcular:

`dias_para_reajuste`

Exemplo:

Próximo reajuste:

`30/09/2026`

Hoje:

`31/08/2026`

Resultado:

`30 dias`

---

## 11. Configuração dos Alertas

Permitir configurar quais antecedências serão utilizadas.

Valores inicialmente suportados:

* 7 dias;
* 15 dias;
* 30 dias.

Tela sugerida:

`Financeiro → Reajustes → Configurações`

Configurações:

* alerta de 30 dias: ativo/inativo;
* alerta de 15 dias: ativo/inativo;
* alerta de 7 dias: ativo/inativo;
* envio por e-mail: ativo/inativo.

Não deixar os dias espalhados em código.

Preferencialmente armazenar em configuração.

---

## 12. Destinatários dos Alertas

Permitir selecionar usuários do O3Cloud Manager que receberão os e-mails.

Exemplo:

`Usuários notificados`

* Financeiro Gestor;
* Diretoria;
* Executivo responsável;
* outros usuários selecionados.

Não utilizar uma lista fixa no código.

Criar relação entre configuração de alerta e usuários.

---

## 13. Notificação em Tela

Quando um contrato entrar em uma janela de alerta, exibir notificação no sistema.

Exemplo:

`Contrato 2026/00150 – Cliente ABC`

`Reajuste contratual em 15 dias.`

Informações:

* cliente;
* contrato;
* data inicial;
* próximo aniversário;
* dias restantes;
* valor atual;
* vendedor.

---

## 14. Cores dos Alertas

Sugestão visual:

30 dias:

`azul`

15 dias:

`amarelo`

7 dias:

`laranja`

vencido:

`vermelho`

reajustado:

`verde`

Seguir o padrão visual atual do O3Cloud Manager.

---

## 15. E-mails

Quando configurado, enviar e-mail para os usuários selecionados.

Assunto sugerido:

`[O3Cloud Manager] Reajuste contratual em {dias} dias – {cliente}`

Conteúdo:

* cliente;
* contrato;
* início da vigência;
* próximo aniversário;
* dias restantes;
* valor atual;
* vendedor;
* link interno para abrir o contrato.

Não enviar um e-mail novo toda vez que a rotina rodar.

---

## 16. Controle de Duplicidade dos Alertas

Registrar cada alerta enviado.

Criar tabela:

`contratos_reajustes_alertas`

Campos sugeridos:

* id;
* uuid;
* contrato_id;
* aniversario_referencia;
* antecedencia_dias;
* tipo;
* exibido_em;
* email_enviado_em;
* created_at.

Criar unicidade conceitual:

`contrato_id + aniversario_referencia + antecedencia_dias`

Isso evita:

* vários e-mails de 30 dias;
* vários alertas de 15 dias;
* vários alertas de 7 dias.

No próximo aniversário, novos alertas poderão ser gerados normalmente.

---

## 17. Configuração de Usuários

Criar tabela conceitual:

`reajustes_configuracoes_usuarios`

ou adaptar ao mecanismo de configurações existente.

Relacionar:

* configuração;
* usuário;
* receber_email;
* receber_notificacao.

---

## 18. Rotina de Verificação

Criar Service específico:

`ReajusteContratoService`

Métodos conceituais:

* `calcular_proximo_aniversario()`
* `calcular_idade_contrato()`
* `calcular_dias_para_reajuste()`
* `verificar_reajuste()`
* `identificar_alerta()`
* `processar_alertas()`
* `registrar_historico_valor()`

Repository não deve conter regra de aniversário ou cálculo de percentual.

---

## 19. Execução Automática

A arquitetura deverá permitir execução diária.

Pode ser acionada futuramente por:

* cron;
* scheduler;
* n8n;
* job interno.

A primeira versão poderá possuir também botão:

`Verificar Reajustes Agora`

para homologação e execução manual.

Não prender a regra de negócio ao mecanismo de agendamento.

---

## 20. Integração com a Sincronização OMIE

Após sincronizar contratos:

1. atualizar contrato;
2. verificar alteração de valores;
3. registrar histórico se necessário.

Separar:

`sincronização OMIE`

de:

`análise de reajuste`

O sync não deve enviar e-mails diretamente.

---

## 21. Modelagem Sugerida

### contratos_valores_historico

* id;
* uuid;
* contrato_id;
* valor_mensal;
* valor_servicos_bruto;
* valor_descontos;
* valor_servicos_liquido;
* detectado_em;
* created_at.

### contratos_reajustes_alertas

* id;
* uuid;
* contrato_id;
* aniversario_referencia;
* antecedencia_dias;
* status;
* exibido_em;
* email_enviado_em;
* created_at.

### reajustes_configuracoes

* id;
* alerta_30_dias;
* alerta_15_dias;
* alerta_7_dias;
* enviar_email;
* ativo;
* updated_at.

### reajustes_configuracoes_usuarios

* id;
* configuracao_id;
* usuario_id;
* receber_notificacao;
* receber_email.

Adaptar nomes e FKs à arquitetura real.

---

## 22. Tela de Detalhe do Contrato

Adicionar nova seção:

`Reajuste Contratual`

Exibir:

* início da vigência;
* idade;
* próximo aniversário;
* dias restantes;
* valor de referência;
* valor atual;
* último reajuste detectado;
* percentual;
* status.

Exemplo:

`Início: 15/09/2025`

`Próximo reajuste: 15/09/2026`

`Faltam: 32 dias`

`Valor atual: R$ 1.500,00`

`Status: Aguardando reajuste`

---

## 23. Histórico Visual

No detalhe:

`Histórico de Valores`

Exemplo:

`15/09/2025 – R$ 1.000,00`

`15/09/2026 – R$ 1.050,00 (+5%)`

`15/09/2027 – R$ 1.108,50 (+5,57%)`

Não recalcular o passado com valores atuais.

---

## 24. Tratamento de Casos Especiais

### Contrato sem início de vigência

Status:

`SEM_DATA_VIGENCIA`

Não gerar alerta.

### Contrato cancelado

Não gerar novos alertas.

### Contrato suspenso

Definir inicialmente como não elegível para novos alertas, salvo decisão posterior.

### Contrato com valor zero/null

Exibir:

`SEM_BASE_COMPARACAO`

### Contrato antigo recém-importado

Se existir primeiro faturamento sincronizado recorrente, usar esse faturamento como base inicial contra o valor atual.

Se nao existir faturamento inicial nem historico suficiente, manter `SEM_BASE_COMPARACAO` e nao afirmar que houve ou nao reajuste anterior sem evidencia.

---

## 25. Cuidado com Histórico Anterior ao Sistema

Se o O3Cloud Manager comecou a registrar historico proprio em 2026 e o contrato existe desde 2022, o sistema nao possui automaticamente todos os valores de 2022-2025.

Quando houver primeiro faturamento sincronizado, o sistema pode comparar esse valor com o valor atual e exibir `Sem reajuste detectado` se ambos forem iguais. Essa situacao deve ser investigada pelo Financeiro, pois indica ausencia de alteracao detectada na base disponivel, nao aprovacao automatica.

Quando nao houver primeiro faturamento sincronizado nem historico suficiente, exibir `Sem base de comparacao`.

Essa regra é obrigatória.

---

## 26. Permissões

Criar permissões equivalentes:

* `REAJUSTES_VISUALIZAR`
* `REAJUSTES_CONFIGURAR`
* `REAJUSTES_NOTIFICAR`

A tela e as rotas devem respeitar o sistema atual de perfis/permissões.

---

## 27. Filtros úteis

Na tela principal:

* próximos 7 dias;
* próximos 15 dias;
* próximos 30 dias;
* vencidos;
* reajustados;
* sem reajuste identificado;
* sem base de comparação.

Também:

* cliente;
* vendedor;
* contrato;
* projeto;
* período.

---

## 28. Cards

Cards simples:

* Reajustes nos próximos 30 dias;
* Reajustes nos próximos 15 dias;
* Reajustes nos próximos 7 dias;
* Reajustes vencidos;
* Reajustes detectados no mês.

---

## 29. Testes Obrigatórios

Testar:

1. contrato com 2 meses;
2. contrato com 11 meses;
3. exatamente 30 dias para aniversário;
4. exatamente 15;
5. exatamente 7;
6. exatamente na data do aniversário;
7. 1 dia vencido;
8. 12 meses;
9. 24 meses;
10. vários anos;
11. contrato sem data;
12. contrato cancelado;
13. contrato suspenso;
14. valor sem alteração;
15. valor aumentado;
16. valor reduzido;
17. valor NULL;
18. histórico vazio;
19. alertas repetidos;
20. novo aniversário;
21. múltiplos usuários;
22. e-mail desabilitado;
23. e-mail habilitado;
24. falha de e-mail;
25. execução manual repetida;
26. sync OMIE repetido;
27. alteração real do valor.

---

## 30. Critérios de Aceite

Sprint concluído quando:

* data inicial dos contratos estiver sendo utilizada;
* idade contratual estiver correta;
* próximo aniversário for calculado;
* contratos com mais de 12 meses forem identificados;
* histórico de valores existir;
* alterações de valor forem detectadas;
* percentual puder ser calculado;
* ausência de histórico for tratada corretamente;
* alertas de 7/15/30 dias forem configuráveis;
* usuários destinatários puderem ser selecionados;
* notificações aparecerem em tela;
* e-mails opcionais funcionarem;
* alertas não forem duplicados;
* contratos cancelados não gerarem alertas;
* detalhe do contrato mostrar situação de reajuste;
* permissões forem respeitadas;
* testes existentes continuarem passando;
* documentação e CHANGELOG forem atualizados.

---

## 31. Fora do Escopo

Não implementar neste Sprint:

* alteração automática do preço no OMIE;
* aplicação automática de índice;
* emissão automática de aditivo;
* reajuste automático sem aprovação humana;
* alteração automática do contrato;
* cobrança automática ao cliente.

O sistema deverá:

`detectar → alertar → permitir análise humana`

e não aplicar reajustes automaticamente.

---

## 32. Regra de Desenvolvimento para o Codex

Antes de programar:

1. revisar `contratos.inicio_vigencia`;
2. revisar campos atuais de valores;
3. revisar sincronização OMIE;
4. verificar sistema de usuários/permissões;
5. verificar serviço atual de e-mail;
6. revisar tabela de configurações;
7. propor migrations;
8. só então implementar.

Seguir:

Repository → Service → Routes → Templates → Testes.

Não alterar o significado de campos atuais e não realizar refatorações fora do Sprint.


#SPRINT 23 -

# Sprint – Agendamento de Upgrade de CPU e Memória no Proxmox

## 1. Objetivo

Criar no O3Cloud Manager um módulo para agendar alterações de CPU e memória de máquinas virtuais no Proxmox em uma data e horário definidos pelo usuário.

O fluxo deve permitir:

* selecionar Cluster;
* selecionar Node;
* selecionar VM;
* visualizar CPU e memória atuais;
* informar nova quantidade de CPU;
* informar nova quantidade de memória;
* definir data e hora da execução;
* desligar a VM de forma controlada quando necessário;
* aplicar as alterações;
* religar a VM quando ela estava ligada antes do agendamento;
* validar o resultado;
* manter histórico completo e auditável.

O módulo não deve executar alterações imediatamente durante a requisição HTTP da interface.

A execução deve ocorrer por worker/scheduler separado.

---

# 2. Localização no Sistema

Adicionar dentro do módulo:

`Infraestrutura`

novo menu:

```text
Infraestrutura
├── Clusters
├── Nodes
├── Máquinas Virtuais
├── Containers
└── Agendamentos
```

Tela principal:

`Infraestrutura → Agendamentos`

---

# 3. Escopo Inicial

A primeira versão será exclusivamente para:

* Máquinas Virtuais QEMU;
* alteração de vCPU;
* alteração de memória RAM;
* execução agendada;
* shutdown/start automático quando necessário.

Não implementar inicialmente:

* resize de disco;
* alteração de storage;
* mudança de rede;
* migração;
* snapshot;
* alteração de LXC;
* atualização de sistema operacional;
* execução genérica de comandos.

Esses itens poderão ser evoluções futuras.

---

# 4. Novo Agendamento

Adicionar botão:

`+ Novo Agendamento`

Fluxo:

1. selecionar Cluster;
2. selecionar Node;
3. selecionar VM;
4. carregar configuração atual;
5. exibir status atual;
6. informar CPU desejada;
7. informar memória desejada;
8. informar data;
9. informar hora;
10. informar motivo;
11. revisar;
12. confirmar agendamento.

---

# 5. Exemplo de Interface

```text
Novo Upgrade Proxmox

Cluster
C1-O3CLOUD-EVEO

Node
sp1-sd-o3cloud-07

VM
375 - CLIENTE-APP

Status atual
RUNNING

CPU atual
4 vCPU

Nova CPU
8 vCPU

Memória atual
8192 MB

Nova memória
16384 MB

Executar em
31/08/2026 23:30

[x] Desligar automaticamente se necessário
[x] Religar automaticamente após alteração

Motivo
Upgrade contratado pelo cliente

[Cancelar] [Agendar]
```

---

# 6. Regra de Estado Original

No momento da execução, registrar antes de qualquer alteração:

* status original;
* CPU original;
* memória original;
* Node atual;
* Cluster atual.

Exemplo:

```text
status_original = RUNNING
cpu_original = 4
memoria_original_mb = 8192
```

Essa informação é obrigatória para auditoria e recuperação.

---

# 7. Regra de Ligamento

A VM somente poderá ser ligada automaticamente ao final se:

`status_original == RUNNING`

Exemplo:

### VM estava ligada

Fluxo:

```text
RUNNING
↓
shutdown
↓
configuração
↓
start
```

### VM já estava desligada

Fluxo:

```text
STOPPED
↓
configuração
↓
permanece STOPPED
```

Nunca ligar automaticamente uma VM que já estava desligada antes da manutenção.

---

# 8. Hotplug

Antes de desligar a VM, verificar se a alteração solicitada pode ser aplicada por hotplug.

Se:

* hotplug estiver habilitado;
* configuração do Proxmox permitir;
* alteração solicitada for suportada;
* guest permitir;

o sistema poderá aplicar sem shutdown.

Caso contrário:

executar manutenção com desligamento.

Não assumir que toda alteração de CPU/RAM pode ser feita online.

---

# 9. Estratégia Recomendada

Para a primeira versão, priorizar segurança.

Sugestão:

`modo padrão = manutenção com shutdown`

Mesmo quando hotplug estiver disponível, deixar opção futura para habilitar atualização online.

Não tornar hotplug requisito para entrega do Sprint.

---

# 10. Shutdown Gracioso

Para VM em execução:

utilizar primeiro shutdown gracioso pela API do Proxmox.

Fluxo:

```text
request shutdown
↓
aguardar STOPPED
↓
aplicar configuração
```

Não utilizar `stop` imediatamente.

---

# 11. Timeout de Shutdown

Criar configuração:

```env
PROXMOX_VM_SHUTDOWN_TIMEOUT=300
```

Exemplo:

300 segundos.

Após esse período:

status do agendamento:

`ERRO`

Mensagem:

`VM não desligou dentro do tempo configurado.`

Na primeira versão, não executar `stop` forçado automaticamente.

Isso evita corrupção ou desligamentos inesperados.

---

# 12. Alteração de Configuração

Após VM estar em estado apropriado:

aplicar somente os campos realmente modificados.

Exemplo:

CPU:

`cores`

Memória:

`memory`

Não enviar configuração completa da VM desnecessariamente.

Não alterar:

* discos;
* redes;
* boot;
* BIOS;
* machine;
* storage;
* tags;
* description.

---

# 13. Validação Após Alteração

Após atualização:

consultar novamente a configuração da VM.

Validar:

```text
CPU configurada == CPU solicitada
RAM configurada == RAM solicitada
```

Se não corresponder:

marcar:

`ERRO`

Não assumir sucesso apenas porque a API retornou HTTP 200.

---

# 14. Start

Se a VM estava originalmente RUNNING:

executar start.

Aguardar status:

`RUNNING`

Criar timeout configurável:

```env
PROXMOX_VM_START_TIMEOUT=180
```

Se a VM não entrar em RUNNING:

marcar execução como erro operacional.

---

# 15. Validação Final

Ao concluir:

registrar:

```text
CPU anterior
CPU nova

RAM anterior
RAM nova

Status anterior
Status final

Node

Início
Fim

Resultado
```

Status esperado:

`CONCLUIDO`

---

# 16. Status do Agendamento

Criar estados:

```text
AGENDADO
VALIDANDO
DESLIGANDO
AGUARDANDO_DESLIGAMENTO
APLICANDO
VALIDANDO_CONFIGURACAO
LIGANDO
VALIDANDO_INICIALIZACAO
CONCLUIDO
ERRO
CANCELADO
```

Não utilizar apenas:

`PENDENTE / FINALIZADO`.

O estado detalhado facilita diagnóstico.

---

# 17. Cancelamento

Permitir cancelar somente quando:

`status = AGENDADO`

Depois que a execução entrar em:

`VALIDANDO`

não permitir cancelamento pela interface na primeira versão.

Isso evita estado inconsistente.

---

# 18. Concorrência

Não permitir dois agendamentos ativos simultaneamente para a mesma VM.

Considerar ativos:

```text
AGENDADO
VALIDANDO
DESLIGANDO
AGUARDANDO_DESLIGAMENTO
APLICANDO
VALIDANDO_CONFIGURACAO
LIGANDO
VALIDANDO_INICIALIZACAO
```

Caso exista outro:

mostrar:

`Já existe uma manutenção pendente ou em execução para esta VM.`

---

# 19. Validação Antes de Criar Agendamento

Antes de salvar:

validar:

* Cluster existe;
* Node existe;
* VM existe;
* API Proxmox está acessível;
* CPU nova é válida;
* RAM nova é válida;
* pelo menos CPU ou RAM mudou;
* data/hora está no futuro;
* usuário possui permissão;
* não existe manutenção conflitante.

---

# 20. Validação Imediatamente Antes da Execução

Mesmo que o agendamento tenha sido validado no momento da criação, validar novamente no horário da manutenção.

Verificar:

* Cluster disponível;
* Node online;
* VM ainda existe;
* VM ainda está no Node esperado;
* configuração atual;
* status atual;
* nenhum outro job conflitante.

Nunca confiar apenas na situação existente no momento em que o agendamento foi criado.

---

# 21. VM Migrada de Node

Se a VM tiver sido migrada para outro Node antes do horário:

NÃO executar automaticamente no Node antigo.

Na primeira versão:

marcar:

`ERRO`

Mensagem:

`VM não está mais localizada no Node originalmente agendado.`

Futuramente pode existir opção de localizar automaticamente a VM no Cluster.

---

# 22. Backup em Execução

Antes da manutenção:

consultar jobs/tasks do Proxmox e verificar se existe backup ativo para aquela VM.

Se houver:

não executar.

Marcar:

`ERRO` ou `ADIADO`, dependendo do design final.

Para primeira versão:

preferir `ERRO` com mensagem clara:

`Existe backup em execução para a VM.`

Não interromper backup automaticamente.

---

# 23. Migração em Execução

Também impedir execução caso exista:

* migration;
* snapshot ativo;
* lock de backup;
* lock de clone;
* outro lock impeditivo.

Não remover locks automaticamente.

---

# 24. Permissões

Criar permissões equivalentes:

```text
PROXMOX_AGENDAMENTOS_VISUALIZAR
PROXMOX_AGENDAMENTOS_CRIAR
PROXMOX_AGENDAMENTOS_CANCELAR
PROXMOX_AGENDAMENTOS_EXECUTAR
```

Somente usuários autorizados podem agendar alterações de recursos.

Não depender somente do nome textual do perfil.

---

# 25. Auditoria

Registrar obrigatoriamente:

* usuário que criou;
* usuário que cancelou;
* data de criação;
* data agendada;
* início real;
* fim real;
* CPU anterior;
* CPU solicitada;
* CPU final;
* RAM anterior;
* RAM solicitada;
* RAM final;
* status;
* motivo;
* mensagem de erro;
* Cluster;
* Node;
* VMID;
* nome da VM.

---

# 26. Modelagem Sugerida

Criar tabela:

`proxmox_agendamentos`

Campos conceituais:

```text
id
uuid

cluster_identificador
node_nome

vmid
vm_nome

tipo_recurso

cpu_original
cpu_nova

memoria_original_mb
memoria_nova_mb

status_original
status_final

executar_em

status

desligar_se_necessario
religar_automaticamente

motivo

created_by
cancelled_by

created_at
updated_at

iniciado_em
finalizado_em
cancelado_em

mensagem_erro
```

Adaptar tipos ao padrão atual do projeto.

---

# 27. Histórico de Etapas

Recomendado criar também:

`proxmox_agendamentos_eventos`

Campos:

```text
id
agendamento_id
status
mensagem
created_at
```

Exemplo:

```text
23:30:01 VALIDANDO VM encontrada.
23:30:03 DESLIGANDO Shutdown solicitado.
23:30:22 AGUARDANDO_DESLIGAMENTO VM ainda running.
23:30:41 APLICANDO CPU 4 → 8.
23:30:42 APLICANDO RAM 8192 → 16384.
23:30:45 LIGANDO Start solicitado.
23:31:12 CONCLUIDO VM running.
```

Isso será extremamente útil para suporte e auditoria.

---

# 28. Não Armazenar Credenciais

As credenciais/API Token do Proxmox devem utilizar o mecanismo atual de integração.

Nunca armazenar token dentro do registro do agendamento.

Não gravar:

* password;
* secret;
* token secreto;
* ticket;
* cookie de sessão.

---

# 29. Arquitetura Python

Seguir padrão do projeto.

Sugestão:

```text
app/infraestrutura/agendamentos/
├── __init__.py
├── repository.py
├── service.py
├── executor.py
└── routes.py
```

Integração:

```text
app/integracoes/proxmox/
├── client.py
├── service.py
└── ...
```

Templates:

```text
app/templates/infraestrutura/agendamentos/
├── index.html
├── form.html
└── view.html
```

---

# 30. Responsabilidades

## Repository

Somente persistência:

```text
listar
buscar_por_id
criar
atualizar_status
registrar_inicio
registrar_fim
cancelar
buscar_pendentes
registrar_evento
```

Não chamar API Proxmox.

---

# 31. Service

`ProxmoxAgendamentoService`

Responsável por:

```text
validar_criacao
criar_agendamento
cancelar_agendamento
validar_execucao
```

---

# 32. Executor

Criar:

`ProxmoxAgendamentoExecutor`

Responsável exclusivamente por executar a manutenção.

Fluxo:

```text
carregar agendamento
↓
lock
↓
validar
↓
capturar estado original
↓
shutdown
↓
aguardar
↓
alterar CPU/RAM
↓
validar
↓
start se necessário
↓
validar
↓
concluir
```

---

# 33. Scheduler / Worker

Não executar agendamentos dentro de request Flask.

Criar processo separado.

Opções aceitáveis:

* script Python executado por systemd timer;
* worker;
* scheduler existente no projeto.

Primeira versão recomendada:

script independente executado periodicamente.

Exemplo:

```bash
python -m scripts.processar_agendamentos_proxmox
```

---

# 34. Frequência

Executar o worker a cada minuto.

O worker deve localizar:

```text
status = AGENDADO
AND executar_em <= NOW()
```

Processar de forma controlada.

Não utilizar `sleep()` dentro do servidor Flask.

---

# 35. Lock de Execução

Evitar que dois workers executem o mesmo agendamento.

Implementar claim atômico.

Exemplo conceitual:

```text
AGENDADO
↓
UPDATE atômico
↓
VALIDANDO
```

Somente o processo que conseguir alterar o estado poderá continuar.

Não usar apenas:

`SELECT → executar`.

---

# 36. Timezone

As datas devem respeitar o timezone configurado no sistema.

Preferencialmente:

`America/Sao_Paulo`

Não misturar horário local e UTC sem conversão explícita.

Na interface mostrar:

`DD/MM/YYYY HH:mm`

---

# 37. Tela de Listagem

Exemplo:

```text
AGENDAMENTOS PROXMOX

[ + Novo Agendamento ]

VM          Alteração              Data/Hora        Status
----------------------------------------------------------------
APP01       CPU 4→8 RAM 8→16GB     31/08 23:30      AGENDADO
SQL01       RAM 16→32GB             01/09 01:00      CONCLUIDO
WEB01       CPU 2→4                 02/09 22:00      ERRO
```

Filtros:

* status;
* Cluster;
* Node;
* VMID/nome;
* período;
* usuário.

---

# 38. Tela de Detalhe

Exibir:

```text
VM
Cluster
Node

Status da VM antes
Status final

CPU anterior
CPU nova

RAM anterior
RAM nova

Agendado para

Executado em

Criado por

Motivo

Status
```

E timeline:

```text
23:30 Validando
23:31 Desligando
23:32 Aplicando configuração
23:33 Ligando
23:34 Concluído
```

---

# 39. Atualização da Interface após Execução

Após conclusão:

badge verde:

`CONCLUÍDO`

Em erro:

badge vermelho:

`ERRO`

Mostrar mensagem de erro de forma segura.

Não expor dados sensíveis retornados pela API.

---

# 40. Notificações

Preparar arquitetura para enviar notificações futuramente.

Opcional na primeira versão:

notificação interna ao usuário quando:

* concluído;
* erro.

Se existir serviço de e-mail já consolidado no projeto, poderá ser reutilizado.

Não tornar e-mail requisito para a execução funcionar.

---

# 41. Falha Durante Alteração

Exemplo:

VM desligou.

CPU foi alterada.

RAM falhou.

O sistema deve:

* registrar exatamente o que ocorreu;
* consultar configuração final;
* não fingir rollback se a API não o realizou;
* registrar status ERRO;
* tentar religar a VM se ela estava originalmente RUNNING, desde que seja seguro;
* informar configuração final real.

---

# 42. Rollback

Não implementar rollback automático complexo na primeira versão.

Motivo:

a tentativa automática de reverter configuração após falha pode gerar estado ainda mais inconsistente.

Porém sempre registrar valores originais.

Isso permite:

* análise;
* recuperação manual;
* futura implementação de rollback seguro.

---

# 43. Prioridade de Disponibilidade

Mesmo se a alteração de configuração falhar após a VM ter sido desligada:

se:

```text
status_original = RUNNING
```

o executor deverá avaliar tentativa segura de start com a configuração existente.

A prioridade operacional é evitar deixar VM desligada desnecessariamente.

Registrar essa tentativa no histórico.

---

# 44. Idempotência

O mesmo agendamento não pode executar duas vezes.

Após:

```text
CONCLUIDO
ERRO
CANCELADO
```

não selecionar novamente pelo worker.

Criar validações tanto no banco quanto no Service.

---

# 45. Validação de CPU

Antes de aceitar:

* inteiro;
* maior que zero;
* dentro dos limites do Proxmox/VM;
* diferente da configuração atual quando for única alteração.

Não aceitar valores negativos ou zero.

---

# 46. Validação de Memória

Aceitar memória internamente em MB.

Interface pode exibir GB.

Exemplo:

```text
16 GB
```

persistir:

```text
16384 MB
```

Validar:

* inteiro positivo;
* limite suportado;
* conversão correta.

---

# 47. Redução de Recursos

Por segurança, a primeira versão deverá decidir explicitamente se permitirá redução.

Recomendação inicial:

permitir apenas:

```text
nova_cpu >= cpu_atual
nova_memoria >= memoria_atual
```

Ou seja:

**somente upgrades.**

Bloquear downgrade.

Mensagem:

`Esta versão do módulo permite somente aumento de CPU e memória.`

---

# 48. Pré-validação Opcional

Criar botão:

`Validar Agendamento`

antes de confirmar.

Mostrar:

```text
✓ Cluster acessível
✓ Node online
✓ VM encontrada
✓ VM sem lock
✓ CPU válida
✓ Memória válida
✓ Nenhum conflito
```

Se falhar:

não salvar.

---

# 49. Revalidação é Obrigatória

Mesmo que a pré-validação passe:

revalidar no horário de execução.

A infraestrutura pode mudar entre criação e execução.

---

# 50. API Proxmox

Utilizar API oficial existente.

Não usar SSH para executar:

```text
qm set
qm shutdown
qm start
```

se a integração API já estiver disponível.

Preferir:

```text
Proxmox REST API
```

A integração deve possuir métodos explícitos, por exemplo:

```python
get_vm_status()
get_vm_config()
shutdown_vm()
start_vm()
update_vm_config()
get_task_status()
```

---

# 51. Tasks/UPID

Quando a API retornar UPID/task:

acompanhar até:

```text
status = stopped
exitstatus = OK
```

Não assumir conclusão porque a chamada retornou um UPID.

---

# 52. Testes Obrigatórios

Testar pelo menos:

1. VM RUNNING + CPU;
2. VM RUNNING + RAM;
3. VM RUNNING + CPU/RAM;
4. VM STOPPED + CPU;
5. VM STOPPED + RAM;
6. VM STOPPED permanece desligada;
7. VM inexistente;
8. Node offline;
9. Cluster indisponível;
10. shutdown normal;
11. shutdown timeout;
12. alteração rejeitada;
13. start com sucesso;
14. start com erro;
15. VM migrada antes do horário;
16. backup em execução;
17. VM locked;
18. agendamento duplicado;
19. duplo worker;
20. cancelamento;
21. tentativa de cancelar execução em andamento;
22. CPU inválida;
23. RAM inválida;
24. downgrade de CPU;
25. downgrade de RAM;
26. data no passado;
27. timezone;
28. API timeout;
29. HTTP 401/403;
30. HTTP 5xx;
31. worker reiniciado;
32. aplicação Flask reiniciada;
33. histórico preservado.

---

# 53. Teste Inicial Seguro

Homologar primeiro em VM não crítica.

Exemplo:

```text
VM teste
2 CPU
4 GB RAM
```

Agendar:

```text
2 → 4 CPU
4 → 8 GB RAM
```

Confirmar:

* shutdown;
* configuração;
* start;
* estado final;
* log.

Somente depois testar em ambiente produtivo.

---

# 54. Critérios de Aceite

Sprint concluído quando:

* tela Agendamentos existir;
* Cluster puder ser selecionado;
* Node puder ser selecionado;
* VM puder ser selecionada;
* CPU/RAM atuais forem exibidas;
* novo valor puder ser informado;
* data/hora puder ser agendada;
* agendamento persistir após restart;
* worker identificar tarefa vencida;
* execução não depender da sessão web;
* VM puder ser desligada de forma graciosa;
* CPU/RAM forem alteradas;
* configuração final for validada;
* VM originalmente ligada for religada;
* VM originalmente desligada permanecer desligada;
* duplicidade de execução for impedida;
* concorrência for protegida;
* logs detalhados existirem;
* erros forem auditáveis;
* permissões forem respeitadas;
* cancelamento funcionar;
* nenhum segredo for persistido;
* testes existentes continuarem passando;
* documentação, DER, modelo físico e CHANGELOG forem atualizados.

---

# 55. Fora do Escopo

Não implementar nesta Sprint:

* execução genérica de shell;
* SSH arbitrário;
* resize de disco;
* mudança de storage;
* migração automática;
* backup automático;
* snapshot automático;
* upgrade de SO;
* kernel update;
* alteração de network;
* LXC;
* rollback completo;
* HA orchestration;
* manutenção simultânea em lote;
* automação de Windows/Linux dentro da VM.

---

# 56. Evoluções Futuras

Preparar arquitetura para futuramente suportar:

* upgrade de disco;
* alteração de network;
* resize de filesystem;
* snapshot antes da manutenção;
* backup obrigatório antes da alteração;
* LXC;
* manutenção em lote;
* aprovação em duas etapas;
* janela de manutenção;
* notificações por e-mail;
* integração com chamados;
* vínculo com contrato/upgrade vendido;
* rollback automatizado;
* execução condicionada ao PBS;
* agendamento de reboot;
* desligamento programado;
* alteração de recursos sem shutdown quando hotplug seguro.

---

# 57. Regra de Desenvolvimento para o Codex

Antes de alterar qualquer arquivo:

1. ler a documentação atual;
2. revisar módulo Infraestrutura;
3. revisar integração Proxmox atual;
4. verificar como Clusters e Nodes são modelados;
5. verificar sistema de permissões;
6. verificar padrão de migrations;
7. verificar BaseRepository;
8. identificar serviço/API existente;
9. apresentar proposta de tabelas;
10. implementar por etapas.

Seguir:

**Repository → Service → Executor → Routes → Templates → Worker → Testes**

Não alterar funcionalidades existentes fora deste Sprint.

Não executar comandos reais em VMs de produção durante desenvolvimento.

Utilizar VM de homologação até conclusão dos testes.


___________________________________________________________________________________________

# Sprint Final Planejada

## Integracao Receita Federal para Cadastro de Clientes

Status:

Planejada para a sprint final

Objetivo:

Permitir que o cadastro manual de novos clientes consulte uma API de dados da Receita Federal, ou provedor homologado, a partir do CNPJ informado, preenchendo automaticamente os dados cadastrais disponiveis.

Escopo previsto:

- Consultar dados cadastrais pelo CNPJ durante o cadastro de cliente.
- Preencher campos compativeis do cliente, mantendo revisao manual antes do salvamento.
- Tratar indisponibilidade da API como aviso operacional, sem bloquear cadastro manual.
- Definir provedor, limites, cache, autenticacao e auditoria tecnica apenas na sprint final.

Observacao:

Esta integracao fica fora da Sprint 15 e das sprints intermediarias de infraestrutura, permanecendo como backlog final para fechamento da versao.

---

# Diretriz

Toda evolução do projeto deve permanecer alinhada ao ROADMAP.md, que é a fonte oficial para sequência das próximas etapas.

---

# 46. Fechamento Tecnico - 10/08/2026

Status: Concluida tecnicamente.

Documento de fechamento: `docs/37-FECHAMENTO-SPRINT-20.md`.

Resumo:

* modulo Relatorios implementado com catalogo de fontes autorizadas;
* builder sem SQL livre;
* modelos salvos com visibilidade PRIVADO, PERFIL e GLOBAL;
* exportacoes CSV, XLSX, DOCX, PDF e impressao HTML;
* fila de jobs para geracao de relatorios;
* retencao de cache e sincronismos agendados em Configuracoes;
* DER, modelo fisico, visao geral e CHANGELOG atualizados.

A homologacao operacional permanece pendente de validacao assistida com usuarios, perfis e dados reais controlados.

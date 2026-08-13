# Modelo Físico de Dados

## O3Cloud Manager V2

**Versão:** 2.0

---

# Objetivo

Este documento define a estrutura física do banco de dados do O3Cloud Manager V2.

Seu objetivo é transformar o Modelo de Domínio e o DER em uma estrutura pronta para implementação no MariaDB.

O banco de dados deverá representar o negócio da O3Cloud e não a estrutura dos sistemas integrados.

---

# Princípios

* Toda informação possui um sistema responsável.
* Nenhuma tela consulta APIs externas.
* Todo dado utilizado pela aplicação deve existir no banco local.
* Toda regra de negócio pertence à camada Services.
* O banco representa o domínio do negócio.
* O sistema será preparado para crescimento futuro.

---

# Convenções

## Banco

MariaDB 11

---

## Charset

utf8mb4

---

## Collation

utf8mb4_unicode_ci

---

## Engine

InnoDB

---

## Nome das tabelas

Sempre em português.

Sempre no plural.

Sempre snake_case.

Exemplos

clientes

grupos_economicos

contratos

recursos

licencas

---

## Chave Primária

Todas as tabelas utilizarão:

* id BIGINT AUTO_INCREMENT

---

## UUID

Todas as entidades principais possuirão:

* uuid CHAR(36)

Objetivo:

Preparar a plataforma para APIs, integrações e futuras aplicações móveis.

---

## Auditoria

Sempre que aplicável:

* created_at
* updated_at
* created_by
* updated_by
* ativo

---

## Soft Delete

Nenhum cadastro será removido fisicamente.

Utilizar:

ativo = 0

---

# Domínio Financeiro

## clientes

Descrição

Empresas atendidas pela O3Cloud.

Origem

* OMIE
* Manual

grupos

Representa os grupos econômicos.

produtos

Produtos comercializados pela O3Cloud.

Atualmente:

VPS
O3CloudShare
Outros

contratos

Representa o contrato comercial.

Possui valores recorrentes, setup/projeto e campos comerciais sincronizados do OMIE quando aplicavel.

faturamentos

Representa o faturamento mensal do contrato.

Possui histórico por competência.

licencas_cliente

Controle das licenças dos produtos.


parametros_financeiros

Centraliza todos os custos utilizados para cálculo da rentabilidade.

configuracoes

Configurações gerais do sistema.

sync_execucoes

Histórico das integrações.

schema_migrations

Controle de versões do banco.

relatorios_modelos

Modelos de relatórios customizáveis salvos por usuários autorizados.

relatorios_execucoes

Histórico de execução dos relatórios.

relatorios_jobs

Fila de geração assíncrona de relatórios exportados.

config_cache_retencao

Políticas administrativas de retenção dos caches locais.

config_cache_limpezas

Histórico de limpezas de cache executadas.

config_sincronismos_agendados

Configuração de automações de sincronismo.

config_sincronismos_execucoes

Histórico de execuções dos sincronismos agendados.


Tipo

Cadastro

Campos principais

* id
* uuid
* codigo_externo
* origem
* nome_fantasia
* razao_social
* cnpj
* email
* telefone
* cidade
* estado
* ativo
* created_at
* updated_at
* created_by
* updated_by

Relacionamentos

* Grupo Econômico
* Contratos
* Receitas
* Licenças
* Recursos

---

## grupos_economicos

Descrição

Agrupamento empresarial utilizado para consolidação financeira.

Origem

O3Cloud

---

## grupo_clientes

Relacionamento N:N entre clientes e grupos econômicos.

---

## contratos

Descrição

Contratos sincronizados do ERP.

Origem

OMIE

Campos

* codigo_externo
* origem
* cliente_id
* numero
* descricao
* valor_mensal
* codigo_vendedor
* vendedor_nome
* codigo_projeto
* projeto_nome
* observacoes
* observacao_contrato
* valor_servicos_bruto
* valor_descontos
* valor_servicos_liquido
* status

---

## contrato_detalhes

Informações gerenciais mantidas exclusivamente pela O3Cloud.

Exemplos

* observações
* percentual_comissao
* observacoes_comerciais

---

## receitas

Descrição

Receitas utilizadas pelos indicadores financeiros.

Origem

* OMIE
* MANUAL

Relacionamento

Cliente

Contrato (opcional)

---

## financeiro_recebimentos

Descrição

Títulos recebidos do OMIE utilizados como base de validação financeira para comissões.

Origem

OMIE Contas a Receber

Campos principais

* codigo_externo
* cliente_id
* contrato_id
* numero_documento
* numero_documento_fiscal
* numero_parcela
* numero_contrato
* categoria_codigo
* categoria_nome
* categoria_excluida
* motivo_exclusao
* valor_original
* valor_recebido
* valor_desconto
* valor_juros
* data_vencimento
* data_recebimento
* data_emissao
* situacao
* codigo_cliente_omie
* codigo_contrato_omie
* codigo_vendedor
* codigo_projeto
* origem
* synced_at

Regras

* `codigo_externo` é único e usa `codigo_lancamento_omie`.
* vínculo com contrato usa `codigo_cliente_omie` + `numero_contrato`.
* categorias contendo SETUP ou IMPLANTACAO/IMPLANTAÇÃO são marcadas como excluídas da comissão.

---

## licencas

Descrição

Controle de licenciamento administrado pela O3Cloud.

Inicialmente

* O3WEB

Preparado para expansão futura.

---

## parametros_financeiros

Tabela de configuração dos cálculos financeiros.

Campos previstos

* custo_cpu
* custo_ram
* custo_disco
* custo_licenca
* margem_minima

---

# Domínio Infraestrutura

## datacenters

Origem

Cadastro manual.

---

## clusters

Origem

Proxmox.

---

## hosts

Origem

Proxmox.

---

## storages

Origem

Proxmox.

---

## recursos

Representa qualquer recurso computacional pertencente a um cliente.

Pode representar:

* VM
* LXC

Origem

* Proxmox
* NetBox

Relacionamentos

Cliente

Host

Cluster

Storage

---

## backups

Origem

PBS.

---

# Administração

## usuarios

Usuários do sistema.

---

## perfis

Perfis de acesso.

---

## permissoes

Permissões individuais.

---

## perfil_permissoes

Relacionamento entre perfis e permissões.

---

## auditoria

Registro de alterações do sistema.

---

---

## financeiro_inadimplencias

Controle histórico de pendências financeiras por contrato.

Campos principais:

* id
* uuid
* contrato_id
* status: PENDENTE ou LIBERADO
* motivo
* observacoes
* bloqueado_em
* bloqueado_por / bloqueado_por_email
* tipo_liberacao: QUITACAO ou ACORDO
* observacao_liberacao
* liberado_em
* liberado_por / liberado_por_email
* indicadores e erros de envio de e-mail para suporte e cliente, incluindo bloqueio e liberação
* ativo
* created_at
* updated_at

Relacionamentos:

* contrato_id -> contratos.id
* cliente derivado por contratos.cliente_id

Regras:

* Um contrato não pode possuir duas inadimplências PENDENTE ativas.
* Cliente é considerado inadimplente quando qualquer contrato ativo possui inadimplência PENDENTE e ativo=1.
* Liberação preserva histórico e não remove registros.
* Exclusão operacional permitida somente para perfil ADMIN deve ser lógica, usando ativo=0.
* Registros inativos não devem bloquear propostas/implantações e não aparecem nas consultas operacionais padrão.

# Integrações

## sync_execucoes

Histórico das sincronizações.

---

## sync_logs

Logs detalhados.

---

# Sistemas Responsáveis

| Informação        | Sistema Oficial |
| ----------------- | --------------- |
| Clientes          | OMIE / O3Cloud  |
| Contratos         | OMIE            |
| Recursos          | Proxmox         |
| Inventário        | NetBox          |
| Backups           | PBS             |
| Monitoramento     | Zabbix          |
| Licenças          | O3Cloud         |
| Grupos Econômicos | O3Cloud         |
| Indicadores       | O3Cloud         |
| Relatórios        | O3Cloud         |
| Cache Local       | O3Cloud         |
| Sincronismos      | O3Cloud         |

---

# Ordem das Migrations

## 001

Financeiro

---

## 002

Administração

---

## 003

Infraestrutura

---

## 004

Integrações

---

## 077

Relatórios Customizáveis

Tabelas:

* relatorios_modelos
* relatorios_execucoes

---

## 078

Jobs de Relatórios

Tabela:

* relatorios_jobs

---

## 079

Retenção de Cache

Tabelas:

* config_cache_retencao
* config_cache_limpezas

---

## 080

Sincronismos Agendados

Tabelas:

* config_sincronismos_agendados
* config_sincronismos_execucoes

---

# Objetivo Final

O banco de dados deverá servir como base única para:

* Dashboards Executivos
* Indicadores Financeiros
* Indicadores Operacionais
* Relatórios
* Exportações
* APIs
* Futuras funcionalidades da V3



---

# Atualizacao 13/08/2026 - ASO, Premiacoes e Receitas por Servidor

## administrativo_aso_agendamentos

Tabela de agendamentos ASO vinculados ao colaborador administrativo.

Campos funcionais relevantes:

* colaborador_id
* gestor_usuario_id
* agenda_usuario_id
* data_agendamento
* observacoes
* ativo

## administrativo_aso_lembretes

Tabela de lembretes de ASO.

Campo adicionado:

* enviar_email TINYINT(1): indica se o lembrete deve disparar e-mail.

Regras:

* antecedencia permitida: 7, 15 ou 30 dias.
* lembrete e vinculado ao agendamento ASO.

## parceiros

Campo adicionado:

* premiacao_ativa TINYINT(1) NOT NULL DEFAULT 0

Regra:

* parceiro com `premiacao_ativa = 1` pode participar do calculo de premiacoes de campanha.

## parceiros_executivos

Campo funcional:

* premiacao_ativa TINYINT(1) NOT NULL DEFAULT 0

Regras:

* alteracao rapida de premiacao atualiza somente `premiacao_ativa`.
* exclusao operacional de executivo deve manter historico: `ativo = 0` e `parceiro_id = NULL`.

## Receita por Servidor

A tela `Financeiro > Receitas por Servidor` nao cria nova tabela. Ela calcula leitura operacional a partir das tabelas existentes:

* proxmox_node_inventory
* proxmox_vm_inventory
* ambiente_proxmox_recursos
* ambientes
* ambiente_contratos
* contratos
* clientes

Regra de calculo:

* considerar somente node Proxmox ativo e integracao Proxmox ativa;
* considerar somente recurso Proxmox ativo;
* considerar somente ambiente ativo;
* considerar somente contrato ativo com status `ATIVO`;
* receita mensal = `valor_promocional` quando maior que zero, senao `valor_mensal`;
* o mesmo contrato deve ser contado apenas uma vez por node, ainda que possua multiplos recursos Proxmox vinculados.

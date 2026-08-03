# Requisitos Funcionais

## Objetivo

Este documento descreve todas as funcionalidades previstas para o O3Cloud Manager V2.

---

# RF001 - Dashboard Executivo

O sistema deverá apresentar indicadores consolidados da operação da O3Cloud.

Indicadores previstos:

* Receita Total
* Custo Total
* Margem Operacional
* Lucro Gerencial
* Clientes Ativos
* Hosts
* Clusters
* Recursos
* Licenças O3Web

---

# RF002 - Gestão de Clientes

O sistema deverá permitir:

* Sincronizar clientes do OMIE
* Cadastrar clientes manuais
* Editar clientes manuais
* Desativar clientes
* Associar grupos econômicos

---

# RF003 - Grupos Econômicos

Permitir:

* Criar grupos
* Editar grupos
* Remover grupos
* Vincular clientes
* Desvincular clientes

---

# RF004 - Contratos

Sincronizar contratos do OMIE.

Complementar informações operacionais.

Permitir:

* Observações
* Comissão (%)
* Rateios

---

# RF005 - Infraestrutura

Sincronizar:

* Datacenters
* Clusters
* Hosts
* Recursos

---

# RF006 - Rentabilidade

Calcular indicadores por:

* Cliente
* Grupo Econômico
* Host
* Cluster
* Datacenter

---

# RF007 - Relatórios

Exportação:

* CSV
* XLSX

Filtros:

* Cliente
* Grupo
* Cluster
* Host
* Competência

---

# RF008 - Administração

Gerenciar:

* Usuários
* Perfis
* Permissões
* Auditoria

---

# RF009 - Licenciamento O3Web

Cadastrar:

* Número da licença
* Quantidade
* Cliente
* Contrato
* Observações

---

# RF010 - Timeline

Registrar eventos relevantes do cliente para consulta histórica.

---

# RF011 - Consulta de CNPJ na Receita Federal

Planejado para a sprint final.

O sistema devera permitir, no cadastro manual de cliente, consultar dados cadastrais a partir do CNPJ informado usando API da Receita Federal ou provedor homologado.

Regras previstas:

* Preencher automaticamente dados publicos compativeis com o cadastro interno.
* Permitir conferencia e edicao manual antes de salvar.
* Nao bloquear o cadastro quando a API estiver indisponivel.
* Definir provedor, autenticacao, limites de consulta e cache apenas na sprint final.

---

# RF012 - Propostas, ClickSign e Representante Legal

O sistema devera permitir que a proposta comercial informe explicitamente o Representante Legal responsavel pela assinatura eletronica.

Regras funcionais:

* Selecionar contato ativo do tipo Representante Legal na proposta.
* Oferecer atalho para cadastrar Representante Legal quando ele nao existir.
* Exigir nome completo e CPF do Representante Legal antes do envio para ClickSign.
* Bloquear reenvio para ClickSign quando ja existir envelope vinculado a proposta.
* Cancelar envelope pendente na ClickSign quando proposta for cancelada/rejeitada/expirada.
* Exibir acao de gerar documento para propostas aprovadas.
* Exibir acao de enviar somente quando o documento ja tiver sido gerado.
* Bloquear nova geracao de documento quando o fluxo ClickSign ja estiver assinado ou concluido.


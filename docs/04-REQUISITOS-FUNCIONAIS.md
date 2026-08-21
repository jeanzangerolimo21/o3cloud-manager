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

O sistema devera permitir cadastrar e acompanhar licencas O3Web por cliente.

Campos operacionais:

* Cliente e CNPJ
* Chave de ativacao
* ID da licenca
* Tipo da licenca (`Trial` ou `Permanente`)
* Usuarios
* Dias de validade
* Edicao
* Backup habilitado
* Data de ativacao
* Data de expiracao
* URLs principal e secundaria
* Comments e observacao

Regras funcionais:

* Ao selecionar `Trial`, informar `Data ativacao` e `Dias`, calcular automaticamente `Data expiracao` como data de ativacao + quantidade de dias.
* Manter a data de expiracao editavel para permitir ajuste manual quando necessario.
* Respeitar `-` em `Data expiracao` como marcador de licenca permanente, sem substituir por calculo automatico.
* Recalcular a expiracao na interface quando tipo, dias ou data de ativacao forem alterados, desde que o usuario nao tenha sobrescrito manualmente o campo.
* Reaplicar o calculo no backend ao salvar quando a expiracao vier vazia, garantindo consistencia mesmo sem JavaScript no navegador.

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
* Agrupar recursos de servidor em blocos separados por servidor dentro da proposta.
* Permitir criar novo bloco com `Novo servidor`, deixando-o selecionado para receber os proximos recursos.
* Permitir selecionar explicitamente o servidor de destino antes de adicionar um recurso.
* Usar a acao `Adicionar ao Servidor` somente para incluir o recurso selecionado no servidor selecionado.
* Usar `Servidor basico` para incluir o conjunto padrao de recursos em bloco separado quando ja houver servidor cadastrado.

---

# RF013 - Autenticacao, Usuarios e Acessos

O sistema devera disponibilizar em Configuracoes uma tela de Usuarios e Acessos para administrar usuarios locais, convites por e-mail, perfis, permissoes e provedores externos de autenticacao.

Regras funcionais:

* Permitir cadastro manual de usuario local com envio de convite por e-mail.
* Permitir que o usuario convidado cadastre a propria senha por link seguro e temporario.
* Permitir sincronizar usuarios pelo FreeIPA quando houver integracao ativa configurada.
* Permitir configurar servidor LDAP generico e testar comunicacao antes de ativar.
* Permitir configurar Active Directory e validar autenticacao de usuario.
* Permitir mapear grupos externos para perfis internos.
* Permitir bloquear, inativar, reativar e alterar perfil de usuario.
* Auditar acoes administrativas sensiveis.
* Manter senhas, tokens e segredos mascarados na interface e fora dos logs.

Documento de detalhamento:

* `docs/28-AUTENTICACAO-USUARIOS-SPRINT-16.md`
---

# RF014 - Sucesso do Cliente

O sistema devera disponibilizar uma tela de Sucesso do Cliente dentro do CRM Comercial para acompanhamento dos contratos ativos.

Informacoes exibidas por contrato:

* Razao Social
* Nome Fantasia
* CNPJ
* Usuarios
* Vendedor OMIE
* Projeto OMIE
* Valor Bruto
* Observacoes do Contrato OMIE
* Contato vinculado do CRM Comercial

Regras funcionais:

* Classificar automaticamente contratos de valor bruto maior ou igual a R$ 2.999,99 como Curva A.
* Classificar contratos de R$ 1.000,00 ate abaixo de R$ 2.999,99 como Curva B.
* Classificar contratos abaixo de R$ 1.000,00 como Curva C.
* Permitir vincular um contato existente do CRM Comercial ao contrato acompanhado.
* Exibir atalho para cadastro de contato quando nao houver contato cadastrado.
* Permitir registrar historico de relacionamento com status `Otimo`, `Bom`, `Regular` e `Critico`.
* Destacar contratos com status `Critico` em vermelho na listagem/dashboard para acionamento rapido.
* Permitir anexar arquivos a cada comentario de relacionamento.
* Registrar data, hora e usuario autor de cada comentario.
* Registrar auditoria operacional para comentarios e vinculos de contato.

---

# RF015 - Agrupamento de Cards de Implantacao

O sistema devera permitir agrupar cards de implantacao quando multiplos contratos/unidades de negocio utilizarem o mesmo ambiente operacional.

Regras funcionais:

* Permitir vincular um card secundario a um card principal.
* Impedir que um card seja vinculado a ele mesmo.
* Impedir que um card ja vinculado seja usado como principal de outro vinculo.
* Manter o card vinculado ativo para rastreabilidade do contrato original.
* Ocultar cards vinculados da lista principal de implantacao por padrao.
* Ocultar cards vinculados do Kanban operacional por padrao.
* Disponibilizar filtro para visualizar `Cards principais`, `Cards vinculados` ou `Todos`.
* Exibir no detalhe do card principal todos os cards vinculados a ele.
* Registrar historico e auditoria para cada vinculo e desvinculo.

Documento de detalhamento:

* `docs/48-MELHORIAS-BETA-2026-08-21.md`

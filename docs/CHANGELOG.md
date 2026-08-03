# Changelog

## v2.0.0-alpha

Data:
Junho/2026

### Arquitetura

- Novo modelo por domínios
- Separação Repository / Service
- Estrutura modular

### Banco

- Novo domínio Financeiro
- Produtos
- Contratos
- Faturamentos
- Licenciamento
- Configurações
- Controle de Migrations

### Infraestrutura

- Ubuntu Server 24.04
- MariaDB
- GitHub
- Branch Develop

### Próxima versão

- Dashboard
- Flask
- Bootstrap 5
- Integração OMIE
- Integração Proxmox

# O3Cloud Manager v3.0

# CHANGELOG

Todas as mudanças importantes deste projeto serão registradas neste documento.

O formato é baseado no Keep a Changelog e adaptado às necessidades do O3Cloud Manager.

---

## 2026-08-03 - Melhorias Pre-Sprint 16

### Comercial e ClickSign

- Criado `docs/26-MELHORIAS-PRE-SPRINT-16.md` para registrar refinamentos aplicados apos o fechamento tecnico da Sprint 15 e antes da abertura da Sprint 16.
- Propostas passaram a armazenar `representante_legal_id` e selecionar explicitamente contato do tipo Representante Legal.
- Envio para ClickSign passou a exigir nome completo e CPF valido do representante legal antes de chamar a API.
- Bloqueado reenvio duplicado quando a proposta ja possui envelope ClickSign.
- Cancelamento de proposta rejeitada/expirada/cancelada passa a cancelar envelope pendente na ClickSign quando aplicavel.
- Listagem de propostas aprovadas passou a mostrar Gerar documento e Enviar apenas apos documento gerado e sem envelope existente.
- Geracao de documento foi bloqueada para fluxos ClickSign assinados ou concluidos.

### Operacional

- Registrados refinamentos de PDF de proposta, pipeline comercial, rastreabilidade, contratos e cofre de senhas.
- Menu Configuracoes voltou a exibir Integracoes Tecnicas, mantendo removidos apenas os atalhos das telas operacionais.
- Sidebar recebeu rolagem interna propria e cabecalho compactado para acessar opcoes inferiores sem mover o conteudo principal.
- Configuracao SMTP de naoresponda@o3cloud.com.br e automacoes de email de implantacao foram validadas por teste/simulacao.

## 2026-08-03 - Fechamento Oficial Sprint 15

### Documentacao

- Dashboard principal `Visao Geral` passou a exibir Sprint 15 concluida e as acoes propostas para a Sprint 16.
- Sprint 15 marcada como concluida em `docs/25-FECHAMENTO-SPRINT-15.md`, `docs/05-SPRINT_ATUAL`, `docs/17-SPRINTS.md`, `docs/ROADMAP.md` e `docs/00-VISAO-GERAL.md`.
- Validacao final registrou 11 rotas de infraestrutura com HTTP 200, AST OK em 13 modulos e `git diff --check` sem erros.
- Pendencias remanescentes foram encaminhadas para validacao assistida ou sprint futura, sem bloquear o fechamento tecnico.

## 2026-08-03 - Revisao de Fechamento Sprint 15

### Documentacao

- Criado `docs/25-FECHAMENTO-SPRINT-15.md` com entregas consolidadas, validacoes, dados locais e pendencias finais para aceite operacional.
- `docs/05-SPRINT_ATUAL`, `docs/17-SPRINTS.md`, `docs/ROADMAP.md` e `docs/00-VISAO-GERAL.md` passaram a indicar Sprint 15 em revisao final para fechamento.
- Pendencias finais da Sprint 15 foram separadas entre validacao assistida, controle formal de acesso/perfis e historico centralizado opcional para sincronismos Zabbix/TrueNAS.

## 2026-08-03 - Sprint 15 Monitoramento Zabbix

### Infraestrutura

- Tela `/infraestrutura/monitoramento-zabbix` passou a consultar alarmes recentes do Zabbix em modo read-only.
- Alarmes abertos ficam no topo, ordenados por criticidade e data.
- Criticidade media/alta media usa amarelo, alta usa vermelho, critica usa vermelho escuro e resolvidos usam verde.
- Consulta usa a integracao Zabbix ativa cadastrada em Integracoes Tecnicas, sem alterar hosts, itens ou triggers.
- Alarmes Zabbix passaram a usar cache local persistido em `zabbix_alarm_cache`; a tela abre pelo cache e a API so e consultada ao clicar em Sincronizar Zabbix.
- Sincronismo Zabbix passou a limitar a consulta de eventos aos ultimos 30 dias, usar timeout efetivo minimo de 60s e regravar o cache como snapshot para evitar timeout/acumulo de eventos antigos.
- Tela Monitoramento Zabbix ganhou filtro de exibicao por status/criticidade no cache: Todos, Abertos, Resolvidos, Media, Alta media, Alta e Critica.
- Telas operacionais de infraestrutura deixaram de exibir atalhos para Integracoes Tecnicas/Credenciais, mantendo essa area restrita a usuarios avancados.
- Tela `/infraestrutura/backup-nas` passou a monitorar pastas de clientes em `/mnt/BKP1` a `/mnt/BKP7` no TrueNAS, com cache em `truenas_backup_cache` e sincronizacao manual read-only.
- Pastas sem arquivos alterados nas ultimas 24 horas aparecem como alerta amarelo, mantendo a abertura da tela pelo cache local.
- Backup NAS recebeu abas separadas para Alertas e Backups OK com navegacao por link, permitindo abrir a lista de OK mesmo sem JavaScript de abas.
- Tela Backup NAS ganhou filtro de cache por cliente, pasta, ultimo arquivo ou arquivo recente.
- Varredura TrueNAS passou a combinar pastas raiz dos clientes em `/mnt/BKP1` a `/mnt/BKP7` com dumps em `Backup-BD`/`Backups-BD` e `Postgres-BKPs`.
- Alertas Backup NAS passaram a exibir o ultimo arquivo modificado de qualquer extensao, data e tempo desde a ultima alteracao, mantendo tamanho dos arquivos recentes na aba OK.

## 2026-07-30 - Abertura da Sprint 15

### Visao Geral

- Visao Geral passou a informar Sprint 14 finalizada e Sprint 15 iniciada em 30/07/2026.
- `docs/05-SPRINT_ATUAL` passou a registrar Sprint 15 - Infraestrutura Operacional e Sincronismo Read-Only.
- `docs/17-SPRINTS.md` e `docs/ROADMAP.md` passaram a indicar Sprint 15 como sprint atual.
- Foco da Sprint 15 definido para Proxmox VE somente leitura, telas operacionais de infraestrutura e consultas PBS, Zabbix e TrueNAS.

## 2026-07-30 - Sprint 14 Diagnostico Pre-Beta

### Dashboard Executivo

- Adicionado bloco de Diagnostico pre-Beta com pendencias de cadastro comercial, fluxo operacional e dados financeiros.
- Contratos diretos continuam classificados como fluxo valido, sem obrigatoriedade de proposta.
- Custos, faturamentos e parametros financeiros ausentes passam a aparecer como pendencias de carga futura para a Beta, sem calculo definitivo de rentabilidade.
- Incluido checklist de validacao Beta por area: Comercial, Operacoes, Financeiro e Engenharia.
- Visualizacao de Clientes passou a buscar implantacao vinculada na tabela atual implantacoes, exibindo status, etapa Kanban, responsavel, prazo, checklist e link para o fluxo completo.
- Visualizacao de Clientes recebeu diagnostico pre-Beta de saneamento cadastral, contato, localizacao, origem e vinculo operacional.
- Visualizacao de Contratos recebeu diagnostico pre-Beta com classificacao de fluxo valido, pendencia de cadastro e pendencia operacional.
- Visualizacao de Implantacao recebeu diagnostico pre-Beta operacional sem executar automacoes destrutivas.
- Kanban de Implantacao teve colunas ampliadas, altura util ajustada para exibir pelo menos cinco cards por coluna, rolagem horizontal interna e quebra de texto reforcada para evitar sobreposicao.
- Kanban de Implantacao passou a enviar e-mail para contas@o3cloud.com.br quando um card e movido para Finalizado, informando conclusao e liberacao para faturamento.
- Telas de Faturamentos, Produtos por Cliente e Custos de Produtos passaram a reforcar leitura pre-Beta, carga homologada e ausencia de margem/rentabilidade definitiva antes da validacao oficial.
- Tela de Integracoes Tecnicas passou a exibir diagnostico pre-Beta para Proxmox, PBS, Zabbix, FreeIPA e TrueNAS.
- Adicionada migration 034 para historico de validacoes de integracoes tecnicas, registrando resultado, mensagem, usuario e data.
- Validacao de integracoes tecnicas permanece estrutural e nao destrutiva, sem chamada a APIs externas nesta sprint.
- Tela de Integracoes Tecnicas recebeu plano de sincronismo Proxmox VE para Sprint 15, com campos de inventario, regras de somente leitura e fases de execucao.
- Adicionada migration 036 para preparar inventario de VMs Proxmox e historico de execucoes de sync, ainda sem chamada real a API externa.
- Menu lateral de Infraestrutura foi padronizado visualmente com os demais submenus para Clusters, Nodes, Maquinas Virtuais e Containers.
- Adicionados itens de Infraestrutura para Backups PBS, Monitoramento Zabbix e Backup NAS, com telas iniciais de consulta para snapshots, monitoramento e backups TrueNAS.
- Sprint 14 encerrada em `docs/24-FECHAMENTO-SPRINT-14.md`, com cadastros finais e revisao assistida encaminhados para a fase Beta com a equipe.
- Validacao final por Flask test client retornou 200 nas rotas principais de clientes, contratos, implantacao, financeiro, catalogo, integracoes e infraestrutura.

## 2026-07-29 - Fechamento da Sprint 13 e Preparacao Pre-Beta

### Documentacao

- Criado `docs/23-FECHAMENTO-SPRINT-13.md` com a Sprint 13 registrada como decisao/preparacao, adiando dados reais oficiais para a fase Beta com a equipe.
- `docs/05-SPRINT_ATUAL`, `docs/17-SPRINTS.md` e `docs/ROADMAP.md` passaram a indicar Sprint 14 como sprint atual.
- Visao Geral principal passou a informar Sprint 13 finalizada e pendencias da Sprint 14.
- Custos, faturamentos e parametros financeiros ficaram preparados, mas sem carga real, dados ficticios ou importacao prematura antes do saneamento dos cadastros pelo Comercial e areas envolvidas.

## 2026-07-29 - Fechamento da Sprint 12 e Abertura da Sprint 13

### Documentacao

- Criado `docs/22-FECHAMENTO-SPRINT-12.md` com entregas, validacoes e pendencias encaminhadas.
- `docs/05-SPRINT_ATUAL`, `docs/17-SPRINTS.md` e `docs/ROADMAP.md` passaram a indicar Sprint 13 como sprint atual.
- Visao Geral principal passou a informar Sprint 12 finalizada e listar pendencias da Sprint 13.
- Pendencias da Sprint 13 foram organizadas em dados oficiais, validacoes tecnicas nao destrutivas, melhorias operacionais e indicadores gerenciais.

## 2026-07-29 - Rastreabilidade com Proposta Opcional

### Documentacao

- Sprint 12 passou a tratar `proposta_id` como vinculo opcional, nao como obrigatoriedade operacional.
- Contratos fechados diretamente pelo parceiro ou fora do O3Cloud Manager foram documentados como origem valida para implantacao.
- Pendencia de rastreabilidade historica foi fechada com foco em contrato, cliente, parceiro, executivo, implantacao e origem do negocio.
- Dashboard Executivo passou a exibir contratos sem proposta como contratos diretos, sem destaque de erro.
- Vinculos legados com proposta so devem ser corrigidos quando houver evidencia confiavel e trilha auditavel.

## 2026-07-29 - Anexos em Comentarios de Implantacao

### Implantacao

- Comentarios do historico de implantacao passaram a aceitar multiplos anexos.
- Arquivos sao salvos em `storage/implantacoes/<implantacao_id>/comentarios`.
- Banco registra apenas metadados e caminho/url do arquivo anexado em `implantacao_historico_anexos`.
- Exclusao do comentario remove os registros de anexo e os arquivos fisicos correspondentes.

## 2026-07-29 - OMIE e ClickSign na Tela de Integracoes

### Integracoes

- Tela `Integracoes de Negocio` passou a exibir OMIE e ClickSign ja configurados por variaveis de ambiente.
- Segredos de ambiente e tokens cadastrados sao exibidos mascarados como `****` na renderizacao inicial.
- Adicionado botao de visualizacao temporaria do segredo com retorno `no-store`, sem persistir o valor no HTML inicial.

## 2026-07-29 - Configuracoes de Integracoes para Sprint 12

### Integracoes

- Sidebar ganhou a secao `Configuracoes` com `Integracoes de Negocio` e `Integracoes Tecnicas`.
- Integracoes de negocio passaram a contemplar OMIE e ClickSign.
- Integracoes tecnicas passaram a contemplar Proxmox, PBS, Zabbix, FreeIPA e TrueNAS.
- Cadastro continua permitindo multiplas configuracoes por tipo usando nomes distintos.
- Validacao permanece estrutural e nao destrutiva nesta etapa.

## 2026-07-29 - Inicio da Sprint 12

### Documentacao

- Documento `docs/05-SPRINT_ATUAL` atualizado para Sprint 12 - Pendencias Operacionais e Preparacao da Versao Final.
- Roadmap e historico de sprints atualizados para refletir a Sprint 11 como parcialmente concluida e a Sprint 12 como sprint atual.
- Visao Geral passou a indicar Sprint 12 em planejamento e listar os focos de custos oficiais, faturamentos, parametros financeiros, rastreabilidade e validacoes tecnicas.

## 2026-07-29 - Visao Geral Atualizada para Fechamento Parcial da Sprint 11

### Dashboard

- Home `/` passou a informar o fechamento parcial da Sprint 11.
- Card principal da Visao Geral destaca as entregas prontas: telas, menus e importacoes CSV.
- Lista lateral passou a exibir pendencias encaminhadas para a Sprint 12.

## 2026-07-29 - Fechamento Parcial da Sprint 11

### Documentacao

- Sprint 11 encerrada como parcialmente concluida, pois as cargas oficiais de custos, faturamentos e parametros financeiros ficaram condicionadas a fontes validadas da versao final.
- Criado documento `docs/21-FECHAMENTO-SPRINT-11.md` com entregas, validacoes, diagnosticos e pendencias encaminhadas.
- Documentados os dados pendentes sem criar registros ficticios para simular rentabilidade.

## 2026-07-29 - Fluxo de Importacao de Faturamentos

### Sprint 11

- Criada tela `/financeiro/faturamentos` para acompanhar registros carregados por competencia.
- Adicionado modelo CSV `faturamentos_modelo.csv` com contratos elegiveis e colunas de bruto, comissao, liquido, origem e observacoes.
- Adicionada importacao idempotente por contrato e competencia, preservando a chave unica `contrato_id + competencia`.
- Origem padrao da carga manual definida como `MANUAL`; nenhum faturamento ficticio foi criado.

## 2026-07-28 - Fluxo de Importacao de Custos de Produtos

### Sprint 11

- Criada tela `/catalogo/produtos/custos` para listar produtos ativos pendentes de custo.
- Adicionada exportacao CSV `produtos_custos_pendentes.csv` com impacto por itens, clientes e valor vinculado.
- Adicionada importacao CSV por `codigo` para atualizar `valor_custo` somente com valores positivos.
- Lista de produtos ganhou atalho para o fluxo de custos.

---

## 2026-07-28 - Vinculos Omie no Catalogo

### Sprint 11

- Criado seed idempotente `database/seed/004_catalogo_vinculos_omie_sprint11.sql` para cadastrar/vincular 7 codigos de servico Omie ao catalogo.
- Corrigido o join de produtos no dashboard para converter apenas codigos numericos, evitando vinculos falsos com codigo Omie `0`.
- Cobertura de catalogo validada em 256 de 257 itens; custos continuam pendentes porque ainda nao ha fonte oficial validada para `valor_custo`.

---

## 2026-07-28 - Fila de Saneamento de Catalogo e Custos

### Sprint 11

- Dashboard Produtos por Cliente passou a listar os principais itens Omie sem vinculo com catalogo.
- Adicionada lista de produtos ja vinculados a contratos, mas ainda sem custo preenchido.
- Proxima acao operacional ficou direcionada para cadastrar codigos Omie e completar custos antes da rentabilidade.

---

## 2026-07-28 - Inicio da Sprint 11 com Produtos por Cliente

### Sprint 11

- Criada tela `/dashboard/produtos-clientes` para mapear cliente -> contrato -> item contratado.
- Diagnostico inicial usa itens sincronizados de contratos Omie e evidencia lacunas de proposta, catalogo e custo.
- Visao Geral passou a destacar Produtos por Cliente como primeira entrega operacional da Sprint 11.

---

## 2026-07-28 - Visao Geral Atualizada para Sprint 11

### Dashboard

- Visao Geral passou a indicar Sprint 11 como etapa atual de integracoes e melhorias operacionais.
- Dashboard Executivo passou a indicar Sprint 10 como concluida e base de diagnostico para a Sprint 11.

---

## 2026-07-28 - Fechamento da Sprint 10

### Documentacao

- Sprint 10 marcada como concluida oficialmente em 28/07/2026.
- Criado documento `docs/20-FECHAMENTO-SPRINT-10.md` consolidando entregas, regras, validacoes, diagnosticos e pendencias.
- Documento `docs/05-SPRINT_ATUAL` preparado para a Sprint 11 - Integracoes e Melhorias Operacionais.
- Roadmap e historico de sprints atualizados para refletir Dashboard Executivo como Base Alpha concluida.

---

## 2026-07-28 - Rastreabilidade Executiva no Dashboard

### Dashboard Executivo

- Adicionada visao de rastreabilidade proposta -> contrato -> implantacao.
- Dashboard passou a exibir cobertura ponta a ponta, contratos sem proposta e contratos sem implantacao.
- Fluxos operacionais exibem links diretos para proposta, contrato e implantacao quando houver vinculo.

---

## 2026-07-28 - Carga por Responsavel no Dashboard Executivo

### Dashboard Executivo

- Adicionada visao de carga por responsavel/implantador com projetos totais, andamento, atrasos e vencimentos em 7 dias.
- Carga operacional passou a exibir checklist medio e receita mensal vinculada aos contratos de implantacao.
- Visao respeita os filtros executivos aplicados no Dashboard Executivo.

---

## 2026-07-28 - Base Inicial de Rentabilidade e Custos

### Dashboard Executivo

- Adicionada seção de base para rentabilidade com receita recorrente, setup/projeto e cobertura de rastreabilidade.
- Dashboard passou a mapear prontidão das fontes de dados: contratos, faturamentos, produtos/custos, parâmetros financeiros e infraestrutura.
- Adicionada lista de contratos candidatos para cálculo futuro de rentabilidade, sem cálculo definitivo de margem enquanto custos não estiverem validados.

---

## 2026-07-28 - Evolucao Mensal no Dashboard Executivo

### Dashboard Executivo

- Adicionado comparativo mensal para propostas, receita mensal ativa e volume operacional.
- Evolucao mensal passou a respeitar filtros executivos de periodo, parceiro, executivo e status.
- Periodo padrao exibe os ultimos 6 meses; intervalos maiores ficam limitados aos ultimos 12 meses para manter leitura gerencial.

---

## 2026-07-28 - Drill-down Filtrado no Dashboard Executivo

### Dashboard Executivo

- Links do Dashboard Executivo passaram a preservar filtros compatíveis ao abrir Propostas, Contratos e Implantação.
- Atalhos de pendências críticas, contratos a iniciar e assinaturas pendentes passaram a apontar para listagens operacionais já filtradas.
- Corrigido endpoint do link de contratos a iniciar para usar a rota real `contratos.view`.

---

## 2026-07-27 - Filtros Executivos do Dashboard

### Dashboard Executivo

- Adicionados filtros executivos em `/dashboard/executivo` por período, parceiro, executivo, status comercial, status de contrato e status de implantação.
- Consultas agregadas do Dashboard Executivo passaram a aplicar os filtros nos blocos de propostas, contratos e implantação.
- Rankings por executivo/parceiro e listas de atenção passaram a respeitar os recortes selecionados.
- Selects de parceiro e executivo são carregados a partir dos registros ativos da base local.

---

## 2026-07-27 - Dashboard Executivo Dedicado

### Dashboard Executivo

- Criada rota `/dashboard/executivo` para concentrar a visão gerencial de diretoria.
- Home `/` passou a ser uma visão geral resumida com cards principais, status da Sprint 10 e atalhos.
- Menu lateral passou a separar `Visão Geral` e `Dashboard Executivo`.
- Tela executiva mantém indicadores comerciais, contratos, implantação, rankings e listas de atenção.

---

## 2026-07-27 - Início da Sprint 10

### Dashboard Executivo

- Sprint 10 marcada como iniciada para evoluir o Dashboard Executivo.
- Home `/` convertida em painel executivo com dados reais de propostas, contratos e implantação.
- Adicionados cards de receita mensal negociada, receita mensal ativa, implantações em andamento e pendências críticas.
- Adicionados agrupamentos por status comercial, status de contratos, status de implantação, executivo e parceiro.
- Adicionadas listas de atenção para implantações críticas, contratos a iniciar e assinaturas pendentes.
- Atalhos de drill-down conectam o dashboard aos módulos de Propostas, Contratos, Implantação e Kanban.

---

## 2026-07-27 - Fechamento da Sprint 9

### Documentação

- Sprint 9 marcada como concluída oficialmente em 27/07/2026.
- Criado documento `docs/19-FECHAMENTO-SPRINT-9.md` consolidando objetivo, entregas, migrations, regras, validações e pendências encaminhadas.
- Documento `docs/05-SPRINT_ATUAL` preparado para a Sprint 10 - Dashboard Executivo.
- Roadmap e histórico de sprints atualizados para refletir Implantação como Base Alpha concluída e Dashboard Executivo como próxima frente.

---

## 2026-07-27 - Navegação por Pastas no Cofre de Senhas

### Implantação e Provisionamento

- Tela principal do Cofre de Senhas reorganizada em navegação visual por parceiro e pastas de clientes.
- Seleção de parceiro passou a exibir apenas as pastas de clientes vinculadas a ele; credenciais aparecem somente após abrir a pasta do cliente.
- Formulário de pasta de cliente passou a exigir e gravar parceiro, evitando pastas fora da navegação hierárquica.
- Ações de revelar, copiar, editar e inativar credenciais foram preservadas dentro da pasta selecionada.

---

## 2026-07-27 - Base de Integrações Técnicas

### Implantação e Provisionamento

- Adicionada migration 031 para configuração base de integrações Proxmox, PBS e Zabbix.
- Criada tela /implantacao/integracoes para cadastrar, editar, inativar e validar configurações técnicas.
- Tokens e senhas das integrações passaram a ser armazenados criptografados usando a política do cofre.
- Validação desta etapa é estrutural e não executa chamadas externas ou ações destrutivas.
- Adicionado atalho Integrações Técnicas no menu Operações.

---

## 2026-07-27 - Colunas Administrativas do Kanban

### Implantação e Provisionamento

- Adicionada migration 030 para configurar colunas do Kanban de Implantação.
- Criada tela administrativa /implantacao/kanban/colunas para criar, ordenar, renomear, ativar e inativar colunas.
- Kanban, formulário de implantação e notificações passaram a usar as colunas configuradas na base.
- Colunas essenciais FILA, FINALIZADO e CANCELADOS ficam protegidas contra inativação.
- Colunas com cards ativos não podem ser inativadas para evitar perda visual de implantações em andamento.

---

## 2026-07-27 - Rastreabilidade Comercial para Implantação

### Implantação e Provisionamento

- Criada visão compartilhada de rastreabilidade proposta -> contrato -> implantação.
- Telas de Proposta, Contrato e Implantação passaram a exibir atalhos e status do fluxo ponta a ponta.
- Rastreabilidade exibe ClickSign, contrato Omie/manual, etapa Kanban, responsável, prazo e progresso do checklist quando disponíveis.
- Consulta tolera vínculos incompletos, mantendo visibilidade de propostas sem contrato e contratos sem implantação.

---

## 2026-07-27 - Checklist de Implantação Evoluído

### Implantação e Provisionamento

- Checklist de Implantação passou a permitir inclusão manual de itens por projeto.
- Adicionados modelos operacionais de checklist para implantação padrão, Licenças O3Web e Infraestrutura/VPN.
- Aplicação de modelo evita duplicar itens já existentes na implantação.
- Itens do checklist podem ser removidos, com recálculo automático do percentual de conclusão.

---

## 2026-07-27 - Dashboard de Implantação Refinado

### Implantação e Provisionamento

- Dashboard de Implantação passou a aplicar filtros reais por status, responsável, prazo e situação.
- Adicionados indicadores de projetos atrasados, vencendo em 7 dias, vencendo em 30 dias e sem prazo.
- Adicionadas visões resumidas por status e por responsável, respeitando os filtros aplicados.
- Listagem passou a sinalizar prazo atrasado, vencimento próximo e ausência de prazo.

---

## 2026-07-22 - Dashboard Principal da Sprint 9

### Implantação e Provisionamento

- Dashboard Executivo passou a informar que a Sprint 9 está em implantação.
- Adicionado resumo das entregas recentes de Implantação e das pendências principais da Sprint 9.
- Atalho do card principal passa a direcionar para o módulo de Implantação.

---

## 2026-07-22 - Ação Direta Contrato para Implantação

### Implantação e Provisionamento

- Adicionada ação direta em Contratos para iniciar implantação quando o contrato está `ENCAMINHADO_PROJETO`.
- Contratos que já possuem implantação ativa passam a exibir atalho para abrir a implantação existente, sem criar duplicidade.

---

## 2026-07-22 - Cofre de Senhas de Implantação

### Implantação e Provisionamento

- Adicionada migration `028_create_implantacao_cofre_senhas.sql` para armazenar credenciais criptografadas e auditoria de ações.
- Criada tela `Cofre de Senhas` em Implantação com listagem, filtros, cadastro, edição, inativação e revelação controlada de senha.
- Credenciais passaram a vincular cliente, faixa de rede e opcionalmente licença O3Web, com campos futuros para Proxmox, PBS e Zabbix.
- Revelação de senha é feita sob demanda pela interface e registrada em auditoria com usuário e IP de origem quando disponíveis.
- Adicionados botões para copiar senha, usuário, URL e Host/IP na tela do Cofre de Senhas.
- Adicionado gerador local de senha complexa no formulário do Cofre, com política padrão preparada para futura tela de Configurações.
- Formulário do Cofre passa a importar a URL salva em Licenças O3Web quando uma licença é vinculada, deixando o campo editável quando não há vínculo.
- Adicionada migration `029_create_implantacao_cofre_pastas.sql` com pastas do cofre por parceiro, cliente ou usuário logado.
- Tela principal do Cofre passou a permitir criação, edição, seleção e filtro por pastas, com metadados de dono e compartilhamento preparados para futura política de acesso.

---

## 2026-07-22 - Gerenciamento de Faixas de Rede

### Implantação e Provisionamento

- Adicionada migration `026_create_implantacao_faixas_rede.sql` para controle de faixas de rede por cliente.
- Criada tela `Faixas de Rede` em Implantação com listagem, filtros, cadastro, edição, inativação e vínculo com cliente sincronizado do Omie.
- Adicionado cálculo da próxima faixa disponível dentro de uma rede base, escolhendo máscara `/29`, `/28` ou `/27` conforme a quantidade de servidores.
- Cadastro de faixa registra `Rede`, `FW - WAN`, `FW - LAN`, `Cliente`, `VPN`, range de `Portas`, `PVE` e `Observações`.
- Adicionada migration `027_add_port_range_implantacao_faixas_rede.sql` para estruturar `porta_inicio` e `porta_fim`.
- Cadastro de Faixas de Rede bloqueia conflito de range de portas quando o `FW - WAN` é o mesmo em outro cadastro ativo.

---

## 2026-07-22 - Vínculo de Licenças O3Web com Clientes

### Implantação e Provisionamento

- Adicionada migration `025_add_cliente_vinculo_o3web_licencas.sql` com vínculo opcional entre licenças O3Web e clientes cadastrados.
- Cadastro manual de Licenças O3Web passou a selecionar cliente ativo da base de clientes e preencher CNPJ automaticamente.
- Listagem de Licenças O3Web passou a exibir o CNPJ vinculado ao cliente quando disponível.
- Tela de Licenças O3Web passou a exibir paginação quando houver mais de 50 registros, preservando filtros aplicados.
- Adicionado filtro de validade para listar licenças O3Web vencidas ou vigentes.
- Adicionado alerta na tela de Licenças O3Web quando houver licenças vencidas ativas, com atalho para a listagem filtrada.
- Importação CSV permanece compatível com cliente em texto e passa a aceitar CNPJ quando presente.

---

## 2026-07-21 - Licenças O3Web

### Implantação e Provisionamento

- Adicionada migration `024_create_o3web_licencas.sql` para gestão operacional de licenças O3Web.
- Criada tela `/implantacao/licencas-o3web` com dashboard, filtros, cadastro manual, edição e inativação de licenças.
- Criado importador CSV para campos atuais da planilha de licenças, incluindo chave de ativação, ID licença, tipo, backup, dias, usuários, edição, datas, cliente, URLs, comments e observação.
- Importação atualiza registros por `ID Licença` quando disponível e preserva datas originais quando o formato não puder ser normalizado.

---

## 2026-07-21 - Histórico de Implantação

### Implantação e Provisionamento

- Adicionada migration `023_add_implantacao_historico_emails.sql` com histórico de implantação e e-mails adicionais.
- Edição da implantação passou a permitir alteração direta da etapa do Kanban.
- Visualização da implantação passou a exibir histórico com data/hora, autor, comentário e status de envio de e-mail.
- Comentários do histórico passaram a ter ações de editar e excluir, mantendo mudanças de etapa como auditoria somente leitura.
- Comentários podem ser registrados e opcionalmente enviados por e-mail aos envolvidos do projeto.
- E-mails adicionais podem ser cadastrados na implantação para compor as notificações do projeto.

---

## 2026-07-21 - Kanban de Implantação

### Implantação e Provisionamento

- Adicionada migration `022_add_kanban_implantacao.sql` com etapa Kanban e dados de implantador.
- Criada tela `/implantacao/kanban` com colunas operacionais de projeto e movimentação por arrastar e soltar.
- Contratos `ENCAMINHADO_PROJETO` passaram a cair automaticamente na coluna `Fila` como implantação editável.
- Movimentação de coluna passou a notificar implantador, executivo, parceiro e contatos envolvidos quando SMTP estiver configurado.
- Formulário de implantação passou a salvar implantador e e-mail do implantador.
- Implantação criada a partir do Kanban passou a preencher início previsto em 7 dias corridos e entrega prevista 30 dias depois.

---

## 2026-07-21 - Início Sprint 9

### Implantação e Provisionamento

- Sprint 9 iniciada com a fundação do módulo próprio de Implantação.
- Adicionada migration `021_create_implantacao_workflow.sql` com tabelas `implantacoes` e `implantacao_checklist`.
- Adicionados repository, service, routes e templates para listagem, criação, visualização, edição e dashboard inicial de implantações.
- Criação de implantação passou a exigir contrato encaminhado para projeto e gerar checklist técnico padrão.
- Tela de Nova Implantação passou a preencher título e contexto operacional ao selecionar contrato, sem exibir valores de negociação.
- Adicionada visualização operacional do contrato para implantação, omitindo valores comerciais/financeiros.
- Provisionamento foi registrado como etapa planejada/rastreável, sem integração Proxmox automática nesta primeira entrega.

---

## 2026-07-21 - Revisão Sprint 9

### Implantação e Provisionamento

- Sprint 9 revisada para início com foco em módulo próprio de Implantação.
- Escopo definido para workflow pós-contrato encaminhado para projeto, checklist técnico, acompanhamento e preparação de provisionamento.
- Integração Proxmox posicionada como etapa controlada e auditável, sem automação destrutiva na primeira entrega.

---

## 2026-07-21 - Início Sprint 8

### Dashboard Comercial

- Sprint 8 iniciada com foco em consolidação comercial e pós-assinatura.
- Adicionado Dashboard Comercial em `/propostas/dashboard`.
- Dashboard passou a exibir totais de propostas, receita mensal negociada, implantação, propostas em assinatura, assinadas e concluídas.
- Adicionados agrupamentos por executivo, parceiro, status comercial e status ClickSign.
- Adicionados atalhos para o Dashboard Comercial no menu lateral e na listagem de Propostas.

---

## 2026-07-20 - Fechamento Sprint 7

### CRM, Propostas e Contratos

- Sprint 7 concluída com CRM Comercial Alpha, Propostas, Contratos pós-assinatura e integração ClickSign.
- Propostas passaram a gerar contrato a partir de modelo DOCX editável e visualizar PDF antes do envio.
- Contratos passaram a aceitar vínculos com contato, proposta, parceiro e executivo, com edição restrita para contratos Omie.
- Dashboard de Contratos passou a somar valores conforme filtro de status selecionado e agrupar por executivo/parceiro.
- Quantidade de usuários deixou de ser obrigatória em contratos manuais.
- Contratos manuais podem ser excluídos logicamente.

### ClickSign

- Adicionado client real da API ClickSign v3.
- Envio real de contratos para ClickSign com contato do cliente, representante O3 Cloud e executivo como testemunha.
- Adicionado botão `Sincronizar ClickSign` na tela principal de Propostas para sincronização manual em lote.
- Sincronização interpreta `running` como `Aguardando Assinaturas` e `closed` como `Assinado`.
- PDF assinado é baixado da ClickSign e salvo em `storage/contratos`.

### Banco de Dados

- Adicionadas migrations `017`, `018`, `019` e `020` para ClickSign, contratos pós-assinatura, vínculos comerciais e CPF opcional de contatos.

---

# [3.0 Alpha] - Julho/2026

## Situação

🚧 Desenvolvimento Ativo

---

## Adicionado

### Arquitetura

- Definição oficial da arquitetura Repository → Service → Routes → Templates.
- Criação do BaseRepository.
- Padronização do acesso ao banco utilizando SQL puro.
- Implementação de UUID automático.
- Implementação de Soft Delete.
- Padronização do fluxo de desenvolvimento.

---

### Componentes Compartilhados

Criados:

- page_header.html
- filter_bar.html
- crud_actions.html
- alert.html

Templates Base:

- index_base.html
- form_base.html
- view_base.html

Todos homologados.

---

### Módulo Ambientes

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

---

### Módulo Clientes

Concluído:

- CRUD completo.
- Integração OMIE.
- Sincronização.
- Controle de origem.
- Bloqueio de edição para clientes sincronizados.
- Serviço de implantação.

---

### Módulo Contratos

Concluído:

- CRUD.
- Integração OMIE.
- Estrutura de contratos.
- Itens de contrato.
- Repository.
- Service.
- Routes.
- Menu próprio de Contratos.
- Dashboard pós-assinatura com totais por recorrência, setup, usuários, executivo e parceiro.
- Formulário de novo contrato vinculado ao CNPJ do cliente.
- Bloqueio de edição para contratos sincronizados do Omie.
- Upload e download de contrato PDF assinado em `storage/contratos`.

---

### Catálogo Técnico

#### Categorias

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

#### Produtos

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

#### Modelos

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.
- Acesso direto pela home do Catálogo Comercial.

#### Faixas

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.
- Atalho de gestão e criação pela home do Catálogo Comercial.

---

### BaseRepository

Adicionado:

- generate_uuid()
- bool_to_int()

Padronização dos repositories.

---

### Documentação

Criados:

- PROJETO.md
- ROADMAP.md
- 03-ARQUITETURA.md
- 04-PADROES.md
- 05-SPRINT-ATUAL.md
- ENGINEERING_PRINCIPLES.md
- AGENTS.md
- PROJECT_CONTEXT.md
- DOMAIN_RULES.md
- AI_WORKFLOW.md
- 15-CHECKLIST.md
- 16-DEFINITION-OF-DONE.md
- README.md

---

## Alterado

### Arquitetura

Padronização completa da estrutura dos módulos.

Todos os CRUDs passam a seguir:

Repository

↓

Service

↓

Routes

↓

Templates

---

### Desenvolvimento

Definida metodologia oficial:

- Um arquivo por vez.
- Arquivo completo.
- Testes.
- Homologação.
- Atualização da documentação.
- Commit.
- Próxima tarefa.

---

### Inteligência Artificial

Documentação estruturada para suportar:

- OpenAI Codex
- ChatGPT
- Claude Code
- Gemini CLI
- Cursor AI
- GitHub Copilot

---

## Corrigido

### Categorias

- Ajustes nas validações.
- Melhorias no fluxo de ativação e desativação.
- Padronização das mensagens.
- Padronização do Repository.

---

### Produtos

- Padronização do Repository.
- Padronização do Service.
- Ajustes nas rotas.
- Adequação à arquitetura oficial.

### Catálogo Comercial

- Ajustada a home do catálogo para remover duplicação de navegação.
- Adicionados atalhos diretos para Modelos e Faixas.
- Corrigida a contabilização de Categorias, Modelos e Faixas na visão geral.

### Importação do Catálogo

- A tela `Importar Catálogo` passou a exibir um modelo visual de CSV com exemplos de licenciamento e recursos de servidor.
- A interface deixou de referenciar exclusivamente o Base44 e passou a orientar a importação de qualquer arquivo CSV aderente ao formato esperado.
- O fluxo ficou mais claro para validação do cabeçalho e preenchimento dos campos antes da importação.

### CRM Comercial

- O sidebar passou a exibir um separador exclusivo para o módulo `CRM Comercial`.
- O módulo `Leads` foi iniciado com listagem, cadastro, edição, visualização e exclusão.
- O módulo `Contatos` foi iniciado com CRUD base e vínculos opcionais com lead, parceiro e executivo.
- O módulo `Oportunidades` foi iniciado com negociações ativas, estimativa financeira e probabilidade de fechamento.
- O `Pipeline Comercial` foi iniciado com uma visão visual do funil baseada nos status das oportunidades.
- O módulo `Propostas` foi iniciado com versionamento por oportunidade, validade, valor total e anexo opcional.
- A migration `010_create_crm_leads.sql` foi criada e aplicada no banco com vínculos opcionais para parceiros e executivos.
- A migration `011_create_crm_contatos.sql` foi criada para suportar a agenda comercial do CRM.
- A migration `012_create_crm_oportunidades.sql` foi criada para suportar a etapa de negociação ativa do funil comercial.
- A home passou a destacar visualmente o início do CRM com atalho direto para Leads.

---

## Segurança

Implementado:

- Soft Delete.
- UUID obrigatório.
- Prepared Statements.
- Separação entre Repository, Service e Routes.

---

## Próxima Versão

### Sprint 7

Em desenvolvimento.

Objetivos:

- CRM Comercial
- Leads
- Contatos
- Oportunidades
- Pipeline Comercial
- ClickSign

---

## Roadmap Futuro

Sprint 7

- CRM Comercial
- Leads
- Oportunidades
- Pipeline
- ClickSign

Sprint 8

- Propostas
- Precificação
- Versionamento
- PDF

Sprint 9

- Implantação
- Workflow
- Provisionamento

Sprint 10

- Dashboard Executivo

Sprint 11

- Integrações Avançadas
- NetBox
- PBS

---

## Observações

Este projeto segue a documentação oficial localizada em:

/docs

Toda implementação deverá obedecer:

- AGENTS.md
- PROJECT_CONTEXT.md
- DOMAIN_RULES.md
- AI_WORKFLOW.md
- 03-ARQUITETURA.md
- 04-PADROES.md
- ROADMAP.md
- 05-SPRINT-ATUAL.md
- ENGINEERING_PRINCIPLES.md
- 15-CHECKLIST.md
- 16-DEFINITION-OF-DONE.md

---

## Status Atual

Versão:

3.0 Alpha

Sprint:

6.4

Situação:

🚧 Desenvolvimento Ativo

Próxima Implementação:

Homologação de Servidores e consolidação da base de Dimensionamento.

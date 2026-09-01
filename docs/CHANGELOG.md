# Changelog

## 2026-09-01 - Email de faturamento da implantacao

- Notificacao financeira de implantacao finalizada passou a ser enviada para `faturamento@o3cloud.com.br`.
- A troca cobre o envio automatico ao mover a implantacao para `Finalizado` no Kanban e o reenvio manual pelo botao `Notificar financeiro`.
- Endereco de destino centralizado em `EMAIL_FINANCEIRO_IMPLANTACAO`, refletido tambem em historico, logs, flash de sucesso e confirmacao do botao.
- Procedimento e validacoes documentados em `docs/60-EMAIL-FATURAMENTO-IMPLANTACAO-BETA.md`.

## 2026-08-31 - Ajustes Beta em Proxmox, navegacao e Pagamento Campanhas

- Corrigido o sincronismo de inventario Proxmox que falhava com `Not all parameters were used in the SQL statement`, ajustando o `INSERT` de `proxmox_vm_inventory` para gravar `raw_payload` com a quantidade correta de parametros.
- `Voltar Inicio` passou a usar retorno inteligente no navegador, preservando a ultima tela operacional/listagem visitada com filtros e query string, sem ficar preso em telas de novo, edicao ou detalhe.
- Botoes locais `Voltar` em telas de visualizacao/formulario foram alinhados ao mesmo retorno inteligente, mantendo o `href` original como fallback.
- `Parceiros > Executivos` recebeu botao de retorno explicito para a listagem geral de parceiros, inclusive quando a tela estiver filtrada por parceiro.
- `Financeiro > Premiacoes > Pagamento Campanhas` passou a permitir editar os destinatarios do e-mail, mantendo os e-mails vindos do cadastro/Omie e permitindo adicionar outros manualmente.
- Destinatarios extras de Pagamento Campanhas sao mesclados no backend, com normalizacao, remocao de duplicados e validacao de formato antes do envio.
- Procedimento e validacoes documentados em `docs/59-MELHORIAS-BETA-2026-08-31.md`.

## 2026-08-31 - Sugestao automatica em Faixas de Rede

- Implantacao > Faixas de Rede passou a sugerir automaticamente a proxima faixa ao clicar em `Cadastrar manualmente`, usando a ultima faixa ativa cadastrada como referencia.
- A sugestao calcula a mascara pela quantidade de servidores, preenchendo `/29`, `/28` ou `/27` conforme a capacidade necessaria.
- O formulario de nova faixa passa a receber `FW - LAN` e `PVE` com IPs sequenciais da nova rede.
- `FW - WAN` passa a sugerir o proximo IPv4 a partir do cadastro anterior, quando o valor anterior for um IP valido.
- O intervalo principal de portas passa a ser sugerido em sequencia fixa de 6 portas, por exemplo `1601-1606` depois de uma ultima porta `1600`.
- Corrigido banco local que estava sem a tabela `implantacao_faixas_rede_portas`, criada pela migration existente `113_create_implantacao_faixas_rede_portas.sql`.
- Procedimento e validacoes documentados em `docs/58-FAIXAS-REDE-SUGESTAO-AUTOMATICA-BETA.md`.

## 2026-08-30 - Pagamento de campanhas de premiação

- Criada a tela `Financeiro > Premiações > Pagamento Campanhas` para simular contas a pagar de premiações por campanha e parceiro.
- A tela considera contratos recebidos no Omie e premiações de adendos, agrupando por campanha, parceiro e executivos vinculados.
- Vínculo de executivo por `Projeto OMIE` passou a ignorar diferença de maiúsculas/minúsculas e a cair no executivo manual quando o projeto preenchido não localizar cadastro correspondente.
- O cálculo padrão de pagamento considera somente premiações com status manual `Lançado`; `Aberto` fica fora do contas a pagar e `Pago` fica disponível apenas para conferência por filtro.
- Adicionados relatório CSV e PDF gerais consolidados com todos os parceiros, além de recibo PDF por parceiro e por executivo com data de recebimento Omie e data de ativação do contrato.
- PDFs e emails passaram a incluir o logo da O3 Cloud e, quando cadastrado, o logo do parceiro.
- Corrigida a reativação de adendos ao marcar novamente `Incluir adendos` após uma simulação sem adendos.
- Adicionado envio de e-mail ao parceiro com corpo editável e anexos de recibo do parceiro e dos executivos vinculados.
- Serviços de Email passou a aceitar a finalidade `Pagamento de campanhas`, com atalho para cadastrar SMTP usando remetente `contas@o3cloud.com.br`.
- Procedimento e validações documentados em `docs/57-PAGAMENTO-CAMPANHAS-PREMIACOES-BETA.md`.

## 2026-08-30 - Ajustes Beta em adendos, premiações, dashboard de contratos e propostas

- E-mail automático de adendo enviado para sac@o3cloud.com.br deixou de incluir o valor recorrente no corpo da mensagem.
- Financeiro > Premiações passou a usar o executivo vinculado manualmente ao contrato quando `Projeto OMIE` estiver vazio, inclusive para regularizar premiações de adendos já lançadas sem executivo.
- Financeiro > Contratos > Dashboard passou a incluir adendos nos totais conforme `data_adendo`, mantendo separação entre contratos principais e adendos na quantidade e na recorrência.
- Adendos de `USUARIOS_ADICIONAIS` passaram a somar a quantidade adicional em `Licenças ativas` no dashboard de contratos.
- Propostas passaram a ocultar `Instalação de recursos` por padrão; o valor só aparece na tela, preview, visualização e documento quando o usuário marca explicitamente `Incluir instalação de recursos`.
- Criada a migration `124_add_incluir_instalacao_recursos_propostas.sql` para persistir a opção de inclusão do valor de instalação de recursos.
- Procedimento e validações documentados em `docs/56-MELHORIAS-BETA-2026-08-30.md`.

## 2026-08-29 - Sprint 23 Proxmox Agendamentos

- Agendamentos Proxmox agora exigem backup PBS da VM nas últimas 24 horas antes de permitir salvar upgrade de CPU/memória.
- E-mails de agendamento Proxmox passaram a ser enviados também em HTML, com resumo operacional, ambiente, CPU/sockets, memória, política de execução, erro quando houver e link para acompanhamento.
- Agendamentos Proxmox passaram a considerar sockets ao aplicar CPU total desejada, exibindo topologia atual e ajustando para 1 socket quando necessário para evitar vCPU dobrada.
- Sprint 23: agendamentos Proxmox notificam por e-mail o usuário criador no cadastro, no início da execução e no resultado final de sucesso ou falha.
- Sprint 23: módulo de agendamentos Proxmox para upgrade programado de CPU/memória em VMs QEMU, com fila persistente, eventos, worker e comando CLI.

## 2026-08-29 - Adendos contratuais e premiações manuais

- Contratos passaram a permitir cadastro, edição, inativação e anexos PDF de adendos contratuais vinculados ao contrato principal.
- Adendos não geram implantação, checklist, fila ou setup Omie.
- Premiações manuais de adendos usam campanha de comissão, valor base, status e observações; parceiro, executivo, percentuais e valores são calculados pela mesma regra da apuração automática.
- Financeiro > Premiações passou a considerar adendos nos filtros por campanha, no total de contratos + adendos, na base de premiação e na premiação prevista.
- Corrigida a normalização decimal do cadastro de adendos para aceitar valores como `435.00` e `435,00` sem multiplicar por 100.
- Adendos de usuários adicionais passaram a enviar solicitação para sac@o3cloud.com.br e incrementar automaticamente a licença O3Web quando houver uma única licença ativa identificável.
- Criadas as migrations `118_create_contratos_adendos.sql` e `119_add_campanha_id_premiacoes_adendos.sql`.

## 2026-08-28 - CRM com vinculo de clientes e ajustes Beta de UI

### Contratos com Setup Omie
- Adicionado sincronismo manual de OS Omie no detalhe do contrato para preencher valor de setup, parcelas e status da OS.
- Criado mapeamento de status de setup: aberto, cancelado, faturado, nao encontrado e nao sincronizado.
- Criada migration `116_add_setup_omie_contratos.sql` para persistir os metadados da OS no contrato.
- Adicionado sincronismo geral de setup Omie na tela principal de Contratos e automacao `OMIE_SETUP_CONTRATOS` em Configuracoes > Automacoes de Sincronismo.
- Criada migration `117_add_omie_setup_contratos_sincronismo.sql` para cadastrar o agendamento, inativo por padrao.


- Removidas referencias visiveis de Sprints em telas da versao Beta, substituindo por linguagem de Beta/homologacao.
- Cofre de Senhas corrigiu a exclusao de arquivos vinculados na edicao da credencial, removendo formulario aninhado e direcionando o POST para a rota correta.
- Contatos do CRM passaram a ter `cliente_id` vinculado a `clientes`, com listagem/detalhe priorizando o cliente cadastrado.
- Oportunidades passaram a usar `Empresa / Cliente` como vinculo direto com Cadastro Clientes, eliminando o seletor duplicado de cliente.
- Criado o componente reutilizavel `app/templates/components/search_picker_script.html`, reaproveitando o padrao de busca/adicao de `Ambientes > Vinculos comerciais`.
- Em Contatos e Oportunidades, o botao `+` do campo `Empresa / Cliente` redireciona para o cadastro manual de cliente em `/clientes/novo`.
- Criada e aplicada localmente a migration `115_add_cliente_id_crm_contatos.sql`.
- Procedimento e validacoes documentados em `docs/54-MELHORIAS-BETA-2026-08-28.md`.

## 2026-08-27 - Melhorias operacionais para Beta

- Cofre de Senhas passou a usar seletores pesquisaveis tambem para Ambiente do Cliente, Implantador, Faixa de rede e Licenca O3Web.
- Cofre de Senhas passou a permitir exclusao de arquivos vinculados na edicao da credencial e links de download na tela principal.
- Ambientes removeu `Implantacao` das opcoes padrao de `Situacao`, mantendo compatibilidade para registros antigos ja salvos com esse valor.
- Premiacoes recebeu checagem manual de pagamento com status `Aberto`, `Lancado` e `Pago`, exibida somente quando o contrato ja esta `Recebido` pelo sistema e salva automaticamente por AJAX.
- Premiacoes passou a listar apenas contratos cuja vigencia se encaixa em uma campanha ativa.
- Criada a migration `114_create_financeiro_premiacoes_pagamento.sql` para persistir o status manual de pagamento da premiacao por contrato e campanha.
- Reajustes Contratuais recebeu sincronismo manual de Faturamento e Previsoes do Omie, com calculo operacional considerando faturamentos a partir de `01/03/2026`.
- Comentarios de Implantacao passaram a permitir envio opcional dos arquivos anexados junto no e-mail do comentario.
- Procedimento e validacoes documentados em `docs/53-MELHORIAS-BETA-2026-08-27.md`.

## 2026-08-25 - Pesquisa de satisfacao publica com rolagem

- Tela publica de resposta da pesquisa de satisfacao da implantacao passou a liberar rolagem vertical no `body`.
- Corrigido cenario em que o botao `Enviar avaliacao` ficava fora da area visivel em telas menores por causa do `overflow: hidden` global.
- Ajuste foi isolado pela classe `public-survey-page`, preservando o layout interno do sistema.
- Procedimento de atualizacao e validacao do Beta documentado em `docs/51-PESQUISA-SATISFACAO-ROLAGEM-BETA.md`.

## 2026-08-25 - Propostas: instalacao de recursos editavel

- Campo `Instalacao de recursos` em propostas comerciais passou a ser editavel na totalizacao geral.
- O valor continua sendo sugerido pela soma dos recursos do bloco de servidores, mas overrides manuais sao preservados ao salvar e reabrir a proposta.
- Backend passou a persistir `crm_propostas.instalacao_servidores` e a usar esse valor no total de instalacao, preview, visualizacao, contrato e DOCX.
- Criada a migration `111_add_instalacao_servidores_propostas.sql`, inicializando propostas antigas pelo total de instalacao ja salvo menos parametrizacao e setup cloud.
- Procedimento de atualizacao e validacao do Beta documentado em `docs/50-PROPOSTAS-INSTALACAO-RECURSOS-BETA.md`.


## 2026-08-25 - Redefinicao de senha

- Adicionado o link `Esqueci minha senha` na tela de login do O3Cloud Manager.
- Criado fluxo publico para solicitar redefinicao por e-mail e cadastrar nova senha por token expiravel de 60 minutos.
- Adicionada auditoria das solicitacoes, ignoradas e conclusoes, com invalidacao do token apos uso.
- Criada a migration `110_auth_password_resets.sql`.
- Procedimento de atualizacao e validacao do Beta documentado em `docs/49-RESET-SENHA-BETA.md`.


## 2026-08-21 - Agrupamento de Cards de Implantacao

- Implantacao passou a permitir vincular um card secundario a um card principal para clientes com multiplas unidades/contratos atendidos pelo mesmo ambiente.
- Cards vinculados continuam rastreaveis por contrato, mas saem da lista principal e do Kanban operacional por padrao para evitar duplicidade de processo.
- Tela principal recebeu filtro `Cards principais`, `Cards vinculados` e `Todos`, alem de acao rapida para vincular ou desvincular cards.
- Detalhe da implantacao mostra os cards vinculados ao principal e registra historico/auditoria para cada vinculo ou desvinculo.

## 2026-08-21 - Sucesso do Cliente no CRM Comercial

- Criada tela `CRM Comercial > Sucesso do Cliente` para acompanhar contratos ativos por Razao Social, Nome Fantasia, CNPJ, usuarios, Vendedor OMIE, Projeto OMIE, valor bruto e observacoes do contrato OMIE.
- Implementada classificacao automatica de curva por valor bruto: Curva A para contratos a partir de R$ 2.999,99, Curva B de R$ 1.000,00 ate abaixo de R$ 2.999,99 e Curva C abaixo de R$ 1.000,00.
- Adicionado vinculo de contato do CRM Comercial ao acompanhamento CS, com atalho para cadastrar contato quando ainda nao existir.
- Criado historico de relacionamento por contrato com status `Otimo`, `Bom`, `Regular` e `Critico`, destacando contratos criticos em vermelho no dashboard/listagem.
- Comentarios de relacionamento aceitam anexos e registram autor, data e hora, com auditoria de inclusao e vinculo de contato.
- Badges de curva usam cores operacionais distintas: Curva A amarela, Curva B cinza e Curva C azul.
- Listagem principal recebeu acao rapida para marcar contrato como `Critico`, registrando historico e auditoria sem exigir abertura da tela de comentario.

## 2026-08-21 - Ajustes Beta em Propostas e Licencas O3Web

- Tela `Nova Proposta` passou a separar servidores em blocos independentes, com selecao explicita do servidor de destino antes de adicionar recursos.
- Botao de recurso em propostas renomeado para `Adicionar ao Servidor`, reduzindo ambiguidade entre criar servidor e incluir recurso no servidor selecionado.
- Acao `Novo servidor` cria e seleciona um novo bloco vazio; acao `Servidor basico` cria bloco separado com os recursos padrao quando ja houver servidor cadastrado.
- Tela `Nova Licenca O3Web` passou a calcular automaticamente `Data expiracao` para licencas `Trial` a partir de `Data ativacao + Dias`.
- Backend de Licencas O3Web tambem calcula a expiracao ao salvar quando o campo vier vazio, preservando valores preenchidos manualmente e o marcador `-` para licenca permanente.

## 2026-08-14 - Instaladores Beta Interativos
- Scripts `deployment/install-db-server.sh` e `deployment/install-app-server.sh` passaram a solicitar em modo interativo os campos obrigatorios ausentes, mantendo suporte a execucao automatizada por variaveis de ambiente.

## 2026-08-14 - Restauracao pela Tela de Backups

- Adicionada secao `Restauracao de backup` em `Configuracoes > Backups do Sistema`, com upload de artefato `.tar.gz`, `.tgz`, `.sql` ou `.sql.gz`, confirmacao textual `RESTAURAR` e selecao de banco/storage.
- Backend reutiliza `deployment/restore-db.sh` com `--yes --skip-service` para restauracao acionada pela interface e restaura `storage.tar.gz` de artefatos completos com validacao contra path traversal.

## 2026-08-14 - Instalacao Beta em Servidores Separados

- Criados scripts `deployment/install-db-server.sh`, `deployment/install-app-server.sh` e `deployment/apply-migrations.sh` para separar banco de dados e servidor de aplicacao/storage.
- Documentado procedimento em `docs/47-INSTALACAO-BETA-SERVIDORES-SEPARADOS.md`, com requisitos recomendados, variaveis obrigatorias, ordem de execucao e validacao pos-instalacao.

## 2026-08-14 - Sprint 22 Monitoramento de Reajustes Contratuais

- Criada tela `Financeiro > Reajustes Contratuais` para monitorar aniversarios contratuais calculados a partir de `contratos.inicio_vigencia`.
- Adicionadas tabelas `contratos_valores_historico`, `contratos_reajustes_alertas`, `reajustes_configuracoes` e `reajustes_configuracoes_usuarios` pela migration `100_create_reajustes_contratuais.sql`.
- Implementado `ReajusteContratoService` com calculo de idade, proximo aniversario, dias restantes, situacao, historico de valores e deduplicacao de alertas.
- Sincronizacao/cadastro/edicao de contratos passaram a registrar historico de valores quando houver alteracao relevante, sem alterar automaticamente valores no OMIE ou no contrato.
- Detalhe do contrato passou a exibir secao `Reajuste Contratual` com status, valores e historico.
- Adicionado comando CLI `flask reajustes-processar-alertas` e cron diario para execucao preventiva.
- Adicionada permissao/menu `reajustes_contratuais` para perfis financeiros autorizados.
- Destacados contratos `Sem base de comparacao` com 12 meses ou mais de vigencia como `Sem base - investigar`, incluindo tempo sem alteracao detectada.
- Comparacao de reajuste passou a priorizar o primeiro faturamento sincronizado do contrato contra o valor atual, identificando contratos sem reajuste detectado.
- Validados os totais atuais da tela: 204 contratos monitorados, 177 com base por primeiro faturamento, 56 com alteracao detectada, 70 sem reajuste detectado e 2 sem base.
- Testes automatizados ampliados para `48 passed`, cobrindo janelas de alerta, vencimento, historico insuficiente, alteracao de valor e deduplicacao.

## 2026-08-14 - Fechamento Tecnico Sprint 17

- Sprint 17 marcado como concluido tecnicamente apos validacao funcional assistida das 8 etapas solicitadas.
- Removido bloqueio redundante de perfil ADMIN nas rotas de `Retencao de Cache`, `Automacoes de Sincronismo` e `Backups do Sistema`, mantendo controle por permissoes `cache_sistema`, `sincronismos_agendados` e `backups_sistema`.
- Perfil Infraestrutura validado para acessar os modulos operacionais de configuracao conforme permissoes concedidas.
- Validacao tecnica final executada com `venv/bin/python -B -m pytest`, resultado `34 passed`, e compilacao Python dos arquivos alterados sem erro.
- Documentacao atualizada para indicar Sprint 17 encerrado e Sprint Final como proxima etapa de homologacao Beta; migrations `096`, `097`, `098` e `099` aplicadas/conferidas e registradas em `schema_migrations` em 14/08/2026.

## 2026-08-14 - Alertas Operacionais por E-mail

- Cadastro de usuario ganhou opcao para receber alertas de operacao por e-mail, com periodicidade diaria ou semanal e horario configuravel pelo Administrador.
- Criado servico `AlertasOperacaoService` para consolidar Zabbix critico aberto, backups PBS fora do prazo e diretorios TrueNAS sem modificacao ha mais de 5 dias.
- Adicionado comando CLI `flask operacao-alertas-enviar` e cron operacional a cada 15 minutos; o horario/periodicidade individual evita envios duplicados.
- Migration `098_auth_usuarios_alertas_operacao.sql` aplicada no banco local em 14/08/2026.
- Testes automatizados cobrem vencimento diario/semanal, envio com alerta e bloqueio de envio sem alertas.

## 2026-08-14 - Correção de Permissões Somente Leitura em Clientes e Contatos

- Perfis com acesso de leitura em `clientes` e `contatos` deixam de ver ações de criação, edição, sincronização e exclusão nas listas e telas de detalhe.
- Controle global de acesso negado passou a redirecionar para a primeira tela permitida do perfil, evitando loop quando o dashboard padrão também não está autorizado.
- Adicionado teste para garantir que perfil somente leitura acessa as listas, não acessa rotas de escrita e recebe fallback para `clientes.index`.

## 2026-08-14 - Ajuste de Mensagem do Convite de Acesso

- Fluxo de aceite de convite deixou de redirecionar para o token ja utilizado apos cadastro da senha.
- Tela `Convite de Acesso` agora exibe estado final de senha cadastrada com botao para login, evitando mensagem incoerente de convite expirado ou ja utilizado apos sucesso.
- Teste unitario cobre o retorno do convite aceito e a marcacao do convite como usado.

## 2026-08-14 - Melhoria Visual do E-mail 2FA

- `EmailService.enviar` passou a aceitar corpo HTML opcional mantendo texto simples como fallback.
- E-mail de 2FA por codigo passou a enviar HTML com o codigo centralizado, fonte maior, espacamento e bloco destacado para facilitar leitura pelo usuario.
- Teste de 2FA atualizado para validar que o codigo segue presente no texto simples e no corpo HTML.

## 2026-08-14 - Checklist de Fechamento Sprint 17

- Criado `docs/46-CHECKLIST-FECHAMENTO-SPRINT-17.md` com pendencias bloqueantes, validacoes funcionais, revisao de permissoes, qualidade tecnica e criterio de entrada no Sprint Final.
- Checklist registra que o Sprint Final deve congelar escopo funcional, aplicar migrations pendentes, validar dados reais controlados, registrar evidencias, fechar changelog e preparar branch/tag/release Beta.

## 2026-08-14 - TOTP para Autenticacao Remota

- Implementado TOTP como metodo de duplo fator para usuarios locais, reaproveitando `two_factor_metodo`, `two_factor_secret` e `two_factor_configurado_em` da migration `097_auth_2fa_email.sql`.
- `Minha Conta` passou a permitir iniciar configuracao TOTP, copiar chave manual/URI `otpauth://`, confirmar o primeiro codigo e desativar TOTP com codigo atual.
- Login `/login/2fa` passou a validar EMAIL ou TOTP conforme metodo do usuario; reenvio de codigo permanece restrito ao metodo EMAIL.
- Segredo TOTP e protegido pelo mecanismo de criptografia do Cofre de Senhas, e Administrador nao consegue selecionar TOTP para usuario que ainda nao concluiu a configuracao.
- Testes de 2FA ampliados para 23 cenarios, incluindo vetor RFC 6238, confirmacao, login TOTP e desativacao.

## 2026-08-14 - Documentacao de Acompanhamento Sprint 17

- Criado `docs/45-ACOMPANHAMENTO-SPRINT-17-2026-08-13.md` para registrar as etapas realizadas em 13/08/2026.
- Documento separa entregas consolidadas no commit `a06604b` das alteracoes ainda pendentes no workspace, como 2FA por e-mail, CPF unico e exclusao de colaboradores ASO.
- 2FA por e-mail revisado e aprovado para homologacao assistida, com testes unitarios em `tests/test_auth_2fa_email_service.py` cobrindo envio, hash, expiracao, tentativas, validacao e dispositivo confiavel.
- Evolucao TOTP foi registrada e implementada na entrada especifica de 14/08/2026 para autenticacao remota.
- `docs/05-SPRINT_ATUAL` e `docs/17-SPRINTS.md` passaram a referenciar o acompanhamento para orientar a continuidade e finalizacao do Sprint 17.

## 2026-08-13 - Ajustes Operacionais ASO, Premiações e Receita por Servidor

- Tela `Administrativo > Agendamento ASO` passou a permitir criar agendamento já no cadastro do colaborador, vinculando o compromisso à agenda do Gestor Administrativo.
- Agendamento ASO passou a aceitar compartilhamento com outro usuário que tenha agenda habilitada e lembretes por e-mail com 7, 15 ou 30 dias de antecedência.
- Campo `Exames realizados` no ASO recebeu seleção incremental de múltiplos arquivos, com lista dos nomes anexados abaixo do campo para reduzir ambiguidade operacional.
- Lista de Implantações e cards do Kanban de Implantação passaram a exibir CNPJ do cliente sem exigir abertura do detalhe.
- Cadastro de Parceiros recebeu flag `premiacao_ativa`, permitindo campanhas que premiam apenas Parceiro, apenas Executivo ou ambos.
- Tela `Financeiro > Premiações` passou a listar somente contratos com Parceiro ou Executivo habilitado para premiação e a considerar somente o primeiro título/parcela do contrato ativo.
- Cadastro e edição de Parceiros passaram a ocultar `Importar de Cliente` para perfis não Administrador.
- Tela de Executivos passou a permitir exclusão operacional para perfis Administrador e Diretoria, inativando o executivo e removendo o vínculo com o parceiro sem apagar histórico financeiro.
- Lista de Executivos passou a permitir alteração rápida do status de premiação (`Habilitada` / `Não habilitada`) sem abrir a edição completa.
- Criada tela `Financeiro > Receitas por Servidor`, calculando receita recorrente mensal por node Proxmox a partir dos ambientes e contratos ativos vinculados.
- Nova permissão/menu `receitas_servidor` adicionada ao grupo Financeiro.
- Migrations relacionadas: `092_add_premiacao_ativa_executivos.sql`, `093_create_administrativo_aso.sql`, `094_add_enviar_email_aso_lembretes.sql` e `095_add_premiacao_ativa_parceiros.sql`.

## 2026-08-12 - Sprint 17 Etapas 17.1 a 17.3

- Criada tela `Financeiro > Comissões` com consulta operacional de contratos ativos, campanhas, vigência, recebimentos OMIE elegíveis, comissão prevista e alerta vermelho para contratos com títulos atrasados.
- Tela `Financeiro > Comissões` recebeu botão de cálculo por contrato e nova tela de cálculo com campo livre `valor_manual_base`, aplicando o percentual executivo da campanha vinculada pela vigência.
- Adicionada permissão/menu `comissoes` pela migration `091_permissao_comissoes_sprint17.sql`, herdando acesso dos perfis que já visualizam `faturamento`.
- Tela de Faturamentos recebeu paginação dos Recebimentos OMIE e destaque vermelho para títulos `ATRASADO`; sincronização passou a buscar `PAGO` e `ATRASADO`.
- `Regras Campanhas` passou a exibir contratos ativos elegíveis pela data de início de vigência dentro do intervalo da campanha, com contagem na listagem e tabela no formulário.
- Tela de Faturamentos deixou de exibir importação CSV/modelo CSV, mantendo foco na consulta do cache de Recebimentos OMIE.
- Cache de Recebimentos OMIE passou a persistir somente títulos com contrato, cliente e nota fiscal vinculados; migration `090_limpar_recebimentos_omie_sem_vinculo_sprint17.sql` removeu 90 registros fora do escopo operacional.
- Visualização de Contratos passou a exibir a vigência sincronizada do OMIE (`inicio_vigencia` e `fim_vigencia`) para conferência de comissão.
- Sincronização de contratos OMIE passou a enviar `cExibeObs=S`, garantindo retorno de `observacoes.cObsContrato` para a observação de contrato que não sai na Nota Fiscal.
- Recebimentos OMIE ficaram em cache local na tabela `financeiro_recebimentos`, consultados pela tela de Faturamentos sem chamada direta ao OMIE.
- Criado sincronismo separado `OMIE_RECEBIMENTOS`, inativo por padrão, disponível em Configurações > Automações de Sincronismo para execução manual ou agendada.
- Tela `Financeiro > Faturamentos` recebeu ação manual `Sincronizar OMIE` para atualizar o cache de Contas a Receber sob demanda.
- Documentada a descoberta OMIE inicial em `docs/44-DESCOBERTA-OMIE-SPRINT-17.md`, incluindo contratos, vendedores, projetos e Contas a Receber.
- Criada e aplicada no banco local a migration `087_expandir_contratos_comissoes_sprint17.sql` para campos comerciais de contratos.
- Sincronizacao de contratos OMIE passou a resolver `vendedor_nome` e `projeto_nome` com cache por execucao, evitando chamadas repetidas por contrato.
- Contratos OMIE passaram a persistir `observacao_contrato`, `valor_servicos_bruto`, `valor_descontos` e `valor_servicos_liquido`.
- Sincronizacao completa atualizou 210 contratos OMIE com os novos campos comerciais.
- Detalhe de Contratos passou a exibir `Informações Comerciais` e desconto dos itens.
- Criada e aplicada no banco local a migration `088_create_financeiro_recebimentos_sprint17.sql` para recebimentos OMIE.
- Implementada sincronizacao de recebimentos com idempotencia por `codigo_lancamento_omie`, vinculo por cliente OMIE + numero do contrato e exclusao de categorias SETUP/IMPLANTACAO.
- Carga inicial de recebimentos persistiu 595 titulos na janela de 90 dias, com 505 vinculados a contratos e 89 categorias excluidas de comissao.
- Tela `Financeiro > Faturamentos` passou a exibir os recebimentos OMIE sincronizados, com filtros por texto, periodo, vinculo de contrato e categoria elegivel/excluida.

## 2026-08-12 - Fechamento Sprint 21 e Retomada Sprint 17

- Sprint 21 registrada como concluida tecnicamente em `docs/43-FECHAMENTO-SPRINT-21.md`, com backup, restore, servico systemd, versionamento e atualizacoes controladas encaminhados para homologacao Beta.
- `docs/05-SPRINT_ATUAL` passou a registrar o Sprint 17 como sprint retomada para desenvolvimento.
- `docs/00-VISAO-GERAL.md` e `docs/ROADMAP.md` atualizados para refletir Sprint 21 como ultima sprint encerrada e Sprint 17 como frente atual.
- Sprint 17 ajustada para reaproveitar a tela existente de `Regras Campanhas`, exibindo dentro de cada campanha os contratos ativos com inicio de vigencia dentro do intervalo da campanha.
- Definido que, quando nao houver campanha cadastrada, a visualizacao geral nao deve aplicar filtro por campanha.
- Iniciada implementação do Sprint 21 com módulo administrativo de Backups do Sistema: migration 083_create_config_backups.sql, tela em Configurações, serviço de geração de backup banco/storage/completo, comando CLI agendado e cron operacional.
- Aberto planejamento da Sprint 21 - Release Beta, Backup e Atualizacoes, documentando arquitetura Beta, estrategia de branches/releases, backup/restore e atualizacoes do sistema.
- Criados `docs/39-SPRINT-21-RELEASE-BETA.md`, `docs/40-ARQUITETURA-BETA.md`, `docs/41-BACKUP-RESTORE.md` e `docs/42-ATUALIZACOES-SISTEMA.md`.
- Adicionado entrypoint `wsgi.py`, unit file `deployment/o3cloud-manager.service` e script `deployment/install-systemd-service.sh` para executar o O3Cloud Manager via systemd/gunicorn como usuário `o3cloud`, sem `python app.py` em debug.
- Documentada a operação do daemon em `docs/38-SERVICO-SYSTEMD.md`, incluindo validação, logs e regra para não iniciar a aplicação como `root`.

## 2026-08-10 - Visao Geral Operacional e Estrutura Sprint 17

- Tela `Visao Geral` ampliada com blocos de maiores contratos, clientes inadimplentes, demandas administrativas, propostas recentes, ClickSign pendente, alertas Zabbix, consumo/alocacao Proxmox, backups PBS/TrueNAS e movimentacoes do Kanban de Implantacao.
- Incluidas as ultimas 5 atualizacoes dos cards Kanban e os ultimos 5 projetos que entraram na fila.
- `FinanceiroRepository.dashboard_executivo()` passou a entregar o agrupamento `visao_geral` para alimentar o painel principal com dados reais dos modulos.
- Sprint 17 mantido como etapa pendente de estruturacao antes do Sprint Final de homologacao Beta.

## 2026-08-10 - Fechamento Tecnico Sprint 20

- Cofre de Senhas passou a vincular credenciais a implantadores cadastrados, e Implantacao passou a selecionar Responsavel/Implantador pelo cadastro oficial de implantadores.
- Sprint 20 registrada como concluida tecnicamente em `docs/37-FECHAMENTO-SPRINT-20.md`.
- Atualizados `docs/00-VISAO-GERAL.md` e `docs/05-SPRINT_ATUAL` para refletir Relatorios Customizaveis como ultima sprint encerrada.
- Tela `Visao Geral` atualizada para exibir fechamento do Sprint 20 e pendencias do Sprint Final.
- Atualizados DER e modelo fisico com tabelas de relatorios, jobs, retencao de cache e sincronismos agendados.

## 2026-08-10 - Implementacao inicial Sprint 20 Relatorios Customizaveis

- Criado modulo `Relatorios` com fontes autorizadas, catalogo de campos, construtor sem SQL livre, filtros, ordenacao, agrupamentos e agregacoes seguras.
- Migration `077_create_relatorios_customizaveis.sql` aplicada no banco local em 10/08/2026.
- Adicionados modelos salvos com visibilidade PRIVADO, PERFIL e GLOBAL, auditoria de execucao e controle por permissao `relatorios`.
- Incluidas exportacoes CSV, XLSX, DOCX, PDF e impressao HTML com identificacao O3Cloud.
- Construtor passou a respeitar ordem explicita das colunas e formatar valores na visualizacao HTML.
- Adicionadas protecoes de carga com previa limitada, exportacao direta controlada e exigencia de periodo para fontes grandes.
- Criada fila de relatorios em segundo plano pela migration `078_create_relatorios_jobs.sql`, com arquivo em `storage/relatorios`, link de download e tentativa de envio por e-mail ao usuario logado.
- Adicionado comando CLI `flask relatorios-processar-jobs` para processar jobs pendentes fora da request HTTP.
- Incluidas fontes de infraestrutura no catalogo de relatorios usando cache local: Alarmes Zabbix, Backups PBS, Backups TrueNAS, VMs/Containers Proxmox e Nodes Proxmox.
- Criada tela administrativa Configuracoes > Retencao de Cache com politicas de 30 a 365 dias, limpeza por retencao, limpeza total e historico de execucoes.
- Migration `079_create_config_cache_retencao.sql` aplicada no banco local em 10/08/2026.
- Criada tela administrativa Configuracoes > Automacoes de Sincronismo para agendar Omie, Zabbix, Proxmox, ClickSign, PBS e TrueNAS por periodicidade configuravel.
- Adicionado comando CLI `flask sincronismos-processar-agendados` e migration `080_create_config_sincronismos_agendados.sql`, aplicada no banco local em 10/08/2026.
- Eventos de Leads passam a permitir cadastro manual de participantes por permissao `eventos_participante_manual`, liberada por padrao ao perfil ADMIN pela migration `081_permissao_eventos_participante_manual.sql`.

## 2026-08-10 - Planejamento Sprint 20 Relatórios Customizáveis

- Documentado escopo do módulo de Relatórios Customizáveis com fontes autorizadas, catálogo de campos, filtros, agrupamentos, cálculos, exportações, auditoria e segurança sem SQL livre.
- Definido cabeçalho padrão obrigatório com logo da O3Cloud nos relatórios HTML/impressão, PDF, DOCX e XLSX quando suportado; CSV deve usar identificação textual.
- Confirmados `python-docx==1.2.0` para DOCX e `reportlab==5.0.0` para PDF nas exportações do Sprint 20.

## 2026-08-10 - Sprint 19 Inadimplência Financeira

- Adicionada migration `076_create_financeiro_inadimplencias.sql` para controle histórico de pendências financeiras por contrato.
- Criadas telas Financeiro > Inadimplentes para registrar, consultar e liberar pendências financeiras, com busca de contrato por número, cliente, razão social ou CNPJ.
- Criada regra central `InadimplenciaService.validar_operacao_cliente` para bloquear novas propostas e novas implantações de clientes inadimplentes.
- Clientes, Propostas e Implantação passam a exibir destaque visual de pendência financeira ativa.
- CNPJ passa a ser exibido no padrão `00.000.000/0000-00` nos cadastros e buscas de Clientes, Parceiros, Contratos, Propostas, Financeiro e Implantação aceitam CNPJ com ou sem máscara.
- Notificações de bloqueio/liberação foram integradas ao serviço de e-mail existente, com falha de envio registrada sem rollback da pendência.
- E-mail enviado ao cliente por bloqueio financeiro passou a incluir razão social, CNPJ do contrato bloqueado, telefone `19 3142-0232 opção 3`, WhatsApp `19 99912-4028` e e-mail `contas@o3cloud.com.br` para regularização.
- E-mails internos enviados ao SAC e plantão técnico por bloqueio/liberação financeira passaram a incluir razão social e CNPJ para facilitar localização do cliente.
- E-mail de liberação financeira enviado ao cliente também passou a incluir razão social e CNPJ do contrato liberado.
- Login ADMIN passou a poder remover histórico de inadimplência da lista por inativação lógica, útil para ciclos de teste sem liberar essa ação a outros perfis.

## 2026-08-07 - Atualizacao Final Sprint 18

### Governanca de Acesso

- Administradores passam a remover usuarios de acesso ao sistema pela tela `Configuracoes > Usuarios e Acessos`.
- A remocao possui bloqueio no backend para perfis nao ADMIN, impede autoexclusao e impede remover o ultimo Administrador ativo.
- A acao registra auditoria `USUARIO_REMOVIDO` e remove foto de usuario armazenada quando aplicavel.
- Controle global de acoes destrutivas foi reforcado para ocultar/bloquear exclusoes, desativacoes, inativacoes e remocoes para perfis sem permissao global.

### Operacao e Observabilidade

- Criada configuracao de logs backend em JSON, com logs de acesso, aplicacao, erros, banco, integracoes, seguranca e jobs em `/opt/o3cloud-manager/logs`.
- Adicionado `docs/36-LOGS-BACKEND.md` com localizacao, seguranca, rotacao e eventos cobertos.
- Ajustado `.gitignore` para manter arquivos `.log` fora do Git e preservar a estrutura operacional da pasta de logs.

### Cadastros, Propostas e Usabilidade

- Clientes passaram a normalizar CNPJ alfanumerico e validar duplicidade antes de criacao ou edicao, com migrations `073_normalizar_cnpj_clientes.sql` e `074_unique_cnpj_clientes.sql`.
- Propostas receberam busca rapida de cliente, valor unitario ajustavel por licenca dentro da faixa minimo/tabela, e setup/parametrizacao calculados a partir da primeira mensalidade.
- Impressao/visualizacao de proposta foi refinada para separar condicoes comerciais, totalizacao de setup e layout de impressao.
- Cofre de Senhas recebeu pesquisa de credenciais por cliente, CNPJ, titulo, usuario, host ou URL.
- Cofre de Senhas e Base de Conhecimento receberam vinculo opcional com ambientes via migration `075_vincular_ambiente_cofre_conhecimento.sql`, registrada no banco local em 10/08/2026.
- Sidebar passou a preservar posicao de rolagem entre navegacoes e templates de Contatos, Leads e Oportunidades tiveram correcao de extensao Jinja.

## 2026-08-06 - Consolidacao Sprint 18

- Modulo Administrativo concluido tecnicamente com demandas, agenda corporativa e individual, comentarios, historico, anexos, notificacoes, alertas, dashboard, relatorios e auditoria.
- Perfis `Administrativo Gestor` e `Administrativo Colaborador` adicionados para separar gestao de demandas e execucao operacional.
- Agenda administrativa evoluida com visualizacoes Hoje, Semana, Mes, Lista, formato calendario e recorrencias diaria, semanal, mensal e anual.
- Dashboard principal por perfil foi adicionado em Usuarios e Acessos; login passou a direcionar o usuario para o dashboard permitido pelo perfil, com suporte ao perfil SUPORTE iniciar no Monitoramento Zabbix.
- Fechamento tecnico registrado em `docs/35-FECHAMENTO-SPRINT-18.md`, mantendo validacoes assistidas e homologacao Beta como pendencias controladas.


## 2026-08-06 - Agenda e Recorrencia

- Usuários de outros perfis com `Possui Agenda = SIM` passam a entrar em Minha Agenda quando recebem acesso ao módulo Administrativo.
- Agenda Corporativa ganhou o botão explícito `Formato calendário` para gestores, Diretoria e Administradores.

- Colaboradores passam a entrar diretamente em Minha Agenda; a Agenda Corporativa fica restrita a gestores administrativos, Diretoria e Administradores.

- Agenda recebeu botao Voltar, visualizacao em lista e calendario semanal de segunda a sexta.
- Demandas podem gerar ocorrencias recorrentes diarias, semanais, mensais ou anuais com data final configurada pelo gestor.


## 2026-08-06 - Perfis Administrativos

- Criados os perfis `Administrativo Gestor` e `Administrativo Colaborador` na migration `069_create_perfis_administrativo.sql`.
- Colaboradores visualizam apenas suas demandas e podem comentar nelas, enquanto criação, edição, cancelamento, reagendamento e moderação ficam restritos ao gestor.


## 2026-08-06 - Sprint 18 Etapa 7

### Fechamento Tecnico

- Sprint 18 registrada como concluida tecnicamente, com as validacoes assistidas das etapas 1 a 7 encaminhadas para a release Beta.
- Criado `docs/35-FECHAMENTO-SPRINT-18.md` com entregas, validacoes e pendencias de homologacao.
- Sprint 17 permanece fora do fechamento ate o alinhamento com as equipes Comercial e Financeiro.

## 2026-08-06 - Sprint 18 Etapa 6

### Alertas e Auditoria

- Alerta amarelo global informa demandas vencidas do colaborador e direciona para a lista administrativa.
- Leituras individuais e em lote de notificacoes passam a ser registradas na auditoria centralizada.
- Eventos administrativos continuam sujeitos a sanitizacao de dados sensiveis e ao registro de IP e user agent.


## 2026-08-06 - Sprint 18 Etapa 5

### Dashboard e Relatorios

- Dashboard Administrativo passou a apresentar agenda do dia e da semana, urgencias, pendencias, tempo medio e ranking de produtividade.
- Relatorios passaram a permitir filtro por periodo e agrupamento por responsavel e departamento.


## 2026-08-06 - Sprint 18 Etapa 4

### Notificacoes

- Central de notificacoes recebeu marcacao individual e em lote como lida, contador visual e acesso direto a demanda.
- Alteracoes de prazo e novos comentarios notificam o responsavel na tela e por e-mail quando o SMTP esta configurado.
- Operacoes de leitura de notificacoes passaram a respeitar a permissao de edicao do grupo Administrativo.


## 2026-08-06 - Sprint 18 Etapa 3

### Comentarios, Historico e Anexos

- Comentarios administrativos agora podem ser editados pelo autor ou moderados por gestores, diretoria e administradores.
- Inativacao de comentarios preserva o historico da acao e remove o item da conversa ativa.
- Anexos enviados na criacao e edicao passam a atualizar corretamente o indicador da demanda.


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

## 2026-08-28 - Adendos contratuais

- Documentada a regra de adendos vinculados ao contrato principal, sem criação de implantação e sem setup, com edição dos dados comerciais do adendo.
- Preparado cadastro de adendos com anexos PDF e lançamento manual de premiação financeira para upgrade/usuários adicionais, calculando parceiro e executivo pelas regras de campanha usadas na apuração automática e somando adendos aos totais filtrados por campanha.
- Publicada a tag `v0.9.0-beta.2` com a integração de GitHub Releases; verificação real encontrou 2 tags remotas e 0 releases publicadas no GitHub.
- Tela de Atualizações passou a consultar GitHub Releases pela API pública, com `GITHUB_TOKEN` opcional, exibindo repositório GitHub, total de releases, release recomendada e changelog resumido quando publicado.
- Publicada a tag `v0.9.0-beta.1` no remoto e validada a detecção pela tela de Atualizações do Sistema com 1 tag remota encontrada.
- Adicionado botão `Verificar atualizações` em modo somente leitura, com histórico em `config_atualizacoes_verificacoes`, parsing de tags remotas e release recomendada sem executar instalação.
- Criada tela `Configurações > Atualizações do Sistema` para a Sprint 21 em modo somente leitura, exibindo branch, commit, tags, remoto, upstream, alterações locais e plano de atualização controlada; adicionada migration `084_permissao_atualizacoes_sistema.sql`.
- Criados `deployment/restore-db.sh` e `deployment/healthcheck.sh` para a Sprint 21, com restore SQL operacional a partir do artefato de backup e validação de serviço, banco e HTTP. Teste de escrita em MOUNT/NAS ficou postergado para a Beta até criação do diretório no NAS.

## 2026-08-06 - Sprint 18 Etapa 2

### Agenda

- Agenda Administrativa passou a oferecer visoes Hoje, Semana, Mes e Lista.
- Adicionados filtros por periodo e responsavel, regras de visibilidade e reagendamento rapido.

## 2026-08-06 - Inicio da Implementacao do Sprint 18

### Modulo Administrativo

- Criada a fundacao do modulo Administrativo com demandas, agenda, comentarios, historico, anexos, notificacoes e relatorios.
- Adicionado o grupo Administrativo ao controle de acessos e ao menu lateral.
- Notificacoes visuais e por e-mail foram preparadas para o responsavel da demanda.
- Testes e homologacao encaminhados para `docs/34-PENDENCIAS-TESTES-BETA-SPRINT-18.md`.

## 2026-08-06 - Visao Geral e Proxima Sprint

### Dashboard

- Visao Geral passou a exibir a Sprint 16 como concluida tecnicamente.
- Pendencias de testes assistidos foram indicadas como encaminhadas para a release Beta.
- Dashboard passou a apresentar a proxima sprint de integracao cadastral por CNPJ e suas etapas previstas.

## 2026-08-06 - Fechamento Tecnico Sprint 16

### Documentacao

- Sprint 16 concluida tecnicamente, com entregas de governanca, acessos, auditoria e operacao assistida consolidadas.
- Pendencias de testes assistidos das etapas 1 a 7 encaminhadas para a release Beta em `docs/32-PENDENCIAS-TESTES-BETA-SPRINT-16.md`.
- Criado `docs/33-FECHAMENTO-SPRINT-16.md` com entregas, validacoes e decisao de fechamento.

## 2026-08-05 - Governanca, Integracoes e Refinamentos Sprint 16

### Governanca

- Implementado login global com sessao e protecao gradual de rotas por permissao.
- Criada matriz de permissoes por menu com nivel de acesso de visualizacao ou edicao.
- Adicionado controle de exibicao de valores por perfil e foto de usuario.
- Auditoria operacional expandida com IP, user agent e sanitizacao de dados sensiveis.

### CRM e Comercial

- Propostas receberam comentarios internos com compartilhamento por e-mail.
- Criado modulo de regras de campanhas e comissao com vigencia e validacao de sobreposicao.
- Eventos CRM passaram a registrar disparos de e-mail para participantes.

### Operacoes e Integracoes

- Cofre de Senhas recebeu compartilhamento temporario por token e vinculos com inventarios Proxmox, PBS e Zabbix.
- Servicos de e-mail passaram a suportar provedor Brevo alem de SMTP.
- Parceiros receberam categoria comercial e catalogo tecnico recebeu dimensionamento de hardware por parceiro.

Registro detalhado: docs/31-ENTREGAS-GOVERNANCA-INTEGRACOES-SPRINT-16.md

## 2026-08-05 - Eventos CRM e Base de Conhecimento Sprint 16

### CRM

- Criado o fluxo de eventos com criação, edição e importação de participantes por evento.
- Adicionado importador CSV, XLS e XLSX com mapeamento automático/manual, validação e deduplicação.
- Adicionado atalho para criar nova oportunidade a partir de participante importado.
- Criadas as tabelas da migration 063.

### Base de Conhecimento

- Criadas bases independentes, pastas, subpastas, conhecimentos e anexos.
- Adicionado editor de texto livre, tags, catálogo, compartilhamento e imagens em conhecimentos salvos.
- Arquivos armazenados em /opt/o3cloud-manager/storage/conhecimentos.
- Criadas as tabelas da migration 064.
- Módulo incluído em Operações com permissão base_conhecimento.

Registro detalhado: docs/30-ENTREGAS-OPERACIONAIS-SPRINT-16.md

## 2026-08-04 - Mapeamento de Grupos Externos Sprint 16

### Adicionado
- Criada migration `060_create_auth_grupo_perfil_mapas.sql` para mapear grupos FreeIPA/LDAP/AD para perfis internos.
- Adicionadas rotas e tela em Configuracoes > Usuarios e Acessos para cadastrar, editar e inativar mapeamentos de grupos externos.
- Mapeamentos passam a gerar auditoria administrativa basica.

Todas as mudanças importantes deste projeto serão registradas neste documento.

O formato é baseado no Keep a Changelog e adaptado às necessidades do O3Cloud Manager.

---




## 2026-08-03 - Usuarios e Acessos Sprint 16

### Configuracoes

- Criada base inicial de Usuarios e Acessos em Configuracoes.
- Adicionada migration `050_create_auth_usuarios_acessos.sql` com perfis, usuarios, convites, provedores e auditoria.
- Implementado cadastro/edicao de usuarios locais e externos com origem Local, FreeIPA, LDAP ou Active Directory.
- Implementado convite por e-mail para usuario local cadastrar senha propria.
- Implementado cadastro de provedores FreeIPA, LDAP e Active Directory com teste de comunicacao.
- Adicionado atalho `Usuarios e Acessos` no menu Configuracoes.

## 2026-08-03 - Escopo de Autenticacao Sprint 16

### Documentacao

- Criado `docs/28-AUTENTICACAO-USUARIOS-SPRINT-16.md` com o desenho inicial de Usuarios e Acessos.
- Definido que Configuracoes deve ter tela para gerenciamento de usuarios, perfis, convites e provedores externos.
- Registradas regras para usuario local convidado por e-mail, sincronismo FreeIPA, configuracao LDAP e autenticacao Active Directory.
- Atualizados requisitos funcionais, modelo de permissoes, roadmap e documentos da Sprint 16.

## 2026-08-03 - Abertura Sprint 16

### Documentacao

- Criado `docs/27-ABERTURA-SPRINT-16.md` para registrar a Sprint 16 como aberta.
- `docs/05-SPRINT_ATUAL` passou a apontar a Sprint 16 como sprint atual.
- `docs/17-SPRINTS.md`, `docs/ROADMAP.md` e `docs/00-VISAO-GERAL.md` foram atualizados com o escopo inicial candidato.
- Sprint 16 registrada com foco em governanca, acessos, auditoria operacional, validacao assistida da Beta e refinamentos priorizados.

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
- Kanban de Implantacao envia e-mail para faturamento@o3cloud.com.br quando um card e movido para Finalizado, informando conclusao e liberacao para faturamento.
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

## 2026-08-06

- Adicionado Dashboard principal configurável por perfil de acesso, com redirecionamento seguro no login e fallback conforme permissões.

- Perfil SUPORTE configurado para iniciar no Monitoramento Zabbix.

- Cadastro manual de clientes bloqueia CNPJ duplicado, com normalizacao de pontuacao.
- Sincronizacao OMIE prioriza registros OMIE por CNPJ, codigo externo e contratos manuais correspondentes.

## 2026-08-26

- Cofre de Senhas passou a permitir anexos em credenciais e exibicao dos arquivos vinculados na edicao.
- Cofre de Senhas preserva a pasta selecionada ao retornar do cadastro de nova credencial.
- Campo Cliente do Cofre de Senhas passou a usar busca digitavel por nome, razao social e CNPJ.
- Checklist Tecnico da implantacao passou a permitir selecao de varios itens e salvamento em lote.
- Telas operacionais com listas extensas preservam a posicao de rolagem ao selecionar ou desselecionar itens.
- Comentarios de implantacao passam a registrar como autor o usuario logado, nao o responsavel da implantacao.
- Licencas O3Web passaram a usar selecao pesquisavel de cliente no cadastro.
- Faixas de Rede passaram a aceitar ranges adicionais de portas, com validacao de sobreposicao e conflito por FW - WAN.
- Documentacao detalhada adicionada em `docs/52-MELHORIAS-BETA-2026-08-26.md`.

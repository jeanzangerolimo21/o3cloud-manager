# Melhorias Pre-Sprint 16

Versao: 3.0 Alpha

Data de registro: 03/08/2026

Status: Registrado antes da abertura da Sprint 16

---

# Contexto

A Sprint 15 foi concluida tecnicamente em 03/08/2026 com foco em infraestrutura operacional read-only.

Apos o fechamento, foram aplicados refinamentos comerciais e operacionais solicitados para estabilizar o fluxo de propostas, ClickSign, pipeline, cofre de senhas e rastreabilidade antes da abertura formal da Sprint 16.

Este documento registra esses ajustes como pacote pre-Sprint 16, sem reabrir o escopo da Sprint 15.

---

# Melhorias Entregues

## 1. Propostas e ClickSign

Status: concluido

Entregas:

- Proposta passou a permitir selecionar explicitamente o contato do tipo Representante Legal.
- Campo `representante_legal_id` foi adicionado em `crm_propostas`.
- Tela de proposta ganhou atalho `+` para cadastrar contato de Representante Legal quando ele nao existir.
- Cadastro de contato pode abrir ja sugerindo o tipo Representante Legal quando acessado pelo atalho da proposta.
- Envio para ClickSign passou a usar o Representante Legal selecionado, nao mais heuristica baseada apenas no nome da empresa.
- Representante Legal passou a exigir nome completo e CPF valido antes do envio para ClickSign.
- Mensagens de erro do envio para ClickSign ficaram mais explicitas para nome incompleto, nome invalido e CPF ausente.
- Reenvio para ClickSign passou a ser bloqueado quando a proposta ja possui envelope enviado.
- Tela de proposta passou a orientar cancelamento da proposta atual e geracao de nova proposta quando houver alteracoes apos envio.
- Cancelamento de proposta em status comercial cancelado/rejeitado/expirado passa a cancelar envelope pendente na API ClickSign.
- Fluxo ClickSign passou a reconhecer status `CANCELADO`.
- Tela de propostas aprovada exibe acao para gerar documento de contrato.
- Acao Enviar para ClickSign na listagem aparece apenas quando o documento ja foi gerado e ainda nao existe envelope.
- Geracao de novo documento fica bloqueada quando a proposta ja esta `ASSINADO` ou `CONCLUIDO` no fluxo ClickSign.

## 2. Propostas Comerciais e PDF

Status: concluido

Entregas:

- PDF da proposta recebeu maior espacamento entre blocos de setup, mensalidade e informacoes complementares.
- Rodape da proposta passou a centralizar `O3 CLOUD SOLUCOES EM TECNOLOGIA LTDA` em caixa alta.
- Informacoes complementares cadastradas na proposta passaram a aparecer no PDF.
- Tela de proposta ganhou atalho `+` ao lado da selecao de cliente para cadastro rapido de novo cliente.
- Cadastro de cliente passou a buscar dados publicos por CNPJ para agilizar a criacao de propostas.

## 3. Pipeline Comercial e Dashboard

Status: concluido

Entregas:

- Pipeline comercial passou a buscar propostas sem origem em leads/oportunidades.
- Propostas passaram a permitir alteracao de status diretamente na tela de listagem, sem abrir edicao completa.
- Tela de proposta passou a exibir comentarios comerciais internos.
- Propostas passaram a registrar semaforo de fechamento: frio, morno e quente.
- Dashboard comercial deixou de exibir botao Nova Proposta.
- Origem comercial de propostas salvas passou a exibir nome do cliente para facilitar identificacao.

## 4. Contratos e Rastreabilidade

Status: concluido

Entregas:

- Criacao de novo contrato deixou de exigir upload de PDF manual.
- Propostas fechadas/aprovadas passaram a exibir atalho para gerar contrato.
- Geracao de contrato passou a validar dados incompletos e orientar ajuste do cliente quando necessario.
- Rastreabilidade Comercial -> Implantacao passou a exibir cliente alem do numero da proposta.
- Texto de diagnostico pre-Beta foi removido da tela de Rastreabilidade Comercial -> Implantacao.

## 5. Cofre de Senhas

Status: concluido

Entregas:

- Criacao de credencial no Cofre de Senhas deixou de exigir faixa de rede.
- Cofre passou a permitir pastas particulares do usuario.
- Pastas particulares podem ser compartilhadas opcionalmente com usuarios selecionados.
- Selecao de compartilhamento usa usuarios cadastrados no sistema.

## 6. Configuracoes e Interface

Status: concluido

Entregas:

- Menu Configuracoes voltou a exibir Integracoes Tecnicas, preservando a remocao apenas dos atalhos nas telas operacionais.
- Sidebar recebeu rolagem interna propria para acessar opcoes inferiores sem mover a area de conteudo.
- Cabecalho do sidebar foi compactado para ampliar a area util de rolagem do menu.
- Configuracao SMTP com naoresponda@o3cloud.com.br foi validada no cadastro de Servicos de Email.
- Automacoes de email de implantacao foram validadas por simulacao: movimento de Kanban, comentario com envio marcado e notificacao ao financeiro quando a implantacao e finalizada.

---

# Migrations Relacionadas

- `database/migrations/047_expandir_propostas_pipeline_comercial.sql`
- `database/migrations/048_permitir_cofre_senha_sem_faixa_rede.sql`
- `database/migrations/049_adicionar_representante_legal_propostas.sql`

---

# Validacoes Registradas

- Rotas principais de propostas renderizadas com HTTP 200 via Flask test client.
- Tela de nova proposta renderizada com HTTP 200.
- Tela de visualizacao/edicao de proposta real renderizada com HTTP 200.
- Tela de novo contato com tipo Representante Legal renderizada com HTTP 200.
- Validacoes de servico simuladas para bloqueio de reenvio, cancelamento ClickSign, nome completo e CPF do representante legal.
- `AST OK` nos modulos Python alterados.
- `git diff --check` sem erros.

---

# Encaminhamento

Estas melhorias ficam registradas como pacote estabilizador antes da Sprint 16.

A Sprint 16 deve ser aberta separadamente, com escopo definido pela equipe e sem reaproveitar pendencias ja fechadas neste pacote.

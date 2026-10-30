# Estrategia de integracao do O3Cloud Central ao O3Cloud Manager

## 1. Estado da decisao

O prototipo O3Cloud Central comprovou a viabilidade tecnica e funcional do
acesso controlado a servicos dos clientes por meio de pfSense e agentes de
terminal.

O prototipo ainda nao esta em producao. Portanto, a implementacao definitiva
sera incorporada ao O3Cloud Manager sem obrigacao de preservar banco, usuarios,
URLs, agentes, certificados ou compatibilidade operacional com a instancia de
teste.

O codigo existente em `/home/o3cloud/o3cloudcentral-main/` sera utilizado como
referencia e fonte de componentes de dominio, validacao, criptografia, politica,
artefatos e testes. A aplicacao FastAPI independente nao sera simplesmente
embutida no processo Flask.

## 2. Objetivo

Criar, dentro do menu **Operacoes** do O3Cloud Manager, um modulo nativo para:

- vincular gateways pfSense aos clientes e ambientes existentes;
- selecionar VMs ja sincronizadas do Proxmox como origem de servicos;
- cadastrar servicos manuais quando o recurso nao estiver no Proxmox;
- definir quais terminais podem acessar cada servico;
- gerar instaladores e comandos controlados;
- receber estado e telemetria dos gateways e terminais;
- revogar acessos;
- auditar todas as operacoes administrativas;
- reutilizar autenticacao, 2FA, perfis, permissoes, layout e seguranca do
  O3Cloud Manager.

## 3. Principios arquiteturais

1. **Modulo nativo do Manager:** interface, rotas administrativas, permissoes e
   auditoria seguem os padroes Flask existentes.
2. **Uma fonte de verdade para clientes:** o modulo referencia o cadastro atual
   de clientes; nao cria um segundo cadastro paralelo.
3. **Uma fonte de verdade para infraestrutura:** VMs conhecidas devem ser
   selecionadas do inventario Proxmox sincronizado.
4. **Cadastro manual permitido:** equipamentos e servicos que nao pertencem ao
   Proxmox continuam suportados.
5. **Banco relacional:** dados operacionais ficam em tabelas normalizadas e nao
   em um documento JSON agregado.
6. **Segredos nao reversiveis:** tokens de autenticacao sao armazenados somente
   como hash sempre que o protocolo permitir.
7. **Menor privilegio:** consulta, edicao, geracao de acesso e revogacao podem
   ter autorizacoes distintas.
8. **Processos periodicos fora do Gunicorn:** monitoramento e manutencao nao
   executam em loops dentro dos workers web.
9. **APIs de maquina separadas:** endpoints de pfSense e agentes nao dependem de
   sessao de navegador.
10. **Implementacao incremental:** primeiro a administracao e o modelo; depois
    gateways, terminais, instaladores e automacao.

## 4. Arquitetura-alvo

```text
Administrador / Operador
          |
          v
O3Cloud Manager - Flask/Gunicorn
          |
          +-- Clientes, contratos e ambientes existentes
          +-- Inventario Proxmox sincronizado
          +-- Modulo Operacoes > O3Cloud Central
          +-- Auditoria, RBAC, 2FA e storage protegido
          |
          +-- API de gateway <---------- pfSense do cliente
          |
          +-- API de agentes <---------- Windows / Linux via pfSense
          |
          +-- Jobs periodicos ---------- cron/systemd/sincronismos
          |
          v
MariaDB do O3Cloud Manager
```

O trafego de tunel permanece entre terminal e pfSense. O Manager atua como
plano de administracao, distribuicao de politica, emissao de cadastros e coleta
de telemetria.

## 5. Organizacao do codigo

Estrutura aprovada:

```text
app/o3central/
|-- __init__.py
|-- routes.py
|-- service.py
|-- gateway_service.py
|-- device_service.py
|-- artifact_service.py
|-- policy_service.py
|-- crypto.py
|-- validators.py
`-- jobs.py

app/repositories/
|-- o3central_gateway_repository.py
|-- o3central_network_repository.py
|-- o3central_service_repository.py
|-- o3central_device_repository.py
|-- o3central_grant_repository.py
|-- o3central_ticket_repository.py
`-- o3central_report_repository.py

app/templates/o3central/
|-- index.html
|-- gateway_form.html
|-- gateway_detail.html
|-- service_form.html
|-- devices.html
`-- device_detail.html
```

Responsabilidades:

- `routes.py`: HTTP, formulario, CSRF, redirect e respostas JSON.
- services: regra de negocio, autorizacao contextual e transacoes compostas.
- repositories: SQL parametrizado e persistencia.
- `crypto.py`: hash, comparacao constante, chaves e tokens.
- `validators.py`: IP, CIDR, endpoint, porta, hostname e selecao de servicos.
- `policy_service.py`: cria o snapshot de politica entregue ao gateway.
- `artifact_service.py`: comandos, tickets e downloads autorizados.
- `jobs.py`: expiracao de tickets, limpeza e verificacao de estado.

## 6. Funcionalidades administrativas

### 6.1 Dashboard

- quantidade de clientes habilitados;
- gateways online, offline e nunca conectados;
- terminais ativos, offline e revogados;
- servicos publicados;
- tickets de instalacao ativos e expirados;
- alertas de versao, comunicacao e configuracao;
- filtros por cliente, ambiente e status.

### 6.2 Gateways

- cliente obrigatorio;
- ambiente opcional;
- nome do gateway;
- endpoint publico usado pelos terminais;
- endereco e porta de escuta no pfSense;
- URL do portal, se aplicavel;
- redes internas autorizadas;
- estado, versao, ultima comunicacao e diagnostico;
- geracao, rotacao e revogacao do cadastro;
- comando de instalacao exibido apenas a usuario autorizado.

Um cliente pode ter varios gateways. Um gateway pertence a exatamente um
cliente, evitando cruzamento de servicos entre clientes.

### 6.3 Servicos

O cadastro oferece duas origens:

1. **VM Proxmox:** usuario escolhe cliente, ambiente e VM sincronizada; nome e
   enderecos conhecidos sao sugeridos.
2. **Manual:** usuario informa nome, IP, porta, protocolo e tipo para NAS,
   firewall, switch, banco, equipamento fisico ou aplicacao externa ao Proxmox.

Regras:

- destino deve pertencer a uma rede autorizada do gateway;
- portas devem estar entre 1 e 65535;
- a porta local nao pode colidir dentro da mesma selecao de terminal;
- um recurso do Proxmox nao pode ser selecionado fora do cliente/ambiente ao
  qual esta vinculado;
- alteracoes que invalidem acessos ativos exigem confirmacao e auditoria.

### 6.4 Terminais

- cadastro por ticket, sem criacao manual obrigatoria;
- hostname, IP local, sistema, versao do agente e ultima comunicacao;
- chave publica e token armazenado de forma segura;
- servicos autorizados;
- estado de conexao e sessoes reportadas;
- revogacao imediata;
- historico de concessoes e revogacoes.

### 6.5 Instaladores e tickets

- plataforma Windows ou Linux;
- servicos selecionados;
- validade configuravel;
- limite de instalacoes;
- uso unico ou reutilizavel;
- revogacao antes do vencimento;
- contador de utilizacoes;
- download autenticado ou link temporario;
- nunca registrar o token em log ou auditoria.

## 7. Modelo de dados aprovado

Os nomes definitivos devem ser validados contra o esquema atual antes da
primeira migration.

### 7.1 `o3central_gateways`

- `id`, `uuid`;
- `cliente_id` obrigatorio;
- `ambiente_id` opcional;
- `nome`, `endpoint_publico`, `endereco_escuta`, `portal_url`;
- `gateway_token_hash`, `host_public_key`;
- `status`, `versao`, `last_seen_at`;
- `ativo`, `created_by`, `updated_by`, timestamps.

### 7.2 `o3central_gateway_redes`

- `id`, `gateway_id`;
- `cidr` normalizado;
- `ativo`, timestamps;
- unicidade de `gateway_id + cidr`.

### 7.3 `o3central_servicos`

- `id`, `uuid`, `gateway_id`, `cliente_id`;
- `ambiente_id` opcional;
- referencia opcional ao registro da VM no inventario Proxmox;
- `origem` com valores `PROXMOX` ou `MANUAL`;
- `nome`, `ip_destino`, `porta_destino`, `porta_local`;
- `protocolo`, `tipo`, `ativo`;
- timestamps e responsaveis.

### 7.4 `o3central_terminais`

- `id`, `uuid`, `gateway_id`, `cliente_id`;
- `hostname`, `ip_local`, `sistema_operacional`, `versao_agente`;
- `public_key`, `token_hash`;
- `status`, `last_seen_at`, `revogado_at`, `revogado_by`;
- timestamps.

### 7.5 `o3central_terminal_servicos`

- `terminal_id`, `servico_id`;
- `concedido_by`, `concedido_at`, `revogado_at`;
- chaves estrangeiras devem garantir que terminal e servico pertencam ao mesmo
  gateway e cliente.

### 7.6 `o3central_tickets`

- `id`, `uuid`, `gateway_id`, terminal opcional;
- `token_hash`, `tipo`, `plataforma`;
- `expires_at`, `max_instalacoes`, `total_instalacoes`;
- `revogado_at`, `created_by`, timestamps.

### 7.7 `o3central_ticket_servicos`

- `ticket_id`, `servico_id`, ordem;
- integridade de propriedade por gateway.

### 7.8 `o3central_gateway_reports`

- `gateway_id`, `received_at`, `versao`;
- resumo normalizado para consultas frequentes;
- payload adicional limitado e validado, caso necessario.

### 7.9 Historico

Eventos sensiveis devem usar a auditoria existente. Uma tabela de eventos de
dominio pode ser criada somente se for necessaria para reconstruir concessoes,
rotacoes e estados sem depender do log geral.

## 8. Integracao com dados existentes

### 8.1 Clientes

- `cliente_id` e a fronteira principal de isolamento.
- somente clientes ativos podem receber novos gateways ou acessos;
- desativar um cliente nao deve apagar automaticamente identidade ou historico;
- a politica de suspensao/revogacao deve ser explicita.

### 8.2 Ambientes

- gateway e servico podem ser relacionados a um ambiente;
- o ambiente deve pertencer ao cliente selecionado;
- o relacionamento facilita operacao, auditoria e filtros.

### 8.3 Inventario Proxmox

- listar apenas VMs relacionadas ao cliente/ambiente selecionado;
- salvar uma referencia estavel ao registro de inventario, nao apenas o nome;
- copiar para o servico o IP operacional escolhido no momento da publicacao;
- mudanca posterior no inventario nao deve alterar silenciosamente o destino;
- divergencias devem gerar aviso e reconciliacao assistida.

### 8.4 Auditoria e usuarios

- toda criacao, alteracao, rotacao, concessao, download administrativo,
  revogacao e exclusao deve chamar a auditoria central;
- dados de auditoria nao incluem tokens, senhas, chaves privadas ou conteudo de
  instaladores;
- IDs, cliente, gateway, terminal, acao, resultado e IP de origem devem ser
  registrados.

## 9. Rotas aprovadas

### 9.1 Interface administrativa

```text
GET  /operacoes/o3central/
GET  /operacoes/o3central/gateways
GET  /operacoes/o3central/gateways/novo
POST /operacoes/o3central/gateways/novo
GET  /operacoes/o3central/gateways/<id>
POST /operacoes/o3central/gateways/<id>/editar
POST /operacoes/o3central/gateways/<id>/rotacionar
POST /operacoes/o3central/gateways/<id>/revogar
POST /operacoes/o3central/gateways/<id>/servicos
POST /operacoes/o3central/servicos/<id>/editar
POST /operacoes/o3central/servicos/<id>/desativar
GET  /operacoes/o3central/terminais
GET  /operacoes/o3central/terminais/<id>
POST /operacoes/o3central/terminais/<id>/servicos
POST /operacoes/o3central/terminais/<id>/revogar
POST /operacoes/o3central/tickets
POST /operacoes/o3central/tickets/<id>/revogar
```

### 9.2 API de maquinas

```text
POST /api/o3central/enroll
POST /api/o3central/gateway/sync
POST /api/o3central/gateway/portal
POST /api/o3central/agent/policy
GET  /api/o3central/install/<token>
GET  /api/o3central/install/<token>/artifact
GET  /api/o3central/health
```

Os caminhos podem mudar durante a implementacao. Depois que agentes forem
publicados, tornam-se contrato versionado e nao devem mudar sem compatibilidade.

## 10. Perfis e permissoes

Permissoes aprovadas:

- `o3central_dashboard`: visualizar indicadores e estado;
- `o3central_gateways`: consultar ou editar gateways;
- `o3central_servicos`: consultar ou editar servicos;
- `o3central_terminais`: consultar ou administrar terminais;
- `o3central_instaladores`: gerar e revogar tickets/instaladores.

Niveis:

- `LEITURA`: consultas sem revelar credenciais ou comandos sensiveis;
- `EDICAO`: criacao e alteracao comum;
- exclusao, rotacao e revogacao seguem os perfis com autorizacao sensivel do
  Manager, alem do nivel de edicao.

O controle deve ocorrer no backend para cada endpoint. Ocultar botoes nao e
controle de autorizacao.

## 11. Seguranca

- CSRF em todas as operacoes administrativas por sessao;
- tokens aleatorios com entropia adequada e comparacao em tempo constante;
- tokens exibidos uma unica vez quando tecnicamente possivel;
- rate limiting por endpoint, identidade e IP;
- limite de tamanho e tempo de leitura de requests;
- validacao estrita de JSON e rejeicao de campos desconhecidos;
- separacao de credenciais de gateway, terminal e ticket;
- rotacao sem reutilizacao de identidade;
- verificacao de propriedade por cliente/gateway em toda transacao;
- storage privado para CA, chaves e artefatos;
- downloads por streaming ou mecanismo interno do Nginx;
- nenhuma chave privada no banco, log, Git ou resposta administrativa;
- endpoints de maquina sem desafio interativo da Cloudflare, mas protegidos
  pelo protocolo, rate limiting e regras especificas;
- politica de retencao para telemetria, tickets e terminais revogados;
- backup deve incluir banco e material criptografico indispensavel;
- restauracao deve ser testada antes da liberacao geral.

## 12. Componentes do prototipo a aproveitar

Avaliar e portar, com testes:

- `common.py`: validadores e composicao de politica;
- `crypto.py`: primitivas criptograficas;
- `gateway_policy.py`: validacao e representacao da politica;
- `central_artifacts.py`, `linux_artifacts.py` e instaladores;
- partes de `central.py` relacionadas a protocolo, enrollment e regras;
- implementacoes de gateway e agente;
- testes de interoperabilidade, seguranca, pfSense, Windows e Linux.

Nao portar diretamente:

- autenticacao administrativa propria de `central_auth.py`;
- sessao e usuarios administrativos do prototipo;
- `StateRepository` como estado agregado;
- templates/painel independente como interface final;
- loop de monitoramento dentro do processo web;
- instalador de uma Central independente como arquitetura definitiva.

## 13. Processamento em segundo plano

Jobs previstos:

- marcar gateway/terminal offline por tempo sem comunicacao;
- expirar tickets;
- remover sessoes e dados temporarios;
- verificar divergencias entre servico e inventario Proxmox;
- gerar alertas operacionais;
- manter artefatos e versoes permitidas.

Cada job deve usar lock para impedir execucao concorrente, ser idempotente e
produzir log operacional sem segredos.

## 14. Fases de implementacao

### Fase 0 - Descoberta detalhada

- confirmar tabelas e relacionamentos atuais de clientes, ambientes e Proxmox;
- mapear o protocolo completo do prototipo;
- identificar dependencias Python e licencas;
- definir politica de CA, certificados, DNS e backup;
- produzir decisoes arquiteturais registradas.

### Fase 1 - Fundacao administrativa

- migrations relacionais;
- repositories e services;
- permissao e item no menu Operacoes;
- dashboard inicial;
- CRUD de gateways, redes e servicos manuais;
- auditoria e testes de acesso.

### Fase 2 - Integracao Proxmox

- selecao de cliente, ambiente e VM;
- sugestao de IP e metadados;
- vinculo persistente;
- deteccao de divergencia sem alteracao automatica destrutiva.

### Fase 3 - Protocolo de gateway

- enrollment;
- emissao de identidade;
- sincronizacao de politica;
- telemetria;
- estado e diagnostico;
- testes com pfSense de laboratorio.

### Fase 4 - Terminais e autorizacoes

- tickets;
- cadastro Windows/Linux;
- concessoes de servicos;
- politica por terminal;
- revogacao e telemetria.

### Fase 5 - Artefatos e instaladores

- pipeline reproduzivel de build;
- checksums e manifesto;
- downloads controlados;
- versionamento e compatibilidade;
- assinatura de artefatos quando aplicavel.

### Fase 6 - Homologacao

- ambiente isolado;
- um cliente piloto;
- testes de falha, expiracao, rotacao, revogacao e restore;
- revisao de seguranca;
- documentacao operacional e suporte.

## 15. Estrategia de testes

### Unitarios

- validacao de CIDR, IP, porta e endpoint;
- hash, token, expiracao e comparacao;
- isolamento entre clientes;
- composicao e validacao de politica;
- selecao de servicos e colisao de portas;
- transicoes de estado.

### Integracao

- migrations em banco vazio e banco existente;
- relacionamentos com clientes, ambientes e inventario Proxmox;
- rollback de transacao composta;
- RBAC por perfil e nivel;
- CSRF e acesso direto por URL;
- enrollment, sync, policy e revogacao;
- jobs concorrentes e idempotencia.

### Ponta a ponta

- cadastrar gateway para um cliente;
- publicar VM Proxmox como servico;
- gerar ticket;
- instalar terminal de laboratorio;
- acessar somente servicos permitidos;
- revogar acesso e confirmar bloqueio;
- restaurar backup em ambiente separado.

## 16. Criterios de aceite da primeira entrega

- modulo aparece em Operacoes somente para perfis autorizados;
- usuario sem permissao recebe bloqueio tambem acessando a URL diretamente;
- gateway sempre pertence a um cliente existente;
- redes e servicos passam por validacao estrita;
- VM somente pode ser selecionada no escopo correto do cliente/ambiente;
- servico manual funciona sem dependencia do Proxmox;
- nenhuma credencial e salva ou exibida em texto puro indevidamente;
- auditoria identifica usuario, cliente, objeto, acao e resultado;
- dashboard e CRUD funcionam sem degradar modulos existentes;
- migrations e suite completa passam em homologacao;
- existe runbook de backup, implantacao, smoke test e rollback.

## 17. Fora do escopo inicial

- migrar dados do banco do prototipo;
- manter compatibilidade com agentes ou pfSenses do teste;
- publicar diretamente em producao;
- acesso de usuarios finais dos clientes ao painel;
- faturamento automatico do recurso;
- alta disponibilidade multi-regiao;
- alteracao automatica de firewall fora do agente controlado;
- substituir o inventario Proxmox existente.

Esses itens podem ser planejados depois que o nucleo estiver homologado.

## 18. Riscos e mitigacoes

| Risco | Mitigacao |
|---|---|
| Cruzamento de dados entre clientes | FKs compostas, filtros obrigatorios e testes de isolamento |
| Token ou instalador vazado | Hash, validade, limite de uso, revogacao e ausencia em logs |
| Worker Gunicorn bloqueado | Jobs externos e downloads por streaming/Nginx |
| Alteracao de IP da VM | Divergencia assistida, sem mudanca silenciosa |
| Politica invalida no pfSense | Validacao dupla, versao e ultimo snapshot valido |
| Perda da CA/chaves | Backup criptografado e teste de restauracao |
| Dependencias Python conflitantes | Analise antes de adicionar, pins e auditoria de CVE |
| Regressao no Manager | modulo isolado, migrations incrementais e suite completa |

## 19. Documentos complementares

O pacote de desenho previo a implementacao e composto por:

1. [modelo fisico e integridade](72-O3CENTRAL-MODELO-FISICO-DADOS.md);
2. [contrato versionado da API](73-O3CENTRAL-CONTRATO-API-V1.md);
3. [matriz de permissoes](74-O3CENTRAL-MATRIZ-PERMISSOES.md);
4. [ADR de identidade, CA e chaves](75-O3CENTRAL-ADR-001-IDENTIDADE-CA-E-CHAVES.md);
5. [ADR de jobs e concorrencia](76-O3CENTRAL-ADR-002-JOBS-E-CONCORRENCIA.md);
6. [build, artefatos e supply chain](77-O3CENTRAL-BUILD-ARTEFATOS-E-SUPPLY-CHAIN.md);
7. [plano de homologacao e piloto](78-O3CENTRAL-PLANO-HOMOLOGACAO-PILOTO.md);
8. [runbook de implantacao, backup e rollback](79-O3CENTRAL-RUNBOOK-IMPLANTACAO-BACKUP-ROLLBACK.md);
9. [registro de decisoes fechadas](80-O3CENTRAL-REGISTRO-DECISOES-FECHADAS.md).

Esses documentos estao aprovados para implementacao. Numeros de migration e
comandos finais serao preenchidos durante a implementacao sem alterar as decisoes
arquiteturais registradas.

## 20. Referencias locais

- Prototipo: `/home/o3cloud/o3cloudcentral-main/`
- Backend do prototipo: `python/o3cloudcentral/`
- Interface do prototipo: `web/`
- Testes do prototipo: `python/tests/`
- Instalacao e operacao: `deploy/`
- Controle de acesso do Manager: `app/core/access_control.py`
- Menu do Manager: `app/templates/components/sidebar.html`
- Inventario Proxmox do Manager: `app/infraestrutura/` e repositories associados.

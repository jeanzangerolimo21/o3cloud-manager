# O3Central integrado - modelo fisico de dados

Status: APROVADO PARA IMPLEMENTACAO. Nenhuma migration foi criada nesta etapa.

## Dependencias existentes

- `clientes(id)`: fronteira principal de isolamento.
- `ambientes(id)`: agrupamento operacional; o vinculo valido com cliente deve
  ser confirmado por `ambientes.cliente_id` ou `ambiente_clientes`.
- `proxmox_vm_inventory(id)`: inventario sincronizado.
- `ambiente_proxmox_recursos`: confirma que a VM pertence ao ambiente.
- `auth_usuarios(id)` e `auth_auditoria`: identidade e trilha administrativa.

Nunca relacionar cliente por nome, tag ou prefixo. Toda selecao deve validar IDs
e registros ativos no momento da operacao.

## Tabelas novas

### `o3central_gateways`

| Coluna | Tipo aprovado | Regra |
|---|---|---|
| id | BIGINT | PK auto incremento |
| uuid | CHAR(36) | unico, identificador publico administrativo |
| cliente_id | BIGINT | FK clientes, obrigatorio, RESTRICT ao excluir |
| ambiente_id | BIGINT NULL | FK ambientes, SET NULL ao excluir |
| nome | VARCHAR(150) | obrigatorio |
| endpoint_publico | VARCHAR(320) | host:porta validado |
| endereco_escuta | VARCHAR(320) | IP:porta do pfSense |
| portal_url | VARCHAR(500) NULL | HTTPS quando informado |
| gateway_token_hash | CHAR(64) NULL | SHA-256 do token; nunca token puro |
| host_public_key | TEXT NULL | chave publica normalizada |
| status | VARCHAR(30) | PENDENTE, ATIVO, OFFLINE, REVOGADO, ERRO |
| versao | VARCHAR(40) NULL | versao reportada |
| last_seen_at | DATETIME NULL | ultima comunicacao valida |
| ativo | TINYINT(1) | remocao logica |
| created_by / updated_by | VARCHAR(180) | e-mail administrativo |
| created_at / updated_at | DATETIME | timestamps |

Indices: cliente/ativo, ambiente, status/last_seen e endpoint. Ambiente, quando
informado, deve pertencer ao cliente; esta regra exige validacao transacional no
service porque o modelo atual aceita varios clientes por ambiente.

### `o3central_gateway_redes`

`id`, `uuid`, `gateway_id`, `cidr VARCHAR(64)`, `ativo`, timestamps. Unico por
`gateway_id + cidr`. CIDR deve ser canonicalizado com `ip_network(strict=False)`;
redes `/0` nao sao permitidas.

### `o3central_servicos`

| Coluna | Regra |
|---|---|
| gateway_id | FK obrigatoria |
| cliente_id | FK obrigatoria, igual ao cliente do gateway |
| ambiente_id | FK opcional e pertencente ao cliente |
| proxmox_inventory_id | FK opcional; obrigatoria quando origem=PROXMOX |
| origem | PROXMOX ou MANUAL |
| nome | ate 120 bytes |
| ip_destino | IPv4/IPv6 canonicalizado |
| porta_destino / porta_local | 1..65535 |
| protocolo | inicialmente TCP |
| tipo | WEB, SSH, RDP, BANCO ou TCP |
| ativo | remocao logica |
| snapshot_origem | JSON limitado, sem credenciais |

Para origem Proxmox, deve existir `ambiente_proxmox_recursos` ligando a VM ao
ambiente escolhido. O IP publicado e congelado no servico; mudanca no inventario
gera divergencia, nunca alteracao silenciosa.

### `o3central_terminais`

`id`, `uuid`, `gateway_id`, `cliente_id`, `hostname`, `local_ip`, `os`,
`agent_version`, `public_key`, `token_hash`, `status`, `last_seen_at`,
`revogado_at`, `revogado_por`, timestamps. Unicidade recomendada da chave
publica ativa e indices por gateway/status e cliente/status.

### `o3central_terminal_servicos`

Chave composta `terminal_id + servico_id`, mais `gateway_id`, `cliente_id`,
`posicao`, `concedido_por`, `created_at`, `revogado_at`. FKs compostas ou
triggers nao devem substituir a validacao de dominio: terminal e servico precisam
pertencer ao mesmo gateway e cliente.

### `o3central_tickets`

`id`, `uuid`, `gateway_id`, `cliente_id`, `token_hash CHAR(64) UNIQUE`, `tipo`,
`plataforma`, `expires_at`, `max_instalacoes`, `total_instalacoes`, `status`,
`created_by`, `revogado_at`, timestamps. Tipos iniciais: GATEWAY,
GATEWAY_UPDATE, GATEWAY_REINSTALL e AGENT_LINK.

### `o3central_ticket_servicos`

Chave composta `ticket_id + servico_id`, com `gateway_id` e `posicao`. Apenas
tickets de agente recebem servicos.

### `o3central_gateway_reports`

Uma linha atual por gateway: `gateway_id`, `received_at`, `versao`, contadores e
`payload_json` limitado. Na primeira entrega nao havera historico detalhado: o
estado atual sera substituido transacionalmente e a auditoria preservara acoes
administrativas.

### `o3central_jobs_execucoes`

`id`, `uuid`, `job_key`, `status`, `lock_owner`, `iniciada_em`, `finalizada_em`,
contadores, `mensagem` sanitizada e timestamps. Serve para observabilidade; o
lock efetivo usa `GET_LOCK` ou mecanismo ja padronizado.

## Integridade e exclusao

- Cliente: `RESTRICT` enquanto houver gateway, exigindo inativacao explicita.
- Gateway: remocao logica; redes e objetos mantidos para auditoria.
- Servico/terminal: revogacao ou inativacao, nao DELETE operacional.
- Ticket expirado: preservado pelo periodo de retencao, sem token puro.
- VM: `SET NULL` no servico se o inventario for removido; snapshot permanece.
- Ambiente: `SET NULL`, preservando cliente e configuracao.

## Migration planejada

Criar uma unica migration estrutural e migrations separadas para seeds de
permissao. Usar o proximo numero livre somente no momento da implementacao.
Migration deve ser idempotente, ter indices nomeados e funcionar em MariaDB do
ambiente de producao. Nao editar migrations anteriores.

## Consultas de isolamento obrigatorias

Toda busca por objeto operacional deve receber tambem `cliente_id` ou derivar o
cliente pelo gateway dentro da mesma query. Atualizacoes devem usar `WHERE id=%s
AND cliente_id=%s`. A existencia de um ID nunca autoriza o acesso por si so.

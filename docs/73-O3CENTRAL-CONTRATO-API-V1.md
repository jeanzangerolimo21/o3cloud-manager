# O3Central integrado - contrato de API v1

Status: APROVADO PARA IMPLEMENTACAO. Prefixo: `/api/o3central/v1`.

## Convencoes

- HTTPS obrigatorio.
- JSON UTF-8, exceto downloads.
- `Content-Type: application/json` em requests JSON.
- Limite padrao de corpo: 128 KiB; politica: 4 MiB; artefatos por streaming.
- Datas UTC em RFC 3339 com `Z`.
- IDs externos sao UUIDs/prefixos opacos, nunca IDs sequenciais do banco.
- Campos desconhecidos sao rejeitados.
- Resposta de erro: `{"error":{"code":"CODIGO","message":"mensagem"},
  "request_id":"..."}`.
- Nunca retornar hash, token armazenado, chave privada ou stack trace.

## Autenticacao

- Gateway: `Authorization: Bearer <token_gateway>`.
- Terminal: `Authorization: Bearer <token_terminal>` quando chamada direta for
  prevista; preferencialmente trafega pelo gateway autenticado.
- Enrollment: token temporario no corpo, consumido/contabilizado atomicamente.
- Administracao nao usa esta API: usa sessao Flask, CSRF e rotas internas.
- Comparacao de token em tempo constante apos hash SHA-256.

## Idempotencia

Enrollment e operacoes mutaveis aceitam `Idempotency-Key` com 16 a 128
caracteres. Repeticao com mesmo corpo retorna o resultado anterior; corpo
diferente retorna 409. A retencao da chave e 24 horas.

## Endpoints

### `GET /health`

Sem detalhes internos. Retorna `service`, `version` e `status`. O Nginx permite
esta rota somente por loopback e redes de monitoramento autorizadas.

### `POST /enroll/gateway`

Entrada: `ticket`, `public_key`, `agent_version` e identificacao minima.
Valida ticket ativo, tipo, limite, gateway ainda elegivel e chave publica.
Resposta unica: `gateway_id`, novo `token`, URL de sync e CA publica necessaria.
O token novo nao volta a ser consultavel.

### `POST /enroll/agent`

Entrada: ticket, plataforma, chave publica, hostname e metadados limitados.
Valida servicos do ticket no mesmo gateway. Resposta: `device_id`, token novo,
endpoint do gateway, host key e politica inicial.

### `POST /gateway/sync`

Autenticacao de gateway. Entrada: versao atual da politica, identidade, estado
resumido e relatorio de terminais. Resposta: revisao, politica assinada/validada,
intervalo de 60 segundos com jitter de ate 15 segundos e comandos permitidos.
Uma politica invalida nunca substitui
o ultimo snapshot valido do gateway.

### `POST /gateway/portal`

Emite ou renova material do portal do gateway conforme protocolo definido no
ADR de certificados. CSR e identidade devem pertencer ao gateway autenticado.

### `POST /agent/policy`

Quando mantido por compatibilidade do protocolo, recebe identidade e estado do
terminal por um gateway autenticado. O header marcador de proxy nao e suficiente
sem bearer valido do gateway. Resposta contem apenas servicos daquele terminal.

### `GET /install/pfsense/{ticket}/package`

Ticket deve estar ativo, pertencer ao gateway e ser do tipo correto. Resposta
por streaming com `Content-Disposition`, tamanho e checksum. Falhas nao revelam
se outro ticket existe.

### `GET /install/agent/{ticket}`

Pagina minima de instalacao, sem dados de outros clientes. Pode oferecer
artefato Windows/Linux conforme plataforma gravada no ticket; query string nao
pode trocar plataforma ou ampliar servicos.

### `GET /install/agent/{ticket}/artifact`

Download controlado, streaming e checksum. Download nao equivale a enrollment;
uso e contabilizado quando a identidade e emitida.

## Status HTTP

- 200/201: sucesso.
- 400: formato ou validacao.
- 401: credencial ausente/invalida.
- 403: identidade valida sem permissao para a operacao.
- 404: objeto nao encontrado no escopo da identidade.
- 409: conflito, replay divergente ou estado concorrente.
- 413: corpo excedido.
- 422: politica semanticamente invalida.
- 429: limite de taxa.
- 503: dependencia temporariamente indisponivel.

## Rate limiting aprovado

- login administrativo: mecanismo existente do Manager.
- enrollment: 10 tentativas/minuto/IP e 5/minuto/ticket.
- gateway sync: 12/minuto/gateway, com burst curto de 5.
- agent policy: 30/minuto por gateway e terminal.
- downloads: 10/hora/ticket e 30/hora/IP.
- erros de autenticacao nao podem criar estrutura de memoria sem limite.

## Versionamento

Mudanca incompatível cria `/v2`. Campos opcionais podem ser adicionados em v1,
mas agentes devem ignorar campos desconhecidos de resposta. Cada politica inclui
`schema_version` e `revision`. Compatibilidade minima/maxima de agentes deve ser
publicada junto aos artefatos.

## Auditoria e logs

Logar request ID, endpoint, resultado, identidade opaca, duracao e IP confiavel.
Nunca logar Authorization, ticket, CSR completo, politica com segredos ou URL
que contenha token. Eventos administrativos usam `auth_auditoria`.

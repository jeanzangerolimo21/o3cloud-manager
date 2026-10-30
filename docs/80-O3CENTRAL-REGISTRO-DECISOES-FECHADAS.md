# O3Central - registro de decisoes fechadas

Status: APROVADO PARA IMPLEMENTACAO em 2026-10-30.

Este registro encerra as escolhas arquiteturais da fase documental. Mudanca
posterior exige atualizar o documento afetado e registrar justificativa.

## Produto e arquitetura

- O3Central sera modulo nativo do O3Cloud Manager em Flask.
- Nao sera mantida a aplicacao FastAPI administrativa independente.
- Nao ha migracao nem compatibilidade obrigatoria com dados/agentes do prototipo.
- UI administrativa usa login, 2FA, CSRF, RBAC e auditoria do Manager.
- API de maquinas usa `/api/o3central/v1` no mesmo hostname publico do Manager.
- Tunel de dados continua terminal-pfSense; o Manager e plano de controle.
- Protocolo inicial suporta somente TCP.

## Vinculos de negocio

- Todo gateway pertence obrigatoriamente a um cliente.
- Ambiente do gateway e opcional, pois um pfSense pode atender mais de um
  ambiente do mesmo cliente.
- Servico Proxmox exige ambiente e vinculo em `ambiente_proxmox_recursos`.
- Servico manual pode ter ambiente opcional.
- IP de servico e congelado na publicacao; mudanca no inventario gera alerta.
- Um cliente pode possuir varios gateways.

## Permissoes

- ADMIN: todas as permissoes em EDICAO e operacoes sensiveis.
- OPERACOES: dashboard, gateways, servicos, terminais e instaladores em EDICAO;
  pode executar operacoes sensiveis quando a chave correspondente estiver em
  EDICAO.
- DIRETORIA: dashboard em LEITURA por padrao.
- SUPORTE: dashboard e terminais em LEITURA por padrao.
- demais perfis: sem permissao por padrao.
- Operacoes sensiveis exigem ADMIN ou OPERACOES, permissao EDICAO, confirmacao e
  auditoria. DIRETORIA pode receber acesso por configuracao futura, nao por seed.

## Identidade e criptografia

- HTTPS web permanece no Nginx/Cloudflare.
- O3Central recebe CA propria, nova e separada da chave HTTPS.
- CA e certificados usam ECDSA P-256 com SHA-256.
- CA vale 5 anos; certificado operacional vale 180 dias e renova 30 dias antes.
- Tokens possuem 32 bytes aleatorios, codificacao URL-safe, e sao persistidos
  somente por SHA-256.
- Chave da CA fica em storage privado modo `0600`, fora do banco e do Git.
- Nao implementar OCSP/CRL na primeira entrega; revogacao ocorre por estado no
  banco e invalidacao de token. Reavaliar antes de adotar mTLS como autenticacao
  primaria.
- Backup da PKI e obrigatoriamente criptografado e testado em restore.

## API e tempos

- Gateway sincroniza a cada 60 segundos, com jitter de ate 15 segundos.
- Gateway fica OFFLINE apos 3 minutos sem sync valido.
- Terminal fica OFFLINE apos 5 minutos sem estado valido.
- Idempotency-Key e mantida por 24 horas.
- Request JSON padrao: 128 KiB; politica: 4 MiB; timeout de leitura: 10 segundos.
- Enrollment: 10 tentativas/minuto/IP e 5/minuto/ticket.
- Gateway sync: 12 requisicoes/minuto/gateway, com burst curto de 5.
- Agent policy: 30 requisicoes/minuto por gateway e terminal.
- Download: 10/hora/ticket e 30/hora/IP.
- `GET /health` fica disponivel apenas ao Nginx local e redes de monitoramento.
- HTTP 422 sera usado para politica semanticamente invalida.

## Jobs e retencao

- Executor: systemd timers chamando comandos Flask/CLI.
- Concorrencia: `GET_LOCK('o3central-job:<job_key>')` no MariaDB.
- Presenca: a cada minuto; tickets: 5 minutos; reconciliacao: 15 minutos;
  alertas: 5 minutos; retencao: diario.
- Execucao de job retida por 90 dias.
- Chave de idempotencia retida por 24 horas.
- Ticket finalizado retido por 180 dias.
- Relatorio de gateway mantem somente estado atual na primeira entrega.
- Gateways, servicos e terminais revogados permanecem como registros inativos;
  expurgo futuro exige politica aprovada.

## Artefatos

- Builds sao reproduziveis, versionados e possuem SHA-256 e manifesto assinado.
- Artefato nunca e substituido mantendo a mesma versao.
- Estados: EM_BUILD, CANDIDATO, APROVADO, DEPRECIADO e REVOGADO.
- Apenas APROVADO gera ticket fora do laboratorio.
- Authenticode e requisito de liberacao produtiva do agente Windows; homologacao
  interna pode usar CANDIDATO sem assinatura, com aceite explicito do risco.
- Durante desenvolvimento e homologacao, artefatos Windows sem Authenticode sao
  permitidos somente em laboratorio, com manifesto e SHA-256 conferidos. Nao se
  deve desativar SmartScreen ou antivirus globalmente.
- SBOM e auditoria de CVEs sao gates de promocao.

## Banco e exclusao

- Tabelas relacionais `o3central_*` no MariaDB atual.
- Cliente usa RESTRICT enquanto possuir gateway.
- Ambiente e VM usam SET NULL quando removidos, preservando snapshot e cliente.
- Operacao normal usa inativacao/revogacao, nao DELETE fisico.
- IDs externos sao UUIDs/opacos; IDs BIGINT nao aparecem na API de maquinas.
- Migrations estruturais e seeds de permissao ficam separadas e idempotentes.

## Implantacao

- Primeiro release entrega fundacao e administracao antes dos agentes.
- Homologacao usa pfSense, Windows e Linux de laboratorio.
- Primeiro cliente utiliza poucos servicos nao criticos e mantem acesso
  administrativo alternativo.
- Nenhum deploy produtivo ocorre antes de backup/restore, isolamento, revogacao,
  auditoria e suite completa passarem.

## Gates ainda externos, mas nao decisoes arquiteturais

- adquirir certificado Authenticode OV de autoridade publica antes da producao
  Windows; a aquisicao foi conscientemente adiada durante desenvolvimento e
  homologacao;
- informar destino externo real do backup criptografado na configuracao do
  ambiente;
- validar ECDSA P-256 em todas as versoes exatas de pfSense/Windows/Linux da
  matriz de homologacao.

Falha em um gate bloqueia promocao, sem reabrir automaticamente a arquitetura.

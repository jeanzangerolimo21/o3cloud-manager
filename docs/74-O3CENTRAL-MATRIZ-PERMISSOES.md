# O3Central integrado - matriz de permissoes

## Chaves de menu

| Chave | Leitura | Edicao |
|---|---|---|
| o3central_dashboard | indicadores e estados | nao adiciona escrita |
| o3central_gateways | listar e detalhar sem credenciais | criar e editar configuracao comum |
| o3central_servicos | listar destinos e divergencias | criar, editar e inativar |
| o3central_terminais | listar, detalhar e ver concessoes | alterar servicos permitidos |
| o3central_instaladores | listar tickets sem token | gerar e revogar tickets/downloads |

Rotacao de identidade, revogacao de gateway/terminal e exclusao logica exigem
EDICAO mais um perfil autorizado a operacoes sensiveis: ADMIN ou OPERACOES.

## Matriz por acao

| Acao | Dashboard | Gateways | Servicos | Terminais | Instaladores | Sensivel |
|---|---:|---:|---:|---:|---:|---:|
| Ver dashboard | L | - | - | - | - | nao |
| Ver gateway | - | L | - | - | - | nao |
| Criar/editar gateway | - | E | - | - | - | nao |
| Rotacionar/revogar gateway | - | E | - | - | - | sim |
| Ver/criar servico | - | L | L/E | - | - | nao |
| Inativar servico em uso | - | - | E | - | - | sim |
| Ver terminal | - | - | - | L | - | nao |
| Alterar concessoes | - | - | L | E | - | sim |
| Revogar terminal | - | - | - | E | - | sim |
| Gerar ticket | - | L | L | - | E | sim |
| Revogar ticket | - | - | - | - | E | sim |
| Ver auditoria | permissao de auditoria existente | | | | | nao |

L = LEITURA; E = EDICAO.

## Regras contextuais

- Permissao de menu nao elimina validacao de cliente, ambiente e gateway.
- O usuario nao recebe token ja emitido, mesmo sendo ADMIN.
- Comando de instalacao e revelado somente na criacao/rotacao autorizada.
- Downloads administrativos geram evento de auditoria.
- POST sem CSRF e bloqueado antes do service.
- APIs de maquina nao usam perfis de usuario; usam identidade propria e escopo
  fixo do gateway/terminal.

## Seeds iniciais

- ADMIN: todas as chaves em EDICAO.
- DIRETORIA: dashboard em LEITURA; demais acessos somente por configuracao
  explicita posterior.
- OPERACOES: todas as chaves O3Central em EDICAO.
- SUPORTE: dashboard e terminais em LEITURA.
- outros perfis: sem acesso por padrao.

Seeds devem usar `INSERT ... SELECT ... WHERE NOT EXISTS` ou upsert seguro, sem
sobrescrever personalizacoes de perfis existentes em atualizacoes futuras.

## Eventos de auditoria

Padrao de acoes: `O3CENTRAL_GATEWAY_CRIADO`, `_ATUALIZADO`, `_ROTACIONADO`,
`_REVOGADO`; `O3CENTRAL_SERVICO_CRIADO`, `_ATUALIZADO`, `_INATIVADO`;
`O3CENTRAL_TERMINAL_PERMISSOES_ATUALIZADAS`, `_REVOGADO`;
`O3CENTRAL_TICKET_CRIADO`, `_ARTEFATO_BAIXADO`, `_REVOGADO`.

Detalhes permitidos: IDs, cliente, plataforma, contagens, status e motivo.
Detalhes proibidos: token, Authorization, senha, chave privada e payload bruto.

# Manual de Configurações

## Objetivo

O módulo de Configurações concentra rotinas administrativas do sistema: usuários, perfis, permissões, e-mail, integrações, cache, auditoria, backups, sincronismos e atualizações.

Por ser uma área sensível, deve ser usada apenas por administradores ou responsáveis autorizados.

## Quem deve usar

- Administradores do sistema.
- TI responsável pela operação.
- Gestores autorizados para permissões e usuários.

## Principais telas

- Usuários.
- Perfis e permissões.
- Provedores de autenticação.
- Convites.
- Configurações de e-mail.
- Backups do Sistema.
- Atualizações do Sistema.
- Auditoria.
- Cache.
- Sincronismos.

## Usuários

Permite criar, editar, ativar ou desativar usuários.

Fluxo recomendado para novo usuário:

1. Criar ou convidar usuário.
2. Definir perfil correto.
3. Confirmar e-mail.
4. Validar se o usuário acessa apenas os módulos necessários.

Boas práticas:

- Não compartilhar contas.
- Desativar usuários desligados.
- Revisar permissões periodicamente.

## Perfis e permissões

Perfis agrupam permissões de acesso.

Exemplos:

- Administrador.
- Comercial.
- Financeiro.
- Implantação.
- Operações.
- Consulta gerencial.

Cuidados:

- Evite dar permissão administrativa sem necessidade.
- Revise impacto antes de alterar um perfil usado por vários usuários.
- Teste com usuário real quando criar novo perfil.

## E-mail e SMTP

Configura o envio de e-mails do sistema.

Impactos:

- Convites.
- Recuperação ou validações.
- 2FA por e-mail.
- Alertas operacionais.

Checklist:

- Host SMTP.
- Porta.
- Usuário.
- Senha ou token.
- Remetente padrão.
- TLS/SSL conforme provedor.
- Teste de envio.

## Integrações

Centraliza parâmetros para integrações de negócio e técnicas.

Exemplos:

- OMIE.
- Zabbix.
- Proxmox.
- PBS.
- TrueNAS.

Cuidados:

- Usar URLs corretas.
- Validar credenciais.
- Não expor segredos em prints ou documentos.
- Registrar alterações críticas.

## Cache

Controla retenção e limpeza de dados temporários ou sincronizados.

Uso recomendado:

- Limpar cache apenas quando houver necessidade operacional.
- Validar impacto em dashboards e relatórios.

## Sincronismos

Controla automações e rotinas agendadas de integração.

Boas práticas:

- Verificar última execução.
- Investigar falhas recorrentes.
- Ajustar periodicidade conforme criticidade dos dados.

## Auditoria

Permite consultar ações relevantes executadas no sistema.

Uso recomendado:

- Investigar alterações críticas.
- Conferir usuário executor.
- Apoiar governança e segurança.

## Backups do Sistema

Permite gerar, baixar e restaurar backups conforme permissão.

Essa rotina é crítica e deve seguir o manual específico de Backup, Restore e Atualizações.

## Atualizações do Sistema

Permite aplicar novas versões publicadas no GitHub, principalmente na branch Beta.

Essa rotina deve ser usada apenas por administradores e em janela controlada.

## Erros comuns

| Situação | Possível causa | Ação recomendada |
| --- | --- | --- |
| Usuário não recebe e-mail | SMTP incorreto | Testar configuração de e-mail |
| Usuário vê menu indevido | Perfil amplo demais | Revisar permissões |
| Integração falha | URL, credencial ou rede | Testar conexão e logs |
| Atualização não inicia | Runner sudoers ausente | Instalar runner de atualização |

## Boas práticas

- Documentar alterações administrativas relevantes.
- Usar usuários individuais para rastreabilidade.
- Fazer backup antes de mudanças críticas.
- Restringir acesso a integrações, backup e atualização.

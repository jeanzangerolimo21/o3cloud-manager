# O3Cloud Manager

# Logs Backend

## Objetivo

Registrar acessos, falhas de aplicação, banco de dados, segurança, integrações e tarefas técnicas para análise por administradores de infraestrutura via SSH.

Os logs não possuem tela no O3Cloud Manager e não são disponibilizados aos usuários ou colaboradores.

## Localização

```text
/opt/o3cloud-manager/logs/
```

Arquivos:

- `access.log`
- `application.log`
- `error.log`
- `database.log`
- `integrations.log`
- `security.log`
- `jobs.log`

Todos os registros são gravados em JSON, com timestamp UTC, nível, logger, processo e, quando disponível, `request_id`, rota, usuário, IP e duração.

## Segurança

- A pasta deve permanecer fora de `storage` e de qualquer rota Flask.
- Os arquivos não devem ser versionados no Git.
- A pasta deve utilizar permissão `750`.
- Os arquivos devem utilizar permissão `640`.
- Senhas, tokens, cookies, segredos e parâmetros sensíveis não devem ser registrados.
- O acesso operacional ocorre somente por SSH e permissões do sistema operacional.

## Rotação

A aplicação utiliza rotação diária com retenção padrão de 30 arquivos. O diretório pode ser alterado pela variável `O3_LOG_DIR` e a retenção pela variável `O3_LOG_BACKUP_COUNT`.

## Eventos cobertos

- Requisições HTTP, status e tempo de resposta.
- Exceções não tratadas do Flask.
- Falhas de conexão e operações do banco.
- Falhas de validação e sincronização de integrações.
- Login aprovado ou recusado.
- Inicialização do backend.

A auditoria funcional permanece separada e continua responsável por registrar ações de negócio, como criação, alteração, aprovação e inativação.

# Redefinicao de senha no O3Cloud Manager

Data: 25/08/2026

## Entrega

Foi adicionado o fluxo publico de redefinicao de senha para usuarios locais ativos:

- O login exibe o link `Esqueci minha senha` abaixo do botao `Entrar`.
- A tela aceita e-mail ou login e sempre apresenta uma mensagem generica, sem revelar se o usuario existe.
- O sistema envia um link exclusivo por e-mail quando o cadastro esta apto para redefinicao.
- O token e armazenado somente em formato hash, expira em 60 minutos e deixa de ser valido apos o uso.
- A nova senha exige no minimo 8 caracteres e confirmacao igual.
- Codigos pendentes de 2FA sao expirados apos a troca da senha.
- As solicitacoes, ignoradas e conclusoes sao registradas na auditoria.

## Arquivos principais

- `app/autenticacao/routes.py`
- `app/configuracoes/auth_service.py`
- `app/repositories/auth_repository.py`
- `app/core/access_control.py`
- `app/templates/autenticacao/login.html`
- `app/templates/autenticacao/esqueci_senha.html`
- `app/templates/autenticacao/resetar_senha.html`
- `database/migrations/110_auth_password_resets.sql`

## Atualizacao do Beta

No servidor Beta, executar o fluxo oficial como root:

```bash
sudo /usr/local/sbin/o3cloud-update-beta
```

O fluxo faz backup pre-atualizacao, atualiza a branch `beta`, instala dependencias, aplica migrations, reinicia `o3cloud-manager.service` e executa o healthcheck.

Se o runner ainda nao estiver instalado, executar uma vez no servidor:

```bash
cd /opt/o3cloud-manager
sudo deployment/install-update-runner.sh
```

## Validacao pos-atualizacao

1. Abrir a tela `/login` e confirmar o link `Esqueci minha senha`.
2. Informar um e-mail ou login cadastrado e confirmar o recebimento da mensagem.
3. Abrir o link recebido, cadastrar uma senha valida e fazer login.
4. Tentar reutilizar o mesmo link e confirmar que ele aparece como invalido ou expirado.
5. Conferir se a tabela `auth_password_resets` foi criada e se a migration `110_auth_password_resets.sql` consta em `schema_migrations`.

## Requisitos

- O envio de e-mail precisa estar configurado no `.env` do Beta.
- O servidor precisa conseguir acessar o SMTP configurado.
- O link gerado usa a URL externa da requisicao; por isso o acesso ao Beta deve estar com o dominio/proxy configurado corretamente.

# Releases 1.2.7 a 1.2.11 e hardening de producao

Data de consolidacao: 29/10/2026

Versao estavel: `v1.2.11`

Branch oficial: `main`

## Objetivo

Consolidar as mudancas publicadas entre `v1.2.7` e `v1.2.11`, as configuracoes
aplicadas fora do repositorio e as validacoes realizadas no ambiente de
producao.

## Historico das releases

### v1.2.7 - Sidebar responsiva e compacta

- Sidebar recolhivel sem ocultar os icones.
- Comportamento responsivo para dispositivos moveis.
- Ajustes de rolagem, rodape e navegacao.
- Testes de layout responsivo adicionados.

### v1.2.8 - Versao e atualizador

- Versao obtida de `APP_VERSION` ou da tag/commit Git atual.
- Versao real exibida no rodape do sidebar.
- CSS e JavaScript com cache busting baseado na versao.
- Runner de atualizacao atualizado dinamicamente.
- Lock orfao de `/tmp/o3cloud-manager-update.lock` removido somente quando nao existe processo de atualizacao ativo.

### v1.2.9 - Hardening da aplicacao

- Protecao CSRF em formularios e requisicoes AJAX mutaveis.
- Rate limit de login e recuperacao de senha baseado na auditoria existente.
- Cookies de sessao `Secure`, `HttpOnly` e `SameSite=Lax`.
- Sessao com duracao configuravel e senha nova com minimo de 12 caracteres.
- Correcao de open redirect no parametro `next`.
- Logout alterado de GET para POST.
- CSP restritiva, sem `unsafe-eval`, e cabecalhos de seguranca adicionais.
- SRI e `crossorigin` nos assets Bootstrap externos.
- Endpoint publico `/.well-known/security.txt`.
- Script somente leitura `deployment/security-diagnostic.sh`.

### v1.2.10 - Cadeia de proxy

- Gunicorn alterado de `0.0.0.0:5000` para `127.0.0.1:5000`.
- Unidade systemd reinstalada pelo runner de atualizacao.
- `security.txt` passou a usar `PUBLIC_BASE_URL` no canonical.
- Limite amplo por IP ajustado para reduzir bloqueio coletivo atras de proxy; o limite estrito por usuario e IP foi preservado.
- Recuperacao de senha passou a limitar por identificador e IP.
- Script reversivel `deployment/configure-local-nginx-proxy.sh` para preservar protocolo e IP encaminhados pelo proxy externo.
- Diagnostico passou a detectar bind publico do Gunicorn e CSP duplicada.

### v1.2.11 - Dependencias Python

| Pacote | Versao anterior | Versao corrigida |
|---|---:|---:|
| `certifi` | 2026.6.17 | 2026.10.23 |
| `urllib3` | 2.7.0 | 2.8.0 |
| `Werkzeug` | 3.1.8 | 3.1.9 |
| `requests` | 2.32.5 | 2.34.2 |

- Auditoria final: `No known vulnerabilities found`.
- Nenhuma migration de banco foi necessaria entre `v1.2.7` e `v1.2.11`.

## Topologia validada

```text
Internet
  -> Cloudflare
  -> Nginx externo 177.104.183.61 / 10.10.10.2
  -> Nginx local 10.10.10.210:80
  -> Gunicorn 127.0.0.1:5000
  -> MariaDB 10.10.10.209:3306
```

- O servidor MariaDB aceita conexao somente do servidor da aplicacao.
- O pfSense `10.10.10.1` controla o trafego das redes internas, VPN, monitoramento Zabbix e backup.
- O Nginx externo possui interface publica propria e encaminha o O3Manager pela interface interna.

## Configuracoes aplicadas em producao

Estas configuracoes nao sao integralmente aplicadas pelo deploy Git e devem ser preservadas na operacao dos servidores:

- Regra Cloudflare por hostname: `o3manager.o3cloud.com.br -> SSL/TLS Strict`.
- Proxy DNS da Cloudflare habilitado para o hostname do O3Manager.
- Protecoes DDoS de rede e SSL/TLS ativas.
- Cloudflare Free Managed Ruleset e nivel `Sempre protegido`.
- Nginx externo com CSP generica removida somente do virtual host do O3Manager; a CSP passa a ser fornecida pela aplicacao.
- Nginx externo confiando em `CF-Connecting-IP` somente para as redes oficiais da Cloudflare e enviando um unico `X-Forwarded-For` confiavel.
- `client_max_body_size 10M` no virtual host externo do O3Manager.
- Nginx local preservando `X-Forwarded-For` e enviando `X-Forwarded-Proto https` ao Gunicorn.
- Chrony ativo e sincronizado; TOTP depende de horario UTC correto.
- TOTP configurado para a conta administrativa; demais contas permanecem com segundo fator por email durante migracao gradual.

## Validacoes realizadas

- HTTP redireciona para HTTPS.
- TLS 1.0 e 1.1 recusados; TLS 1.2 e 1.3 aceitos.
- Certificado de origem Let's Encrypt valido e correspondente a `o3manager.o3cloud.com.br`.
- HSTS, CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` e `Permissions-Policy` presentes.
- CSP unica e sem `unsafe-eval`.
- Cookie de sessao `Secure`, `HttpOnly` e `SameSite=Lax`.
- TRACE bloqueado e CORS externo nao autorizado.
- CSRF presente no formulario de login.
- `.env`, `.git/config` e source maps nao expostos publicamente.
- Gunicorn ouvindo somente em `127.0.0.1:5000`.
- `pip-audit -r requirements.txt` sem vulnerabilidades conhecidas.
- Backups pre-update gerados antes das atualizacoes.

## Comandos de verificacao

```bash
cd /opt/o3cloud-manager
sudo ./deployment/security-diagnostic.sh
sudo ss -ltnp | grep ':5000'
curl -I https://o3manager.o3cloud.com.br/login
curl https://o3manager.o3cloud.com.br/.well-known/security.txt
/tmp/o3-pip-audit/bin/pip-audit -r requirements.txt
```

## Pendencias controladas

- Migrar perfis privilegiados e usuarios com dados sensiveis de 2FA por email para TOTP; avaliar passkeys/WebAuthn no futuro.
- Adicionar QR Code e copia da chave TOTP sem espacos no fluxo de cadastro.
- Criar migracao segura para uma `COFRE_SENHAS_KEY` dedicada sem tornar credenciais existentes ilegiveis.
- Remover gradualmente `unsafe-inline` da CSP usando arquivos estaticos, hashes ou nonces.
- Adicionar `Cache-Control: no-store` a respostas autenticadas e fluxos de login, 2FA e recuperacao.
- Avaliar Authenticated Origin Pulls ou restricao equivalente para impedir acesso direto ao IP do Nginx externo e bypass da Cloudflare.
- Revisar ciclo de suporte e patches do pacote Nginx identificado como `nginx/1.14.1` no origin.
- Testar hardening adicional da unidade systemd com `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` e permissoes explicitas de escrita.
- Validar TLS entre aplicacao e MariaDB e revisar privilegios minimos do usuario de banco.
- Reiniciar o servidor de aplicacao em janela controlada para carregar o kernel atualizado indicado pelo sistema operacional.

## Rollback

- Todas as atualizacoes geram backup pre-update antes de alterar o codigo.
- As releases desse intervalo nao possuem migration de banco, permitindo rollback de codigo para a tag anterior com menor risco.
- Alteracoes de Nginx devem usar os backups criados antes da edicao e sempre passar por `nginx -t` antes de `systemctl reload nginx`.

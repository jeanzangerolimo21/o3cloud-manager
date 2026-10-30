# O3Central - runbook de implantacao, backup e rollback

Este runbook e uma especificacao; comandos definitivos serao preenchidos depois
da implementacao e ensaiados em homologacao.

## Pre-implantacao

- confirmar tag/commit e changelog;
- executar testes, `pip-audit` e verificacao de migrations;
- validar espaco em banco e storage;
- gerar backup pre-update do Manager;
- gerar dump consistente das tabelas relacionadas;
- copiar PKI/storage em arquivo criptografado e restrito;
- testar checksum e leitura do backup;
- registrar janela, responsavel e criterio de abortar;
- confirmar que nao ha update/job concorrente.

## Ordem de implantacao

1. Colocar artefatos aprovados no storage temporario.
2. Aplicar codigo por fast-forward/tag aprovada.
3. Instalar dependencias fixadas e executar `pip check`.
4. Aplicar migrations idempotentes.
5. Ajustar proprietarios/permissoes de storage e PKI.
6. Instalar jobs/timers desativados.
7. Reiniciar o servico do Manager.
8. Executar healthcheck geral e smoke test do modulo.
9. Ativar jobs um por vez e observar.
10. Liberar permissoes somente ao grupo de homologacao.

## Smoke test

- login e 2FA;
- sidebar e controle de acesso;
- dashboard O3Central vazio/saudavel;
- criar gateway de laboratorio;
- validar cliente/ambiente/VM;
- criar e inativar servico de teste;
- gerar/revogar ticket sem expor token em log;
- auditoria presente;
- jobs executam uma vez e liberam lock;
- modulos CRM, Operacoes e Infraestrutura continuam acessiveis.

## Backup

Incluir:

- banco do Manager, com tabelas O3Central e relacionamentos;
- `/opt/o3cloud-manager/storage/o3central/`;
- configuracao efetiva sem imprimir segredos;
- manifests e artefatos aprovados;
- versao do codigo e schema.

Backup contendo PKI deve ser criptografado, ter acesso restrito, retencao
definida e copia externa. Testar restauracao periodicamente em rede isolada.

## Criterios de rollback

- migration falha ou excede janela;
- Manager nao inicia/healthcheck falha;
- regressao critica em modulo existente;
- autorizacao ou isolamento incorreto;
- erro criptografico/PKI;
- perda/corrupcao de dados;
- jobs duplicados ou carga anormal.

## Rollback

1. Bloquear novas operacoes O3Central e parar jobs.
2. Preservar logs sanitizados e estado para diagnostico.
3. Reativar release anterior do codigo.
4. Reverter schema somente por migration de rollback previamente testada; se a
   mudanca nao for reversivel, restaurar backup consistente.
5. Restaurar storage/PKI apenas junto ao banco correspondente.
6. Reiniciar Manager e executar healthcheck completo.
7. Confirmar modulos existentes e registrar incidente.

Nunca restaurar apenas banco ou apenas PKI quando identidades ja tiverem sido
emitidas. No piloto, bloquear enrollment durante restauracao evita divergencia.

## Pos-implantacao

- monitorar erros 4xx/5xx, latencia, banco, storage e jobs;
- revisar auditoria e tentativas de enrollment;
- confirmar backup seguinte;
- registrar versoes, resultado e pendencias;
- ampliar permissoes somente apos periodo de observacao.

## Nginx e Cloudflare

Rotas administrativas seguem protecoes do Manager. Rotas de maquina precisam
de limites de corpo/tempo e nao podem receber desafio interativo. Qualquer bypass
de WAF deve ser limitado ao hostname/path e compensado por token, rate limit e
restricao de metodo. Downloads grandes usam streaming ou `X-Accel-Redirect`.

## Monitoramento minimo

- health do Manager e endpoint interno;
- taxa de sync e last_seen de gateways;
- falhas de autenticacao/enrollment;
- jobs atrasados ou falhos;
- crescimento de tabelas e storage;
- validade de certificados;
- artefatos ausentes ou checksum divergente.

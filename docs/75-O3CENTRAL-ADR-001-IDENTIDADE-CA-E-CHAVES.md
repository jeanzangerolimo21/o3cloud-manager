# ADR-001 - Identidade, CA, certificados e chaves do O3Central

Status: ACEITO em 2026-10-30.

## Contexto

O Manager ja possui HTTPS no Nginx/Cloudflare. O protocolo O3Central tambem
precisa identificar gateways e terminais e pode emitir material para portais no
pfSense. O prototipo mantem CA propria e chaves no diretorio de dados.

## Decisao

1. HTTPS publico do Manager continua com certificado do Nginx/origem e
   Cloudflare; sua chave nao e reutilizada para agentes.
2. Criar uma CA operacional exclusiva do O3Central para identidades do
   protocolo, separada da CA web.
3. Manter chave da CA fora do Git e do banco, em diretorio restrito, com
   proprietario do servico e modo `0600`.
4. Banco armazena certificados publicos, fingerprints, serial, validade e
   estado; nao armazena chave privada da CA.
5. Tokens de enrollment e sessao de maquina ficam apenas como hash.
6. Rotacao tem periodo controlado de sobreposicao quando o protocolo exigir;
   revogacao de emergencia nao depende da sobreposicao.

## Caminhos aprovados

```text
/opt/o3cloud-manager/storage/o3central/pki/ca.crt
/opt/o3cloud-manager/storage/o3central/pki/ca.key
/opt/o3cloud-manager/storage/o3central/artifacts/
/opt/o3cloud-manager/storage/o3central/manifests/
```

O Nginx nao serve `pki/`. CA publica e artefatos sao entregues somente por rota
controlada ou `X-Accel-Redirect` para local interno especifico.

## Geracao e algoritmos

- Usar biblioteca `cryptography`, com versao auditada e fixada.
- CA e certificados operacionais usam ECDSA P-256 com SHA-256.
- CA tem validade de 5 anos. Certificados operacionais tem validade de 180 dias
  e renovacao iniciada 30 dias antes do vencimento.
- Tokens usam 32 bytes aleatorios, codificacao URL-safe, e persistencia apenas
  do hash SHA-256.
- Serial aleatorio e extensoes de uso apropriadas.
- Comparacoes de fingerprint/token em tempo constante.
- Nao inventar criptografia nem serializacao propria.

## Backup

A CA e material indispensavel entram no backup criptografado e com acesso
restrito. O restore deve validar permissao, fingerprint e correspondencia com o
banco. Perda da CA pode exigir recadastro de gateways/agentes; portanto restore
de PKI faz parte do teste obrigatorio de recuperacao.

## Rotacao

- CA: procedimento excepcional, documentado, com impacto explicitado.
- Certificado de gateway: renovacao antes do vencimento com identidade atual.
- Token: rotacao gera novo segredo, invalida o anterior atomicamente e audita.
- Chave comprometida: revogar, bloquear sync e exigir novo enrollment.

## Alternativas rejeitadas

- Reutilizar chave TLS do Nginx: mistura dominios de seguranca e amplia impacto.
- Guardar chave privada no banco: aumenta exposicao e complica segregacao.
- Copiar CA do prototipo: nao ha producao a preservar; uma nova raiz controlada
  reduz heranca de laboratorio.

## Fechamento

Nao sera implementado OCSP/CRL na primeira entrega. Revogacao usa estado no
banco e invalidacao do token. ECDSA P-256 precisa passar na matriz de laboratorio
antes da promocao. O destino externo do backup e configuracao operacional do
ambiente e deve estar preenchido antes da producao.

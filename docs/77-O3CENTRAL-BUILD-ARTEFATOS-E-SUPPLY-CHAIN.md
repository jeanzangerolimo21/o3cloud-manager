# O3Central - build, artefatos e cadeia de fornecimento

## Objetivo

Produzir agentes Windows/Linux e pacote pfSense de forma reproduzivel,
verificavel e separada do deploy da aplicacao web.

## Decisao para desenvolvimento e homologacao

Os artefatos Windows de desenvolvimento e homologacao poderao ser gerados sem
Authenticode enquanto o produto nao estiver em producao. Eles devem permanecer
com estado `CANDIDATO`, ser distribuidos somente no laboratorio controlado e
apresentar SHA-256 conferido antes da instalacao.

A ausencia de assinatura e aceita apenas para desenvolvimento/homologacao e
deve constar no roteiro e nas evidencias dos testes. Certificado Authenticode de
uma autoridade publica continua sendo gate obrigatorio para promover o agente
Windows a `APROVADO` para producao.

## Fontes aproveitadas do prototipo

- scripts de build Windows e Linux;
- empacotamento pfSense;
- manifestos de dependencias por plataforma;
- controles de release e verificacao de artefatos;
- testes de instalacao, remocao e interoperabilidade.

Esses arquivos serao revisados e importados para uma area claramente delimitada
do repositorio. Binarios gerados nao devem ser commitados sem politica explicita.

## Pipeline

1. Checkout de commit/tag imutavel.
2. Instalacao de dependencias fixadas por hash quando suportado.
3. Testes unitarios e de seguranca.
4. Build em ambiente limpo por plataforma.
5. Geracao de SHA-256, tamanho, versao e matriz de compatibilidade.
6. Assinatura do manifesto; assinatura de binario quando disponivel.
7. Testes de instalacao/desinstalacao em laboratorio.
8. Publicacao em storage privado do Manager.
9. Promocao manual de CANDIDATO para APROVADO.

## Manifesto

Cada release contem: nome, versao, plataforma, arquitetura, SHA-256, tamanho,
commit de origem, data, builder, versoes minima/maxima do protocolo, status e
assinatura. O backend confere manifesto e hash antes de servir o arquivo.

## Estados

- `EM_BUILD`: ainda nao utilizavel.
- `CANDIDATO`: somente homologacao.
- `APROVADO`: liberado para novos tickets.
- `DEPRECIADO`: instalado continua funcionando, novos tickets bloqueados.
- `REVOGADO`: download e enrollment bloqueados.

## Seguranca

- runner de build sem segredos de producao;
- nenhum token de cliente dentro do artefato generico;
- credencial entra somente no bootstrap/ticket;
- SBOM por release;
- auditoria de CVEs antes da promocao;
- logs de build sem chaves;
- controle de acesso e auditoria para promover/revogar;
- Authenticode para Windows deve ser planejado antes de liberacao ampla.

Na fase sem Authenticode, nenhuma instrucao deve orientar usuario a desativar
SmartScreen, antivirus ou outras protecoes. A instalacao ocorre apenas em
maquinas de laboratorio autorizadas, com o hash previamente validado.

## Compatibilidade

Matriz minima: pfSense CE homologado/FreeBSD, Windows suportado e distribuicoes
Linux glibc/systemd. A versao integrada inicia uma nova linha de protocolo; nao
ha obrigacao de compatibilidade com o prototipo sem producao.

## Rollback de artefato

Promover versao anterior aprovada para novos tickets. Nunca substituir arquivo
mantendo o mesmo numero e checksum. Revogacao nao deve apagar evidencias nem
artefatos necessarios para diagnostico durante o periodo de retencao.

# O3Cloud Manager v3.0

# Fechamento da Sprint 12

Versao: 3.0 Alpha

Data de fechamento: 29/07/2026

Status: Oficial

---

# Sprint 12 - Pendencias Operacionais e Preparacao da Versao Final

Status:

✅ Concluida em 29/07/2026

---

# Objetivo

Preparar a continuidade operacional do O3Cloud Manager a partir das pendencias documentadas na Sprint 11, ajustando regras de rastreabilidade, organizando integracoes e evitando dados ficticios enquanto as fontes oficiais de custos, parametros financeiros e faturamentos nao estiverem homologadas.

---

# Entregas Consolidadas

## Rastreabilidade com Proposta Opcional

- `proposta_id` foi definido como vinculo opcional no fluxo operacional.
- Contratos fechados diretamente pelo parceiro, sem proposta comercial no O3Cloud Manager, foram definidos como origem valida para implantacao.
- Rastreabilidade oficial passou a considerar contrato, cliente, parceiro, executivo, implantacao e origem do negocio, usando proposta apenas quando ela existir.
- Vinculo entre contrato e proposta legada so deve ser feito quando houver evidencia confiavel.
- Correcoes historicas devem preservar trilha auditavel e nao devem preencher `proposta_id` automaticamente.
- Dashboard Executivo passou a tratar contratos sem proposta como contratos diretos, sem destaque de erro.

## Integracoes de Negocio e Tecnicas

- Sidebar ganhou a secao `Configuracoes` com `Integracoes de Negocio` e `Integracoes Tecnicas`.
- Integracoes de negocio passaram a contemplar OMIE e ClickSign.
- Integracoes tecnicas passaram a contemplar Proxmox, PBS, Zabbix, FreeIPA e TrueNAS.
- Tela `Integracoes de Negocio` passou a exibir OMIE e ClickSign configurados por variaveis de ambiente.
- Segredos de ambiente e tokens cadastrados sao exibidos mascarados como `****` na renderizacao inicial.
- Visualizacao temporaria de segredo foi adicionada com resposta `no-store`, sem persistir valor sensivel no HTML inicial.
- Cadastro manteve suporte a multiplas configuracoes por tipo usando nomes distintos.
- Validacao permaneceu estrutural e nao destrutiva.

## Comentarios de Implantacao com Anexos

- Comentarios do historico de implantacao passaram a aceitar multiplos anexos.
- Arquivos sao salvos em `storage/implantacoes/<implantacao_id>/comentarios`.
- Banco registra metadados e caminho/url do arquivo anexado em `implantacao_historico_anexos`.
- Exclusao do comentario remove os registros de anexo e os arquivos fisicos correspondentes.

---

# Validacoes Realizadas

- `app/financeiro/repository.py` validado via AST.
- Dashboard Executivo `/dashboard/executivo` validado via Flask test client com retorno HTTP 200.
- Regras documentadas para proposta opcional revisadas na Sprint atual, fechamento da Sprint 11 e Changelog.
- Dashboard Executivo ajustado para nao destacar contrato sem proposta como falha.

---

# Pendencias Encaminhadas para Sprint 13

## Dados oficiais para rentabilidade

- Importar custos oficiais dos produtos pelo fluxo `/catalogo/produtos/custos` quando a fonte oficial estiver disponivel.
- Importar faturamentos oficiais por competencia pelo fluxo `/financeiro/faturamentos`.
- Cadastrar ou importar `parametros_financeiros` com custos unitarios e margem minima oficial.
- Definir regra oficial de custo para produtos, recursos tecnicos e infraestrutura.
- Validar cobertura de custo e faturamento no Dashboard Executivo apos carga real.

## Integracoes tecnicas nao destrutivas

- Evoluir validacoes de OMIE, ClickSign, Proxmox, PBS, Zabbix, FreeIPA e TrueNAS a partir das configuracoes cadastradas.
- Registrar historico de validacoes e falhas de integracao.
- Mapear dados tecnicos necessarios para custo operacional e provisionamento controlado.
- Manter apenas acoes de leitura e diagnostico ate aprovacao especifica para automacoes.

## Melhorias operacionais

- Refinar indicadores consolidados apos avaliacao gerencial.
- Melhorar cobertura de responsaveis/implantadores nas implantacoes existentes.
- Preparar criterios para encerramento operacional de projetos entregues.

---

# Resultado

Sprint 12 encerrada como concluida.

A entrega fechou a regra operacional de proposta opcional, organizou as configuracoes de integracoes e adicionou anexos ao historico de implantacao. As cargas oficiais de custos, faturamentos e parametros financeiros ficaram pendentes para reavaliacao na Sprint 13. A Sprint 13 consolidou posteriormente que essa carga real oficial deve ocorrer apenas na fase Beta com a equipe, apos saneamento dos cadastros e validacao das fontes homologadas.

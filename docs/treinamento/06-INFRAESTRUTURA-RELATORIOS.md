# Manual de Infraestrutura e Relatórios

## Objetivo

As telas de Infraestrutura e Relatórios consolidam informações técnicas e gerenciais para acompanhamento de ambiente, capacidade, backups, alarmes e indicadores.

## Quem deve usar

- Operações.
- Engenharia.
- Suporte.
- Diretoria.
- Financeiro para análises cruzadas.

## Principais telas de infraestrutura

- Consulta de infraestrutura.
- Proxmox clusters.
- Proxmox nodes.
- Proxmox inventory.
- PBS backups.
- TrueNAS backups.
- Zabbix alarmes.
- Escopo PBS.

## Dashboards

Dashboards apresentam visões consolidadas para acompanhamento rápido.

Exemplos:

- Dashboard principal.
- Dashboard executivo.
- Produtos por clientes.

Uso recomendado:

- Acompanhar indicadores em reuniões.
- Identificar alertas críticos.
- Avaliar contratos, propostas, infraestrutura e pendências.

## Proxmox

As telas Proxmox exibem clusters, nodes e inventário sincronizado.

Uso recomendado:

- Conferir disponibilidade e organização da infraestrutura.
- Relacionar recursos técnicos com ambientes e clientes.
- Apoiar análise de capacidade.

## PBS

A área PBS acompanha backups relacionados ao Proxmox Backup Server.

Cuidados:

- Verificar backups fora do prazo.
- Tratar falhas críticas.
- Manter escopos corretamente configurados.

## TrueNAS

Acompanha dados e alertas relacionados aos backups ou compartilhamentos TrueNAS.

Uso recomendado:

- Verificar ausência de modificação quando houver alerta.
- Apoiar análise preventiva de rotinas de backup.

## Zabbix

Exibe alarmes e eventos críticos sincronizados do monitoramento.

Boas práticas:

- Priorizar alarmes críticos.
- Registrar tratativa nos sistemas operacionais apropriados.
- Usar o painel como visão consolidada, não como substituto integral do Zabbix.

## Relatórios

O módulo de Relatórios permite consultar e gerar visões customizadas conforme fontes autorizadas.

Recursos comuns:

- Seleção de fonte de dados.
- Campos selecionáveis.
- Filtros.
- Período.
- Ordenação.
- Agrupamentos e agregações.
- Modelos salvos.
- Exportação em formatos como CSV, XLSX, DOCX, PDF ou impressão HTML.

Fluxo recomendado:

1. Escolha a fonte do relatório.
2. Defina campos e filtros.
3. Valide a prévia.
4. Exporte apenas quando os dados estiverem corretos.
5. Salve modelo se o relatório for recorrente.

## Erros comuns

| Situação | Possível causa | Ação recomendada |
| --- | --- | --- |
| Dado técnico desatualizado | Sincronismo não executado | Verificar automações e cache |
| Relatório vazio | Filtro restritivo | Revisar filtros e período |
| Alarme sem tratativa | Falta de processo operacional | Acionar responsável técnico |
| Exportação incorreta | Campos selecionados errados | Ajustar modelo do relatório |

## Boas práticas

- Conferir data de atualização dos dados.
- Usar filtros para evitar relatórios muito grandes.
- Salvar modelos de relatórios recorrentes.
- Validar alertas críticos com o sistema de origem quando necessário.

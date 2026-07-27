# O3Cloud Manager v3.0

# Fechamento da Sprint 9

Versão: 3.0 Alpha

Data de fechamento: 27/07/2026

Status: Oficial

---

# Sprint 9 - Implantação e Provisionamento

Status:

✅ Concluída

---

# Objetivo

Criar a fundação operacional do módulo de Implantação, conectando contratos encaminhados para projeto ao fluxo técnico de entrega, checklist, acompanhamento, rastreabilidade e preparação para provisionamento controlado.

A Sprint 9 estabeleceu a camada técnica pós-assinatura, partindo das entregas comerciais das Sprints 7 e 8.

---

# Entregas Consolidadas

## Implantação

- Módulo `app/implantacao` criado com routes, service, repository e templates.
- Tabelas `implantacoes`, `implantacao_checklist` e `implantacao_historico` criadas/evoluídas.
- Listagem, visualização, criação e edição de implantações implementadas.
- Criação de implantação limitada a contratos ativos e encaminhados para projeto.
- Materialização automática de implantações a partir de contratos Omie com status `ENCAMINHADO_PROJETO`.
- Histórico operacional com comentários, mudanças de etapa e resultado de notificação por e-mail.

## Kanban

- Kanban operacional em `/implantacao/kanban`.
- Movimentação por arrastar e soltar com persistência de etapa.
- Notificação de mudança de etapa para implantador, executivo, parceiro e contatos envolvidos quando SMTP estiver configurado.
- Administração de colunas em `/implantacao/kanban/colunas`.
- Colunas essenciais protegidas e bloqueio de inativação para colunas com cards ativos.

## Checklist

- Checklist técnico padrão gerado automaticamente por implantação.
- Atualização individual de status, responsável e evidência.
- Inclusão e remoção manual de itens.
- Aplicação de modelos por tipo de projeto: padrão, Licenças O3Web e Infraestrutura/VPN.
- Recalculo automático do percentual de conclusão.

## Licenças O3Web

- Tela operacional `/implantacao/licencas-o3web`.
- Cadastro manual, edição, inativação e importação CSV.
- Vínculo opcional com cliente ativo da base `clientes`.
- Paginação, filtro de validade e alerta para licenças vencidas ativas.
- Importador compatível com arquivos tabulados, ponto e vírgula ou vírgula.

## Faixas de Rede

- Tela operacional `/implantacao/faixas-rede`.
- Cadastro, edição, inativação, filtros e vínculo com cliente.
- Campos `Rede`, `FW - WAN`, `FW - LAN`, `VPN`, range de portas, `PVE` e observações.
- Cálculo de próxima faixa disponível usando `/29`, `/28` ou `/27` conforme quantidade de servidores.
- Bloqueio de conflito de portas para o mesmo `FW - WAN`.

## Cofre de Senhas

- Tela operacional `/implantacao/cofre-senhas`.
- Cadastro, edição, inativação e revelação controlada de credenciais.
- Senhas armazenadas criptografadas.
- Auditoria de criação, atualização, inativação e revelação.
- Botões para copiar senha, usuário, URL e Host/IP.
- Gerador local de senha complexa.
- Vínculo com cliente, faixa de rede, licença O3Web e campos futuros para Proxmox, PBS e Zabbix.
- Organização por pastas com navegação visual `parceiro -> cliente -> credenciais`.
- Pastas de cliente exigem parceiro para garantir navegação correta.

## Rastreabilidade

- Visão compartilhada proposta -> contrato -> implantação.
- Bloco de rastreabilidade nas telas de Proposta, Contrato e Implantação.
- Exibição de ClickSign, contrato Omie/manual, etapa Kanban, responsável, prazo e progresso do checklist quando disponíveis.
- Atalho direto de Contratos para iniciar ou abrir implantação existente.

## Dashboard e Acompanhamento

- Dashboard de Implantação com filtros por status, responsável, prazo e situação.
- Indicadores de atrasadas, vencendo em 7 dias, vencendo em 30 dias e sem prazo.
- Agrupamentos por status e responsável respeitando filtros.
- Listagem com sinalização de prazo atrasado, vencimento próximo e ausência de prazo.
- Dashboard principal atualizado com aviso e atalhos da Sprint 9.

## Integrações Técnicas

- Base de configuração para Proxmox, PBS e Zabbix em `/implantacao/integracoes`.
- Cadastro, edição, inativação e validação estrutural de integrações.
- Tokens e senhas das integrações armazenados criptografados.
- Nenhuma chamada externa ou ação destrutiva executada nesta Sprint.

---

# Migrations Entregues

- `021_create_implantacao_workflow.sql`
- `022_add_kanban_implantacao.sql`
- `023_add_implantacao_historico_emails.sql`
- `024_create_o3web_licencas.sql`
- `025_add_cliente_vinculo_o3web_licencas.sql`
- `026_create_implantacao_faixas_rede.sql`
- `027_add_port_range_implantacao_faixas_rede.sql`
- `028_create_implantacao_cofre_senhas.sql`
- `029_create_implantacao_cofre_pastas.sql`
- `030_create_implantacao_kanban_colunas.sql`
- `031_create_implantacao_integracoes_config.sql`

---

# Regras Implementadas

- Implantação só pode ser criada a partir de contrato ativo e elegível.
- Contrato de origem precisa estar com status `ENCAMINHADO_PROJETO`.
- Cada contrato pode ter somente uma implantação ativa.
- Checklist padrão é persistido por implantação.
- Percentual de conclusão é calculado pelos itens concluídos.
- Etapa `FINALIZADO` ajusta implantação para status `ENTREGUE`.
- Etapa `CANCELADOS` ajusta implantação para status `CANCELADA`.
- E-mail de movimentação e comentário é tolerante a ambiente sem SMTP.
- Provisionamento permanece planejado e rastreável, sem automação destrutiva.
- Credenciais e tokens técnicos são armazenados criptografados.

---

# Validações Realizadas

- Sintaxe Python validada nos módulos alterados.
- Migrations `021` a `031` aplicadas na base local.
- Rotas principais de Implantação, Kanban, Colunas, Integrações, Licenças O3Web, Faixas de Rede e Cofre de Senhas validadas via Flask test client com retorno HTTP 200.
- Criação, edição, validação e cleanup de registros temporários executados para Kanban, Integrações, Licenças O3Web, Faixas de Rede, Cofre de Senhas e Pastas do Cofre.
- Rastreabilidade proposta -> contrato -> implantação validada nas telas de Proposta, Contrato e Implantação.
- Movimentação de Kanban validada com retorno `smtp_nao_configurado` em ambiente sem SMTP.
- Navegação do Cofre por parceiro e pasta validada com criação temporária de pasta de cliente e cleanup.

---

# Pendências Encaminhadas para Próximas Sprints

- Executar integrações reais com Proxmox, PBS e Zabbix somente após desenho e validação dos conectores.
- Evoluir política de usuários, grupos e permissões no Cofre de Senhas.
- Consolidar indicadores executivos com base nos dados comerciais, implantação, contratos e infraestrutura.
- Preparar visão financeira/rentabilidade a partir de contratos, catálogo e custos operacionais.

---

# Resultado

Sprint 9 encerrada com a fundação operacional de Implantação concluída e validada em ambiente local.

Próxima sprint planejada: Sprint 10 - Dashboard Executivo.

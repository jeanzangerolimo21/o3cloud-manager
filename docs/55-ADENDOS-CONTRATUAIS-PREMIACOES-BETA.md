# Adendos Contratuais e Premiações Manuais - Beta

Data: 29/08/2026

## Objetivo

Permitir registrar adendos comerciais de contratos existentes, como upgrades, usuários adicionais e complementos, sem criar nova implantação e sem acionar setup Omie.

## Entregas

- Cadastro de adendos no detalhe do contrato.
- Adendos de usuários adicionais enviam solicitação automática para sac@o3cloud.com.br com dados do cliente, contrato e quantidade.
- Edição dos dados comerciais do adendo: tipo, título, número, data, usuários, valor recorrente, valor pontual e observações.
- Anexos PDF múltiplos por adendo.
- Inativação lógica de adendos.
- Lançamento manual de premiação do adendo em Financeiro > Premiações.
- Cálculo da premiação do adendo pela campanha selecionada, usando a mesma elegibilidade de parceiro/executivo da apuração automática do contrato.
- Soma de adendos nos totais de campanha: quantidade, base de premiação e premiação prevista.
- Correção da leitura de valores decimais para aceitar vírgula ou ponto decimal.
- Atualização automática da quantidade de usuários na licença O3Web quando houver uma única licença ativa localizada por cliente, CNPJ ou nome.

## Regras

- O adendo fica sempre vinculado a um contrato principal.
- O adendo não cria card de implantação, checklist, fila operacional ou setup Omie.
- Para adendo do tipo `USUARIOS_ADICIONAIS`, o sistema envia e-mail ao SAC e tenta atualizar a licença O3Web do cliente.
- Se nenhuma licença O3Web for localizada, ou se houver múltiplas licenças ativas para o mesmo cliente, a licença não é alterada automaticamente e a tela orienta conferência manual.
- O cálculo automático sincronizado do Omie continua restrito ao contrato principal.
- A premiação do adendo é manual porque ainda não há chave confiável para identificar adendos automaticamente no Omie.
- No lançamento manual, o usuário informa campanha, valor base, status e observações.
- Parceiro, executivo, percentuais e valores de premiação são definidos pelo sistema conforme a campanha e os vínculos comerciais elegíveis do contrato.

## Migrations

- `database/migrations/118_create_contratos_adendos.sql`
- `database/migrations/119_add_campanha_id_premiacoes_adendos.sql`

## Validação

- `python3 -B -m py_compile app/contratos/routes.py app/contratos/service.py app/repositories/contrato_adendo_repository.py app/financeiro/service.py app/financeiro/repository.py app/financeiro/routes.py`
- `git diff --check`
- Consulta real validou adendo da Panificadora do Baixinho com valor recorrente `435.00` e premiação base `435.00`.
- Resumo de campanha validado com contratos e adendos somados no topo de Financeiro > Premiações.

## Atualização Beta

1. Atualizar a branch `beta` no servidor.
2. Aplicar migrations pendentes.
3. Reiniciar o serviço da aplicação.
4. Validar acesso a Contratos e Financeiro > Premiações.
5. Conferir se os adendos aparecem nos totais quando filtrados por campanha.

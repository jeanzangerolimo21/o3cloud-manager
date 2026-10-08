# Cancelamentos de Clientes

## Objetivo

Criar, abaixo de `Financeiro > Inadimplentes`, um fluxo rastreável para solicitar o cancelamento de um cliente e orientar o SAC sobre o desligamento e a retirada de suas rotinas operacionais.

## Fluxo funcional

1. O usuário acessa `Financeiro > Cancelamentos` e seleciona `Novo cancelamento`.
2. Seleciona um ou mais contratos com status `ATIVO` ou `ENCAMINHADO_PROJETO` por número, cliente, razão social ou CNPJ.
3. Todos os contratos selecionados devem pertencer ao mesmo cliente.
4. Informa obrigatoriamente o motivo e a data/hora a partir da qual o servidor deverá ser desligado.
5. Confirma as providências de monitoramento, backup e remoção total do ambiente e pode complementar cada uma com detalhes técnicos.
6. Pode preencher observações relevantes, que são reproduzidas no corpo do e-mail.
7. O sistema registra a solicitação, seu responsável e o resultado do envio de e-mail.
8. O SAC recebe a mensagem em `sac@o3cloud.com.br`.
9. Em caso de falha SMTP, o registro é preservado e pode ser reenviado pela tela de detalhes.

## Conteúdo do e-mail

- Assunto: `Cancelamento - <cliente> - <CNPJ>`.
- Cliente, razão social, CNPJ e a relação de contratos elegíveis selecionados.
- Motivo e observações do cancelamento.
- Data e hora programadas para o desligamento.
- Responsável pela solicitação.
- Providências solicitadas para:
  - remover as rotinas de monitoramento;
  - remover as rotinas de backup;
  - desligar o servidor/ambiente na data informada;
  - realizar a remoção total do ambiente conforme o procedimento operacional.

## Segurança operacional

- O cadastro e o e-mail não executam desligamento ou exclusão automática de infraestrutura.
- A remoção total permanece uma atividade da equipe responsável, conforme validações e procedimentos internos.
- Não é permitido incluir em uma nova solicitação um contrato já vinculado a outro cancelamento ativo.
- Falhas de e-mail não descartam a solicitação e ficam registradas para diagnóstico.
- Criação e reenvio são gravados na auditoria.

## Permissões

- Novo menu `cancelamentos` no grupo Financeiro.
- Perfis `DIRETORIA` e `FINANCEIRO` recebem acesso de edição na migration.
- Perfis podem ter acesso ajustado posteriormente em `Configurações > Usuários e Acessos`.

## Critérios de aceite

- Menu `Cancelamentos` visível abaixo de `Inadimplentes` para usuários autorizados.
- Busca de contratos ativos ou encaminhados para projeto por cliente, CNPJ ou número, com seleção múltipla para o mesmo cliente.
- Data/hora de desligamento e motivo obrigatórios.
- Registro persistido mesmo se o SMTP falhar.
- Observações relevantes reproduzidas no corpo do e-mail.
- E-mail enviado somente para `sac@o3cloud.com.br` com cliente e CNPJ no assunto.
- Lista e detalhe exibem status do envio e permitem reenvio.

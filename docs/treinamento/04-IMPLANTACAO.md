# Manual de Implantação

## Objetivo

O módulo de Implantação organiza o processo de entrega após a venda, conectando contratos, ambientes, etapas, responsáveis, integrações e informações técnicas necessárias para ativação do cliente.

## Quem deve usar

- Time de Implantação.
- Operações.
- Engenharia.
- Comercial para acompanhamento.
- Diretoria para visão gerencial.

## Principais telas

- Implantação.
- Kanban de implantação.
- Contrato operacional.
- Ambientes.
- Implantadores.
- Integrações.
- Licenças O3Web.
- Faixas de rede.
- Cofre de senhas.

## Implantação

Registra o processo de entrega de um cliente ou contrato.

Informações comuns:

- Cliente.
- Contrato ou proposta relacionada.
- Responsável.
- Status.
- Etapas.
- Datas previstas e realizadas.
- Observações e anexos.

Fluxo recomendado:

1. Criar implantação a partir de contrato aprovado.
2. Definir responsáveis.
3. Preencher informações técnicas obrigatórias.
4. Acompanhar pelo Kanban.
5. Atualizar status até conclusão.

## Kanban de implantação

O Kanban mostra implantações por etapa.

Uso recomendado:

- Acompanhar prioridades.
- Identificar bloqueios.
- Revisar tarefas em reunião operacional.
- Manter etapas atualizadas para evitar perda de visibilidade.

## Ambientes

Ambientes representam estruturas técnicas associadas ao cliente.

Exemplos:

- Ambiente de produção.
- Ambiente de homologação.
- Serviços contratados.
- Relação com infraestrutura.

## Contrato operacional

A tela de contrato operacional consolida informações necessárias para execução técnica do contrato.

Uso recomendado:

- Validar escopo contratado.
- Conferir recursos provisionados.
- Registrar dados que impactam operação e suporte.

## Integrações

Integrações registram conexões ou dependências técnicas do ambiente do cliente.

Cuidados:

- Validar credenciais e endpoints.
- Registrar responsáveis.
- Atualizar status em caso de falha.

## Licenças O3Web

Controla licenças associadas aos clientes e ambientes.

Boas práticas:

- Manter quantidade e status atualizados.
- Importar dados com atenção.
- Revisar licenças antes da entrega final.

## Faixas de rede

Registra redes e faixas utilizadas em ambientes de clientes.

Cuidados:

- Evitar conflito de faixas.
- Confirmar dados técnicos antes de salvar.
- Manter rastreabilidade de alterações.

## Cofre de senhas

Armazena ou organiza credenciais sensíveis conforme permissões.

Regras importantes:

- Acesso deve ser restrito.
- Compartilhamentos devem ter validade quando aplicável.
- Nunca registrar senha em campo inadequado ou observação pública.
- Remover acessos desnecessários.

## Erros comuns

| Situação | Possível causa | Ação recomendada |
| --- | --- | --- |
| Implantação parada | Etapa não atualizada ou bloqueio não registrado | Atualizar Kanban e observações |
| Ambiente incompleto | Dados técnicos ausentes | Revisar contrato operacional |
| Credencial indisponível | Permissão ou cofre não configurado | Acionar responsável pelo cofre |
| Conflito de rede | Faixa cadastrada incorretamente | Validar com engenharia |

## Boas práticas

- Não iniciar implantação sem escopo validado.
- Atualizar status no mesmo dia em que houver mudança.
- Registrar bloqueios de forma objetiva.
- Usar anexos para evidências e documentos técnicos.

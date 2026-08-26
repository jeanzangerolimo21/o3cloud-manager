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

## Comentários da implantação

Comentários registram decisões, impedimentos e atualizações da entrega.

Regras atuais:

- O autor do comentário é o usuário logado no sistema.
- O responsável pela implantação não substitui o autor do comentário.
- Quando outra pessoa comentar, basta ela estar autenticada com seu próprio login para manter a rastreabilidade correta.

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

## Checklist técnico

O Checklist técnico fica na visualização da implantação e apoia o preenchimento dos itens operacionais da entrega.

Uso recomendado:

- Selecionar vários itens quando a revisão for feita em lote.
- Alterar os campos necessários nos itens selecionados.
- Usar o botão de salvamento em lote para gravar as alterações de uma vez.
- Deixar desmarcados os itens que não devem ser modificados naquele salvamento.

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
- Ao criar nova licença, pesquisar o cliente no campo digitável por nome fantasia, razão social ou CNPJ e selecionar o resultado correto antes de salvar.

## Faixas de rede

Registra redes, faixas e intervalos de portas utilizadas em ambientes de clientes.

Cuidados:

- Evitar conflito de faixas.
- Confirmar dados técnicos antes de salvar.
- Manter rastreabilidade de alterações.
- Usar `Adicionar range` quando o cliente precisar de mais de um intervalo de portas no mesmo FW - WAN.
- Conferir se os ranges adicionais não se sobrepõem ao range principal nem a outros registros ativos.

## Cofre de senhas

Armazena ou organiza credenciais sensíveis conforme permissões.

Regras importantes:

- Acesso deve ser restrito.
- Compartilhamentos devem ter validade quando aplicável.
- Nunca registrar senha em campo inadequado ou observação pública.
- Remover acessos desnecessários.
- Ao cadastrar credencial, pesquisar o cliente no campo digitável por nome fantasia, razão social ou CNPJ.
- Usar anexos da credencial para documentos, evidências ou arquivos técnicos diretamente relacionados à senha.
- Ao trabalhar dentro de uma pasta, conferir que o retorno após salvar permanece no mesmo contexto.

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

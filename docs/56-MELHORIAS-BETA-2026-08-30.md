# Melhorias Beta - 30/08/2026

Data: 30/08/2026

## Objetivo

Registrar o pacote de ajustes liberado para atualizacao do Beta em 30/08/2026, cobrindo adendos contratuais, premiacoes, dashboard financeiro de contratos e propostas comerciais.

## Adendos contratuais

- O e-mail automatico enviado para sac@o3cloud.com.br em adendos de usuarios adicionais nao informa mais o valor recorrente do adendo.
- A mensagem permanece com dados operacionais necessarios para a equipe tecnica: cliente, contrato, tipo de adendo, quantidade e observacoes.

## Premiacoes

- Quando `Projeto OMIE` estiver vazio na base de calculo, a apuracao usa o executivo vinculado manualmente ao contrato em `Editar vinculos`.
- Se `Projeto OMIE` e o vinculo manual estiverem vazios, a premiacao continua sem executivo associado.
- Premiacoes manuais de adendos tambem passam pela mesma regra de fallback para executivo manual.
- Adendos ja lancados sem executivo podem ser regularizados pela tela de Premiacoes ao carregar a apuracao.

## Dashboard de contratos

- `Financeiro > Contratos > Dashboard` considera contratos principais e adendos no total do periodo filtrado.
- Adendos entram no filtro de data por `data_adendo`; quando a data do adendo estiver ausente, o sistema usa a data de criacao do registro.
- A recorrencia total combina contratos principais e adendos, mas exibe a separacao entre os dois grupos.
- Adendos de `USUARIOS_ADICIONAIS` somam `quantidade_usuarios` em `Licencas ativas`, tambem separado do total vindo dos contratos principais.

## Propostas comerciais

- O campo `Instalacao de recursos` fica oculto por padrao no cadastro e edicao de propostas.
- O usuario precisa marcar `Incluir instalacao de recursos` para visualizar, preencher e enviar esse valor na proposta.
- Quando a opcao nao estiver marcada, `instalacao_servidores` fica zerado no backend e nao compoe `Total das Instalacoes` nem `Total Geral`.
- Visualizacao, impressao, documento de contrato e DOCX omitem a linha `Recursos adicionais de instalacao` quando a opcao nao estiver marcada.
- Propostas antigas com valor salvo em `instalacao_servidores` tambem deixam de exibir ou somar esse valor enquanto a nova opcao estiver desmarcada.

## Banco de dados

- `database/migrations/124_add_incluir_instalacao_recursos_propostas.sql`

A migration adiciona a coluna:

```sql
crm_propostas.incluir_instalacao_recursos TINYINT(1) NOT NULL DEFAULT 0
```

O padrao `0` mantem o valor de instalacao de recursos omitido para propostas novas e antigas ate que o usuario marque a opcao manualmente.

## Validacao tecnica

Executado em 30/08/2026:

```bash
venv/bin/python -B -m pytest tests/test_proposta_instalacao_recursos.py tests/test_contrato_dashboard_repository.py tests/test_financeiro_premiacoes_service.py tests/test_contrato_service_omie_sync.py -q
python3 -B -m py_compile app/propostas/routes.py app/propostas/service.py app/repositories/proposta_repository.py app/repositories/contrato_repository.py
```

Resultado: 22 testes passaram.

## Atualizacao do Beta

No servidor Beta, executar o fluxo oficial como root:

```bash
sudo /usr/local/sbin/o3cloud-update-beta
```

O fluxo deve atualizar a branch `beta`, aplicar migrations pendentes, reiniciar o servico e executar o healthcheck.

## Validacao pos-atualizacao

1. Abrir `Financeiro > Contratos > Dashboard` e filtrar pelo mes de agosto de 2026.
2. Confirmar que contratos principais e adendos aparecem separados no card de quantidade e recorrencia.
3. Confirmar que adendos de usuarios adicionais somam em `Licencas ativas`.
4. Abrir `Financeiro > Premiacoes` e validar um contrato sem `Projeto OMIE`, mas com executivo manual vinculado.
5. Criar ou editar uma proposta sem marcar `Incluir instalacao de recursos` e confirmar que o campo nao aparece na proposta nem entra no total.
6. Marcar `Incluir instalacao de recursos`, salvar e confirmar que a linha passa a aparecer com o valor escolhido.

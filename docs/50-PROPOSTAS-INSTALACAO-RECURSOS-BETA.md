# Propostas - Instalacao de recursos editavel e opcional

Data: 25/08/2026

## Entrega

O campo `Instalacao de recursos` da proposta comercial e um valor opcional para casos especificos. Por padrao ele fica oculto e nao compoe a proposta; o usuario precisa marcar `Incluir instalacao de recursos` para visualizar, editar e enviar essa informacao.

Quando a opcao esta marcada, a regra operacional permanece a mesma: o valor sugerido nasce da soma dos recursos adicionados no bloco de servidores. O comercial pode editar o subtotal quando houver negociacao, ajuste de implantacao ou excecao operacional que nao deva alterar item por item.

## Mudancas implementadas

- O formulario exibe a chave `Incluir instalacao de recursos`, desmarcada por padrao.
- Enquanto a chave estiver desmarcada, o campo monetario fica oculto, `instalacao_servidores` e zerado no backend e o valor nao entra em `Total das Instalacoes` nem `Total Geral`.
- Quando a chave estiver marcada, o formulario exibe `Instalacao de recursos` como campo monetario editavel na totalizacao geral.
- Ao adicionar, remover ou editar recursos de servidores, o campo e preenchido automaticamente enquanto nao houver edicao manual.
- Quando o usuario altera manualmente o campo, o valor informado passa a compor `Total das Instalacoes` e `Total Geral`.
- Preview, visualizacao, impressao, contrato e DOCX exibem `Recursos adicionais de instalacao` somente quando a chave estiver marcada.
- Ao salvar e reabrir a proposta, o override manual e preservado somente quando a inclusao opcional estiver ativa.
- Propostas antigas com valor salvo em `instalacao_servidores` tambem omitem esse valor enquanto a nova opcao estiver desmarcada.
- A normalizacao no backend recalcula totais usando `instalacao_servidores` apenas quando a inclusao opcional esta ativa.

## Arquivos principais

- `app/templates/propostas/form.html`
- `app/propostas/routes.py`
- `app/propostas/service.py`
- `app/repositories/proposta_repository.py`
- `database/migrations/111_add_instalacao_servidores_propostas.sql`
- `database/migrations/124_add_incluir_instalacao_recursos_propostas.sql`

## Banco de dados

A migration `111_add_instalacao_servidores_propostas.sql` adiciona a coluna:

```sql
crm_propostas.instalacao_servidores DECIMAL(12,2) NOT NULL DEFAULT 0.00
```

Para propostas existentes, a migration inicializa o novo campo com:

```text
max(total_instalacao - parametrizacao_sistema - setup_ambiente_cloud, 0)
```

Isso preserva o valor que ja aparecia como recursos adicionais de instalacao antes da mudanca.

A migration `124_add_incluir_instalacao_recursos_propostas.sql` adiciona a coluna:

```sql
crm_propostas.incluir_instalacao_recursos TINYINT(1) NOT NULL DEFAULT 0
```

O padrao `0` mantem `Instalacao de recursos` oculto e fora dos totais ate marcacao explicita do usuario.

## Atualizacao do Beta

No servidor Beta, executar o fluxo oficial como root:

```bash
sudo /usr/local/sbin/o3cloud-update-beta
```

O fluxo faz backup pre-atualizacao, atualiza a branch `beta`, instala dependencias, aplica migrations, reinicia `o3cloud-manager.service` e executa o healthcheck.

Se for necessario aplicar manualmente apenas a migration no ambiente ja atualizado:

```bash
cd /opt/o3cloud-manager
sudo APP_DIR=/opt/o3cloud-manager deployment/apply-migrations.sh
```

## Validacao pos-atualizacao

1. Abrir `CRM Comercial > Propostas` e criar ou editar uma proposta.
2. Adicionar pelo menos um servidor com recurso que possua valor de instalacao.
3. Confirmar que `Instalacao de recursos` nao aparece e nao entra nos totais enquanto `Incluir instalacao de recursos` estiver desmarcado.
4. Marcar `Incluir instalacao de recursos` e confirmar que o campo e preenchido automaticamente pela soma dos recursos.
5. Alterar manualmente `Instalacao de recursos` para outro valor.
6. Confirmar que `Total das Instalacoes`, `Total Geral` e preview usam o valor manual.
7. Salvar a proposta, reabrir a edicao e confirmar que a opcao marcada e o valor manual foram preservados.
8. Desmarcar a opcao, salvar e confirmar que o valor nao aparece na visualizacao/impressao nem entra no total.
9. Conferir se `111_add_instalacao_servidores_propostas.sql` e `124_add_incluir_instalacao_recursos_propostas.sql` constam em `schema_migrations`.

## Validacoes tecnicas realizadas

- `venv/bin/python -B -m py_compile app/propostas/routes.py app/propostas/service.py app/repositories/proposta_repository.py`
- `git diff --check`
- Testes de normalizacao confirmando que a instalacao de recursos e omitida por padrao e incluida somente quando a opcao e marcada.

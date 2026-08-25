# Propostas - Instalacao de recursos editavel

Data: 25/08/2026

## Entrega

O campo `Instalacao de recursos` da proposta comercial deixou de ser apenas um subtotal fixo calculado pelos recursos dos servidores.

A regra operacional permanece a mesma: o valor sugerido nasce da soma dos recursos adicionados no bloco de servidores. A diferenca e que o comercial agora pode editar o subtotal quando houver uma negociacao, ajuste de implantacao ou excecao operacional que nao deva alterar item por item.

## Mudancas implementadas

- O formulario de proposta exibe `Instalacao de recursos` como campo monetario editavel na totalizacao geral.
- Ao adicionar, remover ou editar recursos de servidores, o campo e preenchido automaticamente enquanto nao houver edicao manual.
- Quando o usuario altera manualmente o campo, o valor informado passa a compor `Total das Instalacoes` e `Total Geral`.
- O preview da proposta usa o valor manual em `Recursos adicionais de instalacao`.
- Ao salvar e reabrir a proposta, o override manual e preservado.
- A normalizacao no backend recalcula totais usando `instalacao_servidores` quando informado, sem depender apenas da soma dos itens de servidor.

## Arquivos principais

- `app/templates/propostas/form.html`
- `app/propostas/routes.py`
- `app/propostas/service.py`
- `app/repositories/proposta_repository.py`
- `database/migrations/111_add_instalacao_servidores_propostas.sql`

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
3. Confirmar que `Instalacao de recursos` e preenchido automaticamente pela soma dos recursos.
4. Alterar manualmente `Instalacao de recursos` para outro valor.
5. Confirmar que `Total das Instalacoes`, `Total Geral` e preview usam o valor manual.
6. Salvar a proposta, reabrir a edicao e confirmar que o valor manual foi preservado.
7. Abrir a visualizacao/impressao da proposta e confirmar `Recursos adicionais de instalacao` com o valor salvo.
8. Conferir se `111_add_instalacao_servidores_propostas.sql` consta em `schema_migrations`.

## Validacoes tecnicas realizadas

- `venv/bin/python -B -m py_compile app/propostas/routes.py app/propostas/service.py app/repositories/proposta_repository.py`
- `git diff --check`
- Simulacao de normalizacao confirmando que override manual de instalacao substitui a soma automatica dos recursos.

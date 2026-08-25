# Pesquisa de Satisfacao - Rolagem da Tela Publica

Data: 25/08/2026

## Entrega

A tela publica de resposta da pesquisa de satisfacao da implantacao passou a permitir rolagem vertical no navegador do destinatario.

Antes da correcao, o CSS global do sistema aplicava `overflow: hidden` ao `body`. Como a tela publica nao usa o layout interno com `.content`, o botao `Enviar avaliacao` podia ficar fora da area visivel em telas menores, exigindo zoom out do usuario para concluir a resposta.

## Mudancas implementadas

- O template publico da pesquisa recebeu a classe `public-survey-page` no `body`.
- O CSS global passou a liberar `overflow-y: auto` apenas para essa tela publica.
- A altura da pagina publica foi ajustada para `height: auto` e `min-height: 100%`, preservando o comportamento das telas internas do sistema.
- Nenhuma migration ou alteracao de banco de dados foi necessaria.

## Arquivos principais

- `app/templates/sucesso_cliente/pesquisa_publica.html`
- `app/static/css/style.css`

## Impacto operacional

Destinatarios que recebem o link individual da pesquisa conseguem rolar a pagina ate o botao de envio, inclusive em notebooks, monitores com baixa altura util e navegadores com zoom padrao.

## Atualizacao do Beta

No servidor Beta, executar o fluxo oficial como root:

```bash
sudo /usr/local/sbin/o3cloud-update-beta
```

O fluxo faz backup pre-atualizacao, atualiza a branch `beta`, instala dependencias se necessario, aplica migrations pendentes, reinicia `o3cloud-manager.service` e executa o healthcheck.

Como esta melhoria nao altera banco de dados, nao ha migration especifica para conferir.

## Validacao pos-atualizacao

1. Enviar ou abrir um link valido de pesquisa de satisfacao da implantacao.
2. Acessar a URL publica `/sucesso-cliente/pesquisa/<token>` em uma tela com altura reduzida.
3. Confirmar que a pagina possui rolagem vertical.
4. Preencher as notas obrigatorias e confirmar que o botao `Enviar avaliacao` fica acessivel sem zoom out.
5. Enviar a pesquisa e confirmar a tela de agradecimento.

## Validacoes tecnicas realizadas

- `git diff --check`

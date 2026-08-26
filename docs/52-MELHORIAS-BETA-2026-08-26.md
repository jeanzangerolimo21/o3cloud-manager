# Melhorias Beta - 26/08/2026

Status: Documentado

Branch: `beta`

Commits de referencia:

- `b02a413` Permite anexos em credenciais do cofre
- `17faf97` Preserva pasta ao voltar do cofre
- `c75d465` Permite salvar checklist tecnico em lote
- `f72232e` Preserva rolagem nas telas operacionais
- `85005bf` Usa usuario logado como autor de comentario
- `b10f39e` Melhora selecao de cliente em licencas O3Web
- `395927c` Permite ranges adicionais em faixas de rede
- `50dcc6c` Torna cliente pesquisavel no cofre de senhas

---

# Objetivo

Registrar as melhorias liberadas para validacao Beta em 26/08/2026, focadas em produtividade operacional nas telas de Implantacao, Cofre de Senhas, Licencas O3Web, Faixas de Rede e navegacao das listagens.

---

# 1. Cofre de Senhas - Anexos em Credenciais

## Problema tratado

Algumas credenciais exigem arquivos vinculados, como documentos de senha, evidencias, planilhas, PDFs ou arquivos de apoio tecnico. Antes, esses arquivos precisavam ficar fora do cadastro da credencial.

## Mudancas implementadas

- O formulario de credencial passou a aceitar upload multiplo de anexos.
- A edicao da credencial exibe os arquivos vinculados com o nome original.
- Os anexos ficam associados diretamente ao registro da credencial.
- O armazenamento respeita os formatos e limite por arquivo definidos para o cofre.

## Resultado operacional

A credencial passa a concentrar usuario, senha, vinculos tecnicos e arquivos relacionados, reduzindo perda de contexto em atendimento e implantacao.

---

# 2. Cofre de Senhas - Retorno Preservando Pasta

## Problema tratado

Ao criar uma nova credencial dentro de uma pasta do cofre, o retorno da tela nao preservava a pasta que estava sendo editada, obrigando o usuario a refazer o caminho.

## Mudancas implementadas

- O fluxo de criacao preserva o contexto da pasta selecionada.
- O botao de voltar e os redirecionamentos consideram `pasta_id` quando disponivel.
- A experiencia de cadastro fica alinhada ao uso por pastas do cofre.

## Resultado operacional

Depois de salvar uma credencial, o usuario retorna ao contexto correto, sem precisar navegar novamente pela arvore de pastas.

---

# 3. Cofre de Senhas - Cliente Pesquisavel

## Problema tratado

O campo `Cliente` no cadastro de credenciais era uma caixa de selecao simples. Em bases com muitos clientes, a selecao exigia rolagem manual e nao seguia o padrao usado em `Ambientes > Novo Ambiente`.

## Mudancas implementadas

- O campo `Cliente` foi trocado para um picker pesquisavel.
- A busca aceita nome fantasia, razao social e CNPJ.
- O usuario digita no proprio campo e seleciona o cliente filtrado.
- O formulario impede salvar texto livre sem selecionar um cliente valido da lista.
- A edicao preserva o cliente atual exibindo o label selecionado.

## Resultado operacional

A criacao e edicao de credenciais ficam mais rapidas e consistentes com o padrao de selecao usado em Ambientes.

---

# 4. Checklist Tecnico - Salvamento em Lote

## Problema tratado

Na visualizacao de implantacoes, o Checklist Tecnico exigia salvar cada item individualmente. Isso tornava lento o preenchimento quando varios itens eram revisados na mesma sessao.

## Mudancas implementadas

- Cada item do checklist recebeu checkbox de selecao para edicao em lote.
- A tela passou a permitir alterar varios itens e salvar todos de uma vez.
- O backend processa apenas os itens selecionados.
- Os testes cobrem o fluxo de atualizacao em lote.

## Resultado operacional

O responsavel tecnico pode revisar e completar varios itens do checklist em uma unica acao, acelerando o preenchimento da implantacao.

---

# 5. Telas Operacionais - Preservacao de Rolagem

## Problema tratado

Em telas com muitas linhas ou cards, como Cofre de Senhas, Contratos, Clientes e outras listagens, selecionar ou desselecionar um item fazia a tela voltar para o topo.

## Mudancas implementadas

- A posicao de rolagem passa a ser preservada durante interacoes de selecao/deselecao.
- O comportamento evita retorno automatico ao cabecalho da pagina.
- O ajuste foi aplicado como melhoria transversal para telas operacionais com listas extensas.

## Resultado operacional

O usuario permanece na mesma area da pagina ao trocar selecoes, reduzindo retrabalho em listas grandes.

---

# 6. Comentarios de Implantacao - Autor pelo Usuario Logado

## Problema tratado

Ao inserir comentario em uma implantacao, o autor era preenchido com o responsavel pela implantacao. Em alguns casos, quem comenta e outra pessoa.

## Mudancas implementadas

- O autor do comentario passou a ser identificado pelo usuario autenticado na sessao.
- O responsavel pela implantacao continua independente do autor do comentario.
- Quando nao houver usuario identificavel, o sistema usa fallback operacional.

## Resultado operacional

O historico de comentarios fica mais fiel a quem realmente registrou a informacao.

---

# 7. Licencas O3Web - Selecao de Cliente Pesquisavel

## Problema tratado

Ao adicionar uma nova licenca O3Web, a selecao do cliente precisava seguir o mesmo padrao de busca usado em `Ambientes > Novo Ambiente`.

## Mudancas implementadas

- O campo de cliente em Licencas O3Web passou a usar picker pesquisavel.
- A busca considera nome fantasia, razao social e CNPJ.
- A selecao continua gravando o `cliente_id` esperado pelo backend.

## Resultado operacional

A criacao de licencas O3Web fica mais rapida para bases com muitos clientes e consistente com o padrao de Ambientes.

---

# 8. Faixas de Rede - Ranges Adicionais de Portas

## Problema tratado

Uma faixa de rede podia armazenar apenas um intervalo de portas principal. Alguns clientes precisam de mais de um intervalo no mesmo FW - WAN.

## Mudancas implementadas

- O formulario de Faixas de Rede recebeu o botao `Adicionar range`.
- Cada range adicional possui `Porta inicio adicional` e `Porta fim adicional`.
- A listagem exibe o range principal junto dos ranges adicionais.
- O backend valida portas entre 1 e 65535.
- O backend impede ranges sobrepostos dentro do mesmo cadastro.
- A verificacao de conflito considera ranges principais e adicionais ja cadastrados no mesmo FW - WAN.

## Migration adicionada

```text
database/migrations/113_create_implantacao_faixas_rede_portas.sql
```

Estrutura criada:

```text
implantacao_faixas_rede_portas
- id
- uuid
- faixa_rede_id
- porta_inicio
- porta_fim
- portas
- created_at
```

## Resultado operacional

A engenharia pode registrar multiplos intervalos de portas para o mesmo cliente/faixa sem criar cadastros duplicados ou perder a validacao de conflitos.

---

# 9. Validacoes Tecnicas Realizadas

- Compilacao Python dos modulos alterados.
- Compilacao dos templates Jinja impactados.
- Testes focados do Checklist Tecnico em lote.
- Testes focados de ranges adicionais em Faixas de Rede.
- Validacao de whitespace nos diffs de templates.
- Push dos commits para `origin beta`.

Testes executados durante as entregas:

```text
venv/bin/python -B -m pytest tests/test_implantacao_checklist_lote.py
venv/bin/python -B -m pytest tests/test_faixa_rede_portas_adicionais.py
python3 -B -m py_compile app/implantacao/routes.py app/implantacao/faixas_rede_service.py app/repositories/faixa_rede_repository.py
```

---

# 10. Procedimento para Atualizar o Beta

1. Fazer backup do banco e do storage antes da atualizacao.
2. Atualizar a branch `beta` para o commit `50dcc6c` ou superior.
3. Aplicar as migrations pendentes, incluindo `113_create_implantacao_faixas_rede_portas.sql`.
4. Reiniciar o servico da aplicacao.
5. Validar as telas:
   - `Implantacao > Cofre de Senhas`
   - `Implantacao > Visualizar Implantacao > Checklist Tecnico`
   - `Implantacao > Licencas O3Web`
   - `Implantacao > Faixas de Rede`
   - Listagens operacionais com selecao de itens

---

# 11. Pontos de Homologacao

## Cofre de Senhas

- Criar credencial dentro de uma pasta e confirmar retorno ao mesmo contexto.
- Anexar um ou mais arquivos em uma credencial.
- Editar a credencial e confirmar exibicao dos nomes dos arquivos vinculados.
- Digitar parte do nome/CNPJ do cliente e selecionar pelo picker pesquisavel.
- Tentar salvar texto digitado sem selecao valida e confirmar bloqueio.

## Checklist Tecnico

- Abrir uma implantacao com varios itens pendentes.
- Selecionar multiplos itens do checklist.
- Alterar valores e salvar em lote.
- Confirmar que itens nao selecionados nao foram modificados.

## Rolagem em Listagens

- Abrir uma listagem com muitos itens.
- Rolar ate o meio/fim da pagina.
- Selecionar e desselecionar itens.
- Confirmar que a pagina permanece na mesma regiao visual.

## Comentarios de Implantacao

- Logar com usuario diferente do responsavel pela implantacao.
- Inserir comentario.
- Confirmar que o autor exibido e o usuario logado.

## Licencas O3Web

- Criar nova licenca.
- Pesquisar cliente por nome fantasia, razao social ou CNPJ.
- Confirmar que a licenca salva vinculada ao cliente selecionado.

## Faixas de Rede

- Criar faixa com range principal e dois ranges adicionais.
- Confirmar exibicao dos ranges na listagem.
- Tentar cadastrar ranges sobrepostos no mesmo registro e confirmar bloqueio.
- Tentar cadastrar range que conflita com outro registro ativo no mesmo FW - WAN e confirmar bloqueio.

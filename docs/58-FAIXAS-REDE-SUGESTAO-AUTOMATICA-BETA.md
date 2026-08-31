# Faixas de Rede - Sugestao Automatica Beta

Data: 31/08/2026

## Objetivo

Reduzir preenchimento manual no cadastro de faixas de rede, sugerindo automaticamente a proxima faixa, os IPs internos, o proximo FW - WAN e o proximo intervalo de portas a partir da ultima faixa ativa cadastrada.

## Tela

A melhoria fica em:

```text
Implantacao > Faixas de Rede
/implantacao/faixas-rede
```

Ao clicar em `Cadastrar manualmente`, o formulario de nova faixa passa a abrir com sugestoes preenchidas.

## Regras de sugestao

- Se o usuario informar `Quantidade de servidores` antes de cadastrar, essa quantidade define a mascara.
- Se a quantidade nao for informada, o sistema usa 5 servidores como padrao e sugere `/29`.
- Ate 5 servidores: mascara `/29`.
- Ate 13 servidores: mascara `/28`.
- Ate 29 servidores: mascara `/27`.
- A nova rede parte da ultima faixa ativa cadastrada e avanca para a proxima rede disponivel.
- Se a ultima faixa ativa for `10.200.101.192/29`, com 5 servidores, a sugestao sera `10.200.101.200/29`.
- O `FW - LAN` usa o primeiro IP util da rede sugerida.
- O campo `PVE` recebe os proximos IPs uteis em sequencia, respeitando a quantidade de servidores.
- O `FW - WAN` tenta incrementar o IP anterior em 1. Exemplo: `10.100.100.120` vira `10.100.100.121`.
- O intervalo principal de portas usa sempre 6 portas: se a ultima porta final for `1600`, a proxima sugestao sera `1601-1606`.
- Se o FW - WAN anterior nao for IPv4 valido, o campo fica em branco.
- Se nao houver porta anterior valida, as portas ficam em branco.

## Botao Calcular

O fluxo antigo de calcular por `Rede base` continua existindo. Quando a sugestao calculada for usada, o link `Usar esta faixa` tambem envia FW - WAN, FW - LAN, PVE e portas sugeridas para o formulario.

## Banco de dados

Esta entrega nao cria migration nova.

A tela depende da migration ja existente:

```text
database/migrations/113_create_implantacao_faixas_rede_portas.sql
```

Essa migration cria `implantacao_faixas_rede_portas`, usada para ranges adicionais e para considerar a maior porta final ja vinculada a ultima faixa ativa.

## Validacao tecnica

Executado em 31/08/2026:

```bash
venv/bin/python -B -m pytest tests/test_faixa_rede_portas_adicionais.py
python3 -B -m py_compile app/implantacao/faixas_rede_service.py app/implantacao/routes.py app/repositories/faixa_rede_repository.py
git diff --check
```

Resultado: 5 testes passaram.

## Validacao pos-atualizacao

1. Abrir `Implantacao > Faixas de Rede`.
2. Informar `Quantidade de servidores` como 5 e clicar em `Cadastrar manualmente`.
3. Confirmar que a nova faixa sugerida segue a ultima faixa ativa cadastrada.
4. Confirmar que `FW - LAN` e `PVE` foram preenchidos com IPs sequenciais.
5. Confirmar que `FW - WAN` foi preenchido com o proximo IP do cadastro anterior quando o valor anterior for IPv4.
6. Confirmar que `Porta inicio` e `Porta fim` foram preenchidas como proximo intervalo de 6 portas.
7. Salvar a faixa e confirmar que a listagem abre sem erro.

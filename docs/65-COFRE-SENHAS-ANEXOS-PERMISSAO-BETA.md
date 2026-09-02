# Cofre de Senhas: permissao para excluir anexos no Beta

Data: 2026-09-02

## Contexto

Usuarios do perfil Operacoes com permissao `cofre_senhas` em leitura e escrita conseguiam criar e editar credenciais, mas recebiam bloqueio ao excluir anexos dessas credenciais.

A rota `implantacao.excluir_anexo_senha_cofre` ja estava vinculada ao modulo `cofre_senhas`, porem o controle global tratava qualquer endpoint com `excluir` como acao restrita aos perfis com permissao administrativa de exclusao.

## Ajuste implementado

- Criada excecao pontual para `implantacao.excluir_anexo_senha_cofre`.
- A excecao permite a exclusao de anexos quando o usuario possui `cofre_senhas` com nivel `EDICAO`.
- Usuarios com `cofre_senhas` apenas em `LEITURA` continuam bloqueados.
- A exclusao da credencial inteira, pasta do cofre e demais exclusoes continuam exigindo perfil com permissao administrativa de exclusao.

## Validacao

Executar:

```bash
venv/bin/python -B -m pytest tests/test_access_control_permissions.py tests/test_cofre_senhas_service.py
```

Cenarios cobertos:

- Operacoes com `cofre_senhas=EDICAO` pode chamar `implantacao.excluir_anexo_senha_cofre`.
- O mesmo perfil nao pode chamar `implantacao.excluir_senha_cofre`.
- Operacoes com `cofre_senhas=LEITURA` nao pode excluir anexos.

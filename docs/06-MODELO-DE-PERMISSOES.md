Administrador

Diretoria

Financeiro

Comercial

Operações

Implantação

Suporte

| Módulo              | Admin | Diretoria | Financeiro | Comercial | Operações |
| ------------------- | ----- | --------- | ---------- | --------- | --------- |
| Dashboard           | ✔     | ✔         | ✔          | ✔         | ✔         |
| Valores Financeiros | ✔     | ✔         | ✔          | ❌        | ❌        |
| Clientes            | CRUD  | Leitura   | CRUD       | Leitura   | Leitura   |
| Contratos           | CRUD  | Leitura   | CRUD       | Leitura   | Leitura   |
| Infraestrutura      | CRUD  | Leitura   | Leitura    | ❌        | CRUD      |
| Licenças            | CRUD  | Leitura   | CRUD       | Leitura   | CRUD      |
| Administração       | CRUD  | ❌        | ❌         | ❌        | ❌        |

Regra importante: ocultar valores financeiros deve ser feito no backend. Usuários sem permissão não devem receber esses dados na resposta da aplicação.


---

# Sprint 16 - Usuarios e Acessos

A administracao de usuarios deve ficar em Configuracoes > Usuarios e Acessos.

Acesso permitido:

- Administrador: acesso completo.
- Diretoria: leitura opcional, sem editar usuarios ou provedores.
- Demais perfis: sem acesso por padrao.

Escopo da tela:

- Usuarios locais convidados por e-mail.
- Usuarios sincronizados por FreeIPA, LDAP ou Active Directory.
- Perfis internos.
- Mapeamento de grupos externos para perfis internos.
- Configuracao e teste de provedores externos.
- Auditoria de acoes sensiveis.

Regra importante: segredos de LDAP, Active Directory e FreeIPA nao devem ser exibidos em texto puro, trafegar em logs ou ser retornados para usuarios sem permissao administrativa.

Documento de detalhamento: `docs/28-AUTENTICACAO-USUARIOS-SPRINT-16.md`


---

# Atualizacao 13/08/2026 - Permissoes Financeiras e Executivos

Nova permissao de menu:

- `receitas_servidor`: libera a tela `Financeiro > Receitas por Servidor` para perfis autorizados no grupo Financeiro.

Regras operacionais adicionadas:

- Exclusao de Executivos permitida apenas para perfis `ADMIN` e `DIRETORIA`.
- A exclusao de Executivo e logica: define `ativo = 0` e remove o vinculo com Parceiro, preservando historico financeiro/contratual.
- Alteracao rapida do status de premiacao do Executivo ocorre pela lista de Executivos e atualiza somente `premiacao_ativa`.
- Importacao de dados de Cliente no cadastro/edicao de Parceiros aparece apenas para perfil `ADMIN`.

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

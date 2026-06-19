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

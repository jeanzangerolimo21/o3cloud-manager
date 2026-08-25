# Manual Geral do O3Cloud Manager

## Objetivo

O O3Cloud Manager centraliza informações comerciais, operacionais, financeiras, administrativas e de infraestrutura para apoiar a gestão da O3Cloud.

O sistema não substitui todos os sistemas especialistas, como OMIE, Proxmox, PBS, TrueNAS ou Zabbix. Ele consolida os dados importantes desses ambientes e organiza os processos internos em uma visão operacional e gerencial.

## Quem deve usar

- Diretoria.
- Comercial.
- Financeiro.
- Administrativo.
- Implantação.
- Operações.
- Engenharia.
- Suporte.

Cada usuário deve acessar apenas os módulos compatíveis com sua função e permissões.

## Acesso ao sistema

O acesso é feito pela tela de login do O3Cloud Manager.

Fluxo básico:

1. Acesse a URL do sistema.
2. Informe e-mail e senha.
3. Caso o segundo fator esteja habilitado, conclua a validação solicitada.
4. Após o login, o sistema exibirá o painel e o menu lateral.

## Navegação

O menu lateral organiza os módulos principais do sistema. Os itens exibidos podem variar conforme o perfil do usuário.

Áreas comuns:

- Dashboards.
- Clientes e contatos.
- Leads, oportunidades e pipeline.
- Propostas e contratos.
- Catálogo.
- Implantação.
- Financeiro.
- Administrativo.
- Infraestrutura.
- Relatórios.
- Configurações.

## Padrão das telas

A maioria das telas segue o mesmo padrão:

- Lista de registros.
- Filtros de pesquisa.
- Botão para novo cadastro.
- Ações de visualizar, editar ou excluir, conforme permissão.
- Página de detalhe com informações do registro.
- Histórico ou rastreabilidade quando aplicável.

## Permissões

O sistema usa perfis e permissões para controlar acesso.

Conceitos importantes:

- Usuário: pessoa que acessa o sistema.
- Perfil: conjunto de permissões aplicado a um ou mais usuários.
- Permissão: autorização para visualizar, criar, editar, excluir ou executar uma função.
- Administrador: usuário com acesso às rotinas sensíveis do sistema.

Boas práticas:

- Cada colaborador deve usar seu próprio usuário.
- Evite compartilhar senhas.
- Permissões administrativas devem ser restritas.
- Usuários desligados devem ser desativados.

## Cadastro e edição

Ao criar ou editar registros:

1. Preencha os campos obrigatórios.
2. Revise nomes, e-mails, CNPJ, valores e datas.
3. Salve o registro.
4. Confira se o registro apareceu corretamente na lista ou na tela de detalhe.

## Anexos e documentos

Alguns módulos permitem anexar arquivos, documentos, propostas, contratos ou evidências.

Cuidados:

- Use nomes de arquivo claros.
- Evite duplicar documentos.
- Confira se o arquivo pertence ao cliente ou processo correto.
- Não envie arquivos sensíveis para registros errados.

## Erros comuns

| Situação | Possível causa | Ação recomendada |
| --- | --- | --- |
| Usuário não vê um menu | Falta de permissão | Solicitar revisão do perfil ao administrador |
| Login não avança | Senha, 2FA ou SMTP | Validar credenciais e configuração de e-mail |
| Cadastro não salva | Campo obrigatório ou formato inválido | Revisar mensagens da tela |
| Registro não aparece | Filtro ativo | Limpar filtros e pesquisar novamente |
| Tela apresenta erro interno | Falha de aplicação ou permissão de arquivo | Acionar administrador com horário e ação realizada |

## Boas práticas gerais

- Pesquise antes de cadastrar para evitar duplicidade.
- Mantenha dados cadastrais atualizados.
- Registre informações relevantes no sistema, não apenas em conversas externas.
- Use filtros e relatórios para acompanhar pendências.
- Em caso de dúvida operacional, consulte o manual do módulo específico.

# Entregas Operacionais - Sprint 16

Versao: 3.0 Alpha

Data: 05/08/2026

Status: Implementado e documentado

---

# Objetivo

Registrar as entregas implementadas durante a Sprint 16 para os fluxos de CRM e documentação operacional, mantendo o sprint aberto para as etapas restantes de governança, auditoria e validação assistida da Beta.

---

# CRM - Eventos e Importação de Participantes

## Funcionalidades

- Criar eventos com nome e data.
- Editar o nome e a data depois da criação.
- Importar participantes individualmente por evento.
- Visualizar participantes somente dentro do evento correspondente.
- Criar nova oportunidade comercial a partir de um participante importado.
- Abrir a oportunidade com título, empresa e observações preenchidas.

## Formatos suportados

- CSV.
- XLS.
- XLSX.

## Mapeamento

O importador sugere automaticamente as colunas para:

- Nome ou nome completo.
- Telefone, celular, WhatsApp ou fone.
- E-mail.
- Empresa, razão social ou fantasia.
- CNPJ.

O usuário pode ajustar manualmente o mapeamento antes da confirmação.

## Validações

- Nome obrigatório.
- E-mail ou telefone obrigatório.
- E-mail normalizado em minúsculas.
- Telefone normalizado para deduplicação e exibido no padrão (DDD) 99999-9999.
- CNPJ numérico validado pelos dígitos verificadores.
- CNPJ alfanumérico de 14 caracteres aceito.
- Duplicidades identificadas dentro do arquivo e no evento.
- Somente linhas válidas são gravadas após confirmação.

## Migration

- database/migrations/063_create_crm_eventos_importacoes.sql

Tabelas:

- crm_eventos
- crm_evento_importacoes
- crm_evento_participantes

## Arquivos principais

- app/leads/evento_importer.py
- app/leads/evento_routes.py
- app/repositories/evento_repository.py
- app/templates/leads/eventos/

## Exemplos validados

- EXPOSUPER: 70 de 80 linhas válidas.
- SUPERBAHIA: 66 de 80 linhas válidas.
- APAS: 532 de 537 linhas válidas.
- Super Inter: 85 de 85 linhas válidas.

---

# Base de Conhecimento

## Funcionalidades

- Criar múltiplas bases independentes.
- Editar o nome e a descrição da base.
- Criar pastas e subpastas.
- Fazer upload de arquivos na raiz ou em pastas.
- Criar conhecimentos dentro de qualquer pasta.
- Editar conhecimentos existentes.
- Utilizar texto livre com formatação básica.
- Inserir imagens no conteúdo de conhecimentos já salvos.
- Adicionar anexos opcionais.
- Adicionar tags separadas por vírgula ou Enter.
- Selecionar catálogo: Todos, Infraestrutura, Clientes ou Procedimentos.
- Marcar conhecimento como compartilhado.
- Pesquisar conhecimentos dentro da localização atual.
- Voltar para a pasta pai ou para a lista de bases.

## Armazenamento

Os arquivos são armazenados exclusivamente em:

/opt/o3cloud-manager/storage/conhecimentos

Cada base possui um diretório físico próprio. O banco armazena apenas:

- Caminho relativo da base.
- Caminho relativo das pastas.
- Caminho relativo dos arquivos.
- Nome original e nome armazenado.
- MIME type e tamanho.
- Relacionamentos entre base, pasta, conhecimento e arquivo.

Limite de upload:

- 25 MB por arquivo.

## Segurança

- Nomes de arquivos e pastas passam por normalização segura.
- Extensões não permitidas são rejeitadas.
- Caminhos são mantidos relativos ao diretório da Base de Conhecimento.
- Conteúdo HTML passa por sanitização antes do salvamento.
- Acesso às rotas depende da permissão base_conhecimento.
- Acesso foi incluído no menu Operações, abaixo do Cofre de Senhas.

## Migration

- database/migrations/064_create_base_conhecimento.sql

Tabelas:

- kb_bases
- kb_pastas
- kb_conhecimentos
- kb_arquivos

## Arquivos principais

- app/conhecimentos/routes.py
- app/conhecimentos/service.py
- app/repositories/conhecimento_repository.py
- app/templates/conhecimentos/

---

# Dependências

Adicionadas para importação de planilhas:

- openpyxl==3.1.5
- xlrd==2.0.1

---

# Validações Técnicas

Executado com sucesso:

- Aplicação das migrations 063 e 064 no banco local.
- Verificação das tabelas criadas.
- Registro das rotas no Flask.
- Compilação dos módulos Python.
- Renderização do formulário de novo conhecimento.
- Teste de sanitização HTML.
- git diff --check.

---

# Status da Sprint 16

A Sprint 16 permanece aberta.

Entregas documentadas nesta etapa:

- Controle inicial de usuários e acessos.
- Bootstrap seguro do administrador.
- Mapeamento de grupos externos.
- Eventos e importação de participantes no CRM.
- Base de Conhecimento.
- Refinamentos de menu, permissões e usabilidade.

Pendências para o fechamento final:

- Consolidar auditoria operacional.
- Executar roteiro de validação assistida da Beta.
- Revisar permissões por perfil.
- Registrar aceite operacional da equipe.

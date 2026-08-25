# Treinamento O3Cloud Manager

## Objetivo

Este material serve como base para treinamento dos colaboradores que irão utilizar o O3Cloud Manager na rotina comercial, operacional, administrativa e gerencial.

A documentação foi organizada por módulos para facilitar a criação de PDFs separados e guias rápidos por área.

## Como usar este material

- Use o Manual Geral no primeiro treinamento de qualquer colaborador.
- Use o manual do módulo apenas com os times que irão operar aquela área.
- Use os guias rápidos como material de consulta no dia a dia.
- Atualize os PDFs sempre que uma nova versão do sistema alterar telas, permissões ou fluxos.

## Manuais disponíveis

| Arquivo | Conteúdo | Público principal |
| --- | --- | --- |
| `01-MANUAL-GERAL.md` | Visão geral, login, navegação, permissões e uso básico | Todos os usuários |
| `02-COMERCIAL.md` | Clientes, contatos, leads, oportunidades, propostas, contratos e pipeline | Comercial, Diretoria |
| `03-CATALOGO.md` | Produtos, categorias, modelos, faixas, recursos, servidores e preços | Comercial, Operações, Financeiro |
| `04-IMPLANTACAO.md` | Implantação, ambientes, integrações, licenças, faixas de rede e cofre de senhas | Implantação, Operações |
| `05-FINANCEIRO-ADMINISTRATIVO.md` | Inadimplências, comissões, faturamentos, reajustes, ASO e rotinas administrativas | Financeiro, Administrativo, Diretoria |
| `06-INFRAESTRUTURA-RELATORIOS.md` | Proxmox, PBS, TrueNAS, Zabbix, dashboards e relatórios | Operações, Engenharia, Diretoria |
| `07-CONFIGURACOES.md` | Usuários, perfis, permissões, e-mail, integrações, backups e atualizações | Administradores |
| `08-BACKUP-RESTORE-ATUALIZACOES.md` | Rotinas críticas de backup, restore e atualização da versão Beta/produção | Administradores, TI |

## Padrão recomendado para gerar PDFs

Cada arquivo Markdown pode ser convertido para PDF com uma ferramenta como Pandoc, Typora, VS Code ou outro editor Markdown.

Exemplo com Pandoc:

```bash
pandoc docs/treinamento/01-MANUAL-GERAL.md -o docs/treinamento/01-MANUAL-GERAL.pdf
```

## Controle de versão

Todo ajuste neste material deve ser salvo no Git junto com as mudanças do sistema. Assim, a documentação acompanha a versão Beta e a futura produção.

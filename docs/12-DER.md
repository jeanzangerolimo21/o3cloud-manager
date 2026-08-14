                                     O3Cloud Manager

                                            │
────────────────────────────────────────────┼────────────────────────────────────────────

                     Financeiro             Infraestrutura             Operações

────────────────────────────────────────────┼────────────────────────────────────────────

Clientes                             Datacenters                 Implantações

Grupos Econômicos                    Clusters                    Licenças

Contratos                            Hosts                       Timeline

Receitas                             Recursos                    Observações

Rateios                              Backups

Rentabilidade                        Monitoramento

────────────────────────────────────────────┼────────────────────────────────────────────

                             Administração            Integrações

────────────────────────────────────────────┼────────────────────────────────────────────

Usuários                              OMIE

Perfis                                Proxmox

Permissões                            NetBox

Auditoria                             PBS

Configurações                         Zabbix

                                      TrueNAS

__________________________________________________________________________________________
Dominio Financeiro
__________________________________________________________________________________________

Grupo Econômico
        │
        │ 1:N
        ▼
Cliente
        │
        │ 1:N
        ▼
Contrato
        │
        ├──────────────┬────────────────────┬────────────────────┐
        ▼              ▼                    ▼                    ▼
 Receita         Contrato Detalhes   Dados Comerciais OMIE  Recebimentos OMIE
                        │                    │
                        ▼                    ▼
                  Licenças O3Web      Vendedor, Projeto,
                                      Bruto, Desconto, Líquido

Contrato
   │
   │ N:N via ambiente_contratos
   ▼
Ambiente
   │
   │ N:N via ambiente_proxmox_recursos
   ▼
Recurso Proxmox
   │
   │ N:1 por integracao_id + node
   ▼
Node Proxmox
   │
   ▼
Receita por Servidor

__________________________________________________________________________________________
Dominio Infraestrutura
__________________________________________________________________________________________

Datacenter
      │
      ▼
Cluster
      │
      ▼
Host
      │
      ▼
Storage
      │
      ▼
Recurso
      │
      ▼
Backup

__________________________________________________________________________________________
Dominio Operações
__________________________________________________________________________________________

Cliente
     │
     ├─────────────┐
     ▼             ▼
Implantação     Licenças
     │
     ▼
Checklist

     │
     ▼
Timeline

_________________________________________________________________________________________

Administracao
_________________________________________________________________________________________

Perfil

↓

Usuário

↓

Permissões

↓

Auditoria

__________________________________________________________________________________________
Integrações
__________________________________________________________________________________________

Integração

↓

Execução

↓

Log

__________________________________________________________________________________________
Estrutura
__________________________________________________________________________________________

                              produtos
                                 │
                                 │
                    ┌────────────┘
                    │
                contratos
                    │
                    ▼
              faturamentos
                    │
                    │
clientes ───────────┘
    │
    │
    ▼
licencas_cliente
    │
    ▼
produtos

clientes
    │
    ▼
clientes_grupos
    │
    ▼
grupos



__________________________________________________________________________________________
Sprint 19 - Inadimplência Financeira
__________________________________________________________________________________________

clientes
    │
    ▼
contratos
    │
    ▼
financeiro_inadimplencias

Regra:

financeiro_inadimplencias.status = PENDENTE
    ↓
cliente com restrição financeira
    ↓
bloqueio de novas propostas e novas implantações

financeiro_inadimplencias.status = LIBERADO
    ↓
histórico preservado
    ↓
cliente liberado somente se não houver outra pendência ativa

financeiro_inadimplencias.ativo = 0
    ↓
remoção lógica restrita ao perfil ADMIN
    ↓
registro sai das consultas operacionais sem exclusão física

__________________________________________________________________________________________
Sprint 20 - Relatórios Customizáveis
__________________________________________________________________________________________

auth_usuarios
    │
    ├──────────────┐
    ▼              ▼
relatorios_modelos     relatorios_execucoes
    │                         ▲
    │                         │
    └─────────────────────────┘
              │
              ▼
        relatorios_jobs

Regra:

relatorios_modelos.configuracao_json
    ↓
fonte, campos, filtros, ordenação, agrupamentos e agregações validados por catálogo interno
    ↓
consulta parametrizada sem SQL livre digitado pelo usuário
    ↓
execução auditada em relatorios_execucoes
    ↓
exportação síncrona ou job assíncrono em relatorios_jobs

Configurações operacionais relacionadas:

config_cache_retencao
    ↓
config_cache_limpezas

config_sincronismos_agendados
    ↓
config_sincronismos_execucoes

__________________________________________________________________________________________
Dominio Autenticacao - 2FA
__________________________________________________________________________________________

Usuario
   │
   ├── 1:N Codigos 2FA por e-mail
   │
   ├── 1:N Dispositivos confiaveis
   │
   └── 1:1 Configuracao TOTP

Regras principais:

* EMAIL usa codigo temporario enviado por SMTP;
* TOTP usa segredo individual configurado em Minha Conta;
* login em duas etapas seleciona EMAIL ou TOTP conforme metodo do usuario;
* dispositivo confiavel permite dispensar segundo fator por ate 30 dias.
__________________________________________________________________________________________
Alertas Operacionais por E-mail
__________________________________________________________________________________________

auth_usuarios
    │
    ├── preferencias de alerta operacional
    │
    ▼
zabbix_alarm_cache + pbs_backup_snapshots + truenas_backup_cache
    │
    ▼
comando flask operacao-alertas-enviar
    │
    ▼
e-mail basico para usuarios selecionados

Regra:

* Zabbix considera alarmes abertos com severidade critica.
* PBS considera recursos ativos sem backup dentro da politica configurada.
* TrueNAS considera diretorios sem modificacao ha mais de 5 dias.
* O usuario recebe somente se estiver habilitado, ativo, com e-mail e no horario/periodicidade configurados.


## Sprint 22 - Monitoramento de Reajustes Contratuais

Novas entidades:

- `contratos_valores_historico`: historico auditavel de valores recorrentes e valores comerciais sincronizados por contrato.
- `financeiro_recebimentos`: fonte operacional do primeiro faturamento recorrente usado como valor base de comparacao quando disponivel.
- `contratos_reajustes_alertas`: controle de alertas por contrato, aniversario e antecedencia, evitando duplicidade.
- `reajustes_configuracoes`: configuracao central das janelas 30/15/7 dias e envio por e-mail.
- `reajustes_configuracoes_usuarios`: usuarios destinatarios de notificacoes/e-mails de reajuste.

Relacionamentos principais:

- `contratos_valores_historico.contrato_id -> contratos.id`
- `financeiro_recebimentos.contrato_id -> contratos.id`
- `contratos_reajustes_alertas.contrato_id -> contratos.id`
- `reajustes_configuracoes_usuarios.configuracao_id -> reajustes_configuracoes.id`
- `reajustes_configuracoes_usuarios.usuario_id -> auth_usuarios.id`

# Manual de Backup, Restore e Atualizações

## Objetivo

Este manual orienta administradores sobre rotinas críticas de backup, restauração e atualização do O3Cloud Manager.

Essas ações podem alterar banco de dados, arquivos do storage e código da aplicação. Execute com atenção e, quando possível, em janela de manutenção.

## Quem deve usar

- Administradores do sistema.
- Responsáveis por TI.
- Equipe autorizada para operação da Beta e futura produção.

## Backups

A tela fica em:

```text
Configurações > Backups do Sistema
```

Tipos comuns:

- Banco de dados.
- Storage.
- Completo.

Destino comum na Beta:

- Storage local.
- Caminho montado ou NAS, quando configurado.

Fluxo recomendado:

1. Acesse Backups do Sistema.
2. Escolha tipo e destino.
3. Gere o backup.
4. Aguarde status OK.
5. Baixe ou copie o arquivo para local seguro.
6. Valide o arquivo quando for backup crítico.

## Restore pela tela

A restauração pela tela deve ser usada com atenção.

Requisitos:

- Permissão administrativa.
- Arquivo de backup válido.
- Confirmação textual `RESTAURAR`.
- Seleção explícita do que será restaurado.

Fluxo recomendado:

1. Avise os usuários sobre janela de manutenção.
2. Gere backup do estado atual.
3. Acesse a tela de restauração.
4. Envie o arquivo de backup.
5. Escolha se irá restaurar banco, storage ou ambos.
6. Digite `RESTAURAR`.
7. Aguarde conclusão.
8. Rode healthcheck.
9. Valide login e telas principais.

## Restore por terminal

Quando necessário, o restore do banco pode ser feito por script operacional.

Exemplo:

```bash
cd /opt/o3cloud-manager
sudo RESTORE_CONFIRM=o3cloud_manager deployment/restore-db.sh /caminho/do/backup.tar.gz --yes
deployment/healthcheck.sh
```

Para storage, valide permissões após a restauração:

```bash
sudo chown -R o3cloud:o3cloud /opt/o3cloud-manager/storage
sudo chmod 0770 /opt/o3cloud-manager/storage
sudo systemctl restart o3cloud-manager
deployment/healthcheck.sh
```

## Atualizações do Sistema

A tela fica em:

```text
Configurações > Atualizações do Sistema
```

Uso planejado:

- Atualizar primeiro o servidor Beta.
- Validar com usuários-chave.
- Depois repetir o processo em produção, quando existir.

Fluxo recomendado:

1. Confirmar que as alterações foram publicadas no GitHub na branch correta.
2. Acessar Atualizações do Sistema.
3. Selecionar branch `beta` para o servidor Beta.
4. Digitar `ATUALIZAR`.
5. Iniciar atualização.
6. Acompanhar log.
7. Confirmar healthcheck OK.
8. Validar login e fluxos principais.

## Runner de atualização

Para o painel conseguir atualizar o sistema, o runner precisa estar instalado no servidor.

Instalação:

```bash
cd /opt/o3cloud-manager
sudo bash deployment/install-update-runner.sh
sudo systemctl restart o3cloud-manager
deployment/healthcheck.sh
```

Acompanhamento do log:

```bash
tail -f /opt/o3cloud-manager/logs/update-beta-*.log
```

Execução manual, se necessário:

```bash
sudo /usr/local/sbin/o3cloud-update-beta
```

## Condições para atualizar com segurança

- O repositório local deve estar limpo, sem alterações manuais pendentes.
- A branch correta deve existir no GitHub.
- O banco deve estar acessível.
- O backup pré-atualização deve ser gerado com sucesso.
- O healthcheck deve retornar OK após o restart.

## Validações após atualização

Execute:

```bash
deployment/healthcheck.sh
```

Também valide pela interface:

- Login.
- Dashboard principal.
- Clientes.
- Propostas.
- Contratos.
- Configurações.
- Backups.
- Atualizações.

## Erros comuns

| Situação | Possível causa | Ação recomendada |
| --- | --- | --- |
| Atualização não inicia | Runner não instalado | Rodar `install-update-runner.sh` |
| Atualização bloqueada | Alterações locais no servidor | Fazer commit/stash ou revisar mudanças |
| Healthcheck falha | Serviço, banco ou HTTP indisponível | Verificar logs e status do systemd |
| Restore falha por permissão | Storage com dono root | Corrigir `chown` e `chmod` |
| Backup inválido | Arquivo corrompido ou formato errado | Gerar novo backup e validar |

## Boas práticas

- Nunca atualizar produção antes de validar na Beta.
- Guardar backup fora do próprio servidor.
- Registrar data, versão e responsável pela atualização.
- Validar fluxos críticos após cada atualização.
- Evitar alterações manuais diretamente no servidor Beta.

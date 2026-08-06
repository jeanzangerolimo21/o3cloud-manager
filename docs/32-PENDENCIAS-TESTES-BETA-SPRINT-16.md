# Pendencias de Testes da Release Beta - Sprint 16

Versao: 3.0 Alpha

Data de encaminhamento: 06/08/2026

Status: Encaminhadas para a release Beta

---

# Objetivo

Registrar as validacoes assistidas que permanecem pendentes e serao executadas quando a release Beta estiver disponivel para uso acompanhado pela equipe.

Estas pendencias nao bloqueiam o fechamento tecnico da Sprint 16. O resultado de cada teste deve ser registrado durante a Beta com status aprovado, aprovado com ajuste ou reprovado.

---

# Roteiro de Testes Pendentes

## 1. Usuarios, Login e Convites

- Criar usuario local e enviar convite por e-mail.
- Aceitar convite e cadastrar senha propria.
- Validar bloqueio, reativacao e expiracao de convite.
- Confirmar login, logout e redirecionamento de rota protegida.
- Validar bootstrap do primeiro administrador em ambiente homologado.

## 2. Permissoes, Perfis e Valores

- Revisar a matriz de permissoes com representantes das areas.
- Validar acesso de administrador, gestor, operador e usuario somente leitura.
- Confirmar diferenca entre visualizacao e edicao.
- Confirmar ocultacao de valores comerciais e financeiros quando `mostrar_valores` estiver desabilitado.
- Validar comportamento de GET, POST, PUT e DELETE em rotas protegidas.

## 3. Auditoria e Seguranca

- Confirmar auditoria de login, alteracoes administrativas e operacoes sensiveis.
- Verificar usuario, entidade, acao, IP e user agent registrados.
- Confirmar que senhas, tokens, chaves, CPF e CNPJ nao aparecem nos detalhes auditados.
- Validar consulta administrativa e retencao inicial de eventos.

## 4. CRM, Importacoes e E-mails

- Revalidar importacoes CSV, XLS e XLSX com planilhas oficiais.
- Confirmar mapeamento, normalizacao, deduplicacao e criacao de oportunidade.
- Disparar e-mail para participantes de evento com anexo controlado.
- Confirmar status, totais, erros e configuracao utilizada no registro do disparo.
- Validar comentarios internos de propostas e compartilhamento por e-mail.

## 5. Regras Comerciais e Parceiros

- Cadastrar, editar e inativar regras de campanhas e comissao.
- Confirmar bloqueio de sobreposicao de vigencias ativas.
- Validar categoria de parceiros nas listagens e detalhes.
- Importar a planilha oficial de hardware por parceiro e conferir a normalizacao dos registros.

## 6. Cofre e Inventarios Tecnicos

- Criar compartilhamento temporario do cofre com dados controlados.
- Confirmar expiracao, primeiro acesso, revogacao, token em hash e registro de IP.
- Validar vinculos com inventarios Proxmox, PBS e Zabbix.
- Confirmar associacao com hosts Zabbix sincronizados sem executar automacoes destrutivas.

## 7. Integracoes Externas

- Testar SMTP e Brevo com credenciais homologadas.
- Confirmar limite diario, remetente, reply-to, ambiente, HTML e anexo.
- Validar comunicacao e autenticacao LDAP/Active Directory quando o ambiente estiver disponivel.
- Validar sincronismo de usuarios e grupos FreeIPA/LDAP/AD e mapeamento para perfis internos.
- Registrar timeout, falha de credencial, indisponibilidade e mensagem apresentada ao usuario.

---

# Registro do Resultado

Para cada etapa, registrar:

- Data e ambiente do teste.
- Responsavel e area participante.
- Dados ou credenciais utilizadas, sem registrar segredos.
- Resultado: aprovado, aprovado com ajuste ou reprovado.
- Evidencia ou referencia da tela/fluxo validado.
- Pendencia criada, quando aplicavel.

---

# Condicao de Encerramento das Pendencias

As pendencias serao encerradas apos a execucao do roteiro na Beta, registro dos resultados e aceite operacional das areas envolvidas. Falhas encontradas devem ser encaminhadas para correcao ou nova sprint, sem alterar retroativamente o fechamento tecnico da Sprint 16.

# Pendencias de Testes da Release Beta - Sprint 18

Versao: 3.0 Alpha

Data de encaminhamento: 06/08/2026

Status: Encaminhadas para a release Beta

---

# Objetivo

Registrar os testes assistidos e a homologacao do Modulo Administrativo que serao executados com a equipe na release Beta.

O Sprint 17 permanece fora do corte atual e sera retomado apos o alinhamento dos processos com as equipes Comercial e Financeiro.

---

# Roteiro de Homologacao

## 1. Demandas e Permissoes

- Criar, editar, consultar e cancelar demandas.
- Validar categorias, prioridades, status, prazos, responsavel e departamento.
- Confirmar que gestores podem administrar demandas e colaboradores visualizam apenas as suas.
- Validar leitura e edicao pela matriz de permissoes do grupo Administrativo.

## 2. Agenda

- Consultar agenda geral e agenda individual.
- Validar visoes Hoje, Semana, Mes e Lista.
- Reagendar uma demanda diretamente pela agenda e conferir o historico da alteracao.
- Validar filtro por responsável e prazo.
- Confirmar que colaborador nao visualiza agendas de terceiros.
- Validar demanda sem prazo e demanda atrasada calculada pela data limite.

## 3. Comentarios, Historico e Anexos

- Adicionar comentarios em demandas permitidas.
- Editar comentario pelo proprio autor e confirmar que gestor, diretoria ou administrador pode moderar comentarios de terceiros.
- Inativar comentario e confirmar que ele deixa de aparecer na conversa sem remover os registros de historico ou auditoria.
- Confirmar historico de criacao, alteracao, reatribuicao, comentario e cancelamento.
- Anexar arquivos permitidos e confirmar acesso ao arquivo salvo.
- Validar limites de extensao e tamanho conforme o storage existente.

## 4. Notificacoes

- Criar demanda atribuida a um colaborador ativo.
- Confirmar notificacao visual no menu e na tela de notificacoes.
- Confirmar envio de e-mail para o endereco do responsavel.
- Validar notificacoes de nova demanda e reatribuicao.
- Marcar uma notificacao como lida e conferir atualizacao do contador.
- Marcar todas as notificacoes como lidas e confirmar que o contador do menu zera.
- Abrir a demanda a partir da notificacao e conferir o status do envio de e-mail.
- Alterar prazo ou registrar comentario e confirmar nova notificacao visual e por e-mail para o responsavel.

## 5. Dashboards e Relatorios

- Conferir totais de demandas abertas, pendentes, em andamento, concluidas e atrasadas.
- Validar visao do gestor e visao restrita do colaborador.
- Conferir relatorio por responsavel, concluidas e atrasadas.
- Confirmar que demandas canceladas nao aparecem como pendencias abertas.

## 6. Auditoria

- Confirmar registros no menu Configuracoes > Auditoria.
- Validar usuario, acao, entidade, identificador, IP e user agent.
- Confirmar que detalhes nao registram senhas, tokens ou outros segredos.

---

# Registro do Resultado

Para cada etapa, registrar data, ambiente, responsavel, perfil utilizado, resultado, evidencia e pendencia encontrada. Os resultados devem ser classificados como aprovado, aprovado com ajuste ou reprovado.

Falhas encontradas devem ser encaminhadas para correcao ou nova sprint, sem considerar a homologacao Beta como concluida automaticamente pela implementacao tecnica.

# O3Cloud Manager v3.0

# 15 - CHECKLIST DE DESENVOLVIMENTO

Versão: 1.0

Status: Oficial

---

# Objetivo

Este documento define o checklist obrigatório antes da conclusão de qualquer tarefa.

Todo desenvolvedor (humano ou IA) deve executar este checklist antes de considerar uma implementação finalizada.

---

# 1. Arquitetura

Verificar:

- [ ] A arquitetura Repository → Service → Routes → Templates foi respeitada.
- [ ] Não foi criada arquitetura paralela.
- [ ] O código segue o 03-ARQUITETURA.md.

---

# 2. Repository

Verificar:

- [ ] Não existe regra de negócio.
- [ ] Não existe HTML.
- [ ] Não existe Flask.
- [ ] Não existe Request.
- [ ] Utiliza BaseRepository.
- [ ] Utiliza Prepared Statements.
- [ ] Utiliza connection().
- [ ] Utiliza close().

---

# 3. Service

Verificar:

- [ ] Toda validação está no Service.
- [ ] Não existe SQL.
- [ ] Não existe HTML.
- [ ] Não existe Flask.
- [ ] Não existe acesso direto ao banco.

---

# 4. Routes

Verificar:

- [ ] Apenas recebe Request.
- [ ] Apenas chama Service.
- [ ] Apenas renderiza Template.
- [ ] Apenas executa Redirect.
- [ ] Apenas executa Flash Messages.

---

# 5. Templates

Verificar:

- [ ] Utiliza index_base.html.
- [ ] Utiliza form_base.html.
- [ ] Utiliza view_base.html.
- [ ] Utiliza page_header.html.
- [ ] Utiliza filter_bar.html.
- [ ] Utiliza crud_actions.html.
- [ ] Utiliza alert.html.
- [ ] Não existe HTML duplicado.

---

# 6. Banco de Dados

Verificar:

- [ ] Utiliza UUID.
- [ ] Utiliza Soft Delete.
- [ ] Não existe DELETE físico.
- [ ] Utiliza BaseRepository.generate_uuid().
- [ ] Utiliza BaseRepository.bool_to_int().

---

# 7. Código

Verificar:

- [ ] Código limpo.
- [ ] Métodos padronizados.
- [ ] Classes padronizadas.
- [ ] Imports organizados.
- [ ] Sem código morto.
- [ ] Sem comentários desnecessários.

---

# 8. Interface

Verificar:

- [ ] Layout compatível.
- [ ] Responsivo.
- [ ] Bootstrap 5.
- [ ] Componentes compartilhados.
- [ ] Botões padronizados.
- [ ] Flash Messages funcionando.

---

# 9. Testes

Verificar:

- [ ] Arquivo sem erro de sintaxe.
- [ ] AST validado.
- [ ] Jinja validado.
- [ ] Fluxo testado.
- [ ] CRUD funcionando.

---

# 10. Git

Verificar:

- [ ] Git Diff revisado.
- [ ] Apenas arquivos esperados foram alterados.
- [ ] Não existem arquivos temporários.
- [ ] Não existem arquivos órfãos.

---

# 11. Documentação

Verificar:

- [ ] Roadmap atualizado.
- [ ] Sprint atual atualizada.
- [ ] Changelog atualizado (quando aplicável).

---

# 12. Homologação

Verificar:

- [ ] Arquivo homologado.
- [ ] Usuário validou.
- [ ] Próxima tarefa autorizada.

---

# Regra Oficial

Nenhuma tarefa poderá ser considerada concluída antes da execução completa deste checklist.

O Codex deverá utilizar este documento como referência obrigatória ao finalizar qualquer implementação.

Este checklist faz parte da arquitetura oficial do O3Cloud Manager.

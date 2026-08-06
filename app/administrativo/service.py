from datetime import date, datetime

from app.core.email import EmailService
from app.core.storage import StorageService
from app.repositories.administrativo_repository import AdministrativoRepository


class AdministrativoService:
    repository = AdministrativoRepository
    CATEGORIAS = ("ADMINISTRATIVO", "FINANCEIRO", "COMERCIAL", "IMPLANTACAO", "SUPORTE", "INFRAESTRUTURA", "RH", "DIRETORIA", "OUTROS")
    PRIORIDADES = ("BAIXA", "NORMAL", "ALTA", "URGENTE")
    STATUS = ("PENDENTE", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA")

    @classmethod
    def contexto_index(cls, filtros, usuario_id):
        demandas = cls.repository.listar_demandas(filtros, 50, 0)
        return {"demandas": demandas, "total": cls.repository.total_demandas(filtros), "dashboard": cls.repository.dashboard(usuario_id),
                "departamentos": cls.repository.listar_departamentos(), "usuarios": cls.repository.listar_usuarios_ativos()}

    @classmethod
    def criar(cls, dados, arquivos, usuario_email):
        payload = cls._normalizar(dados)
        payload["possui_anexos"] = bool(arquivos) or payload.get("possui_anexos") or anterior.get("possui_anexos")
        payload["criado_por"] = usuario_email; payload["updated_by"] = usuario_email
        cls._validar(payload)
        demanda_id = cls.repository.inserir_demanda(payload)
        cls.repository.inserir_historico(demanda_id, {"tipo": "CRIACAO", "comentario": "Demanda criada.", "status_novo": payload["status"], "responsavel_novo_id": payload.get("responsavel_id"), "autor_email": usuario_email})
        cls._notificar_responsavel(demanda_id, payload.get("responsavel_id"), "NOVA_DEMANDA", "Nova demanda atribuída", payload["titulo"])
        cls._salvar_anexos(demanda_id, arquivos)
        return demanda_id

    @classmethod
    def atualizar(cls, demanda_id, dados, arquivos, usuario_email):
        anterior = cls.repository.buscar_demanda(demanda_id)
        if not anterior: raise ValueError("Demanda não encontrada.")
        payload = cls._normalizar(dados); payload["possui_anexos"] = bool(arquivos) or payload.get("possui_anexos"); payload["updated_by"] = usuario_email; cls._validar(payload)
        cls.repository.atualizar_demanda(demanda_id, payload)
        if anterior.get("status") != payload.get("status") or anterior.get("responsavel_id") != payload.get("responsavel_id"):
            cls.repository.inserir_historico(demanda_id, {"tipo": "ALTERACAO", "comentario": "Demanda atualizada.", "status_anterior": anterior.get("status"), "status_novo": payload.get("status"), "responsavel_anterior_id": anterior.get("responsavel_id"), "responsavel_novo_id": payload.get("responsavel_id"), "autor_email": usuario_email})
        if anterior.get("responsavel_id") != payload.get("responsavel_id"):
            cls._notificar_responsavel(demanda_id, payload.get("responsavel_id"), "DEMANDA_REATRIBUIDA", "Demanda atribuída a você", payload["titulo"])
        elif (anterior.get("status") != payload.get("status") or anterior.get("data_limite") != payload.get("data_limite")) and payload.get("responsavel_id"):
            labels = {"CONCLUIDA": "Demanda concluída", "CANCELADA": "Demanda cancelada", "EM_ANDAMENTO": "Demanda em andamento", "PENDENTE": "Demanda pendente"}
            titulo = labels.get(payload.get("status"), "Prazo da demanda atualizado")
            cls._notificar_responsavel(demanda_id, payload.get("responsavel_id"), "DEMANDA_ATUALIZADA", titulo, payload["titulo"])
        cls._salvar_anexos(demanda_id, arquivos)

    @classmethod
    def comentar(cls, demanda_id, comentario, arquivos, usuario_email):
        demanda = cls.repository.buscar_demanda(demanda_id)
        if not demanda: raise ValueError("Demanda não encontrada.")
        if not demanda.get("permitir_comentarios"): raise ValueError("Comentários estão desabilitados para esta demanda.")
        texto = (comentario or "").strip()
        if not texto: raise ValueError("Informe um comentário.")
        comentario_id = cls.repository.inserir_comentario(demanda_id, texto, usuario_email)
        cls.repository.inserir_historico(demanda_id, {"tipo": "COMENTARIO", "comentario": texto, "autor_email": usuario_email})
        cls._salvar_anexos(demanda_id, arquivos, comentario_id)
        cls._notificar_responsavel(demanda_id, demanda.get("responsavel_id"), "NOVO_COMENTARIO", "Novo comentário na sua demanda", demanda["titulo"], usuario_email)

    @classmethod
    def editar_comentario(cls, demanda_id, comentario_id, texto, usuario_email, moderador=False):
        comentario = cls.repository.buscar_comentario(comentario_id, demanda_id)
        if not comentario or not comentario.get("ativo"):
            raise ValueError("Comentário não encontrado.")
        if not moderador and (comentario.get("autor_email") or "").lower() != (usuario_email or "").lower():
            raise ValueError("Somente o autor ou um gestor pode editar este comentário.")
        texto = (texto or "").strip()
        if not texto:
            raise ValueError("Informe um comentário.")
        cls.repository.atualizar_comentario(comentario_id, texto)
        cls.repository.inserir_historico(demanda_id, {"tipo": "COMENTARIO_EDITADO", "comentario": texto, "autor_email": usuario_email})

    @classmethod
    def excluir_comentario(cls, demanda_id, comentario_id, usuario_email, moderador=False):
        comentario = cls.repository.buscar_comentario(comentario_id, demanda_id)
        if not comentario or not comentario.get("ativo"):
            raise ValueError("Comentário não encontrado.")
        if not moderador and (comentario.get("autor_email") or "").lower() != (usuario_email or "").lower():
            raise ValueError("Somente o autor ou um gestor pode excluir este comentário.")
        cls.repository.inativar_comentario(comentario_id)
        cls.repository.inserir_historico(demanda_id, {"tipo": "COMENTARIO_INATIVADO", "comentario": "Comentário inativado.", "autor_email": usuario_email})

    @classmethod
    def cancelar(cls, demanda_id, usuario_email):
        demanda = cls.repository.buscar_demanda(demanda_id)
        if not demanda: raise ValueError("Demanda não encontrada.")
        cls.repository.excluir_demanda(demanda_id, usuario_email)
        cls.repository.inserir_historico(demanda_id, {"tipo": "CANCELAMENTO", "status_anterior": demanda.get("status"), "status_novo": "CANCELADA", "autor_email": usuario_email})

    @classmethod
    def detalhe(cls, demanda_id):
        demanda = cls.repository.buscar_demanda(demanda_id)
        if demanda:
            demanda["historico"] = cls.repository.listar_historico(demanda_id)
            demanda["comentarios"] = cls.repository.listar_comentarios(demanda_id)
            demanda["anexos"] = cls.repository.listar_anexos(demanda_id)
        return demanda

    @classmethod
    def notificar_pendencias(cls, usuario_id):
        return cls.repository.listar_notificacoes(usuario_id)

    @classmethod
    def marcar_notificacao(cls, notificacao_id, usuario_id):
        cls.repository.marcar_notificacao_lida(notificacao_id, usuario_id)

    @classmethod
    def marcar_notificacoes(cls, usuario_id):
        if usuario_id:
            cls.repository.marcar_notificacoes_lidas(usuario_id)

    @classmethod
    def _notificar_responsavel(cls, demanda_id, usuario_id, tipo, titulo, demanda_titulo, ignorar_email=None):
        if not usuario_id: return
        usuario = next((item for item in cls.repository.listar_usuarios_ativos() if int(item["id"]) == int(usuario_id)), None)
        if not usuario: return
        if ignorar_email and (usuario.get("email") or "").lower() == ignorar_email.lower(): return
        mensagem = f"{titulo}: {demanda_titulo}. Acesse o módulo Administrativo para acompanhar a atividade."
        notificacao_id = cls.repository.criar_notificacao(usuario_id, demanda_id, tipo, titulo, mensagem)
        enviado = False
        try: enviado = bool(EmailService.enviar(titulo, mensagem, [usuario.get("email")]).get("enviado"))
        except Exception: enviado = False
        if enviado: cls.repository.execute("UPDATE administrativo_notificacoes SET email_enviado=1 WHERE id=%s", (notificacao_id,))

    @classmethod
    def _salvar_anexos(cls, demanda_id, arquivos, comentario_id=None):
        for arquivo in arquivos or []:
            if not arquivo or not arquivo.filename: continue
            pasta = f"administrativo/{demanda_id}"
            salvo = StorageService.salvar(arquivo, pasta)
            if salvo: cls.repository.inserir_anexo(demanda_id, salvo, comentario_id)

    @classmethod
    def _normalizar(cls, dados):
        def texto(chave): return (dados.get(chave) or "").strip() or None
        def inteiro(chave):
            valor = texto(chave)
            return int(valor) if valor else None
        status = (texto("status") or "PENDENTE").upper()
        return {"titulo": texto("titulo"), "descricao": texto("descricao"), "categoria": (texto("categoria") or "OUTROS").upper(), "prioridade": (texto("prioridade") or "NORMAL").upper(), "responsavel_id": inteiro("responsavel_id"), "departamento_id": inteiro("departamento_id"), "data_inicial": cls._data(dados.get("data_inicial")), "data_limite": cls._data(dados.get("data_limite")), "hora": texto("hora"), "status": status, "observacoes": texto("observacoes"), "permitir_comentarios": cls._flag(dados, "permitir_comentarios"), "possui_anexos": bool(dados.get("possui_anexos") or dados.get("anexos"))}

    @classmethod
    def _validar(cls, payload):
        if not payload["titulo"]: raise ValueError("Título é obrigatório.")
        if payload["categoria"] not in cls.CATEGORIAS: raise ValueError("Categoria inválida.")
        if payload["prioridade"] not in cls.PRIORIDADES: raise ValueError("Prioridade inválida.")
        if payload["status"] not in cls.STATUS: raise ValueError("Status inválido.")
        if payload["data_inicial"] and payload["data_limite"] and payload["data_limite"] < payload["data_inicial"]: raise ValueError("Data limite não pode ser anterior à data inicial.")

    @staticmethod
    def _data(valor):
        if not valor: return None
        if hasattr(valor, "year"): return valor
        try: return datetime.strptime(str(valor), "%Y-%m-%d").date()
        except ValueError as erro: raise ValueError("Informe uma data válida.") from erro

    @staticmethod
    def _flag(dados, chave):
        return str(dados.get(chave) or "").lower() in ("1", "true", "on", "sim")

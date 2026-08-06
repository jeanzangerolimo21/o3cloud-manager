from datetime import date, datetime, timedelta
import calendar

from app.core.email import EmailService
from app.core.storage import StorageService
from app.repositories.administrativo_repository import AdministrativoRepository


class AdministrativoService:
    repository = AdministrativoRepository
    CATEGORIAS = ("ADMINISTRATIVO", "FINANCEIRO", "COMERCIAL", "IMPLANTACAO", "SUPORTE", "INFRAESTRUTURA", "RH", "DIRETORIA", "OUTROS")
    PRIORIDADES = ("BAIXA", "NORMAL", "ALTA", "URGENTE")
    STATUS = ("PENDENTE", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA")
    RECORRENCIA_TIPOS = ("DIARIA", "SEMANAL", "MENSAL", "ANUAL")

    @classmethod
    def contexto_index(cls, filtros, usuario_id):
        demandas = cls.repository.listar_demandas(filtros, 50, 0)
        return {"demandas": demandas, "total": cls.repository.total_demandas(filtros), "dashboard": cls.repository.dashboard_completo(usuario_id),
                "departamentos": cls.repository.listar_departamentos(), "usuarios": cls.repository.listar_usuarios_ativos()}

    @classmethod
    def criar(cls, dados, arquivos, usuario_email):
        payload = cls._normalizar(dados)
        payload["possui_anexos"] = bool(arquivos) or payload.get("possui_anexos")
        payload["criado_por"] = usuario_email; payload["updated_by"] = usuario_email
        cls._validar(payload)
        demanda_id = cls.repository.inserir_demanda(payload)
        cls.repository.inserir_historico(demanda_id, {"tipo": "CRIACAO", "comentario": "Demanda criada.", "status_novo": payload["status"], "responsavel_novo_id": payload.get("responsavel_id"), "autor_email": usuario_email})
        cls._notificar_responsavel(demanda_id, payload.get("responsavel_id"), "NOVA_DEMANDA", "Nova demanda atribuída", payload["titulo"])
        cls._salvar_anexos(demanda_id, arquivos)
        cls._criar_ocorrencias_recorrentes(demanda_id, payload)
        return demanda_id

    @classmethod
    def _criar_ocorrencias_recorrentes(cls, demanda_id, payload):
        datas = cls._datas_recorrentes(payload)
        if not datas:
            return
        duracao = None
        if payload.get("data_inicial") and payload.get("data_limite"):
            duracao = payload["data_limite"] - payload["data_inicial"]
        for data_limite in datas:
            clone = dict(payload)
            clone["data_limite"] = data_limite
            clone["data_inicial"] = data_limite - duracao if duracao else data_limite
            clone["recorrente"] = False
            clone["recorrencia_tipo"] = None
            clone["recorrencia_dia_semana"] = None
            clone["recorrencia_dia_mes"] = None
            clone["recorrencia_mes"] = None
            clone["recorrencia_data_fim"] = None
            clone["recorrencia_id"] = demanda_id
            clone_id = cls.repository.inserir_demanda(clone)
            cls.repository.inserir_historico(clone_id, {"tipo": "RECORRENCIA", "comentario": f"Ocorrência criada a partir da demanda {demanda_id}.", "status_novo": clone["status"], "responsavel_novo_id": clone.get("responsavel_id"), "autor_email": payload.get("criado_por")})


    @classmethod
    def _datas_recorrentes(cls, payload):
        if not payload.get("recorrente"):
            return []
        inicio = payload.get("data_limite") or payload.get("data_inicial")
        fim = payload.get("recorrencia_data_fim")
        tipo = payload.get("recorrencia_tipo")
        if not inicio or not fim or tipo not in cls.RECORRENCIA_TIPOS:
            return []
        datas = []
        cursor = inicio
        while len(datas) < 366:
            if tipo == "DIARIA":
                cursor += timedelta(days=1)
            elif tipo == "SEMANAL":
                cursor += timedelta(days=1)
                while cursor.weekday() != int(payload.get("recorrencia_dia_semana") or inicio.weekday()):
                    cursor += timedelta(days=1)
            elif tipo == "MENSAL":
                mes = cursor.month + 1
                ano = cursor.year + (1 if mes == 13 else 0)
                mes = 1 if mes == 13 else mes
                dia = min(int(payload.get("recorrencia_dia_mes") or inicio.day), calendar.monthrange(ano, mes)[1])
                cursor = date(ano, mes, dia)
            else:
                ano = cursor.year + 1
                mes = int(payload.get("recorrencia_mes") or inicio.month)
                dia = min(int(payload.get("recorrencia_dia_mes") or inicio.day), calendar.monthrange(ano, mes)[1])
                cursor = date(ano, mes, dia)
            if cursor > fim:
                break
            datas.append(cursor)
        return datas

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
    def comentar(cls, demanda_id, comentario, arquivos, usuario_email, usuario_id=None, colaborador=False):
        demanda = cls.repository.buscar_demanda(demanda_id)
        if not demanda: raise ValueError("Demanda não encontrada.")
        if not demanda.get("permitir_comentarios"): raise ValueError("Comentários estão desabilitados para esta demanda.")
        if colaborador and int(demanda.get("responsavel_id") or 0) != int(usuario_id or 0): raise ValueError("Você só pode comentar nas suas próprias demandas.")
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
        return {"titulo": texto("titulo"), "descricao": texto("descricao"), "categoria": (texto("categoria") or "OUTROS").upper(), "prioridade": (texto("prioridade") or "NORMAL").upper(), "responsavel_id": inteiro("responsavel_id"), "departamento_id": inteiro("departamento_id"), "data_inicial": cls._data(dados.get("data_inicial")), "data_limite": cls._data(dados.get("data_limite")), "hora": texto("hora"), "status": status, "observacoes": texto("observacoes"), "permitir_comentarios": cls._flag(dados, "permitir_comentarios"), "possui_anexos": bool(dados.get("possui_anexos") or dados.get("anexos")), "recorrente": cls._flag(dados, "recorrente"), "recorrencia_tipo": (texto("recorrencia_tipo") or "").upper() or None, "recorrencia_dia_semana": inteiro("recorrencia_dia_semana"), "recorrencia_dia_mes": inteiro("recorrencia_dia_mes"), "recorrencia_mes": inteiro("recorrencia_mes"), "recorrencia_data_fim": cls._data(dados.get("recorrencia_data_fim")), "recorrencia_id": inteiro("recorrencia_id")}

    @classmethod
    def _validar(cls, payload):
        if not payload["titulo"]: raise ValueError("Título é obrigatório.")
        if payload["categoria"] not in cls.CATEGORIAS: raise ValueError("Categoria inválida.")
        if payload["prioridade"] not in cls.PRIORIDADES: raise ValueError("Prioridade inválida.")
        if payload["status"] not in cls.STATUS: raise ValueError("Status inválido.")
        if payload["data_inicial"] and payload["data_limite"] and payload["data_limite"] < payload["data_inicial"]: raise ValueError("Data limite não pode ser anterior à data inicial.")
        if payload.get("recorrente"):
            if not (payload.get("data_limite") or payload.get("data_inicial")): raise ValueError("Informe uma data para a primeira ocorrência.")
            if payload.get("recorrencia_tipo") not in cls.RECORRENCIA_TIPOS: raise ValueError("Selecione o tipo de recorrência.")
            if not payload.get("recorrencia_data_fim"): raise ValueError("Informe até quando a recorrência deve ser criada.")
            if payload.get("recorrencia_data_fim") < (payload.get("data_limite") or payload.get("data_inicial")): raise ValueError("O fim da recorrência deve ser posterior à primeira ocorrência.")
            if payload.get("recorrencia_tipo") == "SEMANAL" and payload.get("recorrencia_dia_semana") is None: raise ValueError("Selecione o dia da semana.")
            if payload.get("recorrencia_tipo") == "MENSAL" and not 1 <= int(payload.get("recorrencia_dia_mes") or 0) <= 31: raise ValueError("Informe o dia do mês.")
            if payload.get("recorrencia_tipo") == "ANUAL" and not (1 <= int(payload.get("recorrencia_mes") or 0) <= 12 and 1 <= int(payload.get("recorrencia_dia_mes") or 0) <= 31): raise ValueError("Informe mês e dia da recorrência anual.")

    @staticmethod
    def _data(valor):
        if not valor: return None
        if hasattr(valor, "year"): return valor
        try: return datetime.strptime(str(valor), "%Y-%m-%d").date()
        except ValueError as erro: raise ValueError("Informe uma data válida.") from erro

    @staticmethod
    def _flag(dados, chave):
        return str(dados.get(chave) or "").lower() in ("1", "true", "on", "sim")

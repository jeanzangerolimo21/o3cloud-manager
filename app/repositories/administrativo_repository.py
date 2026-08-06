from datetime import date

from app.repositories.base_repository import BaseRepository


class AdministrativoRepository(BaseRepository):
    @classmethod
    def listar_departamentos(cls):
        return cls.fetch_all("SELECT id, uuid, nome FROM administrativo_departamentos WHERE ativo=1 ORDER BY nome")

    @classmethod
    def listar_usuarios_ativos(cls):
        return cls.fetch_all("SELECT id, nome, email, login, perfil_id, possui_agenda FROM auth_usuarios WHERE status='ATIVO' ORDER BY nome")

    @classmethod
    def listar_demandas(cls, filtros=None, limite=100, offset=0):
        filtros = filtros or {}
        where, params = cls._filtros_demandas(filtros)
        params.extend([limite, offset])
        return cls.fetch_all(f"""
            SELECT d.*, u.nome AS responsavel_nome, u.email AS responsavel_email,
                   dep.nome AS departamento_nome,
                   CASE WHEN d.status NOT IN ('CONCLUIDA','CANCELADA') AND d.data_limite < CURRENT_DATE THEN 'ATRASADA' ELSE d.status END AS status_calculado
            FROM administrativo_demandas d
            LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id
            LEFT JOIN administrativo_departamentos dep ON dep.id=d.departamento_id
            {where} ORDER BY d.data_limite IS NULL, d.data_limite ASC, FIELD(d.prioridade,'URGENTE','ALTA','NORMAL','BAIXA'), d.id DESC
            LIMIT %s OFFSET %s
        """, tuple(params))

    @classmethod
    def total_demandas(cls, filtros=None):
        where, params = cls._filtros_demandas(filtros or {})
        return cls.scalar(f"SELECT COUNT(*) FROM administrativo_demandas d {where}", tuple(params)) or 0

    @classmethod
    def buscar_demanda(cls, demanda_id):
        return cls.fetch_one("""SELECT d.*, u.nome AS responsavel_nome, u.email AS responsavel_email, dep.nome AS departamento_nome
            FROM administrativo_demandas d LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id
            LEFT JOIN administrativo_departamentos dep ON dep.id=d.departamento_id WHERE d.id=%s""", (demanda_id,))

    @classmethod
    def inserir_demanda(cls, dados):
        return cls.execute_insert("""INSERT INTO administrativo_demandas
            (uuid,titulo,descricao,categoria,prioridade,responsavel_id,departamento_id,data_inicial,data_limite,hora,status,observacoes,permitir_comentarios,possui_anexos,criado_por,updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
            cls.generate_uuid(), dados.get('titulo'), dados.get('descricao'), dados.get('categoria'), dados.get('prioridade'),
            dados.get('responsavel_id'), dados.get('departamento_id'), dados.get('data_inicial'), dados.get('data_limite'),
            dados.get('hora'), dados.get('status'), dados.get('observacoes'), cls.bool_to_int(dados.get('permitir_comentarios', True)),
            cls.bool_to_int(dados.get('possui_anexos', False)), dados.get('criado_por'), dados.get('updated_by')))

    @classmethod
    def atualizar_demanda(cls, demanda_id, dados):
        return cls.execute("""UPDATE administrativo_demandas SET titulo=%s,descricao=%s,categoria=%s,prioridade=%s,
            responsavel_id=%s,departamento_id=%s,data_inicial=%s,data_limite=%s,hora=%s,status=%s,observacoes=%s,
            permitir_comentarios=%s,possui_anexos=%s,updated_by=%s,concluida_em=CASE WHEN %s='CONCLUIDA' THEN COALESCE(concluida_em,NOW()) ELSE NULL END WHERE id=%s""", (
            dados.get('titulo'), dados.get('descricao'), dados.get('categoria'), dados.get('prioridade'), dados.get('responsavel_id'),
            dados.get('departamento_id'), dados.get('data_inicial'), dados.get('data_limite'), dados.get('hora'), dados.get('status'),
            dados.get('observacoes'), cls.bool_to_int(dados.get('permitir_comentarios', True)), cls.bool_to_int(dados.get('possui_anexos', False)),
            dados.get('updated_by'), dados.get('status'), demanda_id))

    @classmethod
    def excluir_demanda(cls, demanda_id, usuario_email):
        return cls.execute("UPDATE administrativo_demandas SET status='CANCELADA', updated_by=%s WHERE id=%s", (usuario_email, demanda_id))

    @classmethod
    def inserir_historico(cls, demanda_id, dados):
        return cls.execute_insert("""INSERT INTO administrativo_historico
            (uuid,demanda_id,tipo,comentario,status_anterior,status_novo,responsavel_anterior_id,responsavel_novo_id,autor_email)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (cls.generate_uuid(), demanda_id, dados.get('tipo'), dados.get('comentario'),
            dados.get('status_anterior'), dados.get('status_novo'), dados.get('responsavel_anterior_id'), dados.get('responsavel_novo_id'), dados.get('autor_email')))

    @classmethod
    def listar_historico(cls, demanda_id):
        return cls.fetch_all("SELECT * FROM administrativo_historico WHERE demanda_id=%s ORDER BY created_at DESC,id DESC", (demanda_id,))

    @classmethod
    def inserir_comentario(cls, demanda_id, comentario, autor_email):
        return cls.execute_insert("INSERT INTO administrativo_comentarios (uuid,demanda_id,comentario,autor_email) VALUES (%s,%s,%s,%s)", (cls.generate_uuid(), demanda_id, comentario, autor_email))

    @classmethod
    def buscar_comentario(cls, comentario_id, demanda_id):
        return cls.fetch_one("SELECT * FROM administrativo_comentarios WHERE id=%s AND demanda_id=%s", (comentario_id, demanda_id))

    @classmethod
    def atualizar_comentario(cls, comentario_id, comentario):
        return cls.execute("UPDATE administrativo_comentarios SET comentario=%s,updated_at=NOW() WHERE id=%s", (comentario, comentario_id))

    @classmethod
    def inativar_comentario(cls, comentario_id):
        return cls.execute("UPDATE administrativo_comentarios SET ativo=0,updated_at=NOW() WHERE id=%s", (comentario_id,))

    @classmethod
    def listar_comentarios(cls, demanda_id):
        return cls.fetch_all("SELECT * FROM administrativo_comentarios WHERE demanda_id=%s AND ativo=1 ORDER BY created_at DESC,id DESC", (demanda_id,))

    @classmethod
    def inserir_anexo(cls, demanda_id, dados, comentario_id=None):
        return cls.execute_insert("""INSERT INTO administrativo_anexos (uuid,demanda_id,comentario_id,arquivo_original,nome_arquivo,caminho,url,mime_type,tamanho)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (cls.generate_uuid(), demanda_id, comentario_id, dados.get('arquivo_original'), dados.get('nome'), dados.get('caminho'), dados.get('url'), dados.get('mime_type'), dados.get('tamanho', 0)))

    @classmethod
    def listar_anexos(cls, demanda_id):
        return cls.fetch_all("SELECT * FROM administrativo_anexos WHERE demanda_id=%s ORDER BY created_at DESC,id DESC", (demanda_id,))

    @classmethod
    def listar_agenda(cls, usuario_id=None, data_inicio=None, data_fim=None):
        where = ["d.status NOT IN ('CANCELADA')"]
        params = []
        if usuario_id:
            where.append("d.responsavel_id=%s"); params.append(usuario_id)
        if data_inicio:
            where.append("(d.data_limite IS NULL OR d.data_limite >= %s)"); params.append(data_inicio)
        if data_fim:
            where.append("(d.data_inicial IS NULL OR d.data_inicial <= %s)"); params.append(data_fim)
        return cls.fetch_all("""SELECT d.*,u.nome AS responsavel_nome,dep.nome AS departamento_nome,
            CASE WHEN d.status NOT IN ('CONCLUIDA','CANCELADA') AND d.data_limite < CURRENT_DATE THEN 'ATRASADA' ELSE d.status END AS status_calculado
            FROM administrativo_demandas d LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id LEFT JOIN administrativo_departamentos dep ON dep.id=d.departamento_id
            WHERE """ + " AND ".join(where) + " ORDER BY d.data_limite IS NULL,d.data_limite,d.hora,d.id", tuple(params))

    @classmethod
    def garantir_agenda(cls, usuario_id, ativo, usuario_email="sistema"):
        existente = cls.fetch_one("SELECT id FROM administrativo_agendas WHERE usuario_id=%s", (usuario_id,))
        if existente:
            return cls.execute("UPDATE administrativo_agendas SET ativo=%s WHERE usuario_id=%s", (cls.bool_to_int(ativo), usuario_id))
        if ativo:
            return cls.execute_insert("INSERT INTO administrativo_agendas (uuid,usuario_id,ativo,created_by) VALUES (%s,%s,1,%s)", (cls.generate_uuid(), usuario_id, usuario_email))
        return None



    @classmethod
    def criar_notificacao(cls, usuario_id, demanda_id, tipo, titulo, mensagem):
        return cls.execute_insert("INSERT INTO administrativo_notificacoes (uuid,usuario_id,demanda_id,tipo,titulo,mensagem) VALUES (%s,%s,%s,%s,%s,%s)", (cls.generate_uuid(), usuario_id, demanda_id, tipo, titulo, mensagem))

    @classmethod
    def listar_notificacoes(cls, usuario_id, limite=50):
        return cls.fetch_all("SELECT * FROM administrativo_notificacoes WHERE usuario_id=%s ORDER BY lida_em IS NULL DESC,created_at DESC,id DESC LIMIT %s", (usuario_id, limite))

    @classmethod
    def contar_notificacoes(cls, usuario_id):
        return cls.scalar("SELECT COUNT(*) FROM administrativo_notificacoes WHERE usuario_id=%s AND lida_em IS NULL", (usuario_id,)) or 0

    @classmethod
    def marcar_notificacao_lida(cls, notificacao_id, usuario_id):
        return cls.execute("UPDATE administrativo_notificacoes SET lida_em=NOW() WHERE id=%s AND usuario_id=%s", (notificacao_id, usuario_id))

    @classmethod
    def marcar_notificacoes_lidas(cls, usuario_id):
        return cls.execute("UPDATE administrativo_notificacoes SET lida_em=NOW() WHERE usuario_id=%s AND lida_em IS NULL", (usuario_id,))

    @classmethod
    def dashboard(cls, usuario_id=None):
        filtro = "WHERE responsavel_id=%s" if usuario_id else ""
        params = (usuario_id,) if usuario_id else ()
        resumo = cls.fetch_one(f"""SELECT COUNT(*) total, SUM(status='PENDENTE') pendentes, SUM(status='EM_ANDAMENTO') andamento,
            SUM(status='CONCLUIDA') concluidas, SUM(prioridade='URGENTE' AND status NOT IN ('CONCLUIDA','CANCELADA')) urgentes,
            SUM(status NOT IN ('CONCLUIDA','CANCELADA') AND data_limite < CURRENT_DATE) atrasadas FROM administrativo_demandas {filtro}""", params) or {}
        return resumo

    @classmethod
    def relatorio(cls, usuario_id=None):
        filtro = "WHERE d.responsavel_id=%s" if usuario_id else ""
        params = (usuario_id,) if usuario_id else ()
        return cls.fetch_all(f"""SELECT COALESCE(u.nome,'Sem responsavel') responsavel, COUNT(*) total,
            SUM(d.status='CONCLUIDA') concluidas, SUM(d.status NOT IN ('CONCLUIDA','CANCELADA') AND d.data_limite < CURRENT_DATE) atrasadas
            FROM administrativo_demandas d LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id {filtro}
            GROUP BY d.responsavel_id,u.nome ORDER BY total DESC""", params)


    @classmethod
    def dashboard_completo(cls, usuario_id=None):
        resumo = cls.dashboard(usuario_id)
        filtro = "WHERE d.responsavel_id=%s" if usuario_id else ""
        params = (usuario_id,) if usuario_id else ()
        agenda = cls.fetch_one(f"SELECT SUM(d.data_limite=CURRENT_DATE AND d.status NOT IN (\'CANCELADA\')) agenda_hoje, SUM(d.data_limite BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE, INTERVAL 6 DAY) AND d.status NOT IN (\'CANCELADA\')) agenda_semana FROM administrativo_demandas d {filtro}", params) or {}
        tempo = cls.fetch_one(f"SELECT ROUND(AVG(TIMESTAMPDIFF(HOUR, d.created_at, d.concluida_em)), 1) tempo_medio_horas FROM administrativo_demandas d {filtro} AND d.concluida_em IS NOT NULL" if filtro else "SELECT ROUND(AVG(TIMESTAMPDIFF(HOUR, d.created_at, d.concluida_em)), 1) tempo_medio_horas FROM administrativo_demandas d WHERE d.concluida_em IS NOT NULL", params) or {}
        ranking = cls.fetch_all(f"SELECT COALESCE(u.nome, \"Sem responsavel\") responsavel, COUNT(*) total, SUM(d.status=\'CONCLUIDA\') concluidas, SUM(d.status NOT IN (\'CONCLUIDA\',\'CANCELADA\') AND d.data_limite < CURRENT_DATE) atrasadas FROM administrativo_demandas d LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id {filtro} GROUP BY d.responsavel_id,u.nome ORDER BY concluidas DESC,total DESC LIMIT 10", params)
        resumo.update(agenda); resumo.update(tempo); resumo["ranking"] = ranking
        return resumo


    @classmethod
    def relatorio_periodo(cls, usuario_id=None, data_inicio=None, data_fim=None):
        where = ["1=1"]
        params = []
        if usuario_id:
            where.append("d.responsavel_id=%s"); params.append(usuario_id)
        if data_inicio:
            where.append("d.data_limite >= %s"); params.append(data_inicio)
        if data_fim:
            where.append("d.data_limite <= %s"); params.append(data_fim)
        clausula = "WHERE " + " AND ".join(where)
        return cls.fetch_all(f"SELECT COALESCE(u.nome, \"Sem responsavel\") responsavel, COALESCE(dep.nome, \"Sem departamento\") departamento, COUNT(*) total, SUM(d.status=\'PENDENTE\') pendentes, SUM(d.status=\'EM_ANDAMENTO\') andamento, SUM(d.status=\'CONCLUIDA\') concluidas, SUM(d.status NOT IN (\'CONCLUIDA\',\'CANCELADA\') AND d.data_limite < CURRENT_DATE) atrasadas FROM administrativo_demandas d LEFT JOIN auth_usuarios u ON u.id=d.responsavel_id LEFT JOIN administrativo_departamentos dep ON dep.id=d.departamento_id {clausula} GROUP BY d.responsavel_id,u.nome,d.departamento_id,dep.nome ORDER BY total DESC", tuple(params))


    @staticmethod
    def _filtros_demandas(filtros):
        where = []
        params = []
        if filtros.get('q'):
            where.append("(d.titulo LIKE %s OR d.descricao LIKE %s OR d.observacoes LIKE %s)")
            termo = f"%{filtros['q']}%"; params.extend([termo, termo, termo])
        if filtros.get('status'):
            where.append("d.status=%s"); params.append(filtros['status'])
        if filtros.get('responsavel_id'):
            where.append("d.responsavel_id=%s"); params.append(filtros['responsavel_id'])
        if filtros.get('departamento_id'):
            where.append("d.departamento_id=%s"); params.append(filtros['departamento_id'])
        return ("WHERE " + " AND ".join(where)) if where else "", params

from app.repositories.base_repository import BaseRepository


class AdministrativoAsoRepository(BaseRepository):
    @classmethod
    def listar_clientes_ativos(cls):
        return cls.fetch_all("""
            SELECT id, nome_fantasia, razao_social, cnpj
            FROM clientes
            WHERE ativo=1
            ORDER BY COALESCE(nome_fantasia, razao_social), razao_social
        """)

    @classmethod
    def listar_clientes_com_colaboradores(cls):
        return cls.fetch_all("""
            SELECT c.id, COALESCE(c.nome_fantasia, c.razao_social, a.cliente_nome) AS nome, COUNT(a.id) AS total_colaboradores
            FROM administrativo_aso_colaboradores a
            LEFT JOIN clientes c ON c.id=a.cliente_id
            GROUP BY c.id, COALESCE(c.nome_fantasia, c.razao_social, a.cliente_nome)
            ORDER BY nome
        """)

    @classmethod
    def listar_usuarios_agenda(cls):
        return cls.fetch_all("""
            SELECT u.id, u.nome, u.email, u.possui_agenda, p.codigo AS perfil_codigo
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id=u.perfil_id
            WHERE u.status='ATIVO' AND u.possui_agenda=1
            ORDER BY p.codigo='ADMINISTRATIVO_GESTOR' DESC, u.nome
        """)

    @classmethod
    def listar_usuarios_agenda_por_ids(cls, usuario_ids):
        ids = [int(item) for item in usuario_ids or [] if item]
        if not ids:
            return []
        placeholders = ",".join(["%s"] * len(ids))
        return cls.fetch_all(f"""
            SELECT u.id, u.nome, u.email, u.possui_agenda, p.codigo AS perfil_codigo
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id=u.perfil_id
            WHERE u.status='ATIVO' AND u.possui_agenda=1 AND u.id IN ({placeholders})
        """, tuple(ids))

    @classmethod
    def listar_colaboradores(cls, filtros=None):
        filtros = filtros or {}
        where = ["1=1"]
        params = []
        if filtros.get("q"):
            termo = f"%{filtros['q']}%"
            cpf = f"%{''.join(ch for ch in str(filtros['q']) if ch.isdigit())}%"
            where.append("(a.nome_completo LIKE %s OR a.cpf LIKE %s OR COALESCE(c.nome_fantasia,c.razao_social,a.cliente_nome) LIKE %s)")
            params.extend([termo, cpf, termo])
        if filtros.get("cliente_id"):
            where.append("a.cliente_id=%s")
            params.append(filtros["cliente_id"])
        if filtros.get("status"):
            where.append("a.status=%s")
            params.append(filtros["status"])
        return cls.fetch_all(f"""
            SELECT a.*, COALESCE(c.nome_fantasia, c.razao_social, a.cliente_nome) AS cliente_exibicao, c.cnpj AS cliente_cnpj,
                   (SELECT MAX(l.data_aso) FROM administrativo_aso_lembretes l WHERE l.colaborador_id=a.id) AS proximo_aso,
                   (SELECT COUNT(*) FROM administrativo_aso_exames e WHERE e.colaborador_id=a.id) AS total_exames,
                   (SELECT COUNT(*) FROM administrativo_aso_lembretes l WHERE l.colaborador_id=a.id) AS total_lembretes
            FROM administrativo_aso_colaboradores a
            LEFT JOIN clientes c ON c.id=a.cliente_id
            WHERE {" AND ".join(where)}
            ORDER BY a.updated_at DESC, a.id DESC
            LIMIT 200
        """, tuple(params))

    @classmethod
    def buscar_colaborador(cls, colaborador_id):
        return cls.fetch_one("""
            SELECT a.*, COALESCE(c.nome_fantasia, c.razao_social, a.cliente_nome) AS cliente_exibicao, c.cnpj AS cliente_cnpj
            FROM administrativo_aso_colaboradores a
            LEFT JOIN clientes c ON c.id=a.cliente_id
            WHERE a.id=%s
        """, (colaborador_id,))

    @classmethod
    def buscar_colaborador_por_cpf(cls, cpf, ignorar_id=None):
        params = [cpf]
        filtro_ignorar = ""
        if ignorar_id:
            filtro_ignorar = " AND id<>%s"
            params.append(ignorar_id)
        return cls.fetch_one(f"""
            SELECT id, nome_completo, cpf
            FROM administrativo_aso_colaboradores
            WHERE cpf=%s{filtro_ignorar}
            LIMIT 1
        """, tuple(params))

    @classmethod
    def inserir_colaborador(cls, dados):
        return cls.execute_insert("""
            INSERT INTO administrativo_aso_colaboradores
            (uuid,cliente_id,cliente_nome,nome_completo,cpf,data_nascimento,data_admissao,status,criado_por,updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            cls.generate_uuid(), dados.get("cliente_id"), dados.get("cliente_nome"), dados.get("nome_completo"),
            dados.get("cpf"), dados.get("data_nascimento"), dados.get("data_admissao"), dados.get("status"),
            dados.get("criado_por"), dados.get("updated_by"),
        ))

    @classmethod
    def atualizar_colaborador(cls, colaborador_id, dados):
        return cls.execute("""
            UPDATE administrativo_aso_colaboradores
            SET cliente_id=%s, cliente_nome=%s, nome_completo=%s, cpf=%s, data_nascimento=%s,
                data_admissao=%s, status=%s, updated_by=%s
            WHERE id=%s
        """, (
            dados.get("cliente_id"), dados.get("cliente_nome"), dados.get("nome_completo"), dados.get("cpf"),
            dados.get("data_nascimento"), dados.get("data_admissao"), dados.get("status"), dados.get("updated_by"),
            colaborador_id,
        ))

    @classmethod
    def excluir_colaborador(cls, colaborador_id):
        return cls.execute("DELETE FROM administrativo_aso_colaboradores WHERE id=%s", (colaborador_id,))

    @classmethod
    def inserir_exame(cls, colaborador_id, dados):
        return cls.execute_insert("""
            INSERT INTO administrativo_aso_exames
            (uuid,colaborador_id,arquivo_original,nome_arquivo,caminho,url,mime_type,tamanho)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            cls.generate_uuid(), colaborador_id, dados.get("arquivo_original"), dados.get("nome"),
            dados.get("caminho"), dados.get("url"), dados.get("mime_type"), dados.get("tamanho", 0),
        ))

    @classmethod
    def listar_exames(cls, colaborador_id):
        return cls.fetch_all("SELECT * FROM administrativo_aso_exames WHERE colaborador_id=%s ORDER BY created_at DESC,id DESC", (colaborador_id,))

    @classmethod
    def buscar_exame(cls, exame_id, colaborador_id):
        return cls.fetch_one("SELECT * FROM administrativo_aso_exames WHERE id=%s AND colaborador_id=%s", (exame_id, colaborador_id))

    @classmethod
    def excluir_exame(cls, exame_id, colaborador_id):
        return cls.execute("DELETE FROM administrativo_aso_exames WHERE id=%s AND colaborador_id=%s", (exame_id, colaborador_id))

    @classmethod
    def inserir_lembrete(cls, dados):
        return cls.execute_insert("""
            INSERT INTO administrativo_aso_lembretes
            (uuid,colaborador_id,demanda_id,usuario_id,data_aso,antecedencia_dias,tipo_participacao,enviar_email,created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            cls.generate_uuid(), dados.get("colaborador_id"), dados.get("demanda_id"), dados.get("usuario_id"),
            dados.get("data_aso"), dados.get("antecedencia_dias"), dados.get("tipo_participacao"),
            cls.bool_to_int(dados.get("enviar_email", True)), dados.get("created_by"),
        ))

    @classmethod
    def listar_lembretes(cls, colaborador_id):
        return cls.fetch_all("""
            SELECT l.*, d.titulo, d.status AS demanda_status, u.nome AS usuario_nome, u.email AS usuario_email
            FROM administrativo_aso_lembretes l
            LEFT JOIN administrativo_demandas d ON d.id=l.demanda_id
            LEFT JOIN auth_usuarios u ON u.id=l.usuario_id
            WHERE l.colaborador_id=%s
            ORDER BY l.data_aso DESC, l.id DESC
        """, (colaborador_id,))

    @classmethod
    def buscar_lembrete(cls, lembrete_id, colaborador_id):
        return cls.fetch_one("SELECT * FROM administrativo_aso_lembretes WHERE id=%s AND colaborador_id=%s", (lembrete_id, colaborador_id))

    @classmethod
    def excluir_lembrete(cls, lembrete_id, colaborador_id):
        return cls.execute("DELETE FROM administrativo_aso_lembretes WHERE id=%s AND colaborador_id=%s", (lembrete_id, colaborador_id))

    @classmethod
    def listar_lembretes_pendentes(cls, limite=20):
        return cls.fetch_all("""
            SELECT l.*, a.nome_completo, a.cpf, COALESCE(c.nome_fantasia,c.razao_social,a.cliente_nome) AS cliente_exibicao,
                   d.titulo, u.email AS usuario_email
            FROM administrativo_aso_lembretes l
            JOIN administrativo_aso_colaboradores a ON a.id=l.colaborador_id
            JOIN administrativo_demandas d ON d.id=l.demanda_id
            JOIN auth_usuarios u ON u.id=l.usuario_id
            LEFT JOIN clientes c ON c.id=a.cliente_id
            WHERE l.aviso_enviado=0
              AND l.enviar_email=1
              AND DATE_SUB(l.data_aso, INTERVAL l.antecedencia_dias DAY) <= CURRENT_DATE
              AND d.status NOT IN ('CONCLUIDA','CANCELADA')
            ORDER BY l.data_aso ASC, l.id ASC
            LIMIT %s
        """, (int(limite),))

    @classmethod
    def marcar_lembrete_enviado(cls, lembrete_id):
        return cls.execute("UPDATE administrativo_aso_lembretes SET aviso_enviado=1,aviso_enviado_em=NOW(),erro_email=NULL WHERE id=%s", (lembrete_id,))

    @classmethod
    def marcar_lembrete_erro(cls, lembrete_id, erro):
        return cls.execute("UPDATE administrativo_aso_lembretes SET erro_email=%s WHERE id=%s", (str(erro)[:2000], lembrete_id))

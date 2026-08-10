from app.repositories.base_repository import BaseRepository


class InadimplenciaRepository(BaseRepository):
    @classmethod
    def listar(cls, filtros=None, limit=50, offset=0):
        filtros = filtros or {}
        sql = cls._select_base()
        where, params = cls._filtros(filtros)
        sql += where
        sql += """
            ORDER BY fi.status = 'PENDENTE' DESC, fi.bloqueado_em DESC, fi.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, filtros=None):
        filtros = filtros or {}
        sql = """
            SELECT COUNT(*)
            FROM financeiro_inadimplencias fi
            INNER JOIN contratos c ON c.id = fi.contrato_id
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN auth_usuarios ub ON ub.id = fi.bloqueado_por
            LEFT JOIN auth_usuarios ul ON ul.id = fi.liberado_por
        """
        where, params = cls._filtros(filtros)
        return cls.scalar(sql + where, tuple(params)) or 0

    @classmethod
    def buscar_por_id(cls, inadimplencia_id):
        return cls.fetch_one(cls._select_base() + " WHERE fi.id=%s", (inadimplencia_id,))

    @classmethod
    def buscar_ativa_por_contrato(cls, contrato_id):
        return cls.fetch_one(
            cls._select_base() + " WHERE fi.contrato_id=%s AND fi.status='PENDENTE' AND fi.ativo=1 LIMIT 1",
            (contrato_id,),
        )

    @classmethod
    def listar_ativas_por_cliente(cls, cliente_id):
        return cls.fetch_all(
            cls._select_base() + " WHERE c.cliente_id=%s AND fi.status='PENDENTE' AND fi.ativo=1 ORDER BY fi.bloqueado_em DESC",
            (cliente_id,),
        )

    @classmethod
    def cliente_possui_pendencia(cls, cliente_id):
        return bool(cls.scalar(
            """
            SELECT 1
            FROM financeiro_inadimplencias fi
            INNER JOIN contratos c ON c.id = fi.contrato_id
            WHERE c.cliente_id=%s AND fi.status='PENDENTE' AND fi.ativo=1
            LIMIT 1
            """,
            (cliente_id,),
        ))

    @classmethod
    def clientes_com_pendencia(cls, cliente_ids):
        ids = [int(item) for item in cliente_ids if item]
        if not ids:
            return {}
        placeholders = ",".join(["%s"] * len(ids))
        rows = cls.fetch_all(
            f"""
            SELECT c.cliente_id, COUNT(*) AS total, MIN(fi.bloqueado_em) AS primeira_pendencia
            FROM financeiro_inadimplencias fi
            INNER JOIN contratos c ON c.id = fi.contrato_id
            WHERE c.cliente_id IN ({placeholders}) AND fi.status='PENDENTE' AND fi.ativo=1
            GROUP BY c.cliente_id
            """,
            tuple(ids),
        )
        return {row["cliente_id"]: row for row in rows}

    @classmethod
    def contratos_para_select(cls, pesquisa=None, limit=100):
        params = []
        where = ["c.ativo=1"]
        if pesquisa:
            pesquisa = pesquisa.strip()
            termo = f"%{pesquisa}%"
            cnpj_normalizado = "".join(ch for ch in pesquisa if ch.isalnum()).upper()
            where.append(
                "(c.numero LIKE %s OR cli.nome_fantasia LIKE %s OR cli.razao_social LIKE %s "
                "OR cli.cnpj LIKE %s OR UPPER(REGEXP_REPLACE(cli.cnpj, '[^0-9A-Za-z]', '')) LIKE %s)"
            )
            params.extend([termo, termo, termo, termo, f"%{cnpj_normalizado}%"])
        params.append(limit)
        return cls.fetch_all(
            f"""
            SELECT c.id, c.numero, c.status, c.valor_mensal, c.valor_promocional,
                   c.cliente_id, cli.email AS cliente_email,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   cli.razao_social AS cliente_razao_social, cli.cnpj AS cliente_cnpj,
                   CASE WHEN fi.id IS NULL THEN 0 ELSE 1 END AS inadimplencia_ativa
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN financeiro_inadimplencias fi
              ON fi.contrato_id = c.id AND fi.status='PENDENTE' AND fi.ativo=1
            WHERE {' AND '.join(where)}
            ORDER BY cli.nome_fantasia ASC, c.numero ASC
            LIMIT %s
            """,
            tuple(params),
        )

    @classmethod
    def criar(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO financeiro_inadimplencias (
                uuid, contrato_id, status, motivo, observacoes, bloqueado_em,
                bloqueado_por, bloqueado_por_email
            ) VALUES (UUID(), %s, 'PENDENTE', %s, %s, COALESCE(%s, NOW()), %s, %s)
            """,
            (
                dados["contrato_id"], dados.get("motivo"), dados.get("observacoes"),
                dados.get("bloqueado_em"), dados.get("bloqueado_por"), dados.get("bloqueado_por_email"),
            ),
        )

    @classmethod
    def liberar(cls, inadimplencia_id, dados):
        return cls.execute(
            """
            UPDATE financeiro_inadimplencias
            SET status='LIBERADO', tipo_liberacao=%s, observacao_liberacao=%s,
                liberado_em=COALESCE(%s, NOW()), liberado_por=%s, liberado_por_email=%s
            WHERE id=%s AND status='PENDENTE' AND ativo=1
            """,
            (
                dados.get("tipo_liberacao"), dados.get("observacao_liberacao"), dados.get("liberado_em"),
                dados.get("liberado_por"), dados.get("liberado_por_email"), inadimplencia_id,
            ),
        )

    @classmethod
    def excluir_historico(cls, inadimplencia_id):
        return cls.execute(
            """
            UPDATE financeiro_inadimplencias
            SET ativo=0
            WHERE id=%s AND ativo=1
            """,
            (inadimplencia_id,),
        )

    @classmethod
    def atualizar_email_status(cls, inadimplencia_id, campos):
        permitidos = {
            "email_suporte_enviado", "email_cliente_enviado", "email_liberacao_suporte_enviado",
            "email_liberacao_cliente_enviado", "erro_email_suporte", "erro_email_cliente",
            "erro_email_liberacao_suporte", "erro_email_liberacao_cliente",
        }
        sets = []
        params = []
        for campo, valor in campos.items():
            if campo in permitidos:
                sets.append(f"{campo}=%s")
                params.append(valor)
        if not sets:
            return 0
        params.append(inadimplencia_id)
        return cls.execute(f"UPDATE financeiro_inadimplencias SET {', '.join(sets)} WHERE id=%s", tuple(params))

    @staticmethod
    def _select_base():
        return """
            SELECT fi.*, c.numero AS contrato_numero, c.status AS contrato_status,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS contrato_valor_mensal,
                   c.cliente_id, cli.email AS cliente_email, cli.cnpj AS cliente_cnpj,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   cli.razao_social AS cliente_razao_social,
                   ub.nome AS bloqueado_por_nome, ul.nome AS liberado_por_nome
            FROM financeiro_inadimplencias fi
            INNER JOIN contratos c ON c.id = fi.contrato_id
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN auth_usuarios ub ON ub.id = fi.bloqueado_por
            LEFT JOIN auth_usuarios ul ON ul.id = fi.liberado_por
        """

    @staticmethod
    def _filtros(filtros):
        where = ["fi.ativo=1"]
        params = []
        if filtros.get("q"):
            termo = f"%{filtros['q']}%"
            where.append("(cli.nome_fantasia LIKE %s OR cli.razao_social LIKE %s OR cli.cnpj LIKE %s OR c.numero LIKE %s)")
            params.extend([termo, termo, termo, termo])
        if filtros.get("status"):
            where.append("fi.status=%s")
            params.append(filtros["status"])
        if filtros.get("responsavel_id"):
            where.append("(fi.bloqueado_por=%s OR fi.liberado_por=%s)")
            params.extend([filtros["responsavel_id"], filtros["responsavel_id"]])
        if filtros.get("data_de"):
            where.append("DATE(fi.bloqueado_em) >= %s")
            params.append(filtros["data_de"])
        if filtros.get("data_ate"):
            where.append("DATE(fi.bloqueado_em) <= %s")
            params.append(filtros["data_ate"])
        return " WHERE " + " AND ".join(where), params

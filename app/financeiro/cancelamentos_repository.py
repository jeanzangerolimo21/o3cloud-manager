from app.repositories.base_repository import BaseRepository


class CancelamentoRepository(BaseRepository):
    @classmethod
    def listar(cls, filtros=None, limit=50, offset=0):
        where, params = cls._filtros(filtros or {})
        return cls.fetch_all(
            cls._select_base() + where + " ORDER BY fc.data_desligamento ASC, fc.id DESC LIMIT %s OFFSET %s",
            tuple(params + [limit, offset]),
        )

    @classmethod
    def total(cls, filtros=None):
        where, params = cls._filtros(filtros or {})
        return cls.scalar(
            "SELECT COUNT(*) FROM financeiro_cancelamentos fc INNER JOIN clientes cli ON cli.id=fc.cliente_id" + where,
            tuple(params),
        ) or 0

    @classmethod
    def buscar_por_id(cls, cancelamento_id):
        return cls.fetch_one(cls._select_base() + " WHERE fc.id=%s AND fc.ativo=1", (cancelamento_id,))

    @classmethod
    def contratos_do_cancelamento(cls, cancelamento_id):
        return cls.fetch_all(
            """
            SELECT c.id, c.numero, c.status
            FROM financeiro_cancelamento_contratos fcc
            INNER JOIN contratos c ON c.id=fcc.contrato_id
            WHERE fcc.cancelamento_id=%s
            ORDER BY c.numero
            """,
            (cancelamento_id,),
        )

    @classmethod
    def buscar_ativos_por_contratos(cls, contrato_ids):
        if not contrato_ids:
            return []
        placeholders = ",".join(["%s"] * len(contrato_ids))
        return cls.fetch_all(
            f"""
            SELECT fc.id, fcc.contrato_id
            FROM financeiro_cancelamentos fc
            INNER JOIN financeiro_cancelamento_contratos fcc ON fcc.cancelamento_id=fc.id
            WHERE fc.ativo=1 AND fcc.contrato_id IN ({placeholders})
            """,
            tuple(contrato_ids),
        )

    @classmethod
    def buscar_contratos_ids(cls, contrato_ids):
        if not contrato_ids:
            return []
        placeholders = ",".join(["%s"] * len(contrato_ids))
        return cls.fetch_all(
            f"""
            SELECT c.id, c.numero, c.status, c.cliente_id,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   cli.razao_social AS cliente_razao_social, cli.cnpj AS cliente_cnpj
            FROM contratos c
            INNER JOIN clientes cli ON cli.id=c.cliente_id
            WHERE c.ativo=1 AND c.id IN ({placeholders})
            ORDER BY c.numero
            """,
            tuple(contrato_ids),
        )

    @classmethod
    def contratos_para_select(cls, pesquisa=None, limit=100):
        params = []
        where = ["c.ativo=1", "c.status='ATIVO'"]
        if pesquisa:
            termo = f"%{pesquisa.strip()}%"
            cnpj = "".join(ch for ch in pesquisa if ch.isalnum()).upper()
            where.append(
                "(c.numero LIKE %s OR cli.nome_fantasia LIKE %s OR cli.razao_social LIKE %s "
                "OR cli.cnpj LIKE %s OR UPPER(REGEXP_REPLACE(cli.cnpj, '[^0-9A-Za-z]', '')) LIKE %s)"
            )
            params.extend([termo, termo, termo, termo, f"%{cnpj}%"])
        params.append(limit)
        return cls.fetch_all(
            f"""
            SELECT c.id, c.numero, c.status, c.cliente_id,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   cli.razao_social AS cliente_razao_social, cli.cnpj AS cliente_cnpj,
                   CASE WHEN fc.id IS NULL THEN 0 ELSE 1 END AS cancelamento_ativo,
                   fc.id AS cancelamento_id
            FROM contratos c
            INNER JOIN clientes cli ON cli.id=c.cliente_id
            LEFT JOIN financeiro_cancelamento_contratos fcc ON fcc.contrato_id=c.id
            LEFT JOIN financeiro_cancelamentos fc ON fc.id=fcc.cancelamento_id AND fc.ativo=1
            WHERE {' AND '.join(where)}
            ORDER BY COALESCE(cli.nome_fantasia, cli.razao_social), c.numero
            LIMIT %s
            """,
            tuple(params),
        )

    @classmethod
    def ambientes_por_contratos(cls, contrato_ids):
        if not contrato_ids:
            return []
        placeholders = ",".join(["%s"] * len(contrato_ids))
        return cls.fetch_all(
            f"""
            SELECT DISTINCT a.id, a.nome, a.ambiente_tipo, a.situacao, a.prefixo_proxmox
            FROM ambientes a
            LEFT JOIN ambiente_contratos ac ON ac.ambiente_id=a.id
            WHERE a.ativo=1
              AND (a.contrato_id IN ({placeholders}) OR ac.contrato_id IN ({placeholders}))
            ORDER BY a.nome
            """,
            tuple(contrato_ids) + tuple(contrato_ids),
        )

    @classmethod
    def criar(cls, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO financeiro_cancelamentos (
                    uuid, cliente_id, motivo, data_desligamento,
                    detalhes_monitoramento, detalhes_backup, detalhes_ambiente, observacoes,
                    solicitado_por, solicitado_por_email, destinatario_email
                ) VALUES (UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    dados["cliente_id"], dados["motivo"], dados["data_desligamento"],
                    dados.get("detalhes_monitoramento"), dados.get("detalhes_backup"),
                    dados.get("detalhes_ambiente"), dados.get("observacoes"),
                    dados.get("solicitado_por"), dados.get("solicitado_por_email"),
                    dados.get("destinatario_email"),
                ),
            )
            cancelamento_id = cursor.lastrowid
            cursor.executemany(
                "INSERT INTO financeiro_cancelamento_contratos (cancelamento_id, contrato_id) VALUES (%s, %s)",
                [(cancelamento_id, contrato_id) for contrato_id in dados["contrato_ids"]],
            )
            conn.commit()
            return cancelamento_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def registrar_resultado_email(cls, cancelamento_id, resultado):
        enviado = bool(resultado.get("enviado"))
        erro = None if enviado else (resultado.get("motivo") or resultado.get("erro") or "Falha não informada")[:1000]
        return cls.execute(
            """
            UPDATE financeiro_cancelamentos
            SET email_enviado=%s,
                email_enviado_em=CASE WHEN %s=1 THEN NOW() ELSE email_enviado_em END,
                email_tentativas=email_tentativas+1,
                erro_email=%s
            WHERE id=%s AND ativo=1
            """,
            (1 if enviado else 0, 1 if enviado else 0, erro, cancelamento_id),
        )

    @staticmethod
    def _select_base():
        return """
            SELECT fc.*, cli.email AS cliente_email, cli.cnpj AS cliente_cnpj,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   cli.razao_social AS cliente_razao_social,
                   u.nome AS solicitado_por_nome,
                   (SELECT GROUP_CONCAT(c.numero ORDER BY c.numero SEPARATOR ', ')
                    FROM financeiro_cancelamento_contratos fcc
                    INNER JOIN contratos c ON c.id=fcc.contrato_id
                    WHERE fcc.cancelamento_id=fc.id) AS contratos_numeros,
                   (SELECT COUNT(*) FROM financeiro_cancelamento_contratos fcc
                    WHERE fcc.cancelamento_id=fc.id) AS total_contratos
            FROM financeiro_cancelamentos fc
            INNER JOIN clientes cli ON cli.id=fc.cliente_id
            LEFT JOIN auth_usuarios u ON u.id=fc.solicitado_por
        """

    @staticmethod
    def _filtros(filtros):
        where = ["fc.ativo=1"]
        params = []
        if filtros.get("q"):
            termo = f"%{filtros['q']}%"
            where.append(
                "(cli.nome_fantasia LIKE %s OR cli.razao_social LIKE %s OR cli.cnpj LIKE %s "
                "OR EXISTS (SELECT 1 FROM financeiro_cancelamento_contratos fcc "
                "INNER JOIN contratos c ON c.id=fcc.contrato_id WHERE fcc.cancelamento_id=fc.id AND c.numero LIKE %s))"
            )
            params.extend([termo, termo, termo, termo])
        if filtros.get("email_status") == "ENVIADO":
            where.append("fc.email_enviado=1")
        elif filtros.get("email_status") == "ERRO":
            where.append("fc.email_enviado=0")
        if filtros.get("data_de"):
            where.append("DATE(fc.data_desligamento) >= %s")
            params.append(filtros["data_de"])
        if filtros.get("data_ate"):
            where.append("DATE(fc.data_desligamento) <= %s")
            params.append(filtros["data_ate"])
        return " WHERE " + " AND ".join(where), params

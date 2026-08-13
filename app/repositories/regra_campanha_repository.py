from app.repositories.base_repository import BaseRepository


class RegraCampanhaRepository(BaseRepository):
    TABLE = "regras_campanhas_comissao"

    @classmethod
    def listar(cls, pesquisa=None, ativo="1", limit=50, offset=0):
        where, params = cls._filtros(pesquisa, ativo)
        sql = f"""
            SELECT r.id, r.uuid, r.nome, r.percentual_parceiro, r.percentual_executivo, r.percentual_comissao, r.vigencia_inicio, r.vigencia_fim,
                   r.descricao, r.ativo, r.created_by, r.updated_by, r.created_at, r.updated_at,
                   COUNT(c.id) AS contratos_elegiveis_total
            FROM {cls.TABLE} r
            LEFT JOIN contratos c
              ON c.ativo = 1
             AND c.status = 'ATIVO'
             AND c.inicio_vigencia BETWEEN r.vigencia_inicio AND r.vigencia_fim
            {where}
            GROUP BY r.id, r.uuid, r.nome, r.percentual_parceiro, r.percentual_executivo, r.percentual_comissao, r.vigencia_inicio, r.vigencia_fim,
                     r.descricao, r.ativo, r.created_by, r.updated_by, r.created_at, r.updated_at
            ORDER BY r.vigencia_inicio DESC, r.vigencia_fim DESC, r.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_contratos_elegiveis(cls, inicio, fim):
        if not inicio or not fim:
            return []
        return cls.fetch_all(
            """
            SELECT
                c.id,
                c.numero,
                c.status,
                c.origem,
                c.inicio_vigencia,
                c.fim_vigencia,
                c.valor_mensal,
                c.valor_servicos_bruto,
                c.valor_descontos,
                c.valor_servicos_liquido,
                c.vendedor_nome,
                c.codigo_vendedor,
                c.projeto_nome,
                c.codigo_projeto,
                cli.nome_fantasia AS cliente_nome,
                cli.razao_social AS cliente_razao_social,
                COALESCE(SUM(CASE WHEN r.categoria_excluida = 0 THEN r.valor_recebido ELSE 0 END), 0) AS valor_recebido_elegivel,
                COUNT(r.id) AS recebimentos_total,
                COALESCE(SUM(CASE WHEN r.categoria_excluida = 1 THEN 1 ELSE 0 END), 0) AS recebimentos_excluidos
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN financeiro_recebimentos r ON r.contrato_id = c.id
            WHERE c.ativo = 1
              AND c.status = 'ATIVO'
              AND c.inicio_vigencia BETWEEN %s AND %s
            GROUP BY c.id, c.numero, c.status, c.origem, c.inicio_vigencia, c.fim_vigencia,
                     c.valor_mensal, c.valor_servicos_bruto, c.valor_descontos, c.valor_servicos_liquido,
                     c.vendedor_nome, c.codigo_vendedor, c.projeto_nome, c.codigo_projeto,
                     cli.nome_fantasia, cli.razao_social
            ORDER BY c.inicio_vigencia ASC, cli.nome_fantasia ASC, c.numero ASC
            """,
            (inicio, fim),
        )

    @classmethod
    def total(cls, pesquisa=None, ativo="1"):
        where, params = cls._filtros(pesquisa, ativo)
        return cls.scalar(f"SELECT COUNT(*) FROM {cls.TABLE} r {where}", tuple(params)) or 0

    @classmethod
    def buscar_por_id(cls, regra_id):
        return cls.fetch_one(
            f"""
            SELECT id, uuid, nome, percentual_parceiro, percentual_executivo, percentual_comissao, vigencia_inicio, vigencia_fim,
                   descricao, ativo, created_by, updated_by, created_at, updated_at
            FROM {cls.TABLE}
            WHERE id = %s
            """,
            (regra_id,),
        )

    @classmethod
    def buscar_sobreposicao(cls, inicio, fim, ignorar_id=None):
        params = [fim, inicio]
        sql = f"""
            SELECT id, nome, vigencia_inicio, vigencia_fim
            FROM {cls.TABLE}
            WHERE ativo = 1
              AND vigencia_inicio <= %s
              AND vigencia_fim >= %s
        """
        if ignorar_id:
            sql += "\n              AND id <> %s"
            params.append(ignorar_id)
        sql += "\n            ORDER BY vigencia_inicio ASC, id ASC LIMIT 1"
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            f"""
            INSERT INTO {cls.TABLE} (
                uuid, nome, percentual_parceiro, percentual_executivo, percentual_comissao, vigencia_inicio, vigencia_fim,
                descricao, ativo, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("nome"), dados.get("percentual_parceiro"),
                dados.get("percentual_executivo"), dados.get("percentual_parceiro"),
                dados.get("vigencia_inicio"), dados.get("vigencia_fim"), dados.get("descricao"),
                cls.bool_to_int(dados.get("ativo", True)), dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar(cls, regra_id, dados):
        return cls.execute(
            f"""
            UPDATE {cls.TABLE}
            SET nome=%s,
                percentual_parceiro=%s,
                percentual_executivo=%s,
                percentual_comissao=%s,
                vigencia_inicio=%s,
                vigencia_fim=%s,
                descricao=%s,
                ativo=%s,
                updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("percentual_parceiro"), dados.get("percentual_executivo"),
                dados.get("percentual_parceiro"), dados.get("vigencia_inicio"), dados.get("vigencia_fim"), dados.get("descricao"), cls.bool_to_int(dados.get("ativo", True)),
                dados.get("updated_by"), regra_id,
            ),
        )

    @classmethod
    def excluir(cls, regra_id, usuario_email="sistema"):
        return cls.execute(
            f"UPDATE {cls.TABLE} SET ativo=0, updated_by=%s WHERE id=%s",
            (usuario_email or "sistema", regra_id),
        )

    @classmethod
    def _filtros(cls, pesquisa=None, ativo="1"):
        condicoes = []
        params = []
        if pesquisa:
            condicoes.append("(r.nome LIKE %s OR r.descricao LIKE %s)")
            termo = f"%{pesquisa}%"
            params.extend([termo, termo])
        if str(ativo) in ("0", "1"):
            condicoes.append("r.ativo = %s")
            params.append(int(ativo))
        where = "WHERE " + " AND ".join(condicoes) if condicoes else ""
        return where, params

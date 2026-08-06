from app.repositories.base_repository import BaseRepository


class RegraCampanhaRepository(BaseRepository):
    TABLE = "regras_campanhas_comissao"

    @classmethod
    def listar(cls, pesquisa=None, ativo="1", limit=50, offset=0):
        where, params = cls._filtros(pesquisa, ativo)
        sql = f"""
            SELECT id, uuid, nome, percentual_parceiro, percentual_executivo, percentual_comissao, vigencia_inicio, vigencia_fim,
                   descricao, ativo, created_by, updated_by, created_at, updated_at
            FROM {cls.TABLE}
            {where}
            ORDER BY vigencia_inicio DESC, vigencia_fim DESC, id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, ativo="1"):
        where, params = cls._filtros(pesquisa, ativo)
        return cls.scalar(f"SELECT COUNT(*) FROM {cls.TABLE} {where}", tuple(params)) or 0

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
            condicoes.append("(nome LIKE %s OR descricao LIKE %s)")
            termo = f"%{pesquisa}%"
            params.extend([termo, termo])
        if str(ativo) in ("0", "1"):
            condicoes.append("ativo = %s")
            params.append(int(ativo))
        where = "WHERE " + " AND ".join(condicoes) if condicoes else ""
        return where, params

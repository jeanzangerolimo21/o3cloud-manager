"""Persistencia de Faixas do Catalogo Tecnico."""

from app.repositories.base_repository import BaseRepository


class ProdutoFaixaRepository(BaseRepository):
    """Consultas SQL para a entidade produto_faixas."""

    TABLE = "produto_faixas"

    @classmethod
    def listar(cls):
        sql = f"""
            SELECT
                pf.*,
                pm.produto_id,
                p.nome AS produto,
                pm.nome AS modelo,
                pf.usuarios_inicio AS inicio,
                pf.usuarios_fim AS fim,
                cp.valor_mensal,
                cp.valor_setup,
                cp.tem_projeto,
                cp.ativo AS preco_ativo
            FROM {cls.TABLE} pf
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            LEFT JOIN comercial_precos cp
                ON cp.faixa_id = pf.id
            ORDER BY
                p.nome,
                pm.nome,
                pf.ordem,
                pf.usuarios_inicio,
                pf.id
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar(cls, faixa_id):
        sql = f"""
            SELECT
                pf.*,
                pm.produto_id,
                p.nome AS produto,
                pm.nome AS modelo,
                pf.usuarios_inicio AS inicio,
                pf.usuarios_fim AS fim,
                cp.valor_mensal,
                cp.valor_setup,
                cp.tem_projeto,
                cp.ativo AS preco_ativo
            FROM {cls.TABLE} pf
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            LEFT JOIN comercial_precos cp
                ON cp.faixa_id = pf.id
            WHERE pf.id = %s
        """

        return cls.fetch_one(sql, (faixa_id,))

    @classmethod
    def buscar_por_intervalo(cls, modelo_id, usuarios_inicio, usuarios_fim):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE modelo_id = %s
              AND usuarios_inicio = %s
              AND usuarios_fim = %s
        """

        return cls.fetch_one(sql, (modelo_id, usuarios_inicio, usuarios_fim))

    @classmethod
    def buscar_por_codigo(cls, modelo_id, codigo):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE modelo_id = %s
              AND codigo = %s
        """

        return cls.fetch_one(sql, (modelo_id, codigo))

    @classmethod
    def contar(cls):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE}
        """

        return cls.scalar(sql)

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                modelo_id,
                codigo,
                nome,
                usuarios_inicio,
                usuarios_fim,
                permite_upgrade_manual,
                descricao,
                ordem,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados["modelo_id"],
                dados["codigo"],
                dados["nome"],
                dados["usuarios_inicio"],
                dados["usuarios_fim"],
                cls.bool_to_int(dados.get("permite_upgrade_manual", True)),
                dados.get("descricao"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, faixa_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET modelo_id = %s,
                codigo = %s,
                nome = %s,
                usuarios_inicio = %s,
                usuarios_fim = %s,
                permite_upgrade_manual = %s,
                descricao = %s,
                ordem = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados["modelo_id"],
                dados["codigo"],
                dados["nome"],
                dados["usuarios_inicio"],
                dados["usuarios_fim"],
                cls.bool_to_int(dados.get("permite_upgrade_manual", True)),
                dados.get("descricao"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
                faixa_id,
            ),
        )

    @classmethod
    def desativar(cls, faixa_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 0
            WHERE id = %s
        """

        return cls.execute(sql, (faixa_id,))

    @classmethod
    def reativar(cls, faixa_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 1
            WHERE id = %s
        """

        return cls.execute(sql, (faixa_id,))

    @classmethod
    def listar_produtos(cls):
        sql = """
            SELECT
                id,
                nome
            FROM produtos
            WHERE ativo = 1
            ORDER BY nome
        """

        return cls.fetch_all(sql)

    @classmethod
    def listar_modelos(cls, produto_id=None):
        sql = """
            SELECT
                id,
                produto_id,
                nome
            FROM produto_modelos
            WHERE ativo = 1
        """

        params = ()

        if produto_id is not None:
            sql += "\n  AND produto_id = %s"
            params = (produto_id,)

        sql += "\nORDER BY nome"

        return cls.fetch_all(sql, params)

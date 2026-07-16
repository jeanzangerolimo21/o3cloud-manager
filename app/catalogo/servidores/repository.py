"""Persistencia de Servidores do Catalogo Tecnico."""

from app.repositories.base_repository import BaseRepository


class ProdutoServidorRepository(BaseRepository):
    """Consultas SQL para a entidade produto_servidores."""

    TABLE = "produto_servidores"
    TIPOS_TABLE = "produto_tipos_servidor"

    @classmethod
    def listar(cls):
        sql = f"""
            SELECT
                ps.*,
                pf.modelo_id,
                pm.produto_id,
                p.nome AS produto,
                pm.nome AS modelo,
                pf.codigo AS faixa_codigo,
                pf.nome AS faixa_nome,
                pf.usuarios_inicio,
                pf.usuarios_fim
            FROM {cls.TABLE} ps
            INNER JOIN produto_faixas pf
                ON pf.id = ps.faixa_id
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            ORDER BY
                p.nome,
                pm.nome,
                pf.ordem,
                pf.usuarios_inicio,
                ps.ordem,
                ps.nome,
                ps.id
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar(cls, servidor_id):
        sql = f"""
            SELECT
                ps.*,
                pf.modelo_id,
                pm.produto_id,
                p.nome AS produto,
                pm.nome AS modelo,
                pf.codigo AS faixa_codigo,
                pf.nome AS faixa_nome,
                pf.usuarios_inicio,
                pf.usuarios_fim
            FROM {cls.TABLE} ps
            INNER JOIN produto_faixas pf
                ON pf.id = ps.faixa_id
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            WHERE ps.id = %s
        """

        return cls.fetch_one(sql, (servidor_id,))

    @classmethod
    def buscar_por_codigo(cls, faixa_id, codigo):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE faixa_id = %s
              AND codigo = %s
        """

        return cls.fetch_one(sql, (faixa_id, codigo))

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
                faixa_id,
                codigo,
                nome,
                tipo,
                sistema_operacional,
                observacoes,
                ordem,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados["faixa_id"],
                dados["codigo"],
                dados["nome"],
                dados["tipo"],
                dados.get("sistema_operacional"),
                dados.get("observacoes"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, servidor_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET faixa_id = %s,
                codigo = %s,
                nome = %s,
                tipo = %s,
                sistema_operacional = %s,
                observacoes = %s,
                ordem = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados["faixa_id"],
                dados["codigo"],
                dados["nome"],
                dados["tipo"],
                dados.get("sistema_operacional"),
                dados.get("observacoes"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
                servidor_id,
            ),
        )

    @classmethod
    def desativar(cls, servidor_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 0
            WHERE id = %s
        """

        return cls.execute(sql, (servidor_id,))

    @classmethod
    def reativar(cls, servidor_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 1
            WHERE id = %s
        """

        return cls.execute(sql, (servidor_id,))

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

    @classmethod
    def listar_faixas(cls, produto_id=None, modelo_id=None):
        sql = """
            SELECT
                pf.id,
                pf.modelo_id,
                pm.produto_id,
                pf.codigo,
                pf.nome,
                pf.usuarios_inicio,
                pf.usuarios_fim
            FROM produto_faixas pf
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            WHERE pf.ativo = 1
        """

        params = []

        if produto_id is not None:
            sql += "\n  AND pm.produto_id = %s"
            params.append(produto_id)

        if modelo_id is not None:
            sql += "\n  AND pf.modelo_id = %s"
            params.append(modelo_id)

        sql += "\nORDER BY pf.ordem, pf.usuarios_inicio, pf.nome"

        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_tipos(cls):
        sql = f"""
            SELECT
                codigo,
                nome
            FROM {cls.TIPOS_TABLE}
            WHERE ativo = 1
            ORDER BY ordem, nome
        """

        return cls.fetch_all(sql)

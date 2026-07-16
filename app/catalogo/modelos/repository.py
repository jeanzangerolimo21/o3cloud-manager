"""Persistência de Modelos do Catálogo Técnico."""

from app.repositories.base_repository import BaseRepository


class ProdutoModeloRepository(BaseRepository):
    """Consultas SQL para a entidade produto_modelos."""

    TABLE = "produto_modelos"

    @classmethod
    def listar(cls):
        sql = f"""
            SELECT
                pm.*,
                p.nome AS produto
            FROM {cls.TABLE} pm
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            ORDER BY
                p.nome,
                pm.ordem,
                pm.nome
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar(cls, modelo_id):
        sql = f"""
            SELECT
                pm.*,
                p.nome AS produto
            FROM {cls.TABLE} pm
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            WHERE pm.id = %s
        """

        return cls.fetch_one(sql, (modelo_id,))

    @classmethod
    def buscar_por_codigo(cls, produto_id, codigo):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE produto_id = %s
              AND codigo = %s
        """

        return cls.fetch_one(sql, (produto_id, codigo))

    @classmethod
    def buscar_por_nome(cls, produto_id, nome):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE produto_id = %s
              AND nome = %s
        """

        return cls.fetch_one(sql, (produto_id, nome))

    @classmethod
    def contar(cls):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE}
        """

        return cls.scalar(sql)

    @classmethod
    def existe(cls, produto_id, codigo):
        return cls.buscar_por_codigo(produto_id, codigo) is not None

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                produto_id,
                codigo,
                nome,
                descricao,
                ordem,
                padrao,
                versao,
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
                dados["produto_id"],
                dados["codigo"],
                dados["nome"],
                dados.get("descricao"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("padrao", False)),
                dados.get("versao"),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, modelo_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET produto_id = %s,
                codigo = %s,
                nome = %s,
                descricao = %s,
                ordem = %s,
                padrao = %s,
                versao = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados["produto_id"],
                dados["codigo"],
                dados["nome"],
                dados.get("descricao"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("padrao", False)),
                dados.get("versao"),
                cls.bool_to_int(dados.get("ativo", True)),
                modelo_id,
            ),
        )

    @classmethod
    def desativar(cls, modelo_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 0
            WHERE id = %s
        """

        return cls.execute(sql, (modelo_id,))

    @classmethod
    def reativar(cls, modelo_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 1
            WHERE id = %s
        """

        return cls.execute(sql, (modelo_id,))

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

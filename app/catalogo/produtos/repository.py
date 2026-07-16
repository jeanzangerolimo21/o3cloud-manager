from app.repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):

    TABLE = "produtos"

    ####################################################################
    # LISTAR
    ####################################################################

    @classmethod
    def listar(cls):

        sql = f"""
            SELECT
                p.*,
                c.nome AS categoria,
                pr.nome AS parceiro
            FROM {cls.TABLE} p
            INNER JOIN produtos_categorias c
                ON c.id = p.categoria_id
            LEFT JOIN parceiros pr
                ON pr.id = p.parceiro_id
            ORDER BY
                COALESCE(pr.nome, ''),
                c.nome,
                p.nome
        """

        return cls.fetch_all(sql)

    ####################################################################
    # BUSCAR
    ####################################################################

    @classmethod
    def buscar(cls, produto_id):

        sql = f"""
            SELECT
                p.*,
                c.nome AS categoria,
                pr.nome AS parceiro
              FROM {cls.TABLE} p
              INNER JOIN produtos_categorias c
                ON c.id = p.categoria_id
              LEFT JOIN parceiros pr
                ON pr.id = p.parceiro_id
             WHERE p.id=%s
        """

        return cls.fetch_one(sql, (produto_id,))

    ####################################################################
    # BUSCAR POR CÓDIGO
    ####################################################################

    @classmethod
    def buscar_por_codigo(cls, codigo):

        sql = f"""
            SELECT *
              FROM {cls.TABLE}
             WHERE codigo=%s
        """

        return cls.fetch_one(sql, (codigo,))

    ####################################################################
    # BUSCAR POR NOME
    ####################################################################

    @classmethod
    def buscar_por_nome(cls, nome):

        sql = f"""
            SELECT *
              FROM {cls.TABLE}
             WHERE nome=%s
        """

        return cls.fetch_one(sql, (nome,))

    ####################################################################
    # CONTAR
    ####################################################################

    @classmethod
    def contar(cls):

        sql = f"""
            SELECT COUNT(*)
              FROM {cls.TABLE}
        """

        return cls.scalar(sql)

    ####################################################################
    # EXISTE
    ####################################################################

    @classmethod
    def existe(cls, codigo):

        return cls.buscar_por_codigo(codigo) is not None

    ####################################################################
    # INSERIR
    ####################################################################

    @classmethod
    def inserir(cls, dados):

        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                categoria_id,
                parceiro_id,
                codigo,
                codigo_externo,
                nome,
                descricao,
                unidade,
                tipo_recurso,
                valor_venda,
                valor_custo,
                origem,
                ativo
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados["categoria_id"],
                dados.get("parceiro_id"),
                dados["codigo"],
                dados.get("codigo_externo"),
                dados["nome"],
                dados.get("descricao"),
                dados["unidade"],
                dados.get("tipo_recurso", "SERVICO"),
                dados.get("valor_venda", 0),
                dados.get("valor_custo", 0),
                dados.get("origem", "MANUAL"),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    ####################################################################
    # ATUALIZAR
    ####################################################################

    @classmethod
    def atualizar(cls, produto_id, dados):

        sql = f"""
            UPDATE {cls.TABLE}
               SET categoria_id=%s,
                   parceiro_id=%s,
                   codigo=%s,
                   codigo_externo=%s,
                   nome=%s,
                   descricao=%s,
                   unidade=%s,
                   tipo_recurso=%s,
                   valor_venda=%s,
                   valor_custo=%s,
                   ativo=%s
             WHERE id=%s
        """

        return cls.execute(
            sql,
            (
                dados["categoria_id"],
                dados.get("parceiro_id"),
                dados["codigo"],
                dados.get("codigo_externo"),
                dados["nome"],
                dados.get("descricao"),
                dados["unidade"],
                dados.get("tipo_recurso", "SERVICO"),
                dados.get("valor_venda", 0),
                dados.get("valor_custo", 0),
                cls.bool_to_int(dados.get("ativo", True)),
                produto_id,
            ),
        )

    ####################################################################
    # DESATIVAR
    ####################################################################

    @classmethod
    def desativar(cls, produto_id):

        sql = f"""
            UPDATE {cls.TABLE}
               SET ativo=0
             WHERE id=%s
        """

        return cls.execute(
            sql,
            (
                produto_id,
            ),
        )

    ####################################################################
    # REATIVAR
    ####################################################################

    @classmethod
    def reativar(cls, produto_id):

        sql = f"""
            UPDATE {cls.TABLE}
               SET ativo=1
             WHERE id=%s
        """

        return cls.execute(
            sql,
            (
                produto_id,
            ),
        )

    ####################################################################
    # CATEGORIAS
    ####################################################################

    @classmethod
    def listar_categorias(cls):

        sql = """
            SELECT
                id,
                nome
            FROM produtos_categorias
            WHERE ativo=1
            ORDER BY nome
        """

        return cls.fetch_all(sql)

    @classmethod
    def listar_parceiros(cls):

        sql = """
            SELECT
                id,
                nome,
                sigla
            FROM parceiros
            WHERE ativo = 1
            ORDER BY nome
        """

        return cls.fetch_all(sql)

    ####################################################################
    # TIPOS DE RECURSO
    ####################################################################

    @staticmethod
    def listar_tipos_recurso():

        return [
            ("VM", "VM"),
            ("LXC", "LXC"),
            ("CPU", "CPU"),
            ("RAM", "RAM"),
            ("DISCO", "DISCO"),
            ("STORAGE", "STORAGE"),
            ("BACKUP", "BACKUP"),
            ("LICENCA", "LICENÇA"),
            ("SERVICO", "SERVIÇO"),
            ("OUTRO", "OUTRO"),
        ]

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
    # CUSTOS
    ####################################################################

    @classmethod
    def listar_custos_pendentes(cls):

        sql = f"""
            SELECT
                p.*,
                c.nome AS categoria,
                COUNT(ct.id) AS itens_vinculados,
                COUNT(DISTINCT ct.cliente_id) AS clientes_total,
                COALESCE(SUM(CASE WHEN ct.id IS NOT NULL THEN COALESCE(ci.valor_total, 0) ELSE 0 END), 0) AS valor_total_itens
            FROM {cls.TABLE} p
            INNER JOIN produtos_categorias c
                ON c.id = p.categoria_id
            LEFT JOIN contratos_itens ci
                ON (
                    (ci.codigo_servico IS NOT NULL AND (
                        (p.codigo_externo REGEXP '^[0-9]+$' AND CAST(p.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                        OR (p.codigo REGEXP '^[0-9]+$' AND CAST(p.codigo AS UNSIGNED) = ci.codigo_servico)
                    ))
                    OR (ci.codigo_item IS NOT NULL AND (
                        (p.codigo_externo REGEXP '^[0-9]+$' AND CAST(p.codigo_externo AS UNSIGNED) = ci.codigo_item)
                        OR (p.codigo REGEXP '^[0-9]+$' AND CAST(p.codigo AS UNSIGNED) = ci.codigo_item)
                    ))
                )
            LEFT JOIN contratos ct
                ON ct.id = ci.contrato_id
               AND ct.ativo = 1
            WHERE p.ativo = 1
              AND COALESCE(p.valor_custo, 0) <= 0
            GROUP BY p.id, c.nome
            ORDER BY valor_total_itens DESC, itens_vinculados DESC, p.nome ASC
        """

        return cls.fetch_all(sql)

    @classmethod
    def atualizar_custo_por_codigo(cls, codigo, valor_custo):

        sql = f"""
            UPDATE {cls.TABLE}
               SET valor_custo=%s
             WHERE codigo=%s
               AND ativo=1
        """

        return cls.execute(sql, (valor_custo, codigo))

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

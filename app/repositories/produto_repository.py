from app.repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):

    TABLE = "produtos"

    COLUMNS = (

        "id",

        "uuid",

        "categoria_id",

        "codigo",

        "codigo_externo",

        "nome",

        "descricao",

        "unidade",

        "tipo_recurso",

        "valor_venda",

        "valor_custo",

        "origem",

        "ativo",

        "created_at",

        "updated_at",

    )

    ####################################################################
    # LISTAR
    ####################################################################

    @classmethod
    def listar(cls):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(f"""

                SELECT *

                  FROM {cls.TABLE}

                 ORDER BY nome

            """)

            return cursor.fetchall()

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # BUSCAR
    ####################################################################

    @classmethod
    def buscar(cls, produto_id):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(

                f"""

                SELECT *

                  FROM {cls.TABLE}

                 WHERE id=%s

                """,

                (produto_id,)

            )

            return cursor.fetchone()

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # BUSCAR POR CÓDIGO
    ####################################################################

    @classmethod
    def buscar_por_codigo(cls, codigo):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(

                f"""

                SELECT *

                  FROM {cls.TABLE}

                 WHERE codigo=%s

                """,

                (codigo,)

            )

            return cursor.fetchone()

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # BUSCAR POR NOME
    ####################################################################

    @classmethod
    def buscar_por_nome(cls, nome):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(

                f"""

                SELECT *

                  FROM {cls.TABLE}

                 WHERE nome=%s

                """,

                (nome,)

            )

            return cursor.fetchone()

        finally:

            cls.close(conn, cursor)

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

        conn = cls.connection()

        cursor = conn.cursor()

        try:

            sql = f"""

                INSERT INTO {cls.TABLE}

                (

                    uuid,

                    categoria_id,

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

                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

                )

            """

            cursor.execute(

                sql,

                (

                    cls.generate_uuid(),

                    dados["categoria_id"],

                    dados["codigo"],

                    dados.get("codigo_externo"),

                    dados["nome"],

                    dados.get("descricao"),

                    dados.get("unidade","UN"),

                    dados.get("tipo_recurso","SERVICO"),

                    dados.get("valor_venda",0),

                    dados.get("valor_custo",0),

                    dados.get("origem","MANUAL"),

                    cls.bool_to_int(

                        dados.get("ativo",True)

                    )

                )

            )

            conn.commit()

            return cursor.lastrowid

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # ATUALIZAR
    ####################################################################

    @classmethod
    def atualizar(cls, produto_id, dados):

        conn = cls.connection()

        cursor = conn.cursor()

        try:

            sql = f"""

                UPDATE {cls.TABLE}

                   SET

                       categoria_id=%s,

                       codigo=%s,

                       codigo_externo=%s,

                       nome=%s,

                       descricao=%s,

                       unidade=%s,

                       tipo_recurso=%s,

                       valor_venda=%s,

                       valor_custo=%s,

                       origem=%s,

                       ativo=%s

                 WHERE id=%s

            """

            cursor.execute(

                sql,

                (

                    dados["categoria_id"],

                    dados["codigo"],

                    dados.get("codigo_externo"),

                    dados["nome"],

                    dados.get("descricao"),

                    dados.get("unidade","UN"),

                    dados.get("tipo_recurso","SERVICO"),

                    dados.get("valor_venda",0),

                    dados.get("valor_custo",0),

                    dados.get("origem","MANUAL"),

                    cls.bool_to_int(

                        dados.get("ativo",True)

                    ),

                    produto_id

                )

            )

            conn.commit()

            return True

        finally:

            cls.close(conn, cursor)

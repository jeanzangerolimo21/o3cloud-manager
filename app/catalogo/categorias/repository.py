from app.repositories.base_repository import BaseRepository


class CategoriaRepository(BaseRepository):

    TABLE = "produtos_categorias"

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
                 ORDER BY ordem, nome
            """)

            return cursor.fetchall()

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # BUSCAR
    ####################################################################

    @classmethod
    def buscar(cls, categoria_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(
                f"""
                SELECT *
                  FROM {cls.TABLE}
                 WHERE id=%s
                """,
                (categoria_id,)
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
    # CONTAR
    ####################################################################

    @classmethod
    def contar(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                f"""
                SELECT COUNT(*)
                  FROM {cls.TABLE}
                """
            )

            return cursor.fetchone()[0]

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

            cursor.execute(
                f"""
                INSERT INTO {cls.TABLE}
                (
                    uuid,
                    codigo,
                    nome,
                    descricao,
                    cor,
                    ordem,
                    ativo
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,%s,%s
                )
                """,
                (
                    cls.generate_uuid(),
                    dados["codigo"],
                    dados["nome"],
                    dados.get("descricao"),
                    dados.get("cor", "#0d6efd"),
                    dados.get("ordem", 0),
                    cls.bool_to_int(
                        dados.get("ativo", True)
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
    def atualizar(cls, categoria_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                f"""
                UPDATE {cls.TABLE}
                   SET
                       codigo=%s,
                       nome=%s,
                       descricao=%s,
                       cor=%s,
                       ordem=%s,
                       ativo=%s
                 WHERE id=%s
                """,
                (
                    dados["codigo"],
                    dados["nome"],
                    dados.get("descricao"),
                    dados.get("cor", "#0d6efd"),
                    dados.get("ordem", 0),
                    cls.bool_to_int(
                        dados.get("ativo", True)
                    ),
                    categoria_id
                )
            )

            conn.commit()

            return True

        finally:

            cls.close(conn, cursor)

    ####################################################################
    # EXCLUIR
    ####################################################################

    @classmethod
    def excluir(cls, categoria_id):

        conn = cls.connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                f"""
                DELETE
                  FROM {cls.TABLE}
                 WHERE id=%s
                """,
                (categoria_id,)
            )

            conn.commit()

            return True

        finally:

            cls.close(conn, cursor)
    ####################################################################
    # DESATIVAR
    ####################################################################

    @classmethod
    def desativar(cls, categoria_id):

        conn = cls.connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE produtos_categorias
                   SET ativo = 0
                WHERE id = %s
                """,
                (categoria_id,)
            )

            conn.commit()

            return True

        finally:

            cls.close(conn, cursor)


    ####################################################################
    # REATIVAR
    ####################################################################

    @classmethod
    def reativar(cls, categoria_id):

        conn = cls.connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE produtos_categorias
                   SET ativo = 1
                WHERE id = %s
                """,
                (categoria_id,)
            )

            conn.commit()

            return True

        finally:

            cls.close(conn, cursor)

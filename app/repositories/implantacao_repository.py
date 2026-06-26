from app.repositories.base_repository import BaseRepository


class ImplantacaoRepository(BaseRepository):

    @classmethod
    def buscar_por_cliente(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes_implantacao

            WHERE cliente_id = %s

            LIMIT 1

        """, (cliente_id,))

        dados = cursor.fetchone()

        cls.close(conn, cursor)

        return dados


    @classmethod
    def inserir(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO clientes_implantacao (

                cliente_id

            )

            VALUES (

                %s

            )

        """, (cliente_id,))

        conn.commit()

        cls.close(conn, cursor)


    @classmethod
    def salvar(cls, cliente_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE clientes_implantacao

            SET

                responsavel_implantacao=%s,

                data_implantacao=%s,

                servidor_principal_id=%s,

                cluster=%s,

                ambiente=%s,

                status_implantacao=%s,

                notas_tecnicas=%s

            WHERE cliente_id=%s

        """, (

            dados["responsavel_implantacao"],

            dados["data_implantacao"],

            dados["servidor_principal_id"],

            dados["cluster"],

            dados["ambiente"],

            dados["status_implantacao"],

            dados["notas_tecnicas"],

            cliente_id

        ))

        conn.commit()

        cls.close(conn, cursor)

from app.repositories.base_repository import BaseRepository


class FinanceiroRepository(BaseRepository):

    @classmethod
    def total_clientes(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM clientes
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def total_contratos(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM contratos
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def total_produtos(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM produtos
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def receita_total(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(valor_liquido),0)
            FROM faturamentos
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total


    @classmethod
    def listar_clientes(cls):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                id,
                nome_fantasia,
                cidade,
                estado,
                origem,
                ativo

            FROM clientes

            ORDER BY nome_fantasia

        """)

        dados = cursor.fetchall()

        cls.close(conn, cursor)

        return dados

    @classmethod
    def buscar_cliente(cls, cliente_id):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes

            WHERE id=%s

        """,(cliente_id,))

        cliente = cursor.fetchone()

        cls.close(conn,cursor)

        return cliente

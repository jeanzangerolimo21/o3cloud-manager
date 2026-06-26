from app.repositories.base_repository import BaseRepository


class ContratoRepository(BaseRepository):

    @classmethod
    def listar(cls):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM contratos

            ORDER BY numero

        """)

        contratos = cursor.fetchall()

        cls.close(conn, cursor)

        return contratos

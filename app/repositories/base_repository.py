from uuid import uuid4

from app.core.database import get_connection


class BaseRepository:
    """
    Classe base para todos os repositórios.

    Responsável por:

    - conexão
    - fechamento
    - utilidades comuns
    """

    @classmethod
    def connection(cls):
        return get_connection()

    @staticmethod
    def close(conn=None, cursor=None):

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    @staticmethod
    def generate_uuid():

        return str(uuid4())

    @staticmethod
    def bool_to_int(value):

        return 1 if value else 0

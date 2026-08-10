from uuid import uuid4

from app.core.database import get_connection
from app.core.logging_config import get_logger


database_logger = get_logger("database")


class BaseRepository:
    """
    Classe base para todos os repositórios.

    Responsável por:

    - conexão
    - fechamento
    - geração de UUID
    - conversão de boolean
    - execução de consultas SQL
    """

    @classmethod
    def connection(cls):
        try:
            return get_connection()
        except Exception:
            database_logger.exception("Database connection failed", extra={"repository": cls.__name__})
            raise

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

    @classmethod
    def fetch_all(cls, sql, params=None):
        """
        Executa um SELECT retornando todos os registros.
        """

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

        finally:
            cls.close(conn, cursor)

    @classmethod
    def fetch_one(cls, sql, params=None):
        """
        Executa um SELECT retornando apenas um registro.
        """

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

        finally:
            cls.close(conn, cursor)

    @classmethod
    def execute(cls, sql, params=None):
        """
        Executa INSERT, UPDATE ou DELETE.

        Retorna True quando executado com sucesso.
        """

        conn = cls.connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params or ())
            conn.commit()
            return True

        except Exception:
            database_logger.exception("Database operation failed", extra={"repository": cls.__name__})
            conn.rollback()
            raise

        finally:
            cls.close(conn, cursor)

    @classmethod
    def execute_insert(cls, sql, params=None):
        """
        Executa INSERT e retorna o ID gerado.
        """

        conn = cls.connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.lastrowid

        except Exception:
            database_logger.exception("Database operation failed", extra={"repository": cls.__name__})
            conn.rollback()
            raise

        finally:
            cls.close(conn, cursor)

    @classmethod
    def execute_many(cls, sql, values):
        """
        Executa operações em lote utilizando executemany().
        """

        conn = cls.connection()
        cursor = conn.cursor()

        try:
            cursor.executemany(sql, values)
            conn.commit()
            return cursor.rowcount

        except Exception:
            database_logger.exception("Database operation failed", extra={"repository": cls.__name__})
            conn.rollback()
            raise

        finally:
            cls.close(conn, cursor)

    @classmethod
    def scalar(cls, sql, params=None):
        """
        Retorna o primeiro campo da primeira linha do SELECT.
        """

        conn = cls.connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params or ())
            row = cursor.fetchone()

            if row:
                return row[0]

            return None

        finally:
            cls.close(conn, cursor)


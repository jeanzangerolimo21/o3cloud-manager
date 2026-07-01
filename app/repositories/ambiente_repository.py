from app.repositories.base_repository import BaseRepository
from app.core.constants.origens import ORIGEM_MANUAL


class AmbienteRepository(BaseRepository):

    @classmethod
    def listar(cls, pesquisa=None, limit=50, offset=0):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT

                a.id,
                a.uuid,
                a.cliente_id,
                a.nome,
                a.ambiente_tipo,
                a.tag_proxmox,
                a.descricao,
                a.ativo,
                a.synced_at,
                c.nome_fantasia AS cliente_nome

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id

        """

        parametros = []

        if pesquisa:

            sql += """

                WHERE

                    a.nome LIKE %s

                    OR c.nome_fantasia LIKE %s

                    OR a.tag_proxmox LIKE %s

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo])

        sql += """

            ORDER BY

                c.nome_fantasia,
                a.nome

            LIMIT %s OFFSET %s

        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))

        ambientes = cursor.fetchall()

        cls.close(conn, cursor)

        return ambientes

    @classmethod
    def total(cls, pesquisa=None):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT COUNT(*) AS total

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id

        """

        parametros = []

        if pesquisa:

            sql += """

                WHERE

                    a.nome LIKE %s

                    OR c.nome_fantasia LIKE %s

                    OR a.tag_proxmox LIKE %s

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo])

        cursor.execute(sql, tuple(parametros))

        total = cursor.fetchone()["total"]

        cls.close(conn, cursor)

        return total

    @classmethod
    def buscar_por_id(cls, ambiente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                a.*,

                c.nome_fantasia AS cliente_nome

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id

            WHERE a.id=%s

        """, (ambiente_id,))

        ambiente = cursor.fetchone()

        cls.close(conn, cursor)

        return ambiente

    @classmethod
    def buscar_por_cliente(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM ambientes

            WHERE cliente_id=%s

            ORDER BY nome

        """, (cliente_id,))

        ambientes = cursor.fetchall()

        cls.close(conn, cursor)

        return ambientes

    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO ambientes (

                uuid,
                cliente_id,
                nome,
                ambiente_tipo,
                tag_proxmox,
                descricao,
                ativo

            )

            VALUES (

                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s

            )

        """, (

            uuid,
            dados.get("cliente_id"),
            dados.get("nome"),
            dados.get("ambiente_tipo"),
            dados.get("tag_proxmox"),
            dados.get("descricao"),
            dados.get("ativo", 1)

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def atualizar(cls, ambiente_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE ambientes

            SET

                cliente_id=%s,
                nome=%s,
                ambiente_tipo=%s,
                tag_proxmox=%s,
                descricao=%s,
                ativo=%s

            WHERE id=%s

        """, (

            dados.get("cliente_id"),
            dados.get("nome"),
            dados.get("ambiente_tipo"),
            dados.get("tag_proxmox"),
            dados.get("descricao"),
            dados.get("ativo"),
            ambiente_id

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def excluir(cls, ambiente_id):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            DELETE FROM ambientes

            WHERE id=%s

        """, (ambiente_id,))

        conn.commit()

        cls.close(conn, cursor)

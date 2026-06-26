from app.repositories.base_repository import BaseRepository
from app.core.constants.origens import ORIGEM_MANUAL


class ContratoRepository(BaseRepository):

    SYNC_FIELDS = (
        "codigo_externo",
        "origem",
        "synced_at"
    )

    EDITABLE_FIELDS = (
        "numero",
        "descricao",
        "status",
        "inicio_vigencia",
        "fim_vigencia",
        "valor_mensal",
        "dia_faturamento",
        "tipo_faturamento",
        "codigo_vendedor",
        "codigo_projeto",
        "codigo_cc",
        "observacoes"
    )


    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

        SELECT *

            FROM contratos

            WHERE codigo_externo=%s

        """, (codigo_externo,))

        contrato = cursor.fetchone()

        cls.close(conn, cursor)

        return contrato


    @classmethod
    def buscar_por_id(cls, contrato_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

        SELECT 

            c.*,

            cli.nome_fantasia AS cliente_nome

            FROM contratos c

            INNER JOIN clientes cli
                ON cli.id = c.cliente_id

            WHERE c.id=%s

        """, (contrato_id,))

        contrato = cursor.fetchone()

        cls.close(conn, cursor)

        return contrato

    @classmethod
    def total(cls, pesquisa=None):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT COUNT(*) AS total

            FROM contratos c

            INNER JOIN clientes cli
                ON cli.id = c.cliente_id

        """

        parametros = []

        if pesquisa:

            sql += """

                WHERE

                    c.numero LIKE %s

                    OR cli.nome_fantasia LIKE %s

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo])

        cursor.execute(sql, tuple(parametros))

        total = cursor.fetchone()["total"]

        cls.close(conn, cursor)

        return total

    @classmethod
    def listar(cls, pesquisa=None, limit=50, offset=0):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT

                c.id,
                c.uuid,
                c.cliente_id,
                c.codigo_externo,
                c.numero,
                c.status,
                c.valor_mensal,
                c.dia_faturamento,
                c.inicio_vigencia,
                c.fim_vigencia,
                c.ativo,
                cli.nome_fantasia AS cliente_nome

            FROM contratos c

            INNER JOIN clientes cli
                ON cli.id = c.cliente_id
            
        """

        parametros = []

        if pesquisa:

                sql += """

                    WHERE

                        c.numero LIKE %s

                        OR cli.nome_fantasia LIKE %s

                """

                termo = f"%{pesquisa}%"

                parametros.extend([termo, termo])

        sql += """

        ORDER BY c.id DESC

        LIMIT %s OFFSET %s

        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))
            

        contratos = cursor.fetchall()

        cls.close(conn, cursor)

        return contratos

    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO contratos (

                uuid,
                cliente_id,
                codigo_externo,
                origem,
                numero,
                descricao,
                status,
                inicio_vigencia,
                fim_vigencia,
                observacoes,
                ativo,
                synced_at,
                valor_mensal,
                dia_faturamento,
                tipo_faturamento,
                codigo_vendedor,
                codigo_projeto,
                codigo_cc

            )

            VALUES (

                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                1,
                NOW(),
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
            dados.get("codigo_externo"),
            dados.get("origem"),
            dados.get("numero"),
            dados.get("descricao"),
            dados.get("status"),
            dados.get("inicio_vigencia"),
            dados.get("fim_vigencia"),
            dados.get("observacoes"),
            dados.get("valor_mensal"),
            dados.get("dia_faturamento"),
            dados.get("tipo_faturamento"),
            dados.get("codigo_vendedor"),
            dados.get("codigo_projeto"),
            dados.get("codigo_cc")

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def atualizar_sync(cls, contrato_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE contratos

            SET

                cliente_id=%s,
                codigo_externo=%s,
                origem=%s,
                numero=%s,
                descricao=%s,
                status=%s,
                inicio_vigencia=%s,
                fim_vigencia=%s,
                observacoes=%s,
                valor_mensal=%s,
                dia_faturamento=%s,
                tipo_faturamento=%s,
                codigo_vendedor=%s,
                codigo_projeto=%s,
                codigo_cc=%s,
                synced_at=NOW()

            WHERE id=%s

        """, (

            dados.get("cliente_id"),
            dados.get("codigo_externo"),
            dados.get("origem"),
            dados.get("numero"),
            dados.get("descricao"),
            dados.get("status"),
            dados.get("inicio_vigencia"),
            dados.get("fim_vigencia"),
            dados.get("observacoes"),
            dados.get("valor_mensal"),
            dados.get("dia_faturamento"),
            dados.get("tipo_faturamento"),
            dados.get("codigo_vendedor"),
            dados.get("codigo_projeto"),
            dados.get("codigo_cc"),
            contrato_id

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def atualizar(cls, contrato_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE contratos

            SET

                numero=%s,
                descricao=%s,
                status=%s,
                inicio_vigencia=%s,
                fim_vigencia=%s,
                observacoes=%s,
                valor_mensal=%s,
                dia_faturamento=%s,
                tipo_faturamento=%s,
                codigo_vendedor=%s,
                codigo_projeto=%s,
                codigo_cc=%s

            WHERE id=%s

        """, (

            dados.get("numero"),
            dados.get("descricao"),
            dados.get("status"),
            dados.get("inicio_vigencia"),
            dados.get("fim_vigencia"),
            dados.get("observacoes"),
            dados.get("valor_mensal"),
            dados.get("dia_faturamento"),
            dados.get("tipo_faturamento"),
            dados.get("codigo_vendedor"),
            dados.get("codigo_projeto"),
            dados.get("codigo_cc"),
            contrato_id

        ))

        conn.commit()

        cls.close(conn, cursor)




    @classmethod
    def excluir(cls, contrato_id):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            DELETE FROM contratos

            WHERE id=%s

            AND origem=%s

        """, (

            contrato_id,
            ORIGEM_MANUAL

        ))

        conn.commit()

        cls.close(conn, cursor)

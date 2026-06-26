from app.repositories.base_repository import BaseRepository


class ContratoItemRepository(BaseRepository):

    @classmethod
    def buscar_por_codigo_item(cls, codigo_item):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM contratos_itens

            WHERE codigo_item=%s

        """, (codigo_item,))

        item = cursor.fetchone()

        cls.close(conn, cursor)

        return item
    
    @classmethod
    def listar_por_contrato(cls, contrato_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM contratos_itens

            WHERE contrato_id=%s

            ORDER BY sequencia

        """, (contrato_id,))

        itens = cursor.fetchall()

        cls.close(conn, cursor)

        return itens

    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO contratos_itens (

                uuid,
                contrato_id,
                codigo_item,
                codigo_servico,
                descricao,
                quantidade,
                valor_unitario,
                valor_total,
                desconto,
                acrescimo,
                sequencia

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
                %s

            )

        """, (

            uuid,
            dados.get("contrato_id"),
            dados.get("codigo_item"),
            dados.get("codigo_servico"),
            dados.get("descricao"),
            dados.get("quantidade"),
            dados.get("valor_unitario"),
            dados.get("valor_total"),
            dados.get("desconto"),
            dados.get("acrescimo"),
            dados.get("sequencia")

        ))

        conn.commit()

        cls.close(conn, cursor)


    @classmethod
    def atualizar_sync(cls, item_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE contratos_itens

            SET

                contrato_id=%s,
                codigo_servico=%s,
                descricao=%s,
                quantidade=%s,
                valor_unitario=%s,
                valor_total=%s,
                desconto=%s,
                acrescimo=%s,
                sequencia=%s

            WHERE id=%s

        """, (

            dados.get("contrato_id"),
            dados.get("codigo_servico"),
            dados.get("descricao"),
            dados.get("quantidade"),
            dados.get("valor_unitario"),
            dados.get("valor_total"),
            dados.get("desconto"),
            dados.get("acrescimo"),
            dados.get("sequencia"),
            item_id

        ))

        conn.commit()

        cls.close(conn, cursor)


    @classmethod
    def upsert_omie(cls, dados):

        item = cls.buscar_por_codigo_item(
            dados["codigo_item"]
        )

        if item:

            cls.atualizar_sync(
                item["id"],
                dados
            )

            return "UPDATE"

        cls.inserir(dados)

        return "INSERT"

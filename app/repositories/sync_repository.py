from app.repositories.base_repository import BaseRepository


class SyncRepository(BaseRepository):

    @classmethod
    def iniciar(cls, integracao):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO sync_execucoes (

                uuid,
                integracao,
                inicio,
                status

            )

            VALUES (

                UUID(),
                %s,
                NOW(),
                'EXECUTANDO'

            )

        """, (integracao,))

        conn.commit()

        sync_id = cursor.lastrowid

        cls.close(conn, cursor)

        return sync_id

    @classmethod
    def finalizar(
        cls,
        sync_id,
        status,
        processados,
        novos,
        atualizados,
        erros,
        mensagem=None
    ):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE sync_execucoes

            SET

                fim=NOW(),
                status=%s,
                registros_processados=%s,
                registros_novos=%s,
                registros_atualizados=%s,
                registros_erro=%s,
                mensagem=%s

            WHERE id=%s

        """, (

            status,
            processados,
            novos,
            atualizados,
            erros,
            mensagem,
            sync_id

        ))

        conn.commit()

        cls.close(conn, cursor)

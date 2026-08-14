from app.repositories.base_repository import BaseRepository


class AlertasOperacaoRepository(BaseRepository):
    @classmethod
    def listar_usuarios_habilitados(cls):
        return cls.fetch_all(
            """
            SELECT id, nome, email, receber_alertas_operacao,
                   alertas_operacao_periodicidade, alertas_operacao_horario,
                   alertas_operacao_ultimo_envio_em
            FROM auth_usuarios
            WHERE status = 'ATIVO'
              AND receber_alertas_operacao = 1
              AND email IS NOT NULL
              AND email <> ''
            ORDER BY nome ASC, id ASC
            """
        )

    @classmethod
    def marcar_envio_usuario(cls, usuario_id):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET alertas_operacao_ultimo_envio_em = NOW()
            WHERE id = %s
            """,
            (usuario_id,),
        )

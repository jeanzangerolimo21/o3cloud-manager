from app.repositories.base_repository import BaseRepository


class EmailConfigRepository(BaseRepository):
    TABLE = "config_email_servicos"

    @classmethod
    def listar(cls):
        return cls.fetch_all(
            """
            SELECT id, uuid, nome, smtp_host, smtp_port, smtp_user, smtp_from,
                   usar_tls, ativo, observacoes, ultimo_teste_status,
                   ultimo_teste_mensagem, ultimo_teste_em, created_by, updated_by,
                   created_at, updated_at
            FROM config_email_servicos
            ORDER BY ativo DESC, nome ASC, id ASC
            """
        )

    @classmethod
    def buscar_ativo(cls):
        return cls.fetch_one(
            """
            SELECT *
            FROM config_email_servicos
            WHERE ativo = 1
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """
        )

    @classmethod
    def buscar_por_id(cls, config_id):
        return cls.fetch_one(
            """
            SELECT *
            FROM config_email_servicos
            WHERE id = %s
            """,
            (config_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO config_email_servicos (
                uuid, nome, smtp_host, smtp_port, smtp_user, smtp_password_encrypted,
                smtp_from, usar_tls, ativo, observacoes, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("nome"), dados.get("smtp_host"),
                dados.get("smtp_port"), dados.get("smtp_user"),
                dados.get("smtp_password_encrypted"), dados.get("smtp_from"),
                cls.bool_to_int(dados.get("usar_tls", True)),
                cls.bool_to_int(dados.get("ativo", True)),
                dados.get("observacoes"), dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar(cls, config_id, dados):
        return cls.execute(
            """
            UPDATE config_email_servicos
            SET nome=%s, smtp_host=%s, smtp_port=%s, smtp_user=%s,
                smtp_password_encrypted=COALESCE(%s, smtp_password_encrypted),
                smtp_from=%s, usar_tls=%s, ativo=%s, observacoes=%s, updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("smtp_host"), dados.get("smtp_port"),
                dados.get("smtp_user"), dados.get("smtp_password_encrypted"),
                dados.get("smtp_from"), cls.bool_to_int(dados.get("usar_tls", True)),
                cls.bool_to_int(dados.get("ativo", True)), dados.get("observacoes"),
                dados.get("updated_by"), config_id,
            ),
        )

    @classmethod
    def desativar_outros(cls, config_id):
        return cls.execute(
            """
            UPDATE config_email_servicos
            SET ativo = 0
            WHERE id <> %s
            """,
            (config_id,),
        )

    @classmethod
    def registrar_teste(cls, config_id, status, mensagem):
        return cls.execute(
            """
            UPDATE config_email_servicos
            SET ultimo_teste_status=%s, ultimo_teste_mensagem=%s, ultimo_teste_em=NOW()
            WHERE id=%s
            """,
            (status, mensagem, config_id),
        )

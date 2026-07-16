"""Persistencia de recursos comerciais de servidor do Catalogo Tecnico."""

from app.repositories.base_repository import BaseRepository


class ProdutoRecursoRepository(BaseRepository):
    """Consultas SQL para a entidade catalogo_recursos_servidor."""

    TABLE = "catalogo_recursos_servidor"

    @classmethod
    def listar(cls):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            ORDER BY
                CASE categoria
                    WHEN 'Outro' THEN 10
                    WHEN 'Disco' THEN 20
                    WHEN 'Processador' THEN 30
                    WHEN 'Memoria' THEN 40
                    WHEN 'Backup' THEN 50
                    WHEN 'IP Fixo' THEN 60
                    WHEN 'Suporte Premium' THEN 70
                    WHEN 'Sistema Operacional' THEN 80
                    WHEN 'Call de Acesso' THEN 90
                    WHEN 'VPN' THEN 100
                    ELSE 999
                END,
                ordem,
                nome,
                id
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar(cls, recurso_id):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE id = %s
        """

        return cls.fetch_one(sql, (recurso_id,))

    @classmethod
    def buscar_por_codigo(cls, codigo):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE codigo = %s
        """

        return cls.fetch_one(sql, (codigo,))

    @classmethod
    def buscar_por_nome(cls, nome):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE nome = %s
        """

        return cls.fetch_one(sql, (nome,))

    @classmethod
    def contar(cls):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE}
        """

        return cls.scalar(sql)

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                codigo,
                categoria,
                nome,
                descricao,
                tipo_recurso,
                valor_mensal,
                valor_instalacao,
                ordem,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados['codigo'],
                dados['categoria'],
                dados['nome'],
                dados.get('descricao'),
                dados.get('tipo_recurso', 'SERVICO'),
                dados.get('valor_mensal', 0),
                dados.get('valor_instalacao', 0),
                dados.get('ordem', 0),
                cls.bool_to_int(dados.get('ativo', True)),
            ),
        )

    @classmethod
    def atualizar(cls, recurso_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET codigo = %s,
                categoria = %s,
                nome = %s,
                descricao = %s,
                tipo_recurso = %s,
                valor_mensal = %s,
                valor_instalacao = %s,
                ordem = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados['codigo'],
                dados['categoria'],
                dados['nome'],
                dados.get('descricao'),
                dados.get('tipo_recurso', 'SERVICO'),
                dados.get('valor_mensal', 0),
                dados.get('valor_instalacao', 0),
                dados.get('ordem', 0),
                cls.bool_to_int(dados.get('ativo', True)),
                recurso_id,
            ),
        )

    @classmethod
    def desativar(cls, recurso_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET ativo = 0
            WHERE id = %s
        """

        return cls.execute(sql, (recurso_id,))

    @staticmethod
    def listar_tipos_recurso():
        return [
            ('CPU', 'CPU'),
            ('RAM', 'RAM'),
            ('DISCO', 'DISCO'),
            ('STORAGE', 'STORAGE'),
            ('BACKUP', 'BACKUP'),
            ('LICENCA', 'LICENÇA'),
            ('SERVICO', 'SERVIÇO'),
            ('OUTRO', 'OUTRO'),
        ]

"""Persistencia de precos comerciais por faixa do Catalogo Tecnico."""

from app.repositories.base_repository import BaseRepository


class PrecoCatalogoRepository(BaseRepository):
    """Consultas SQL para a entidade comercial_precos."""

    TABLE = "comercial_precos"

    @classmethod
    def buscar_por_faixa(cls, faixa_id):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE faixa_id = %s
        """

        return cls.fetch_one(sql, (faixa_id,))

    @classmethod
    def listar_licenciamento(cls):
        sql = f"""
            SELECT
                cp.id,
                cp.faixa_id,
                p.codigo AS produto_codigo,
                p.nome AS produto,
                COALESCE(
                    NULLIF(pf.nome, ''),
                    CONCAT(p.nome, ' ', pf.usuarios_inicio, '-', pf.usuarios_fim)
                ) AS software,
                COALESCE(NULLIF(pf.descricao, ''), NULLIF(p.descricao, ''), p.nome) AS descricao,
                cp.valor_mensal,
                cp.valor_setup,
                pf.usuarios_inicio AS qtd_minima,
                cp.tem_projeto,
                cp.ativo,
                pf.usuarios_inicio,
                pf.usuarios_fim
            FROM {cls.TABLE} cp
            INNER JOIN produto_faixas pf
                ON pf.id = cp.faixa_id
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            WHERE p.tipo_recurso = 'LICENCA'
            ORDER BY
                CASE p.codigo
                    WHEN 'LOGUS_STORE' THEN 10
                    WHEN 'LOGUS' THEN 20
                    WHEN 'TARGET' THEN 30
                    WHEN 'USUARIO_ADICIONAL' THEN 40
                    WHEN 'VR' THEN 50
                    ELSE 999
                END,
                CASE
                    WHEN p.codigo = 'LOGUS' THEN -pf.usuarios_inicio
                    WHEN p.codigo = 'TARGET' THEN -pf.usuarios_inicio
                    WHEN p.codigo = 'VR' AND pf.usuarios_inicio <= 5 THEN -pf.usuarios_inicio
                    WHEN p.codigo = 'VR' THEN -pf.usuarios_inicio
                    ELSE pf.usuarios_inicio
                END,
                pf.usuarios_fim DESC,
                cp.id
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar_licenciamento(cls, preco_id):
        sql = f"""
            SELECT
                cp.id,
                cp.faixa_id,
                p.codigo AS produto_codigo,
                p.nome AS produto,
                COALESCE(
                    NULLIF(pf.nome, ''),
                    CONCAT(p.nome, ' ', pf.usuarios_inicio, '-', pf.usuarios_fim)
                ) AS software,
                COALESCE(NULLIF(pf.descricao, ''), NULLIF(p.descricao, ''), p.nome) AS descricao,
                cp.valor_mensal,
                cp.valor_setup,
                pf.usuarios_inicio AS qtd_minima,
                cp.tem_projeto,
                cp.ativo,
                pf.usuarios_inicio,
                pf.usuarios_fim
            FROM {cls.TABLE} cp
            INNER JOIN produto_faixas pf
                ON pf.id = cp.faixa_id
            INNER JOIN produto_modelos pm
                ON pm.id = pf.modelo_id
            INNER JOIN produtos p
                ON p.id = pm.produto_id
            WHERE cp.id = %s
              AND p.tipo_recurso = 'LICENCA'
              AND cp.ativo = 1
        """

        return cls.fetch_one(sql, (preco_id,))

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                faixa_id,
                valor_mensal,
                valor_setup,
                tem_projeto,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados['faixa_id'],
                dados.get('valor_mensal', 0),
                dados.get('valor_setup', 0),
                cls.bool_to_int(dados.get('tem_projeto', False)),
                cls.bool_to_int(dados.get('ativo', True)),
            ),
        )

    @classmethod
    def atualizar_por_faixa(cls, faixa_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET valor_mensal = %s,
                valor_setup = %s,
                tem_projeto = %s,
                ativo = %s
            WHERE faixa_id = %s
        """

        return cls.execute(
            sql,
            (
                dados.get('valor_mensal', 0),
                dados.get('valor_setup', 0),
                cls.bool_to_int(dados.get('tem_projeto', False)),
                cls.bool_to_int(dados.get('ativo', True)),
                faixa_id,
            ),
        )

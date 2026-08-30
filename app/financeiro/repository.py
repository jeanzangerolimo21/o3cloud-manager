from datetime import date
from datetime import datetime

from app.repositories.base_repository import BaseRepository


class FinanceiroRepository(BaseRepository):


    @classmethod
    def receitas_por_servidor(cls, filtros=None):
        filtros = filtros or {}
        where_nodes = ["n.ativo = 1", "i.tipo = 'proxmox'", "i.ativo = 1"]
        params_nodes = []
        where_detalhes = ["n.ativo = 1", "i.tipo = 'proxmox'", "i.ativo = 1"]
        params_detalhes = []

        node = (filtros.get("node") or "").strip()
        if node:
            where_nodes.append("n.node = %s")
            params_nodes.append(node)
            where_detalhes.append("n.node = %s")
            params_detalhes.append(node)

        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            termo = f"%{pesquisa}%"
            where_nodes.append("""
                (
                    n.node LIKE %s
                    OR i.nome LIKE %s
                    OR i.base_url LIKE %s
                    OR EXISTS (
                        SELECT 1
                        FROM proxmox_vm_inventory p_busca
                        LEFT JOIN ambiente_proxmox_recursos apr_busca ON apr_busca.proxmox_inventory_id = p_busca.id
                        LEFT JOIN ambientes a_busca ON a_busca.id = apr_busca.ambiente_id AND a_busca.ativo = 1
                        LEFT JOIN ambiente_clientes ac_busca ON ac_busca.ambiente_id = a_busca.id
                        LEFT JOIN clientes cli_busca ON cli_busca.id = ac_busca.cliente_id
                        LEFT JOIN ambiente_contratos act_busca ON act_busca.ambiente_id = a_busca.id
                        LEFT JOIN contratos c_busca ON c_busca.id = act_busca.contrato_id AND c_busca.ativo = 1
                        WHERE p_busca.integracao_id = n.integracao_id
                          AND p_busca.node = n.node
                          AND p_busca.ativo = 1
                          AND (
                              a_busca.nome LIKE %s
                              OR c_busca.numero LIKE %s
                              OR COALESCE(cli_busca.nome_fantasia, cli_busca.razao_social, '') LIKE %s
                          )
                    )
                )
            """)
            params_nodes.extend([termo, termo, termo, termo, termo, termo])
            where_detalhes.append("""
                (
                    n.node LIKE %s
                    OR i.nome LIKE %s
                    OR i.base_url LIKE %s
                    OR a.nome LIKE %s
                    OR c.numero LIKE %s
                    OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                )
            """)
            params_detalhes.extend([termo, termo, termo, termo, termo, termo])

        nodes = cls.fetch_all(
            f"""
            SELECT
                n.id,
                n.integracao_id,
                i.nome AS cluster_nome,
                i.base_url,
                n.node,
                n.status,
                n.cpu_total,
                n.memoria_total_mb,
                n.disco_total_gb,
                n.ultimo_sync_em,
                COALESCE(rec.recursos_total, 0) AS recursos_total,
                COALESCE(rec.ambientes_total, 0) AS ambientes_total,
                COALESCE(rec.contratos_total, 0) AS contratos_total,
                COALESCE(rec.receita_mensal, 0) AS receita_mensal
            FROM proxmox_node_inventory n
            INNER JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            LEFT JOIN (
                SELECT
                    recursos.integracao_id,
                    recursos.node,
                    recursos.recursos_total,
                    recursos.ambientes_total,
                    COALESCE(receitas.contratos_total, 0) AS contratos_total,
                    COALESCE(receitas.receita_mensal, 0) AS receita_mensal
                FROM (
                    SELECT
                        p.integracao_id,
                        p.node,
                        COUNT(DISTINCT p.id) AS recursos_total,
                        COUNT(DISTINCT a.id) AS ambientes_total
                    FROM proxmox_vm_inventory p
                    LEFT JOIN ambiente_proxmox_recursos apr ON apr.proxmox_inventory_id = p.id
                    LEFT JOIN ambientes a ON a.id = apr.ambiente_id AND a.ativo = 1
                    WHERE p.ativo = 1
                    GROUP BY p.integracao_id, p.node
                ) recursos
                LEFT JOIN (
                    SELECT
                        base.integracao_id,
                        base.node,
                        COUNT(DISTINCT base.contrato_id) AS contratos_total,
                        COALESCE(SUM(base.receita_mensal), 0) AS receita_mensal
                    FROM (
                        SELECT DISTINCT
                            p.integracao_id,
                            p.node,
                            c.id AS contrato_id,
                            COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS receita_mensal
                        FROM proxmox_vm_inventory p
                        INNER JOIN ambiente_proxmox_recursos apr ON apr.proxmox_inventory_id = p.id
                        INNER JOIN ambientes a ON a.id = apr.ambiente_id AND a.ativo = 1
                        INNER JOIN ambiente_contratos act ON act.ambiente_id = a.id
                        INNER JOIN contratos c ON c.id = act.contrato_id AND c.ativo = 1 AND c.status = 'ATIVO'
                        WHERE p.ativo = 1
                    ) base
                    GROUP BY base.integracao_id, base.node
                ) receitas ON receitas.integracao_id = recursos.integracao_id AND receitas.node = recursos.node
            ) rec ON rec.integracao_id = n.integracao_id AND rec.node = n.node
            WHERE {' AND '.join(where_nodes)}
            ORDER BY receita_mensal DESC, n.node ASC
            """,
            tuple(params_nodes),
        )

        detalhes = cls.fetch_all(
            f"""
            SELECT
                n.integracao_id,
                i.nome AS cluster_nome,
                n.node,
                a.id AS ambiente_id,
                a.nome AS ambiente_nome,
                a.ambiente_tipo,
                COALESCE(GROUP_CONCAT(DISTINCT COALESCE(cli_amb.nome_fantasia, cli_amb.razao_social) ORDER BY COALESCE(cli_amb.nome_fantasia, cli_amb.razao_social) SEPARATOR ', '), '-') AS ambiente_clientes,
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_contrato,
                c.status AS contrato_status,
                COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS receita_mensal,
                COUNT(DISTINCT p.id) AS recursos_total,
                GROUP_CONCAT(DISTINCT CONCAT(UPPER(p.tipo), ' ', p.vmid, ' - ', COALESCE(p.nome, '-')) ORDER BY p.vmid SEPARATOR ' | ') AS recursos
            FROM proxmox_node_inventory n
            INNER JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            INNER JOIN proxmox_vm_inventory p ON p.integracao_id = n.integracao_id AND p.node = n.node AND p.ativo = 1
            INNER JOIN ambiente_proxmox_recursos apr ON apr.proxmox_inventory_id = p.id
            INNER JOIN ambientes a ON a.id = apr.ambiente_id AND a.ativo = 1
            LEFT JOIN ambiente_clientes ac ON ac.ambiente_id = a.id
            LEFT JOIN clientes cli_amb ON cli_amb.id = ac.cliente_id
            INNER JOIN ambiente_contratos act ON act.ambiente_id = a.id
            INNER JOIN contratos c ON c.id = act.contrato_id AND c.ativo = 1 AND c.status = 'ATIVO'
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE {' AND '.join(where_detalhes)}
            GROUP BY n.integracao_id, i.nome, n.node, a.id, a.nome, a.ambiente_tipo,
                     c.id, c.numero, cliente_contrato, c.status, c.valor_promocional, c.valor_mensal
            ORDER BY n.node ASC, receita_mensal DESC, a.nome ASC, c.numero ASC
            LIMIT 300
            """,
            tuple(params_detalhes),
        )

        nodes_select = cls.fetch_all(
            """
            SELECT DISTINCT n.node
            FROM proxmox_node_inventory n
            INNER JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            WHERE n.ativo = 1
              AND i.tipo = 'proxmox'
              AND i.ativo = 1
            ORDER BY n.node ASC
            """
        )

        receita_total = sum(item.get("receita_mensal") or 0 for item in nodes)
        recursos_total = sum(item.get("recursos_total") or 0 for item in nodes)
        ambientes_total = len({item.get("ambiente_id") for item in detalhes if item.get("ambiente_id")})
        contratos_total = len({item.get("contrato_id") for item in detalhes if item.get("contrato_id")})

        return {
            "resumo": {
                "nodes_total": len(nodes),
                "nodes_com_receita": len([item for item in nodes if (item.get("receita_mensal") or 0) > 0]),
                "receita_mensal": receita_total,
                "recursos_total": recursos_total,
                "ambientes_total": ambientes_total,
                "contratos_total": contratos_total,
            },
            "nodes": nodes,
            "detalhes": detalhes,
            "nodes_select": nodes_select,
        }


    @classmethod
    def listar_faturamentos(cls, limite=100):

        return cls.fetch_all(
            """
            SELECT f.id, f.contrato_id, f.competencia, f.origem,
                   f.valor_bruto, f.percentual_comissao, f.valor_comissao,
                   f.valor_liquido, f.observacoes, f.updated_at,
                   c.numero AS contrato_numero,
                   c.codigo_externo AS contrato_codigo_externo,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM faturamentos f
            INNER JOIN contratos c
                ON c.id = f.contrato_id
            INNER JOIN clientes cli
                ON cli.id = c.cliente_id
            WHERE f.ativo = 1
            ORDER BY f.competencia DESC, f.updated_at DESC, f.id DESC
            LIMIT %s
            """,
            (limite,),
        )

    @classmethod
    def resumo_faturamentos(cls):

        return cls.fetch_one(
            """
            SELECT COUNT(*) AS total,
                   COUNT(DISTINCT contrato_id) AS contratos_total,
                   MIN(competencia) AS primeira_competencia,
                   MAX(competencia) AS ultima_competencia,
                   COALESCE(SUM(valor_bruto), 0) AS valor_bruto,
                   COALESCE(SUM(valor_liquido), 0) AS valor_liquido
            FROM faturamentos
            WHERE ativo = 1
            """
        ) or {}


    @classmethod
    def listar_recebimentos_omie(cls, filtros=None, limite=50, offset=0):
        filtros = filtros or {}
        where = [
            "r.contrato_id IS NOT NULL",
            "r.cliente_id IS NOT NULL",
            "COALESCE(r.numero_documento_fiscal, '') <> ''",
        ]
        params = []

        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, '') LIKE %s
                    OR COALESCE(cli.razao_social, '') LIKE %s
                    OR COALESCE(c.numero, r.numero_contrato, '') LIKE %s
                    OR COALESCE(r.numero_documento, '') LIKE %s
                    OR COALESCE(r.numero_documento_fiscal, '') LIKE %s
                    OR COALESCE(r.categoria_nome, '') LIKE %s
                )
            """)
            params.extend([like, like, like, like, like, like])

        if filtros.get("data_de"):
            where.append("r.data_recebimento >= %s")
            params.append(filtros["data_de"])
        if filtros.get("data_ate"):
            where.append("r.data_recebimento <= %s")
            params.append(filtros["data_ate"])
        if filtros.get("categoria_excluida") in ("0", "1"):
            where.append("r.categoria_excluida = %s")
            params.append(int(filtros["categoria_excluida"]))
        if filtros.get("situacao"):
            where.append("UPPER(r.situacao) = %s")
            params.append(filtros["situacao"].upper())
        where_sql = " WHERE " + " AND ".join(where)
        params.extend([limite, offset])

        return cls.fetch_all(
            f"""
            SELECT
                r.id,
                r.codigo_externo,
                r.contrato_id,
                r.numero_contrato,
                r.numero_documento,
                r.numero_documento_fiscal,
                r.numero_parcela,
                r.categoria_codigo,
                r.categoria_nome,
                r.categoria_excluida,
                r.motivo_exclusao,
                r.valor_original,
                r.valor_recebido,
                r.valor_desconto,
                r.valor_juros,
                r.data_vencimento,
                r.data_recebimento,
                r.data_emissao,
                r.situacao,
                r.codigo_cliente_omie,
                r.codigo_vendedor,
                r.codigo_projeto,
                c.numero AS contrato_numero,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM financeiro_recebimentos r
            LEFT JOIN contratos c ON c.id = r.contrato_id
            LEFT JOIN clientes cli ON cli.id = r.cliente_id
            {where_sql}
            ORDER BY r.data_recebimento DESC, r.id DESC
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )

    @classmethod
    def resumo_recebimentos_omie(cls, filtros=None):
        filtros = filtros or {}
        where = [
            "r.contrato_id IS NOT NULL",
            "r.cliente_id IS NOT NULL",
            "COALESCE(r.numero_documento_fiscal, '') <> ''",
        ]
        params = []

        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, '') LIKE %s
                    OR COALESCE(cli.razao_social, '') LIKE %s
                    OR COALESCE(c.numero, r.numero_contrato, '') LIKE %s
                    OR COALESCE(r.numero_documento, '') LIKE %s
                    OR COALESCE(r.numero_documento_fiscal, '') LIKE %s
                    OR COALESCE(r.categoria_nome, '') LIKE %s
                )
            """)
            params.extend([like, like, like, like, like, like])

        if filtros.get("data_de"):
            where.append("r.data_recebimento >= %s")
            params.append(filtros["data_de"])
        if filtros.get("data_ate"):
            where.append("r.data_recebimento <= %s")
            params.append(filtros["data_ate"])
        if filtros.get("categoria_excluida") in ("0", "1"):
            where.append("r.categoria_excluida = %s")
            params.append(int(filtros["categoria_excluida"]))
        if filtros.get("situacao"):
            where.append("UPPER(r.situacao) = %s")
            params.append(filtros["situacao"].upper())
        where_sql = " WHERE " + " AND ".join(where)
        return cls.fetch_one(
            f"""
            SELECT
                COUNT(*) AS total,
                COUNT(DISTINCT r.contrato_id) AS contratos_total,
                COALESCE(SUM(CASE WHEN UPPER(COALESCE(r.situacao, '')) IN ('RECEBIDO', 'PAGO', 'LIQUIDADO') THEN r.valor_recebido ELSE 0 END), 0) AS valor_recebido,
                COALESCE(SUM(CASE WHEN UPPER(COALESCE(r.situacao, '')) IN ('ATRASADO', 'VENCIDO') THEN r.valor_recebido ELSE 0 END), 0) AS valor_atrasado,
                COUNT(*) AS vinculados,
                0 AS sem_vinculo,
                SUM(r.categoria_excluida = 1) AS categorias_excluidas,
                MIN(r.data_recebimento) AS primeira_data,
                MAX(r.data_recebimento) AS ultima_data,
                SUM(CASE WHEN UPPER(COALESCE(r.situacao, '')) IN ('ATRASADO', 'VENCIDO') THEN 1 ELSE 0 END) AS atrasados
            FROM financeiro_recebimentos r
            LEFT JOIN contratos c ON c.id = r.contrato_id
            LEFT JOIN clientes cli ON cli.id = r.cliente_id
            {where_sql}
            """,
            tuple(params),
        ) or {}

    @classmethod
    def situacoes_recebimentos_omie(cls):
        return cls.fetch_all(
            """
            SELECT UPPER(COALESCE(situacao, '')) AS situacao, COUNT(*) AS total
            FROM financeiro_recebimentos
            WHERE contrato_id IS NOT NULL
              AND cliente_id IS NOT NULL
              AND COALESCE(numero_documento_fiscal, '') <> ''
            GROUP BY UPPER(COALESCE(situacao, ''))
            ORDER BY situacao
            """
        )

    @classmethod
    def listar_campanhas_comissao(cls):
        return cls.fetch_all(
            """
            SELECT id, nome, percentual_parceiro, percentual_executivo, vigencia_inicio, vigencia_fim, ativo
            FROM regras_campanhas_comissao
            WHERE ativo = 1
            ORDER BY vigencia_inicio DESC, id DESC
            """
        )

    @classmethod
    def buscar_campanha_comissao(cls, campanha_id):
        if not campanha_id:
            return None
        return cls.fetch_one(
            """
            SELECT id, nome, percentual_parceiro, percentual_executivo, vigencia_inicio, vigencia_fim, ativo
            FROM regras_campanhas_comissao
            WHERE id = %s
              AND ativo = 1
            LIMIT 1
            """,
            (campanha_id,),
        )

    @classmethod
    def listar_comissoes_contratos(cls, filtros=None, limite=50, offset=0):
        sql, params = cls._comissoes_sql(filtros)
        params.extend([limite, offset])
        return cls.fetch_all(
            f"""
            {sql}
            ORDER BY base.status_pagamento ASC, base.cliente_nome ASC, base.contrato_numero ASC
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )

    @classmethod
    def buscar_comissao_contrato(cls, contrato_id, campanha_id=None):
        filtros = {"contrato_id": contrato_id}
        if campanha_id:
            filtros["campanha_id"] = campanha_id
        sql, params = cls._comissoes_sql(filtros)
        return cls.fetch_one(
            f"""
            {sql}
            ORDER BY base.campanha_inicio DESC, base.campanha_id DESC
            LIMIT 1
            """,
            tuple(params),
        )

    @classmethod
    def listar_campanhas_contrato(cls, contrato_id):
        return cls.fetch_all(
            """
            SELECT rc.id, rc.nome, rc.percentual_parceiro, rc.percentual_executivo, rc.vigencia_inicio, rc.vigencia_fim
            FROM contratos c
            INNER JOIN regras_campanhas_comissao rc
                ON rc.ativo = 1
               AND c.inicio_vigencia BETWEEN rc.vigencia_inicio AND rc.vigencia_fim
            WHERE c.id = %s
              AND c.ativo = 1
              AND c.status = 'ATIVO'
            ORDER BY rc.vigencia_inicio DESC, rc.id DESC
            """,
            (contrato_id,),
        )

    @classmethod
    def resumo_comissoes_contratos(cls, filtros=None):
        sql, params = cls._comissoes_sql(filtros)
        return cls.fetch_one(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(base.status_pagamento = 'RECEBIDO') AS contratos_recebidos,
                SUM(base.status_pagamento = 'ATRASADO') AS contratos_atrasados,
                SUM(base.status_pagamento = 'NAO_LOCALIZADO') AS contratos_nao_localizados,
                COALESCE(SUM(base.valor_base_comissao), 0) AS valor_base_comissao,
                COALESCE(SUM(base.valor_recebido_elegivel), 0) AS valor_recebido_elegivel,
                COALESCE(SUM(base.valor_atrasado), 0) AS valor_atrasado,
                COALESCE(SUM(base.valor_comissao_prevista), 0) AS valor_comissao_prevista
            FROM ({sql}) base
            """,
            tuple(params),
        ) or {}

    @classmethod
    def _comissoes_sql(cls, filtros=None):
        filtros = filtros or {}
        where = [
            "c.ativo = 1",
            "c.status = 'ATIVO'",
        ]
        params = []

        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, '') LIKE %s
                    OR COALESCE(cli.razao_social, '') LIKE %s
                    OR COALESCE(c.numero, '') LIKE %s
                    OR COALESCE(c.vendedor_nome, '') LIKE %s
                    OR COALESCE(c.projeto_nome, '') LIKE %s
                )
            """)
            params.extend([like, like, like, like, like])

        contrato_id = filtros.get("contrato_id")
        if contrato_id:
            where.append("c.id = %s")
            params.append(contrato_id)

        campanha_id = filtros.get("campanha_id")
        if campanha_id:
            where.append("rc.id = %s")
            params.append(campanha_id)

        where_sql = " AND ".join(where)
        base_valor = "COALESCE(NULLIF(c.valor_servicos_liquido, 0), NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)"
        sql = f"""
            SELECT *
            FROM (
                SELECT
                    c.id AS contrato_id,
                    c.numero AS contrato_numero,
                    c.codigo_externo AS contrato_codigo_externo,
                    c.inicio_vigencia,
                    c.fim_vigencia,
                    c.valor_servicos_liquido,
                    c.valor_promocional,
                    c.valor_mensal,
                    c.vendedor_nome,
                    c.codigo_vendedor,
                    p.id AS parceiro_premiacao_id,
                    p.nome AS parceiro_premiacao_nome,
                    CASE
                        WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' THEN pe_omie.id
                        ELSE pe_manual.id
                    END AS executivo_premiacao_id,
                    CASE
                        WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' THEN pe_omie.nome
                        ELSE pe_manual.nome
                    END AS executivo_premiacao_nome,
                    CASE
                        WHEN p.id IS NOT NULL
                          OR (COALESCE(TRIM(c.projeto_nome), '') <> '' AND pe_omie.id IS NOT NULL)
                          OR (COALESCE(TRIM(c.projeto_nome), '') = '' AND pe_manual.id IS NOT NULL) THEN 1
                        ELSE 0
                    END AS premiacao_liberada,
                    c.projeto_nome,
                    c.codigo_projeto,
                    cli.id AS cliente_id,
                    COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                    cli.razao_social,
                    rc.id AS campanha_id,
                    rc.nome AS campanha_nome,
                    rc.percentual_parceiro,
                    rc.percentual_executivo,
                    CASE WHEN p.id IS NOT NULL THEN rc.percentual_parceiro ELSE 0 END AS percentual_parceiro_aplicado,
                    CASE
                        WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' AND pe_omie.id IS NOT NULL THEN rc.percentual_executivo
                        WHEN COALESCE(TRIM(c.projeto_nome), '') = '' AND pe_manual.id IS NOT NULL THEN rc.percentual_executivo
                        ELSE 0
                    END AS percentual_executivo_aplicado,
                    rc.vigencia_inicio AS campanha_inicio,
                    rc.vigencia_fim AS campanha_fim,
                    COALESCE(fpp.status_manual, 'ABERTO') AS status_premiacao_manual,
                    fpp.updated_at AS status_premiacao_updated_at,
                    fpp.updated_by AS status_premiacao_updated_by,
                    {base_valor} AS valor_base_comissao,
                    COALESCE(SUM(CASE
                        WHEN UPPER(COALESCE(r.situacao, '')) IN ('RECEBIDO', 'PAGO', 'LIQUIDADO')
                         AND COALESCE(r.categoria_excluida, 0) = 0
                        THEN r.valor_recebido ELSE 0 END), 0) AS valor_recebido_elegivel,
                    COALESCE(SUM(CASE
                        WHEN UPPER(COALESCE(r.situacao, '')) IN ('ATRASADO', 'VENCIDO')
                        THEN COALESCE(r.valor_recebido, r.valor_original, 0) ELSE 0 END), 0) AS valor_atrasado,
                    COALESCE(SUM(CASE
                        WHEN COALESCE(r.categoria_excluida, 0) = 1
                        THEN r.valor_recebido ELSE 0 END), 0) AS valor_recebido_excluido,
                    COUNT(r.id) AS recebimentos_total,
                    SUM(COALESCE(r.categoria_excluida, 0) = 1) AS recebimentos_excluidos,
                    CASE
                        WHEN COALESCE(SUM(CASE
                            WHEN UPPER(COALESCE(r.situacao, '')) IN ('ATRASADO', 'VENCIDO')
                            THEN COALESCE(r.valor_recebido, r.valor_original, 0) ELSE 0 END), 0) > 0 THEN 'ATRASADO'
                        WHEN COALESCE(SUM(CASE
                            WHEN UPPER(COALESCE(r.situacao, '')) IN ('RECEBIDO', 'PAGO', 'LIQUIDADO')
                             AND COALESCE(r.categoria_excluida, 0) = 0
                            THEN r.valor_recebido ELSE 0 END), 0) > 0 THEN 'RECEBIDO'
                        ELSE 'NAO_LOCALIZADO'
                    END AS status_pagamento,
                    ROUND(({base_valor}) * CASE WHEN p.id IS NOT NULL THEN COALESCE(rc.percentual_parceiro, 0) ELSE 0 END / 100, 2) AS valor_premiacao_parceiro,
                    ROUND(({base_valor}) * CASE
                        WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' AND pe_omie.id IS NOT NULL THEN COALESCE(rc.percentual_executivo, 0)
                        WHEN COALESCE(TRIM(c.projeto_nome), '') = '' AND pe_manual.id IS NOT NULL THEN COALESCE(rc.percentual_executivo, 0)
                        ELSE 0
                    END / 100, 2) AS valor_premiacao_executivo,
                    ROUND(({base_valor}) * (CASE WHEN p.id IS NOT NULL THEN COALESCE(rc.percentual_parceiro, 0) ELSE 0 END + CASE
                        WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' AND pe_omie.id IS NOT NULL THEN COALESCE(rc.percentual_executivo, 0)
                        WHEN COALESCE(TRIM(c.projeto_nome), '') = '' AND pe_manual.id IS NOT NULL THEN COALESCE(rc.percentual_executivo, 0)
                        ELSE 0
                    END) / 100, 2) AS valor_comissao_prevista
                FROM contratos c
                INNER JOIN clientes cli ON cli.id = c.cliente_id
                LEFT JOIN parceiros p ON p.id = c.parceiro_id AND p.ativo = 1 AND COALESCE(p.premiacao_ativa, 0) = 1
                LEFT JOIN regras_campanhas_comissao rc
                    ON rc.ativo = 1
                   AND c.inicio_vigencia BETWEEN rc.vigencia_inicio AND rc.vigencia_fim
                LEFT JOIN (
                    SELECT
                        LOWER(TRIM(nome)) COLLATE utf8mb4_unicode_ci AS nome_normalizado,
                        MIN(id) AS id,
                        MIN(nome) AS nome
                    FROM parceiros_executivos
                    WHERE ativo = 1
                      AND COALESCE(premiacao_ativa, 0) = 1
                    GROUP BY LOWER(TRIM(nome)) COLLATE utf8mb4_unicode_ci
                ) pe_omie
                    ON pe_omie.nome_normalizado = LOWER(TRIM(c.projeto_nome)) COLLATE utf8mb4_unicode_ci
                LEFT JOIN parceiros_executivos pe_manual
                    ON pe_manual.id = c.executivo_id
                   AND pe_manual.ativo = 1
                   AND COALESCE(pe_manual.premiacao_ativa, 0) = 1
                LEFT JOIN financeiro_premiacoes_pagamento fpp
                    ON fpp.contrato_id = c.id
                   AND fpp.campanha_id = rc.id
                LEFT JOIN financeiro_recebimentos r
                    ON r.id = (
                        SELECT r1.id
                        FROM financeiro_recebimentos r1
                        WHERE r1.contrato_id = c.id
                          AND r1.cliente_id = cli.id
                          AND COALESCE(r1.numero_documento_fiscal, '') <> ''
                        ORDER BY
                          CASE WHEN COALESCE(TRIM(r1.numero_parcela), '') REGEXP '^[0-9]+$' THEN CAST(r1.numero_parcela AS UNSIGNED) ELSE 999999 END ASC,
                          r1.data_vencimento IS NULL ASC,
                          r1.data_vencimento ASC,
                          r1.id ASC
                        LIMIT 1
                    )
                WHERE {where_sql}
                GROUP BY
                    c.id, c.numero, c.codigo_externo, c.inicio_vigencia, c.fim_vigencia,
                    c.valor_servicos_liquido, c.valor_promocional, c.valor_mensal,
                    c.vendedor_nome, c.codigo_vendedor, c.executivo_id, p.id, p.nome, pe_omie.id, pe_omie.nome, pe_manual.id, pe_manual.nome, c.projeto_nome, c.codigo_projeto,
                    cli.id, cli.nome_fantasia, cli.razao_social,
                    rc.id, rc.nome, rc.percentual_parceiro, rc.percentual_executivo, rc.vigencia_inicio, rc.vigencia_fim,
                    fpp.status_manual, fpp.updated_at, fpp.updated_by
            ) base
        """

        filtros_base = ["base.premiacao_liberada = 1", "base.campanha_id IS NOT NULL"]

        status = (filtros.get("status_pagamento") or "").strip().upper()
        if status in ("RECEBIDO", "ATRASADO", "NAO_LOCALIZADO"):
            filtros_base.append("base.status_pagamento = %s")
            params.append(status)

        if filtros_base:
            sql += " WHERE " + " AND ".join(filtros_base)
        return sql, params

    @classmethod
    def salvar_status_premiacao_manual(cls, contrato_id, campanha_id, status_manual, usuario_email=None):
        return cls.execute_insert(
            """
            INSERT INTO financeiro_premiacoes_pagamento (
                uuid, contrato_id, campanha_id, status_manual, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status_manual = VALUES(status_manual),
                updated_by = VALUES(updated_by),
                updated_at = NOW()
            """,
            (
                cls.generate_uuid(),
                contrato_id,
                campanha_id,
                status_manual,
                usuario_email or "sistema",
                usuario_email or "sistema",
            ),
        )

    @classmethod
    def buscar_base_premiacao_contrato(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.cliente_id,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                p.id AS parceiro_premiacao_id,
                p.nome AS parceiro_premiacao_nome,
                CASE
                    WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' THEN pe_omie.id
                    ELSE pe_manual.id
                END AS executivo_premiacao_id,
                CASE
                    WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' THEN pe_omie.nome
                    ELSE pe_manual.nome
                END AS executivo_premiacao_nome,
                CASE
                    WHEN p.id IS NOT NULL
                      OR (COALESCE(TRIM(c.projeto_nome), '') <> '' AND pe_omie.id IS NOT NULL)
                      OR (COALESCE(TRIM(c.projeto_nome), '') = '' AND pe_manual.id IS NOT NULL) THEN 1
                    ELSE 0
                END AS premiacao_liberada
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id AND p.ativo = 1 AND COALESCE(p.premiacao_ativa, 0) = 1
            LEFT JOIN (
                SELECT
                    LOWER(TRIM(nome)) COLLATE utf8mb4_unicode_ci AS nome_normalizado,
                    MIN(id) AS id,
                    MIN(nome) AS nome
                FROM parceiros_executivos
                WHERE ativo = 1
                  AND COALESCE(premiacao_ativa, 0) = 1
                GROUP BY LOWER(TRIM(nome)) COLLATE utf8mb4_unicode_ci
            ) pe_omie
                ON pe_omie.nome_normalizado = LOWER(TRIM(c.projeto_nome)) COLLATE utf8mb4_unicode_ci
            LEFT JOIN parceiros_executivos pe_manual
                ON pe_manual.id = c.executivo_id
               AND pe_manual.ativo = 1
               AND COALESCE(pe_manual.premiacao_ativa, 0) = 1
            WHERE c.id = %s
              AND c.ativo = 1
              AND c.status = 'ATIVO'
            LIMIT 1
            """,
            (contrato_id,),
        )

    @classmethod
    def atualizar_premiacoes_adendos_sem_executivo_por_vinculo_manual(cls, usuario_email="sistema", adendo_id=None):
        where_adendo = ""
        params = []
        if adendo_id:
            where_adendo = "\n              AND pa.adendo_id = %s"
            params.append(adendo_id)

        sql = f"""
            UPDATE financeiro_premiacoes_adendos pa
            INNER JOIN contratos_adendos a
                ON a.id = pa.adendo_id
               AND a.ativo = 1
            INNER JOIN contratos c
                ON c.id = pa.contrato_id
               AND c.ativo = 1
               AND c.status = 'ATIVO'
            INNER JOIN parceiros_executivos pe_manual
                ON pe_manual.id = c.executivo_id
               AND pe_manual.ativo = 1
               AND COALESCE(pe_manual.premiacao_ativa, 0) = 1
            INNER JOIN regras_campanhas_comissao rc
                ON rc.id = pa.campanha_id
               AND rc.ativo = 1
            SET pa.executivo_id = pe_manual.id,
                pa.percentual_executivo = COALESCE(rc.percentual_executivo, 0),
                pa.valor_premiacao_executivo = ROUND(pa.valor_base * COALESCE(rc.percentual_executivo, 0) / 100, 2),
                pa.valor_total = COALESCE(pa.valor_premiacao_parceiro, 0) + ROUND(pa.valor_base * COALESCE(rc.percentual_executivo, 0) / 100, 2),
                pa.updated_by = %s,
                pa.updated_at = NOW()
            WHERE pa.ativo = 1
              AND pa.executivo_id IS NULL
              AND COALESCE(TRIM(c.projeto_nome), '') = ''
              AND c.executivo_id IS NOT NULL{where_adendo}
        """
        return cls.execute(sql, tuple([usuario_email or "sistema", *params]))


    @classmethod
    def listar_premiacoes_adendos(cls, filtros=None, limite=80):
        where, params = cls._filtros_premiacoes_adendos(filtros)
        params.append(limite)
        return cls.fetch_all(
            f"""
            SELECT pa.*,
                   a.titulo AS adendo_titulo,
                   a.tipo AS adendo_tipo,
                   a.numero_adendo,
                   c.numero AS contrato_numero,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   p.nome AS parceiro_nome,
                   pe.nome AS executivo_nome,
                   rc.nome AS campanha_nome
            FROM financeiro_premiacoes_adendos pa
            INNER JOIN contratos_adendos a ON a.id = pa.adendo_id
            INNER JOIN contratos c ON c.id = pa.contrato_id
            INNER JOIN clientes cli ON cli.id = pa.cliente_id
            LEFT JOIN parceiros p ON p.id = pa.parceiro_id
            LEFT JOIN parceiros_executivos pe ON pe.id = pa.executivo_id
            LEFT JOIN regras_campanhas_comissao rc ON rc.id = pa.campanha_id
            WHERE {where}
            ORDER BY pa.data_lancamento DESC, pa.id DESC
            LIMIT %s
            """,
            tuple(params),
        )

    @classmethod
    def resumo_premiacoes_adendos(cls, filtros=None):
        where, params = cls._filtros_premiacoes_adendos(filtros)
        return cls.fetch_one(
            f"""
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(pa.valor_base), 0) AS valor_base,
                   COALESCE(SUM(pa.valor_total), 0) AS valor_total,
                   SUM(pa.status_manual = 'ABERTO') AS abertos,
                   SUM(pa.status_manual = 'LANCADO') AS lancados,
                   SUM(pa.status_manual = 'PAGO') AS pagos
            FROM financeiro_premiacoes_adendos pa
            INNER JOIN contratos_adendos a ON a.id = pa.adendo_id
            INNER JOIN contratos c ON c.id = pa.contrato_id
            INNER JOIN clientes cli ON cli.id = pa.cliente_id
            WHERE {where}
            """,
            tuple(params),
        ) or {}

    @classmethod
    def _filtros_premiacoes_adendos(cls, filtros=None):
        filtros = filtros or {}
        where = ["pa.ativo = 1", "a.ativo = 1", "c.ativo = 1"]
        params = []

        campanha_id = filtros.get("campanha_id")
        if campanha_id:
            where.append("pa.campanha_id = %s")
            params.append(campanha_id)

        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, '') LIKE %s
                    OR COALESCE(cli.razao_social, '') LIKE %s
                    OR COALESCE(c.numero, '') LIKE %s
                    OR COALESCE(a.titulo, '') LIKE %s
                    OR COALESCE(a.numero_adendo, '') LIKE %s
                )
            """)
            params.extend([like, like, like, like, like])

        return " AND ".join(where), params

    @classmethod
    def buscar_premiacao_adendo(cls, adendo_id):
        return cls.fetch_one(
            """
            SELECT *
            FROM financeiro_premiacoes_adendos
            WHERE adendo_id = %s
              AND ativo = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (adendo_id,),
        )

    @classmethod
    def inserir_premiacao_adendo(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO financeiro_premiacoes_adendos (
                uuid, adendo_id, contrato_id, cliente_id, campanha_id, parceiro_id, executivo_id, descricao, data_lancamento,
                valor_base, percentual_parceiro, percentual_executivo, valor_premiacao_parceiro,
                valor_premiacao_executivo, valor_total, status_manual, observacoes, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("adendo_id"), dados.get("contrato_id"), dados.get("cliente_id"),
                dados.get("campanha_id"), dados.get("parceiro_id"), dados.get("executivo_id"), dados.get("descricao"), dados.get("data_lancamento"),
                dados.get("valor_base"), dados.get("percentual_parceiro"), dados.get("percentual_executivo"),
                dados.get("valor_premiacao_parceiro"), dados.get("valor_premiacao_executivo"), dados.get("valor_total"),
                dados.get("status_manual"), dados.get("observacoes"), dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def contratos_para_faturamento(cls):

        return cls.fetch_all(
            """
            SELECT c.id, c.numero, c.codigo_externo,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS valor_mensal
            FROM contratos c
            INNER JOIN clientes cli
                ON cli.id = c.cliente_id
            WHERE c.ativo = 1
              AND c.status IN ('ATIVO', 'EM_IMPLANTACAO', 'CONCLUIDO')
            ORDER BY cliente_nome ASC, c.numero ASC
            """
        )

    @classmethod
    def buscar_contrato_faturamento(cls, identificador):

        contrato = cls.fetch_one(
            """
            SELECT id, numero, codigo_externo
            FROM contratos
            WHERE ativo = 1
              AND CAST(id AS CHAR) = %s
            LIMIT 1
            """,
            (identificador,),
        )
        if contrato:
            return contrato

        return cls.fetch_one(
            """
            SELECT id, numero, codigo_externo
            FROM contratos
            WHERE ativo = 1
              AND (numero = %s OR CAST(codigo_externo AS CHAR) = %s)
            ORDER BY id DESC
            LIMIT 1
            """,
            (identificador, identificador),
        )

    @classmethod
    def salvar_faturamento(cls, dados):

        sql = """
            INSERT INTO faturamentos (
                uuid,
                contrato_id,
                competencia,
                origem,
                valor_bruto,
                percentual_comissao,
                valor_comissao,
                valor_liquido,
                observacoes,
                ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                origem = VALUES(origem),
                valor_bruto = VALUES(valor_bruto),
                percentual_comissao = VALUES(percentual_comissao),
                valor_comissao = VALUES(valor_comissao),
                valor_liquido = VALUES(valor_liquido),
                observacoes = VALUES(observacoes),
                ativo = 1
        """

        return cls.execute(
            sql,
            (
                cls.generate_uuid(),
                dados["contrato_id"],
                dados["competencia"],
                dados["origem"],
                dados["valor_bruto"],
                dados["percentual_comissao"],
                dados["valor_comissao"],
                dados["valor_liquido"],
                dados.get("observacoes"),
            ),
        )

    @classmethod
    def total_clientes(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM clientes
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def total_contratos(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM contratos
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def total_produtos(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM produtos
            WHERE ativo = 1
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total

    @classmethod
    def receita_total(cls):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(COALESCE(NULLIF(valor_promocional, 0), valor_mensal, 0)), 0)
            FROM contratos
            WHERE ativo = 1
              AND status = 'ATIVO'
        """)

        total = cursor.fetchone()[0]

        cls.close(conn, cursor)

        return total


    @classmethod
    def dashboard_executivo(cls, filtros=None):
        filtros = filtros or {}
        proposta_where, proposta_params = cls._filtros_propostas(filtros)
        contrato_where, contrato_params = cls._filtros_contratos(filtros)
        implantacao_where, implantacao_params = cls._filtros_implantacoes(filtros)
        resumo = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM clientes WHERE ativo = 1) AS total_clientes,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where}) AS total_propostas,
                (SELECT COALESCE(SUM(COALESCE(p.total_mensal, 0)), 0) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where}) AS propostas_mensal,
                (SELECT COALESCE(SUM(COALESCE(p.total_instalacao, 0)), 0) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where}) AS propostas_setup,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where} AND COALESCE(p.clicksign_status, 'NAO_ENVIADO') IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')) AS propostas_em_assinatura,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where} AND COALESCE(p.clicksign_status, 'NAO_ENVIADO') IN ('ASSINADO', 'CONCLUIDO')) AS propostas_assinadas,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where}) AS total_contratos,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.status = 'ATIVO') AS contratos_ativos,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.status IN ('ENCAMINHADO_PROJETO', 'EM_ELABORACAO')) AS contratos_encaminhados,
                (SELECT COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.status = 'ATIVO') AS receita_mensal_ativa,
                (SELECT COALESCE(SUM(COALESCE(c.valor_setup, 0) + COALESCE(c.valor_projeto, 0)), 0) FROM contratos c WHERE c.ativo = 1 {contrato_where}) AS contratos_setup,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where}) AS total_implantacoes,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status IN ('EM_EXECUCAO', 'EM_VALIDACAO')) AS implantacoes_em_andamento,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega < CURDATE()) AS implantacoes_atrasadas,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)) AS implantacoes_vence_7,
                (SELECT COALESCE(ROUND(AVG(COALESCE(i.percentual_conclusao, 0)), 0), 0) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA')) AS checklist_medio
            """,
            tuple(
                proposta_params * 5
                + contrato_params * 5
                + implantacao_params * 5
            ),
        )
        return {
            "resumo": resumo or {},
            "pre_beta": cls._pre_beta(filtros),
            "propostas_status": cls._propostas_status(filtros),
            "contratos_status": cls._contratos_status(filtros),
            "implantacoes_status": cls._implantacoes_status(filtros),
            "por_executivo": cls._por_executivo(filtros),
            "por_parceiro": cls._por_parceiro(filtros),
            "implantacoes_criticas": cls._implantacoes_criticas(filtros),
            "contratos_pendentes_implantacao": cls._contratos_pendentes_implantacao(filtros),
            "propostas_pendentes_assinatura": cls._propostas_pendentes_assinatura(filtros),
            "evolucao_mensal": cls._evolucao_mensal(filtros),
            "base_rentabilidade": cls._base_rentabilidade(filtros),
            "contratos_base_rentabilidade": cls._contratos_base_rentabilidade(filtros),
            "carga_implantadores": cls._carga_implantadores(filtros),
            "rastreabilidade_executiva": cls._rastreabilidade_executiva(filtros),
            "fluxos_rastreabilidade": cls._fluxos_rastreabilidade(filtros),
            "visao_geral": cls._visao_geral_operacional(),
        }

    @classmethod
    def _pre_beta(cls, filtros):
        proposta_where, proposta_params = cls._filtros_propostas(filtros)
        contrato_where, contrato_params = cls._filtros_contratos(filtros)
        implantacao_where, implantacao_params = cls._filtros_implantacoes(filtros)

        comercial = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM clientes cli WHERE cli.ativo = 1) AS clientes_total,
                (SELECT COUNT(*) FROM clientes cli WHERE cli.ativo = 1 AND NULLIF(TRIM(cli.cnpj), '') IS NULL) AS clientes_sem_cnpj,
                (SELECT COUNT(*) FROM clientes cli WHERE cli.ativo = 1 AND NULLIF(TRIM(cli.email), '') IS NULL) AS clientes_sem_email,
                (SELECT COUNT(*) FROM clientes cli WHERE cli.ativo = 1 AND NULLIF(TRIM(cli.telefone), '') IS NULL) AS clientes_sem_telefone,
                (SELECT COUNT(*) FROM clientes cli WHERE cli.ativo = 1 AND (NULLIF(TRIM(cli.cidade), '') IS NULL OR NULLIF(TRIM(cli.estado), '') IS NULL)) AS clientes_sem_localizacao,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where}) AS propostas_total,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where} AND p.cliente_id IS NULL) AS propostas_sem_cliente_vinculado,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where} AND NULLIF(TRIM(p.contato_email), '') IS NULL) AS propostas_sem_contato_email,
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where} AND p.executivo_responsavel_id IS NULL) AS propostas_sem_executivo
            """,
            tuple(proposta_params * 4),
        ) or {}

        operacional = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where}) AS contratos_total,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.proposta_id IS NULL) AS contratos_diretos,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) <= 0) AS contratos_sem_receita,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.status = 'ATIVO' AND c.data_ativacao IS NULL) AS contratos_ativos_sem_ativacao,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_where} AND c.status = 'ATIVO' AND c.dia_faturamento IS NULL) AS contratos_ativos_sem_dia_faturamento,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where}) AS implantacoes_total,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA') AND NULLIF(TRIM(COALESCE(i.implantador_nome, i.responsavel)), '') IS NULL) AS implantacoes_sem_responsavel,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega IS NULL) AS implantacoes_sem_prazo,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_where} AND i.status NOT IN ('ENTREGUE', 'CANCELADA') AND COALESCE(i.percentual_conclusao, 0) = 0) AS implantacoes_sem_checklist
            """,
            tuple(contrato_params * 5 + implantacao_params * 4),
        ) or {}

        financeiro = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM faturamentos f INNER JOIN contratos c ON c.id = f.contrato_id WHERE f.ativo = 1 AND c.ativo = 1 {contrato_where}) AS faturamentos_total,
                (SELECT COUNT(*) FROM produtos WHERE ativo = 1) AS produtos_total,
                (SELECT COUNT(*) FROM produtos WHERE ativo = 1 AND COALESCE(valor_custo, 0) <= 0) AS produtos_sem_custo,
                (SELECT COUNT(*) FROM parametros_financeiros) AS parametros_total,
                (SELECT COUNT(*) FROM implantacao_integracoes_config WHERE ativo = 1) AS integracoes_total
            """,
            tuple(contrato_params),
        ) or {}

        return {
            "comercial": comercial,
            "operacional": operacional,
            "financeiro": financeiro,
        }

    @classmethod
    def _visao_geral_operacional(cls):
        return {
            "top_contratos": cls._visao_top_contratos(),
            "inadimplentes": cls._visao_clientes_inadimplentes(),
            "demandas": cls._visao_demandas_administrativo(),
            "propostas": cls._visao_propostas_recentes(),
            "clicksign_pendentes": cls._visao_clicksign_pendentes(),
            "zabbix_alertas": cls._visao_zabbix_alertas(),
            "proxmox_vms": cls._visao_proxmox_vms_maior_alocacao(),
            "proxmox_nodes": cls._visao_proxmox_nodes_consumo(),
            "pbs_pendentes": cls._visao_pbs_backups_pendentes(),
            "truenas_alertas": cls._visao_truenas_alertas(),
            "kanban_atualizacoes": cls._visao_kanban_atualizacoes(),
            "kanban_fila": cls._visao_kanban_fila(),
        }

    @classmethod
    def _visao_top_contratos(cls):
        return cls.fetch_all("""
            SELECT c.id, c.numero, c.status, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS valor_mensal
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE c.ativo = 1 AND c.status = 'ATIVO'
            ORDER BY valor_mensal DESC, c.id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_clientes_inadimplentes(cls):
        return cls.fetch_all("""
            SELECT fi.id, fi.contrato_id, fi.motivo, fi.bloqueado_em, c.numero AS contrato_numero,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS valor_mensal,
                   cli.id AS cliente_id, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome, cli.cnpj AS cliente_cnpj
            FROM financeiro_inadimplencias fi
            INNER JOIN contratos c ON c.id = fi.contrato_id
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE fi.ativo = 1 AND fi.status = 'PENDENTE'
            ORDER BY fi.bloqueado_em DESC, fi.id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_demandas_administrativo(cls):
        return cls.fetch_all("""
            SELECT d.id, d.titulo, d.prioridade, d.status, d.data_limite, d.created_at,
                   u.nome AS responsavel_nome, dep.nome AS departamento_nome,
                   CASE WHEN d.status NOT IN ('CONCLUIDA', 'CANCELADA') AND d.data_limite < CURRENT_DATE THEN 'ATRASADA' ELSE d.status END AS status_calculado
            FROM administrativo_demandas d
            LEFT JOIN auth_usuarios u ON u.id = d.responsavel_id
            LEFT JOIN administrativo_departamentos dep ON dep.id = d.departamento_id
            WHERE d.status <> 'CANCELADA'
            ORDER BY d.created_at DESC, d.id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_propostas_recentes(cls):
        return cls.fetch_all("""
            SELECT p.id, p.codigo_proposta, p.titulo, p.cliente_nome, p.executivo_nome, p.status,
                   p.clicksign_status, p.total_mensal, p.valor_total, p.updated_at
            FROM crm_propostas p
            WHERE p.ativo = 1
            ORDER BY p.updated_at DESC, p.id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_clicksign_pendentes(cls):
        return cls.fetch_all("""
            SELECT p.id, p.codigo_proposta, p.titulo, p.cliente_nome, p.clicksign_status, p.clicksign_sent_at, p.updated_at
            FROM crm_propostas p
            WHERE p.ativo = 1 AND COALESCE(p.clicksign_status, 'NAO_ENVIADO') IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')
            ORDER BY COALESCE(p.clicksign_sent_at, p.updated_at) ASC, p.id ASC
            LIMIT 5
        """)

    @classmethod
    def _visao_zabbix_alertas(cls):
        return cls.fetch_all("""
            SELECT id, host, nome, severidade, severidade_label, status_label, data_evento, acknowledged
            FROM zabbix_alarm_cache
            WHERE aberto = 1
            ORDER BY severidade DESC, COALESCE(data_evento, created_at) DESC, id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_proxmox_vms_maior_alocacao(cls):
        return cls.fetch_all("""
            SELECT p.id, p.node, p.vmid, p.tipo, p.nome, p.status, p.cpu_cores, p.memoria_mb, p.disco_gb,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM proxmox_vm_inventory p
            LEFT JOIN clientes cli ON cli.id = p.cliente_id
            WHERE p.ativo = 1 AND p.template = 0
            ORDER BY COALESCE(p.memoria_mb, 0) DESC, COALESCE(p.disco_gb, 0) DESC, COALESCE(p.cpu_cores, 0) DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_proxmox_nodes_consumo(cls):
        return cls.fetch_all("""
            SELECT id, node, status, cpu_usado_percent, memoria_total_mb, memoria_usada_mb, disco_total_gb, disco_usado_gb,
                   ROUND((COALESCE(memoria_usada_mb, 0) / NULLIF(memoria_total_mb, 0)) * 100, 1) AS memoria_usada_percent,
                   ROUND((COALESCE(disco_usado_gb, 0) / NULLIF(disco_total_gb, 0)) * 100, 1) AS disco_usado_percent
            FROM proxmox_node_inventory
            WHERE ativo = 1
            ORDER BY GREATEST(COALESCE(cpu_usado_percent, 0), COALESCE((memoria_usada_mb / NULLIF(memoria_total_mb, 0)) * 100, 0), COALESCE((disco_usado_gb / NULLIF(disco_total_gb, 0)) * 100, 0)) DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_pbs_backups_pendentes(cls):
        return cls.fetch_all("""
            SELECT base.*
            FROM (
                SELECT pol.id, pol.proxmox_inventory_id, pol.frequencia_horas, p.node, p.vmid, p.tipo, p.nome,
                       MAX(s.backup_time) AS ultimo_backup, TIMESTAMPDIFF(HOUR, MAX(s.backup_time), NOW()) AS horas_sem_backup
                FROM pbs_backup_politicas pol
                INNER JOIN proxmox_vm_inventory p ON p.id = pol.proxmox_inventory_id
                LEFT JOIN pbs_backup_snapshots s ON s.proxmox_inventory_id = pol.proxmox_inventory_id
                WHERE p.ativo = 1
                GROUP BY pol.id, pol.proxmox_inventory_id, pol.frequencia_horas, p.node, p.vmid, p.tipo, p.nome
            ) base
            WHERE base.ultimo_backup IS NULL OR base.horas_sem_backup > base.frequencia_horas
            ORDER BY base.ultimo_backup IS NULL DESC, base.horas_sem_backup DESC, base.node ASC, base.vmid ASC
            LIMIT 5
        """)

    @classmethod
    def _visao_truenas_alertas(cls):
        return cls.fetch_all("""
            SELECT id, prefixo_proxmox, cliente_nome, mountpoint, pasta_path, status, arquivos_recentes, arquivos_total, ultimo_arquivo, ultimo_mtime, sincronizado_em
            FROM truenas_backup_cache
            WHERE status <> 'OK'
            ORDER BY ultimo_mtime IS NULL DESC, ultimo_mtime ASC, updated_at DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_kanban_atualizacoes(cls):
        return cls.fetch_all("""
            SELECT h.id, h.implantacao_id, h.tipo, h.etapa_anterior, h.etapa_nova, h.comentario, h.created_at,
                   i.titulo, i.etapa_kanban, i.status, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM implantacao_historico h
            INNER JOIN implantacoes i ON i.id = h.implantacao_id
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1 AND h.tipo = 'ETAPA'
            ORDER BY h.created_at DESC, h.id DESC
            LIMIT 5
        """)

    @classmethod
    def _visao_kanban_fila(cls):
        return cls.fetch_all("""
            SELECT i.id, i.titulo, i.status, i.etapa_kanban, i.created_at, i.updated_at,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(NULLIF(i.implantador_nome, ''), NULLIF(i.responsavel, ''), 'Sem responsavel') AS responsavel_nome
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1 AND COALESCE(i.etapa_kanban, 'FILA') = 'FILA'
            ORDER BY i.created_at DESC, i.id DESC
            LIMIT 5
        """)

    @classmethod
    def listar_parceiros_dashboard(cls):
        return cls.fetch_all(
            """
            SELECT id, COALESCE(nome_fantasia, nome, razao_social) AS nome
            FROM parceiros
            WHERE ativo = 1
            ORDER BY COALESCE(nome_fantasia, nome, razao_social), nome
            """
        )

    @classmethod
    def listar_executivos_dashboard(cls):
        return cls.fetch_all(
            """
            SELECT id, nome
            FROM parceiros_executivos
            WHERE ativo = 1
            ORDER BY nome
            """
        )

    @classmethod
    def _propostas_status(cls, filtros):
        where, params = cls._filtros_propostas(filtros)
        return cls.fetch_all(
            f"""
            SELECT p.status AS nome, COUNT(*) AS total, COALESCE(SUM(COALESCE(p.total_mensal, 0)), 0) AS valor
            FROM crm_propostas p
            WHERE p.ativo = 1 {where}
            GROUP BY p.status
            ORDER BY total DESC, p.status ASC
            """,
            tuple(params),
        )

    @classmethod
    def _contratos_status(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        return cls.fetch_all(
            f"""
            SELECT c.status AS nome,
                   COUNT(*) AS total,
                   COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS valor
            FROM contratos c
            WHERE c.ativo = 1 {where}
            GROUP BY c.status
            ORDER BY total DESC, c.status ASC
            """,
            tuple(params),
        )

    @classmethod
    def _implantacoes_status(cls, filtros):
        where, params = cls._filtros_implantacoes(filtros)
        return cls.fetch_all(
            f"""
            SELECT i.status AS nome,
                   COUNT(*) AS total,
                   COALESCE(ROUND(AVG(COALESCE(i.percentual_conclusao, 0)), 0), 0) AS progresso
            FROM implantacoes i
            WHERE i.ativo = 1 {where}
            GROUP BY i.status
            ORDER BY total DESC, i.status ASC
            """,
            tuple(params),
        )

    @classmethod
    def _por_executivo(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        return cls.fetch_all(
            f"""
            SELECT
                COALESCE(exec.nome, 'Sem executivo') AS nome,
                COUNT(DISTINCT c.id) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS receita_mensal,
                COUNT(DISTINCT i.id) AS total_implantacoes
            FROM contratos c
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1 {where}
            GROUP BY nome
            ORDER BY receita_mensal DESC, total_contratos DESC, nome ASC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _por_parceiro(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        return cls.fetch_all(
            f"""
            SELECT
                COALESCE(p.nome_fantasia, p.nome, p.razao_social, 'Sem parceiro') AS nome,
                COUNT(DISTINCT c.id) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS receita_mensal,
                COUNT(DISTINCT i.id) AS total_implantacoes
            FROM contratos c
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1 {where}
            GROUP BY nome
            ORDER BY receita_mensal DESC, total_contratos DESC, nome ASC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _rastreabilidade_executiva(cls, filtros):
        proposta_where, proposta_params = cls._filtros_propostas(filtros)
        contrato_where, contrato_params = cls._filtros_contratos(filtros)
        implantacao_where, implantacao_params = cls._filtros_implantacoes(filtros)
        contrato_fluxo_where, contrato_fluxo_params = cls._filtros_contratos(filtros)
        implantacao_fluxo_where, implantacao_fluxo_params = cls._filtros_implantacoes(filtros)
        if filtros.get("status_comercial"):
            contrato_fluxo_where += " AND EXISTS (SELECT 1 FROM crm_propostas fp WHERE fp.id = c.proposta_id AND fp.ativo = 1 AND fp.status = %s)"
            contrato_fluxo_params.append(filtros.get("status_comercial"))
            implantacao_fluxo_where += " AND EXISTS (SELECT 1 FROM crm_propostas fp WHERE fp.id = i.proposta_id AND fp.ativo = 1 AND fp.status = %s)"
            implantacao_fluxo_params.append(filtros.get("status_comercial"))
        resumo = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM crm_propostas p WHERE p.ativo = 1 {proposta_where}) AS propostas_total,
                (SELECT COUNT(DISTINCT p.id) FROM crm_propostas p INNER JOIN contratos c ON c.proposta_id = p.id AND c.ativo = 1 WHERE p.ativo = 1 {proposta_where}) AS propostas_com_contrato,
                (SELECT COUNT(DISTINCT p.id) FROM crm_propostas p INNER JOIN contratos c ON c.proposta_id = p.id AND c.ativo = 1 INNER JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1 WHERE p.ativo = 1 {proposta_where}) AS propostas_com_implantacao,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_fluxo_where}) AS contratos_total,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {contrato_fluxo_where} AND c.proposta_id IS NOT NULL) AS contratos_com_proposta,
                (SELECT COUNT(DISTINCT c.id) FROM contratos c INNER JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1 WHERE c.ativo = 1 {contrato_fluxo_where}) AS contratos_com_implantacao,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_fluxo_where}) AS implantacoes_total,
                (SELECT COUNT(*) FROM implantacoes i WHERE i.ativo = 1 {implantacao_fluxo_where} AND i.proposta_id IS NOT NULL) AS implantacoes_com_proposta
            """,
            tuple(proposta_params * 3 + contrato_fluxo_params * 3 + implantacao_fluxo_params * 2),
        ) or {}

        propostas_total = resumo.get("propostas_total") or 0
        contratos_total = resumo.get("contratos_total") or 0
        implantacoes_total = resumo.get("implantacoes_total") or 0

        resumo["propostas_sem_contrato"] = max(propostas_total - (resumo.get("propostas_com_contrato") or 0), 0)
        resumo["propostas_sem_implantacao"] = max((resumo.get("propostas_com_contrato") or 0) - (resumo.get("propostas_com_implantacao") or 0), 0)
        resumo["contratos_sem_proposta"] = max(contratos_total - (resumo.get("contratos_com_proposta") or 0), 0)
        resumo["contratos_sem_implantacao"] = max(contratos_total - (resumo.get("contratos_com_implantacao") or 0), 0)
        resumo["implantacoes_sem_proposta"] = max(implantacoes_total - (resumo.get("implantacoes_com_proposta") or 0), 0)
        resumo["cobertura_proposta_contrato"] = cls._percentual(resumo.get("propostas_com_contrato"), propostas_total)
        resumo["cobertura_contrato_implantacao"] = cls._percentual(resumo.get("contratos_com_implantacao"), contratos_total)
        resumo["cobertura_ponta_a_ponta"] = cls._percentual(resumo.get("propostas_com_implantacao"), propostas_total)

        return resumo

    @classmethod
    def _fluxos_rastreabilidade(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        if filtros.get("status_comercial"):
            where += " AND prop.status = %s"
            params.append(filtros.get("status_comercial"))
        if filtros.get("status_implantacao"):
            where += " AND i.status = %s"
            params.append(filtros.get("status_implantacao"))
        return cls.fetch_all(
            f"""
            SELECT
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                c.proposta_id,
                prop.codigo_proposta,
                prop.status AS proposta_status,
                prop.clicksign_status,
                i.id AS implantacao_id,
                i.status AS implantacao_status,
                i.etapa_kanban,
                i.responsavel,
                i.implantador_nome,
                i.data_prevista_entrega,
                i.percentual_conclusao,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                COALESCE(exec.nome, 'Sem executivo') AS executivo_nome,
                COALESCE(par.nome_fantasia, par.nome, par.razao_social, 'Sem parceiro') AS parceiro_nome,
                COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS receita_mensal,
                CASE
                    WHEN prop.id IS NULL THEN 'CONTRATO_DIRETO'
                    WHEN i.id IS NULL THEN 'SEM_IMPLANTACAO'
                    WHEN i.status IN ('ENTREGUE', 'CANCELADA') THEN 'FINALIZADO'
                    ELSE 'EM_FLUXO'
                END AS situacao_fluxo
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id AND prop.ativo = 1
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros par ON par.id = c.parceiro_id
            WHERE c.ativo = 1 {where}
            ORDER BY FIELD(situacao_fluxo, 'SEM_IMPLANTACAO', 'EM_FLUXO', 'CONTRATO_DIRETO', 'FINALIZADO'),
                     COALESCE(i.data_prevista_entrega, c.data_fechamento, c.created_at) DESC,
                     c.id DESC
            LIMIT 10
            """,
            tuple(params),
        )

    @classmethod
    def _carga_implantadores(cls, filtros):
        where, params = cls._filtros_implantacoes(filtros)
        return cls.fetch_all(
            f"""
            SELECT
                COALESCE(NULLIF(i.implantador_nome, ''), NULLIF(i.responsavel, ''), 'Sem responsavel') AS nome,
                COUNT(*) AS total_implantacoes,
                SUM(CASE WHEN i.status IN ('AGUARDANDO_INICIO', 'EM_PLANEJAMENTO') THEN 1 ELSE 0 END) AS planejamento,
                SUM(CASE WHEN i.status IN ('EM_EXECUCAO', 'EM_VALIDACAO') THEN 1 ELSE 0 END) AS em_andamento,
                SUM(CASE WHEN i.status = 'ENTREGUE' THEN 1 ELSE 0 END) AS entregues,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega < CURDATE() THEN 1 ELSE 0 END) AS atrasadas,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS vence_7,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega IS NULL THEN 1 ELSE 0 END) AS sem_prazo,
                COALESCE(ROUND(AVG(COALESCE(i.percentual_conclusao, 0)), 0), 0) AS checklist_medio,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS receita_mensal_vinculada
            FROM implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            WHERE i.ativo = 1 {where}
            GROUP BY nome
            ORDER BY atrasadas DESC, em_andamento DESC, vence_7 DESC, total_implantacoes DESC, nome ASC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _implantacoes_criticas(cls, filtros):
        where, params = cls._filtros_implantacoes(filtros)
        return cls.fetch_all(
            f"""
            SELECT i.id, i.titulo, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   i.status, i.responsavel, i.implantador_nome,
                   i.data_prevista_entrega, i.percentual_conclusao
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1 {where}
              AND i.status NOT IN ('ENTREGUE', 'CANCELADA')
              AND (
                    i.data_prevista_entrega < CURDATE()
                    OR i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
              )
            ORDER BY i.data_prevista_entrega IS NULL ASC, i.data_prevista_entrega ASC, i.id DESC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _contratos_pendentes_implantacao(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        return cls.fetch_all(
            f"""
            SELECT c.id, c.numero, c.status, c.descricao,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS valor_mensal
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1 {where}
              AND c.status IN ('ENCAMINHADO_PROJETO', 'EM_ELABORACAO')
              AND i.id IS NULL
            ORDER BY c.data_fechamento DESC, c.id DESC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _propostas_pendentes_assinatura(cls, filtros):
        where, params = cls._filtros_propostas(filtros)
        return cls.fetch_all(
            f"""
            SELECT p.id, p.codigo_proposta, p.titulo, p.cliente_nome, p.executivo_nome,
                   p.clicksign_status, p.total_mensal, p.updated_at
            FROM crm_propostas p
            WHERE p.ativo = 1 {where}
              AND COALESCE(p.clicksign_status, 'NAO_ENVIADO') IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')
            ORDER BY p.updated_at DESC, p.id DESC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _base_rentabilidade(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        resumo = cls.fetch_one(
            f"""
            SELECT
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {where}) AS contratos_total,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {where} AND c.status = 'ATIVO') AS contratos_ativos,
                (SELECT COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) FROM contratos c WHERE c.ativo = 1 {where} AND c.status = 'ATIVO') AS receita_mensal_ativa,
                (SELECT COALESCE(SUM(COALESCE(c.valor_setup, 0) + COALESCE(c.valor_projeto, 0)), 0) FROM contratos c WHERE c.ativo = 1 {where}) AS receita_setup_projeto,
                (SELECT COUNT(*) FROM contratos c WHERE c.ativo = 1 {where} AND c.proposta_id IS NOT NULL) AS contratos_com_proposta,
                (SELECT COUNT(DISTINCT c.id) FROM contratos c INNER JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1 WHERE c.ativo = 1 {where}) AS contratos_com_implantacao,
                (SELECT COUNT(*) FROM faturamentos f INNER JOIN contratos c ON c.id = f.contrato_id WHERE f.ativo = 1 AND c.ativo = 1 {where}) AS faturamentos_total,
                (SELECT COALESCE(SUM(f.valor_liquido), 0) FROM faturamentos f INNER JOIN contratos c ON c.id = f.contrato_id WHERE f.ativo = 1 AND c.ativo = 1 {where}) AS faturamento_liquido,
                (SELECT COUNT(*) FROM parametros_financeiros) AS parametros_total,
                (SELECT COUNT(*) FROM produtos WHERE ativo = 1) AS produtos_total,
                (SELECT COUNT(*) FROM produtos WHERE ativo = 1 AND COALESCE(valor_custo, 0) > 0) AS produtos_com_custo,
                (SELECT COUNT(*) FROM catalogo_recursos_servidor WHERE ativo = 1) AS recursos_total,
                (SELECT COUNT(*) FROM implantacao_integracoes_config WHERE ativo = 1) AS integracoes_total
            """,
            tuple(params * 8),
        ) or {}

        resumo["cobertura_custo_produtos"] = cls._percentual(
            resumo.get("produtos_com_custo"),
            resumo.get("produtos_total"),
        )
        resumo["cobertura_proposta"] = cls._percentual(
            resumo.get("contratos_com_proposta"),
            resumo.get("contratos_total"),
        )
        resumo["cobertura_implantacao"] = cls._percentual(
            resumo.get("contratos_com_implantacao"),
            resumo.get("contratos_total"),
        )

        fontes = [
            {
                "nome": "Contratos",
                "status": "Disponivel" if resumo.get("contratos_total") else "Sem contratos",
                "classe": "success" if resumo.get("contratos_total") else "secondary",
                "detalhe": f"{resumo.get('contratos_ativos') or 0} ativo(s), receita recorrente real disponível.",
            },
            {
                "nome": "Faturamentos",
                "status": "Disponivel" if resumo.get("faturamentos_total") else "Sem dados",
                "classe": "success" if resumo.get("faturamentos_total") else "warning",
                "detalhe": f"{resumo.get('faturamentos_total') or 0} registro(s) para historico por competencia.",
            },
            {
                "nome": "Produtos / custos",
                "status": "Parcial" if resumo.get("produtos_com_custo") else "Pendente",
                "classe": "warning" if resumo.get("produtos_com_custo") else "danger",
                "detalhe": f"{resumo.get('produtos_com_custo') or 0}/{resumo.get('produtos_total') or 0} produto(s) ativo(s) com custo preenchido.",
            },
            {
                "nome": "Parametros financeiros",
                "status": "Configurado" if resumo.get("parametros_total") else "Pendente",
                "classe": "success" if resumo.get("parametros_total") else "danger",
                "detalhe": "Custos unitarios e margem minima para calculo de rentabilidade.",
            },
            {
                "nome": "Infraestrutura",
                "status": "Mapeada" if resumo.get("integracoes_total") else "Estrutural",
                "classe": "warning" if resumo.get("integracoes_total") else "secondary",
                "detalhe": f"{resumo.get('integracoes_total') or 0} integracao(oes) tecnica(s) cadastrada(s), sem consumo/custo automatizado.",
            },
        ]

        lacunas = []
        if not resumo.get("parametros_total"):
            lacunas.append("Cadastrar parametros_financeiros com custos unitarios e margem minima.")
        if not resumo.get("faturamentos_total"):
            lacunas.append("Popular faturamentos para comparar contrato versus competencia faturada.")
        if not resumo.get("produtos_com_custo"):
            lacunas.append("Preencher valor_custo nos produtos ativos ou definir fonte equivalente no catalogo.")
        if resumo.get("recursos_total") and not resumo.get("produtos_com_custo"):
            lacunas.append("Definir regra de custo para recursos de servidor, pois hoje o catalogo registra venda/instalacao.")
        if not resumo.get("contratos_com_implantacao"):
            lacunas.append("Vincular contratos ativos a implantacoes/infraestrutura para futuro custo tecnico por cliente.")

        return {
            "resumo": resumo,
            "fontes": fontes,
            "lacunas": lacunas,
        }

    @classmethod
    def _contratos_base_rentabilidade(cls, filtros):
        where, params = cls._filtros_contratos(filtros)
        return cls.fetch_all(
            f"""
            SELECT c.id, c.numero, c.status,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(par.nome_fantasia, par.nome, par.razao_social, 'Sem parceiro') AS parceiro_nome,
                   COALESCE(exec.nome, 'Sem executivo') AS executivo_nome,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS receita_mensal,
                   COALESCE(c.valor_setup, 0) + COALESCE(c.valor_projeto, 0) AS receita_setup_projeto,
                   CASE WHEN c.proposta_id IS NULL THEN 0 ELSE 1 END AS tem_proposta,
                   CASE WHEN i.id IS NULL THEN 0 ELSE 1 END AS tem_implantacao
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros par ON par.id = c.parceiro_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1 {where}
            ORDER BY c.status = 'ATIVO' DESC, receita_mensal DESC, c.id DESC
            LIMIT 8
            """,
            tuple(params),
        )

    @classmethod
    def _evolucao_mensal(cls, filtros):
        filtros_periodo = cls._filtros_periodo_evolucao(filtros)
        meses = cls._meses_periodo(filtros_periodo["data_de"], filtros_periodo["data_ate"])
        por_mes = {
            mes["chave"]: {
                **mes,
                "propostas_total": 0,
                "propostas_mensal": 0,
                "contratos_total": 0,
                "receita_mensal_ativa": 0,
                "implantacoes_total": 0,
                "implantacoes_entregues": 0,
            }
            for mes in meses
        }

        proposta_where, proposta_params = cls._filtros_propostas(filtros_periodo)
        contrato_where, contrato_params = cls._filtros_contratos(filtros_periodo)
        implantacao_where, implantacao_params = cls._filtros_implantacoes(filtros_periodo)

        propostas = cls.fetch_all(
            f"""
            SELECT DATE_FORMAT(p.updated_at, '%Y-%m') AS mes,
                   COUNT(*) AS total,
                   COALESCE(SUM(COALESCE(p.total_mensal, 0)), 0) AS valor
            FROM crm_propostas p
            WHERE p.ativo = 1 {proposta_where}
            GROUP BY mes
            ORDER BY mes
            """,
            tuple(proposta_params),
        )
        contratos = cls.fetch_all(
            f"""
            SELECT DATE_FORMAT(COALESCE(c.data_fechamento, c.created_at), '%Y-%m') AS mes,
                   COUNT(*) AS total,
                   COALESCE(SUM(CASE WHEN c.status = 'ATIVO' THEN COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) ELSE 0 END), 0) AS valor
            FROM contratos c
            WHERE c.ativo = 1 {contrato_where}
            GROUP BY mes
            ORDER BY mes
            """,
            tuple(contrato_params),
        )
        implantacoes = cls.fetch_all(
            f"""
            SELECT DATE_FORMAT(COALESCE(i.data_prevista_entrega, i.created_at), '%Y-%m') AS mes,
                   COUNT(*) AS total,
                   SUM(CASE WHEN i.status = 'ENTREGUE' THEN 1 ELSE 0 END) AS entregues
            FROM implantacoes i
            WHERE i.ativo = 1 {implantacao_where}
            GROUP BY mes
            ORDER BY mes
            """,
            tuple(implantacao_params),
        )

        for item in propostas:
            if item.get("mes") in por_mes:
                por_mes[item["mes"]]["propostas_total"] = item.get("total") or 0
                por_mes[item["mes"]]["propostas_mensal"] = item.get("valor") or 0
        for item in contratos:
            if item.get("mes") in por_mes:
                por_mes[item["mes"]]["contratos_total"] = item.get("total") or 0
                por_mes[item["mes"]]["receita_mensal_ativa"] = item.get("valor") or 0
        for item in implantacoes:
            if item.get("mes") in por_mes:
                por_mes[item["mes"]]["implantacoes_total"] = item.get("total") or 0
                por_mes[item["mes"]]["implantacoes_entregues"] = item.get("entregues") or 0

        linhas = list(por_mes.values())
        max_receita = max(
            [float(item["propostas_mensal"] or 0) for item in linhas]
            + [float(item["receita_mensal_ativa"] or 0) for item in linhas]
            + [1]
        )
        max_volume = max(
            [
                int(item["propostas_total"] or 0)
                + int(item["contratos_total"] or 0)
                + int(item["implantacoes_total"] or 0)
                for item in linhas
            ]
            + [1]
        )

        for item in linhas:
            propostas_mensal = float(item["propostas_mensal"] or 0)
            receita_ativa = float(item["receita_mensal_ativa"] or 0)
            volume = (
                int(item["propostas_total"] or 0)
                + int(item["contratos_total"] or 0)
                + int(item["implantacoes_total"] or 0)
            )
            item["volume_total"] = volume
            item["propostas_percentual"] = round((propostas_mensal / max_receita) * 100)
            item["receita_percentual"] = round((receita_ativa / max_receita) * 100)
            item["volume_percentual"] = round((volume / max_volume) * 100)

        return linhas

    @classmethod
    def _filtros_propostas(cls, filtros):
        where = []
        params = []
        if filtros.get("data_de"):
            where.append("p.updated_at >= %s")
            params.append(filtros.get("data_de"))
        if filtros.get("data_ate"):
            where.append("p.updated_at < DATE_ADD(%s, INTERVAL 1 DAY)")
            params.append(filtros.get("data_ate"))
        if filtros.get("parceiro_id"):
            where.append("p.parceiro_id = %s")
            params.append(filtros.get("parceiro_id"))
        if filtros.get("executivo_id"):
            where.append("p.executivo_responsavel_id = %s")
            params.append(filtros.get("executivo_id"))
        if filtros.get("status_comercial"):
            where.append("p.status = %s")
            params.append(filtros.get("status_comercial"))
        return (" AND " + " AND ".join(where) if where else ""), params

    @classmethod
    def _filtros_contratos(cls, filtros):
        where = []
        params = []
        if filtros.get("data_de"):
            where.append("COALESCE(c.data_fechamento, c.created_at) >= %s")
            params.append(filtros.get("data_de"))
        if filtros.get("data_ate"):
            where.append("COALESCE(c.data_fechamento, c.created_at) < DATE_ADD(%s, INTERVAL 1 DAY)")
            params.append(filtros.get("data_ate"))
        if filtros.get("parceiro_id"):
            where.append("c.parceiro_id = %s")
            params.append(filtros.get("parceiro_id"))
        if filtros.get("executivo_id"):
            where.append("c.executivo_id = %s")
            params.append(filtros.get("executivo_id"))
        if filtros.get("status_contrato"):
            where.append("c.status = %s")
            params.append(filtros.get("status_contrato"))
        return (" AND " + " AND ".join(where) if where else ""), params

    @classmethod
    def _filtros_implantacoes(cls, filtros):
        where = []
        params = []
        if filtros.get("data_de"):
            where.append("COALESCE(i.data_prevista_entrega, i.created_at) >= %s")
            params.append(filtros.get("data_de"))
        if filtros.get("data_ate"):
            where.append("COALESCE(i.data_prevista_entrega, i.created_at) < DATE_ADD(%s, INTERVAL 1 DAY)")
            params.append(filtros.get("data_ate"))
        if filtros.get("parceiro_id"):
            where.append("i.parceiro_id = %s")
            params.append(filtros.get("parceiro_id"))
        if filtros.get("executivo_id"):
            where.append("i.executivo_id = %s")
            params.append(filtros.get("executivo_id"))
        if filtros.get("status_implantacao"):
            where.append("i.status = %s")
            params.append(filtros.get("status_implantacao"))
        return (" AND " + " AND ".join(where) if where else ""), params

    @staticmethod
    def _percentual(valor, total):
        try:
            valor = float(valor or 0)
            total = float(total or 0)
        except (TypeError, ValueError):
            return 0
        if total <= 0:
            return 0
        return round((valor / total) * 100)

    @classmethod
    def _filtros_periodo_evolucao(cls, filtros):
        filtros_periodo = dict(filtros or {})
        hoje = date.today()
        data_de = cls._parse_data(filtros_periodo.get("data_de"))
        data_ate = cls._parse_data(filtros_periodo.get("data_ate"))

        if not data_de and not data_ate:
            data_ate = hoje
            data_de = cls._adicionar_meses(date(hoje.year, hoje.month, 1), -5)
        elif data_de and not data_ate:
            data_ate = hoje
        elif data_ate and not data_de:
            data_de = cls._adicionar_meses(date(data_ate.year, data_ate.month, 1), -5)

        if data_de > data_ate:
            data_de, data_ate = data_ate, data_de

        primeiro_mes = date(data_de.year, data_de.month, 1)
        limite_inicio = cls._adicionar_meses(date(data_ate.year, data_ate.month, 1), -11)
        if primeiro_mes < limite_inicio:
            data_de = limite_inicio

        filtros_periodo["data_de"] = data_de.isoformat()
        filtros_periodo["data_ate"] = data_ate.isoformat()
        return filtros_periodo

    @classmethod
    def _meses_periodo(cls, data_de, data_ate):
        inicio = cls._parse_data(data_de)
        fim = cls._parse_data(data_ate)
        atual = date(inicio.year, inicio.month, 1)
        ultimo = date(fim.year, fim.month, 1)
        meses = []

        while atual <= ultimo:
            chave = atual.strftime("%Y-%m")
            meses.append({
                "chave": chave,
                "label": atual.strftime("%m/%Y"),
            })
            atual = cls._adicionar_meses(atual, 1)

        return meses

    @staticmethod
    def _parse_data(valor):
        if isinstance(valor, date):
            return valor
        try:
            return datetime.strptime(str(valor), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _adicionar_meses(valor, quantidade):
        mes = valor.month - 1 + quantidade
        ano = valor.year + mes // 12
        mes = mes % 12 + 1
        return date(ano, mes, 1)

    @classmethod
    def produtos_clientes(cls, filtros=None):
        filtros = filtros or {}
        where, params = cls._filtros_produtos_clientes(filtros)
        resumo = cls.fetch_one(
            f"""
            SELECT
                COUNT(DISTINCT c.id) AS contratos_total,
                COUNT(DISTINCT ci.contrato_id) AS contratos_com_itens,
                COUNT(ci.id) AS itens_total,
                COUNT(DISTINCT c.cliente_id) AS clientes_total,
                COALESCE(SUM(COALESCE(ci.valor_total, 0)), 0) AS valor_total_itens,
                SUM(CASE WHEN c.proposta_id IS NOT NULL THEN 1 ELSE 0 END) AS itens_com_proposta,
                SUM(CASE WHEN prod.id IS NOT NULL THEN 1 ELSE 0 END) AS itens_com_produto_catalogo,
                SUM(CASE WHEN prod.id IS NOT NULL AND COALESCE(prod.valor_custo, 0) > 0 THEN 1 ELSE 0 END) AS itens_com_custo
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN contratos_itens ci ON ci.contrato_id = c.id
            LEFT JOIN produtos prod ON prod.ativo = 1 AND (
                (ci.codigo_servico IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                ))
                OR (ci.codigo_item IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                ))
            )
            WHERE c.ativo = 1 {where}
            """,
            tuple(params),
        ) or {}
        resumo["cobertura_itens"] = cls._percentual(
            resumo.get("contratos_com_itens"),
            resumo.get("contratos_total"),
        )
        resumo["cobertura_proposta"] = cls._percentual(
            resumo.get("itens_com_proposta"),
            resumo.get("itens_total"),
        )
        resumo["cobertura_catalogo"] = cls._percentual(
            resumo.get("itens_com_produto_catalogo"),
            resumo.get("itens_total"),
        )
        resumo["cobertura_custo"] = cls._percentual(
            resumo.get("itens_com_custo"),
            resumo.get("itens_total"),
        )

        receita_contratos = cls.fetch_one(
            f"""
            SELECT COALESCE(SUM(base.receita_mensal), 0) AS receita_mensal_contratos
            FROM (
                SELECT DISTINCT
                    c.id,
                    COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS receita_mensal
                FROM contratos c
                INNER JOIN clientes cli ON cli.id = c.cliente_id
                LEFT JOIN contratos_itens ci ON ci.contrato_id = c.id
                LEFT JOIN produtos prod ON prod.ativo = 1 AND (
                    (ci.codigo_servico IS NOT NULL AND (
                        (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                        OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                    ))
                    OR (ci.codigo_item IS NOT NULL AND (
                        (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                        OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                    ))
                )
                WHERE c.ativo = 1 {where}
            ) base
            """,
            tuple(params),
        ) or {}
        resumo["receita_mensal_contratos"] = receita_contratos.get("receita_mensal_contratos") or 0

        ambiente_where, ambiente_params = cls._filtros_ambientes_produtos_clientes(filtros)
        ambientes_resumo = cls.fetch_one(
            f"""
            SELECT
                COUNT(DISTINCT base.ambiente_id) AS ambientes_total,
                COUNT(DISTINCT base.recurso_id) AS recursos_total,
                COUNT(DISTINCT CASE WHEN base.tipo = 'qemu' THEN base.recurso_id END) AS vms_total,
                COUNT(DISTINCT CASE WHEN base.tipo = 'lxc' THEN base.recurso_id END) AS containers_total,
                COUNT(DISTINCT CASE WHEN base.status = 'running' THEN base.recurso_id END) AS recursos_ativos,
                COALESCE(SUM(COALESCE(base.cpu_cores, 0)), 0) AS cpu_total,
                COALESCE(SUM(COALESCE(base.memoria_mb, 0)), 0) AS memoria_total_mb,
                COALESCE(SUM(COALESCE(base.disco_gb, 0)), 0) AS disco_total_gb
            FROM (
                SELECT DISTINCT
                    a.id AS ambiente_id,
                    p.id AS recurso_id,
                    p.tipo,
                    p.status,
                    p.cpu_cores,
                    p.memoria_mb,
                    p.disco_gb
                FROM ambientes a
                INNER JOIN ambiente_clientes ac ON ac.ambiente_id = a.id
                INNER JOIN clientes cli ON cli.id = ac.cliente_id
                LEFT JOIN ambiente_contratos act ON act.ambiente_id = a.id
                LEFT JOIN contratos c ON c.id = act.contrato_id AND c.ativo = 1
                LEFT JOIN ambiente_proxmox_recursos apr ON apr.ambiente_id = a.id
                LEFT JOIN proxmox_vm_inventory p ON p.id = apr.proxmox_inventory_id AND p.ativo = 1
                WHERE a.ativo = 1 {ambiente_where}
            ) base
            """,
            tuple(ambiente_params),
        ) or {}

        ambientes = cls.fetch_all(
            f"""
            SELECT
                a.id,
                a.nome,
                a.ambiente_tipo,
                a.situacao,
                GROUP_CONCAT(DISTINCT COALESCE(cli.nome_fantasia, cli.razao_social) ORDER BY COALESCE(cli.nome_fantasia, cli.razao_social) SEPARATOR ', ') AS clientes_nomes,
                GROUP_CONCAT(DISTINCT c.numero ORDER BY c.numero SEPARATOR ', ') AS contratos_numeros,
                COALESCE(ar.recursos_total, 0) AS recursos_total,
                COALESCE(ar.vms_total, 0) AS vms_total,
                COALESCE(ar.containers_total, 0) AS containers_total,
                COALESCE(ar.cpu_total, 0) AS cpu_total,
                COALESCE(ar.memoria_total_mb, 0) AS memoria_total_mb,
                COALESCE(ar.disco_total_gb, 0) AS disco_total_gb
            FROM ambientes a
            INNER JOIN ambiente_clientes ac ON ac.ambiente_id = a.id
            INNER JOIN clientes cli ON cli.id = ac.cliente_id
            LEFT JOIN ambiente_contratos act ON act.ambiente_id = a.id
            LEFT JOIN contratos c ON c.id = act.contrato_id AND c.ativo = 1
            LEFT JOIN ambiente_proxmox_recursos apr ON apr.ambiente_id = a.id
            LEFT JOIN proxmox_vm_inventory p ON p.id = apr.proxmox_inventory_id AND p.ativo = 1
            LEFT JOIN (
                SELECT
                    apr2.ambiente_id,
                    COUNT(DISTINCT p2.id) AS recursos_total,
                    COUNT(DISTINCT CASE WHEN p2.tipo = 'qemu' THEN p2.id END) AS vms_total,
                    COUNT(DISTINCT CASE WHEN p2.tipo = 'lxc' THEN p2.id END) AS containers_total,
                    COALESCE(SUM(COALESCE(p2.cpu_cores, 0)), 0) AS cpu_total,
                    COALESCE(SUM(COALESCE(p2.memoria_mb, 0)), 0) AS memoria_total_mb,
                    COALESCE(SUM(COALESCE(p2.disco_gb, 0)), 0) AS disco_total_gb
                FROM ambiente_proxmox_recursos apr2
                INNER JOIN proxmox_vm_inventory p2 ON p2.id = apr2.proxmox_inventory_id AND p2.ativo = 1
                GROUP BY apr2.ambiente_id
            ) ar ON ar.ambiente_id = a.id
            WHERE a.ativo = 1 {ambiente_where}
            GROUP BY a.id, a.nome, a.ambiente_tipo, a.situacao, ar.recursos_total, ar.vms_total,
                     ar.containers_total, ar.cpu_total, ar.memoria_total_mb, ar.disco_total_gb
            ORDER BY recursos_total DESC, cpu_total DESC, a.nome ASC
            LIMIT 12
            """,
            tuple(ambiente_params),
        )

        ambiente_recursos = cls.fetch_all(
            f"""
            SELECT
                a.id AS ambiente_id,
                a.nome AS ambiente_nome,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                GROUP_CONCAT(DISTINCT c.numero ORDER BY c.numero SEPARATOR ', ') AS contratos_numeros,
                p.id AS recurso_id,
                p.node,
                p.vmid,
                p.tipo,
                p.nome AS recurso_nome,
                p.status,
                p.cpu_cores,
                p.memoria_mb,
                p.disco_gb,
                p.discos_qtd,
                p.interfaces_qtd
            FROM ambientes a
            INNER JOIN ambiente_clientes ac ON ac.ambiente_id = a.id
            INNER JOIN clientes cli ON cli.id = ac.cliente_id
            LEFT JOIN ambiente_contratos act ON act.ambiente_id = a.id
            LEFT JOIN contratos c ON c.id = act.contrato_id AND c.ativo = 1
            INNER JOIN ambiente_proxmox_recursos apr ON apr.ambiente_id = a.id
            INNER JOIN proxmox_vm_inventory p ON p.id = apr.proxmox_inventory_id AND p.ativo = 1
            WHERE a.ativo = 1 {ambiente_where}
            GROUP BY a.id, a.nome, cliente_nome, p.id, p.node, p.vmid, p.tipo, p.nome, p.status,
                     p.cpu_cores, p.memoria_mb, p.disco_gb, p.discos_qtd, p.interfaces_qtd
            ORDER BY a.nome ASC, p.node ASC, p.vmid ASC
            LIMIT 100
            """,
            tuple(ambiente_params),
        )

        itens = cls.fetch_all(
            f"""
            SELECT
                ci.id,
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                c.origem,
                c.proposta_id,
                prop.codigo_proposta,
                cli.id AS cliente_id,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                COALESCE(par.nome_fantasia, par.nome, par.razao_social, 'Sem parceiro') AS parceiro_nome,
                COALESCE(exec.nome, 'Sem executivo') AS executivo_nome,
                ci.codigo_item,
                ci.codigo_servico,
                ci.descricao,
                ci.quantidade,
                ci.valor_unitario,
                ci.valor_total,
                prod.id AS produto_id,
                prod.codigo AS produto_codigo,
                prod.nome AS produto_nome,
                prod.valor_custo,
                CASE
                    WHEN ci.id IS NULL THEN 'SEM_ITEM'
                    WHEN prod.id IS NULL THEN 'SEM_CATALOGO'
                    WHEN COALESCE(prod.valor_custo, 0) <= 0 THEN 'SEM_CUSTO'
                    ELSE 'COMPLETO'
                END AS situacao_custo
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN contratos_itens ci ON ci.contrato_id = c.id
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id AND prop.ativo = 1
            LEFT JOIN parceiros par ON par.id = c.parceiro_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN produtos prod ON prod.ativo = 1 AND (
                (ci.codigo_servico IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                ))
                OR (ci.codigo_item IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                ))
            )
            WHERE c.ativo = 1 {where}
            ORDER BY ci.id IS NULL ASC,
                     FIELD(situacao_custo, 'SEM_ITEM', 'SEM_CATALOGO', 'SEM_CUSTO', 'COMPLETO'),
                     COALESCE(ci.valor_total, COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0), 0) DESC,
                     c.id DESC,
                     ci.sequencia ASC
            LIMIT 100
            """,
            tuple(params),
        )

        clientes = cls.fetch_all(
            f"""
            SELECT
                cli.id,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS nome,
                COUNT(DISTINCT c.id) AS contratos_total,
                COUNT(ci.id) AS itens_total,
                COALESCE(SUM(COALESCE(ci.valor_total, 0)), 0) AS valor_total_itens,
                SUM(CASE WHEN c.proposta_id IS NOT NULL THEN 1 ELSE 0 END) AS itens_com_proposta,
                SUM(CASE WHEN prod.id IS NOT NULL THEN 1 ELSE 0 END) AS itens_com_catalogo,
                SUM(CASE WHEN prod.id IS NOT NULL AND COALESCE(prod.valor_custo, 0) > 0 THEN 1 ELSE 0 END) AS itens_com_custo
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN contratos_itens ci ON ci.contrato_id = c.id
            LEFT JOIN produtos prod ON prod.ativo = 1 AND (
                (ci.codigo_servico IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                ))
                OR (ci.codigo_item IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                ))
            )
            WHERE c.ativo = 1 {where}
            GROUP BY cli.id, nome
            ORDER BY valor_total_itens DESC, itens_total DESC, nome ASC
            LIMIT 12
            """,
            tuple(params),
        )
        for cliente in clientes:
            cliente["cobertura_custo"] = cls._percentual(
                cliente.get("itens_com_custo"),
                cliente.get("itens_total"),
            )
            cliente["cobertura_catalogo"] = cls._percentual(
                cliente.get("itens_com_catalogo"),
                cliente.get("itens_total"),
            )

        itens_sem_catalogo = cls.fetch_all(
            f"""
            SELECT
                ci.codigo_servico,
                ci.codigo_item,
                LEFT(COALESCE(ci.descricao, 'Sem descricao'), 120) AS descricao,
                COUNT(*) AS ocorrencias,
                COUNT(DISTINCT c.cliente_id) AS clientes_total,
                COUNT(DISTINCT c.id) AS contratos_total,
                COALESCE(SUM(COALESCE(ci.valor_total, 0)), 0) AS valor_total_itens
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            INNER JOIN contratos_itens ci ON ci.contrato_id = c.id
            LEFT JOIN produtos prod ON prod.ativo = 1 AND (
                (ci.codigo_servico IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                ))
                OR (ci.codigo_item IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                ))
            )
            WHERE c.ativo = 1 {where}
              AND prod.id IS NULL
            GROUP BY ci.codigo_servico, ci.codigo_item, descricao
            ORDER BY valor_total_itens DESC, ocorrencias DESC, descricao ASC
            LIMIT 12
            """,
            tuple(params),
        )

        produtos_sem_custo = cls.fetch_all(
            f"""
            SELECT
                prod.id,
                prod.codigo,
                prod.codigo_externo,
                prod.nome,
                prod.valor_custo,
                COUNT(ci.id) AS itens_vinculados,
                COUNT(DISTINCT c.cliente_id) AS clientes_total,
                COALESCE(SUM(COALESCE(ci.valor_total, 0)), 0) AS valor_total_itens
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            INNER JOIN contratos_itens ci ON ci.contrato_id = c.id
            INNER JOIN produtos prod ON prod.ativo = 1 AND (
                (ci.codigo_servico IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_servico)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_servico)
                ))
                OR (ci.codigo_item IS NOT NULL AND (
                    (prod.codigo_externo REGEXP '^[0-9]+$' AND CAST(prod.codigo_externo AS UNSIGNED) = ci.codigo_item)
                    OR (prod.codigo REGEXP '^[0-9]+$' AND CAST(prod.codigo AS UNSIGNED) = ci.codigo_item)
                ))
            )
            WHERE c.ativo = 1 {where}
              AND COALESCE(prod.valor_custo, 0) <= 0
            GROUP BY prod.id, prod.codigo, prod.codigo_externo, prod.nome, prod.valor_custo
            ORDER BY valor_total_itens DESC, itens_vinculados DESC, prod.nome ASC
            LIMIT 12
            """,
            tuple(params),
        )

        lacunas = []
        if not resumo.get("itens_total"):
            lacunas.append("Sincronizar itens de contratos do Omie ou registrar itens comerciais nos contratos.")
        if not resumo.get("itens_com_produto_catalogo"):
            lacunas.append("Vincular codigos de itens do Omie ao catalogo de produtos.")
        if not resumo.get("itens_com_custo"):
            lacunas.append("Preencher custos dos produtos para preparar rentabilidade.")
        if ambientes_resumo.get("recursos_total"):
            lacunas.append("Definir custo operacional por CPU, memoria e disco para calcular lucro/prejuizo dos ambientes.")

        return {
            "resumo": resumo,
            "itens": itens,
            "clientes": clientes,
            "ambientes_resumo": ambientes_resumo,
            "ambientes": ambientes,
            "ambiente_recursos": ambiente_recursos,
            "itens_sem_catalogo": itens_sem_catalogo,
            "produtos_sem_custo": produtos_sem_custo,
            "lacunas": lacunas,
        }

    @classmethod
    def _filtros_ambientes_produtos_clientes(cls, filtros):
        where = []
        params = []
        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            cnpj_like = f"%{''.join(ch for ch in pesquisa if ch.isalnum()).upper()}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, cli.razao_social) LIKE %s
                    OR cli.cnpj LIKE %s
                    OR REGEXP_REPLACE(cli.cnpj, '[^0-9A-Za-z]', '') LIKE %s
                    OR a.nome LIKE %s
                    OR c.numero LIKE %s
                    OR p.nome LIKE %s
                    OR p.node LIKE %s
                    OR CAST(p.vmid AS CHAR) LIKE %s
                )
            """)
            params.extend([like, like, cnpj_like, like, like, like, like, like])
        if filtros.get("status"):
            where.append("c.status = %s")
            params.append(filtros.get("status"))
        if filtros.get("origem"):
            where.append("c.origem = %s")
            params.append(filtros.get("origem"))
        return (" AND " + " AND ".join(where) if where else ""), params

    @classmethod
    def _filtros_produtos_clientes(cls, filtros):
        where = []
        params = []
        pesquisa = (filtros.get("q") or "").strip()
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("""
                (
                    COALESCE(cli.nome_fantasia, cli.razao_social) LIKE %s
                    OR c.numero LIKE %s
                    OR ci.descricao LIKE %s
                    OR CAST(ci.codigo_item AS CHAR) LIKE %s
                    OR CAST(ci.codigo_servico AS CHAR) LIKE %s
                )
            """)
            params.extend([like, like, like, like, like])
        if filtros.get("status"):
            where.append("c.status = %s")
            params.append(filtros.get("status"))
        if filtros.get("origem"):
            where.append("c.origem = %s")
            params.append(filtros.get("origem"))
        if filtros.get("situacao") == "sem_item":
            where.append("ci.id IS NULL")
        elif filtros.get("situacao") == "sem_catalogo":
            where.append("ci.id IS NOT NULL AND prod.id IS NULL")
        elif filtros.get("situacao") == "sem_custo":
            where.append("prod.id IS NOT NULL AND COALESCE(prod.valor_custo, 0) <= 0")
        elif filtros.get("situacao") == "completo":
            where.append("prod.id IS NOT NULL AND COALESCE(prod.valor_custo, 0) > 0")
        return (" AND " + " AND ".join(where) if where else ""), params

    @classmethod
    def listar_clientes(cls):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                id,
                nome_fantasia,
                cidade,
                estado,
                origem,
                ativo

            FROM clientes

            ORDER BY nome_fantasia

        """)

        dados = cursor.fetchall()

        cls.close(conn, cursor)

        return dados

    @classmethod
    def buscar_cliente(cls, cliente_id):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes

            WHERE id=%s

        """,(cliente_id,))

        cliente = cursor.fetchone()

        cls.close(conn,cursor)

        return cliente

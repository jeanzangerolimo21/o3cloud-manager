from datetime import date
from datetime import datetime

from app.repositories.base_repository import BaseRepository


class FinanceiroRepository(BaseRepository):

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
        }

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
                    WHEN prop.id IS NULL THEN 'SEM_PROPOSTA'
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
            ORDER BY FIELD(situacao_fluxo, 'SEM_PROPOSTA', 'SEM_IMPLANTACAO', 'EM_FLUXO', 'FINALIZADO'),
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

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
    def dashboard_executivo(cls):
        resumo = cls.fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM clientes WHERE ativo = 1) AS total_clientes,
                (SELECT COUNT(*) FROM crm_propostas WHERE ativo = 1) AS total_propostas,
                (SELECT COALESCE(SUM(COALESCE(total_mensal, 0)), 0) FROM crm_propostas WHERE ativo = 1) AS propostas_mensal,
                (SELECT COALESCE(SUM(COALESCE(total_instalacao, 0)), 0) FROM crm_propostas WHERE ativo = 1) AS propostas_setup,
                (SELECT COUNT(*) FROM crm_propostas WHERE ativo = 1 AND COALESCE(clicksign_status, 'NAO_ENVIADO') IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')) AS propostas_em_assinatura,
                (SELECT COUNT(*) FROM crm_propostas WHERE ativo = 1 AND COALESCE(clicksign_status, 'NAO_ENVIADO') IN ('ASSINADO', 'CONCLUIDO')) AS propostas_assinadas,
                (SELECT COUNT(*) FROM contratos WHERE ativo = 1) AS total_contratos,
                (SELECT COUNT(*) FROM contratos WHERE ativo = 1 AND status = 'ATIVO') AS contratos_ativos,
                (SELECT COUNT(*) FROM contratos WHERE ativo = 1 AND status IN ('ENCAMINHADO_PROJETO', 'EM_ELABORACAO')) AS contratos_encaminhados,
                (SELECT COALESCE(SUM(COALESCE(NULLIF(valor_promocional, 0), valor_mensal, 0)), 0) FROM contratos WHERE ativo = 1 AND status = 'ATIVO') AS receita_mensal_ativa,
                (SELECT COALESCE(SUM(COALESCE(valor_setup, 0) + COALESCE(valor_projeto, 0)), 0) FROM contratos WHERE ativo = 1) AS contratos_setup,
                (SELECT COUNT(*) FROM implantacoes WHERE ativo = 1) AS total_implantacoes,
                (SELECT COUNT(*) FROM implantacoes WHERE ativo = 1 AND status IN ('EM_EXECUCAO', 'EM_VALIDACAO')) AS implantacoes_em_andamento,
                (SELECT COUNT(*) FROM implantacoes WHERE ativo = 1 AND status NOT IN ('ENTREGUE', 'CANCELADA') AND data_prevista_entrega < CURDATE()) AS implantacoes_atrasadas,
                (SELECT COUNT(*) FROM implantacoes WHERE ativo = 1 AND status NOT IN ('ENTREGUE', 'CANCELADA') AND data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)) AS implantacoes_vence_7,
                (SELECT COALESCE(ROUND(AVG(COALESCE(percentual_conclusao, 0)), 0), 0) FROM implantacoes WHERE ativo = 1 AND status NOT IN ('ENTREGUE', 'CANCELADA')) AS checklist_medio
            """
        )
        return {
            "resumo": resumo or {},
            "propostas_status": cls._propostas_status(),
            "contratos_status": cls._contratos_status(),
            "implantacoes_status": cls._implantacoes_status(),
            "por_executivo": cls._por_executivo(),
            "por_parceiro": cls._por_parceiro(),
            "implantacoes_criticas": cls._implantacoes_criticas(),
            "contratos_pendentes_implantacao": cls._contratos_pendentes_implantacao(),
            "propostas_pendentes_assinatura": cls._propostas_pendentes_assinatura(),
        }

    @classmethod
    def _propostas_status(cls):
        return cls.fetch_all(
            """
            SELECT status AS nome, COUNT(*) AS total, COALESCE(SUM(COALESCE(total_mensal, 0)), 0) AS valor
            FROM crm_propostas
            WHERE ativo = 1
            GROUP BY status
            ORDER BY total DESC, status ASC
            """
        )

    @classmethod
    def _contratos_status(cls):
        return cls.fetch_all(
            """
            SELECT status AS nome,
                   COUNT(*) AS total,
                   COALESCE(SUM(COALESCE(NULLIF(valor_promocional, 0), valor_mensal, 0)), 0) AS valor
            FROM contratos
            WHERE ativo = 1
            GROUP BY status
            ORDER BY total DESC, status ASC
            """
        )

    @classmethod
    def _implantacoes_status(cls):
        return cls.fetch_all(
            """
            SELECT status AS nome,
                   COUNT(*) AS total,
                   COALESCE(ROUND(AVG(COALESCE(percentual_conclusao, 0)), 0), 0) AS progresso
            FROM implantacoes
            WHERE ativo = 1
            GROUP BY status
            ORDER BY total DESC, status ASC
            """
        )

    @classmethod
    def _por_executivo(cls):
        return cls.fetch_all(
            """
            SELECT
                COALESCE(exec.nome, 'Sem executivo') AS nome,
                COUNT(DISTINCT c.id) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS receita_mensal,
                COUNT(DISTINCT i.id) AS total_implantacoes
            FROM contratos c
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1
            GROUP BY nome
            ORDER BY receita_mensal DESC, total_contratos DESC, nome ASC
            LIMIT 8
            """
        )

    @classmethod
    def _por_parceiro(cls):
        return cls.fetch_all(
            """
            SELECT
                COALESCE(p.nome_fantasia, p.nome, p.razao_social, 'Sem parceiro') AS nome,
                COUNT(DISTINCT c.id) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS receita_mensal,
                COUNT(DISTINCT i.id) AS total_implantacoes
            FROM contratos c
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1
            GROUP BY nome
            ORDER BY receita_mensal DESC, total_contratos DESC, nome ASC
            LIMIT 8
            """
        )

    @classmethod
    def _implantacoes_criticas(cls):
        return cls.fetch_all(
            """
            SELECT i.id, i.titulo, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   i.status, i.responsavel, i.implantador_nome,
                   i.data_prevista_entrega, i.percentual_conclusao
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1
              AND i.status NOT IN ('ENTREGUE', 'CANCELADA')
              AND (
                    i.data_prevista_entrega < CURDATE()
                    OR i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
              )
            ORDER BY i.data_prevista_entrega IS NULL ASC, i.data_prevista_entrega ASC, i.id DESC
            LIMIT 8
            """
        )

    @classmethod
    def _contratos_pendentes_implantacao(cls):
        return cls.fetch_all(
            """
            SELECT c.id, c.numero, c.status, c.descricao,
                   COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                   COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0) AS valor_mensal
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            WHERE c.ativo = 1
              AND c.status IN ('ENCAMINHADO_PROJETO', 'EM_ELABORACAO')
              AND i.id IS NULL
            ORDER BY c.data_fechamento DESC, c.id DESC
            LIMIT 8
            """
        )

    @classmethod
    def _propostas_pendentes_assinatura(cls):
        return cls.fetch_all(
            """
            SELECT id, codigo_proposta, titulo, cliente_nome, executivo_nome,
                   clicksign_status, total_mensal, updated_at
            FROM crm_propostas
            WHERE ativo = 1
              AND COALESCE(clicksign_status, 'NAO_ENVIADO') IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')
            ORDER BY updated_at DESC, id DESC
            LIMIT 8
            """
        )


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

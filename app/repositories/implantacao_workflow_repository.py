from app.repositories.base_repository import BaseRepository


class ImplantacaoWorkflowRepository(BaseRepository):
    TABLE = "implantacoes"

    @classmethod
    def total(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo=1, agrupamento="principais"):
        sql = """
            SELECT COUNT(*)
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, status, responsavel, prazo, ativo, agrupamento=agrupamento)
        sql += where
        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo=1, agrupamento="principais", limit=50, offset=0):
        sql = """
            SELECT
                i.id,
                i.uuid,
                i.contrato_id,
                i.cliente_id,
                i.implantacao_principal_id,
                i.titulo,
                i.status,
                i.etapa_kanban,
                i.prioridade,
                i.responsavel,
                i.implantador_nome,
                i.implantador_email,
                i.emails_adicionais,
                i.data_prevista_inicio,
                i.data_prevista_entrega,
                i.data_inicio,
                i.data_entrega,
                i.percentual_conclusao,
                i.provisionamento_status,
                i.ativo,
                i.updated_at,
                DATEDIFF(i.data_prevista_entrega, CURDATE()) AS dias_para_entrega,
                CASE
                    WHEN i.status IN ('ENTREGUE', 'CANCELADA') THEN 'ENCERRADA'
                    WHEN i.data_prevista_entrega IS NULL THEN 'SEM_PRAZO'
                    WHEN i.data_prevista_entrega < CURDATE() THEN 'ATRASADA'
                    WHEN i.data_prevista_entrega <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'VENCE_7'
                    WHEN i.data_prevista_entrega <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'VENCE_30'
                    ELSE 'NO_PRAZO'
                END AS prazo_situacao,
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                cli.cnpj AS cliente_cnpj,
                exec.nome AS executivo_nome,
                p.nome AS parceiro_nome,
                principal.titulo AS implantacao_principal_titulo,
                principal.status AS implantacao_principal_status,
                pc.numero AS implantacao_principal_contrato_numero,
                vinculadas.total_vinculadas,
                checklist.total_itens,
                checklist.total_concluidos
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            LEFT JOIN implantacoes principal ON principal.id = i.implantacao_principal_id
            LEFT JOIN contratos pc ON pc.id = principal.contrato_id
            LEFT JOIN (
                SELECT implantacao_principal_id, COUNT(*) AS total_vinculadas
                FROM implantacoes
                WHERE ativo = 1 AND implantacao_principal_id IS NOT NULL
                GROUP BY implantacao_principal_id
            ) vinculadas ON vinculadas.implantacao_principal_id = i.id
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, status, responsavel, prazo, ativo, agrupamento=agrupamento)
        sql += where
        sql += """
            ORDER BY FIELD(i.status, 'AGUARDANDO_INICIO', 'EM_PLANEJAMENTO', 'EM_EXECUCAO', 'EM_VALIDACAO', 'PAUSADA', 'ENTREGUE', 'CANCELADA'),
                     COALESCE(i.data_prevista_entrega, '2999-12-31') ASC,
                     i.updated_at DESC,
                     i.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def buscar_por_id(cls, implantacao_id):
        sql = """
            SELECT
                i.*,
                principal.titulo AS implantacao_principal_titulo,
                principal.status AS implantacao_principal_status,
                pc.numero AS implantacao_principal_contrato_numero,
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                c.descricao AS contrato_descricao,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                prop.detalhes_negociacao AS proposta_escopo,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                cli.cnpj AS cliente_cnpj,
                exec.nome AS executivo_nome,
                exec.email AS executivo_email,
                p.nome AS parceiro_nome,
                p.email AS parceiro_email,
                cli.email AS cliente_email,
                c.contato_email AS contato_email
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN crm_propostas prop ON prop.id = i.proposta_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            LEFT JOIN implantacoes principal ON principal.id = i.implantacao_principal_id
            LEFT JOIN contratos pc ON pc.id = principal.contrato_id
            WHERE i.id = %s AND i.ativo = 1
        """
        return cls.fetch_one(sql, (implantacao_id,))

    @classmethod
    def buscar_por_cliente_id(cls, cliente_id):
        return cls.fetch_one(
            """
            SELECT
                i.*,
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                c.descricao AS contrato_descricao,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                exec.nome AS executivo_nome,
                p.nome AS parceiro_nome,
                checklist.total_itens,
                checklist.total_concluidos
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN crm_propostas prop ON prop.id = i.proposta_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE i.cliente_id = %s
              AND i.ativo = 1
              AND c.ativo = 1
            ORDER BY FIELD(i.status, 'EM_EXECUCAO', 'EM_VALIDACAO', 'AGUARDANDO_INICIO', 'EM_PLANEJAMENTO', 'PAUSADA', 'ENTREGUE', 'CANCELADA'),
                     COALESCE(i.data_prevista_entrega, '2999-12-31') ASC,
                     i.updated_at DESC,
                     i.id DESC
            LIMIT 1
            """,
            (cliente_id,),
        )

    @classmethod
    def buscar_por_contrato_id(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT *
            FROM implantacoes
            WHERE contrato_id = %s AND ativo = 1
            LIMIT 1
            """,
            (contrato_id,),
        )

    @classmethod
    def desativar_por_contratos_omie_inativos(cls):
        return cls.execute_delete_count(
            """
            UPDATE implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            SET i.ativo = 0,
                i.status = 'CANCELADA',
                i.etapa_kanban = 'CANCELADOS'
            WHERE i.ativo = 1
              AND c.origem = 'OMIE'
              AND c.ativo = 0
            """
        )

    @classmethod
    def desativar_duplicadas_por_cliente(cls):
        return cls.execute_delete_count(
            """
            UPDATE implantacoes duplicada
            INNER JOIN implantacoes manter
                ON manter.cliente_id = duplicada.cliente_id
               AND manter.ativo = 1
               AND duplicada.ativo = 1
               AND manter.implantacao_principal_id IS NULL
               AND duplicada.implantacao_principal_id IS NULL
               AND (
                    manter.id > duplicada.id
                    OR (manter.contrato_id = duplicada.contrato_id AND manter.id > duplicada.id)
               )
            INNER JOIN contratos contrato_manter
                ON contrato_manter.id = manter.contrato_id
               AND contrato_manter.ativo = 1
            SET duplicada.ativo = 0,
                duplicada.status = 'CANCELADA',
                duplicada.etapa_kanban = 'CANCELADOS'
            WHERE duplicada.status = 'AGUARDANDO_INICIO'
              AND COALESCE(duplicada.etapa_kanban, 'FILA') = 'FILA'
            """
        )

    @classmethod
    def listar_contratos_elegiveis(cls):
        return cls.fetch_all(
            """
            SELECT
                c.id,
                c.numero,
                c.status,
                c.cliente_id,
                c.proposta_id,
                c.executivo_id,
                c.parceiro_id,
                c.data_fechamento,
                c.descricao AS contrato_descricao,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                exec.nome AS executivo_nome,
                par.nome AS parceiro_nome,
                prop.titulo AS proposta_titulo,
                prop.detalhes_negociacao AS proposta_escopo
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros par ON par.id = c.parceiro_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            LEFT JOIN implantacoes ic ON ic.cliente_id = c.cliente_id AND ic.ativo = 1
            WHERE c.ativo = 1
              AND i.id IS NULL
              AND ic.id IS NULL
              AND c.status = 'ENCAMINHADO_PROJETO'
            ORDER BY COALESCE(c.data_fechamento, c.created_at) DESC, c.id DESC
            """
        )

    @classmethod
    def buscar_contrato_operacional(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT
                c.id,
                c.numero,
                c.status,
                c.origem,
                c.descricao AS contrato_descricao,
                c.data_fechamento,
                c.inicio_vigencia,
                c.fim_vigencia,
                c.contato_nome,
                c.contato_email,
                c.contato_telefone,
                c.codigo_vendedor,
                c.vendedor_nome,
                c.codigo_projeto,
                c.projeto_nome,
                c.proposta_id,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                cli.razao_social AS cliente_razao_social,
                cli.cnpj AS cliente_cnpj,
                exec.nome AS executivo_nome,
                exec.email AS executivo_email,
                par.nome AS parceiro_nome,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                prop.detalhes_negociacao AS proposta_escopo,
                prop.observacoes AS proposta_observacoes
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros par ON par.id = c.parceiro_id
            WHERE c.id = %s AND c.ativo = 1
            """,
            (contrato_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacoes (
                uuid, contrato_id, cliente_id, proposta_id, executivo_id, parceiro_id,
                titulo, status, etapa_kanban, prioridade, responsavel, implantador_nome,
                implantador_email, emails_adicionais, data_prevista_inicio, data_prevista_entrega,
                observacoes, provisionamento_status, provisionamento_notas, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, 1
            )
            """,
            (
                cls.generate_uuid(),
                dados.get("contrato_id"),
                dados.get("cliente_id"),
                dados.get("proposta_id"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("titulo"),
                dados.get("status"),
                dados.get("etapa_kanban"),
                dados.get("prioridade"),
                dados.get("responsavel"),
                dados.get("implantador_nome"),
                dados.get("implantador_email"),
                dados.get("emails_adicionais"),
                dados.get("data_prevista_inicio"),
                dados.get("data_prevista_entrega"),
                dados.get("observacoes"),
                dados.get("provisionamento_status"),
                dados.get("provisionamento_notas"),
            ),
        )

    @classmethod
    def atualizar(cls, implantacao_id, dados):
        return cls.execute(
            """
            UPDATE implantacoes
            SET titulo=%s,
                status=%s,
                etapa_kanban=%s,
                prioridade=%s,
                responsavel=%s,
                implantador_nome=%s,
                implantador_email=%s,
                emails_adicionais=%s,
                executivo_id=%s,
                parceiro_id=%s,
                data_prevista_inicio=%s,
                data_prevista_entrega=%s,
                data_inicio=%s,
                data_entrega=%s,
                observacoes=%s,
                provisionamento_status=%s,
                provisionamento_notas=%s
            WHERE id=%s AND ativo=1
            """,
            (
                dados.get("titulo"),
                dados.get("status"),
                dados.get("etapa_kanban"),
                dados.get("prioridade"),
                dados.get("responsavel"),
                dados.get("implantador_nome"),
                dados.get("implantador_email"),
                dados.get("emails_adicionais"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("data_prevista_inicio"),
                dados.get("data_prevista_entrega"),
                dados.get("data_inicio"),
                dados.get("data_entrega"),
                dados.get("observacoes"),
                dados.get("provisionamento_status"),
                dados.get("provisionamento_notas"),
                implantacao_id,
            ),
        )

    @classmethod
    def atualizar_percentual(cls, implantacao_id):
        return cls.execute(
            """
            UPDATE implantacoes i
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                WHERE implantacao_id = %s
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            SET i.percentual_conclusao = CASE
                    WHEN COALESCE(checklist.total_itens, 0) = 0 THEN 0
                    ELSE ROUND((checklist.total_concluidos / checklist.total_itens) * 100, 2)
                END
            WHERE i.id = %s
            """,
            (implantacao_id, implantacao_id),
        )

    @classmethod
    def dashboard(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo=1, agrupamento="principais"):
        joins = """
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, status, responsavel, prazo, ativo, agrupamento=agrupamento)
        resumo = cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total_implantacoes,
                SUM(CASE WHEN i.status IN ('AGUARDANDO_INICIO', 'EM_PLANEJAMENTO') THEN 1 ELSE 0 END) AS total_planejamento,
                SUM(CASE WHEN i.status = 'EM_EXECUCAO' THEN 1 ELSE 0 END) AS total_execucao,
                SUM(CASE WHEN i.status = 'EM_VALIDACAO' THEN 1 ELSE 0 END) AS total_validacao,
                SUM(CASE WHEN i.status = 'ENTREGUE' THEN 1 ELSE 0 END) AS total_entregues,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega < CURDATE() THEN 1 ELSE 0 END) AS total_atrasadas,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS total_vence_7,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) AS total_vence_30,
                SUM(CASE WHEN i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega IS NULL THEN 1 ELSE 0 END) AS total_sem_prazo
            """
            + joins
            + where,
            tuple(params),
        )
        por_status = cls.fetch_all(
            """
            SELECT i.status AS nome, COUNT(*) AS total
            """
            + joins
            + where
            + """
            GROUP BY i.status
            ORDER BY total DESC, i.status ASC
            """,
            tuple(params),
        )
        por_responsavel = cls.fetch_all(
            """
            SELECT COALESCE(NULLIF(i.responsavel, ''), NULLIF(i.implantador_nome, ''), 'Sem responsável') AS nome, COUNT(*) AS total
            """
            + joins
            + where
            + """
            GROUP BY nome
            ORDER BY total DESC, nome ASC
            LIMIT 8
            """,
            tuple(params),
        )
        return {"resumo": resumo, "por_status": por_status, "por_responsavel": por_responsavel}


    @classmethod
    def rastreabilidade_por_proposta(cls, proposta_id):
        return cls.fetch_one(
            """
            SELECT
                prop.id AS proposta_id,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                prop.cliente_nome AS proposta_cliente_nome,
                prop.status AS proposta_status,
                prop.clicksign_status,
                prop.clicksign_document_key,
                prop.clicksign_envelope_id,
                prop.clicksign_sent_at,
                prop.clicksign_signed_at,
                prop.clicksign_completed_at,
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.origem AS contrato_origem,
                c.status AS contrato_status,
                c.codigo_externo AS contrato_codigo_externo,
                c.data_fechamento AS contrato_data_fechamento,
                i.id AS implantacao_id,
                i.titulo AS implantacao_titulo,
                i.status AS implantacao_status,
                i.etapa_kanban,
                i.responsavel AS implantacao_responsavel,
                i.implantador_nome,
                i.data_prevista_entrega,
                i.percentual_conclusao,
                checklist.total_itens,
                checklist.total_concluidos
            FROM crm_propostas prop
            LEFT JOIN contratos c ON c.proposta_id = prop.id AND c.ativo = 1
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE prop.id = %s
            ORDER BY COALESCE(i.updated_at, c.updated_at, prop.updated_at) DESC, c.id DESC
            LIMIT 1
            """,
            (proposta_id,),
        )

    @classmethod
    def rastreabilidade_por_contrato(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT
                prop.id AS proposta_id,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                prop.cliente_nome AS proposta_cliente_nome,
                prop.status AS proposta_status,
                prop.clicksign_status,
                prop.clicksign_document_key,
                prop.clicksign_envelope_id,
                prop.clicksign_sent_at,
                prop.clicksign_signed_at,
                prop.clicksign_completed_at,
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.origem AS contrato_origem,
                c.status AS contrato_status,
                c.codigo_externo AS contrato_codigo_externo,
                c.data_fechamento AS contrato_data_fechamento,
                i.id AS implantacao_id,
                i.titulo AS implantacao_titulo,
                i.status AS implantacao_status,
                i.etapa_kanban,
                i.responsavel AS implantacao_responsavel,
                i.implantador_nome,
                i.data_prevista_entrega,
                i.percentual_conclusao,
                checklist.total_itens,
                checklist.total_concluidos
            FROM contratos c
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id
            LEFT JOIN implantacoes i ON i.contrato_id = c.id AND i.ativo = 1
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE c.id = %s AND c.ativo = 1
            LIMIT 1
            """,
            (contrato_id,),
        )

    @classmethod
    def rastreabilidade_por_implantacao(cls, implantacao_id):
        return cls.fetch_one(
            """
            SELECT
                prop.id AS proposta_id,
                prop.codigo_proposta,
                prop.titulo AS proposta_titulo,
                prop.cliente_nome AS proposta_cliente_nome,
                prop.status AS proposta_status,
                prop.clicksign_status,
                prop.clicksign_document_key,
                prop.clicksign_envelope_id,
                prop.clicksign_sent_at,
                prop.clicksign_signed_at,
                prop.clicksign_completed_at,
                c.id AS contrato_id,
                c.numero AS contrato_numero,
                c.origem AS contrato_origem,
                c.status AS contrato_status,
                c.codigo_externo AS contrato_codigo_externo,
                c.data_fechamento AS contrato_data_fechamento,
                i.id AS implantacao_id,
                i.titulo AS implantacao_titulo,
                i.status AS implantacao_status,
                i.etapa_kanban,
                i.responsavel AS implantacao_responsavel,
                i.implantador_nome,
                i.data_prevista_entrega,
                i.percentual_conclusao,
                checklist.total_itens,
                checklist.total_concluidos
            FROM implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN crm_propostas prop ON prop.id = c.proposta_id
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE i.id = %s AND i.ativo = 1
            LIMIT 1
            """,
            (implantacao_id,),
        )


    @classmethod
    def listar_colunas_kanban(cls, ativo=None):
        sql = """
            SELECT id, uuid, codigo, titulo, ordem, ativo, sistema, created_at, updated_at,
                   uso.total_cards
            FROM implantacao_kanban_colunas col
            LEFT JOIN (
                SELECT etapa_kanban, COUNT(*) AS total_cards
                FROM implantacoes
                WHERE ativo = 1 AND implantacao_principal_id IS NULL
                GROUP BY etapa_kanban
            ) uso ON uso.etapa_kanban = col.codigo
            WHERE 1 = 1
        """
        params = []
        if ativo in (0, 1):
            sql += " AND col.ativo = %s"
            params.append(ativo)
        sql += " ORDER BY col.ordem ASC, col.id ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def buscar_coluna_kanban(cls, coluna_id):
        return cls.fetch_one(
            """
            SELECT id, uuid, codigo, titulo, ordem, ativo, sistema
            FROM implantacao_kanban_colunas
            WHERE id = %s
            """,
            (coluna_id,),
        )

    @classmethod
    def buscar_coluna_kanban_por_codigo(cls, codigo):
        return cls.fetch_one(
            """
            SELECT id, uuid, codigo, titulo, ordem, ativo, sistema
            FROM implantacao_kanban_colunas
            WHERE codigo = %s
            """,
            (codigo,),
        )

    @classmethod
    def inserir_coluna_kanban(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
            VALUES (%s, %s, %s, %s, %s, 0)
            """,
            (
                cls.generate_uuid(),
                dados.get("codigo"),
                dados.get("titulo"),
                dados.get("ordem"),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar_coluna_kanban(cls, coluna_id, dados):
        return cls.execute(
            """
            UPDATE implantacao_kanban_colunas
            SET titulo = %s,
                ordem = %s,
                ativo = %s
            WHERE id = %s
            """,
            (
                dados.get("titulo"),
                dados.get("ordem"),
                cls.bool_to_int(dados.get("ativo", True)),
                coluna_id,
            ),
        )

    @classmethod
    def contar_cards_por_coluna_kanban(cls, codigo):
        return cls.scalar(
            """
            SELECT COUNT(*)
            FROM implantacoes
            WHERE ativo = 1 AND implantacao_principal_id IS NULL AND etapa_kanban = %s
            """,
            (codigo,),
        ) or 0

    @classmethod
    def listar_kanban(cls):
        return cls.fetch_all(
            """
            SELECT
                i.id,
                i.contrato_id,
                i.implantacao_principal_id,
                i.titulo,
                i.etapa_kanban,
                i.responsavel,
                i.implantador_nome,
                i.implantador_email,
                i.emails_adicionais,
                i.data_prevista_inicio,
                i.data_prevista_entrega,
                i.updated_at,
                c.numero AS contrato_numero,
                c.contato_email,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                cli.cnpj AS cliente_cnpj,
                cli.email AS cliente_email,
                exec.nome AS executivo_nome,
                exec.email AS executivo_email,
                p.nome AS parceiro_nome,
                p.email AS parceiro_email
            FROM implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            WHERE i.ativo = 1
              AND c.ativo = 1
              AND i.implantacao_principal_id IS NULL
            ORDER BY COALESCE(i.data_prevista_entrega, '2999-12-31') ASC, i.updated_at DESC, i.id DESC
            """
        )

    @classmethod
    def listar_principais_para_vinculo(cls):
        return cls.fetch_all(
            """
            SELECT
                i.id,
                i.titulo,
                i.cliente_id,
                c.numero AS contrato_numero,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1 AND i.implantacao_principal_id IS NULL
            ORDER BY COALESCE(cli.nome_fantasia, cli.razao_social) ASC, i.id DESC
            LIMIT 500
            """
        )

    @classmethod
    def listar_vinculadas(cls, implantacao_id):
        return cls.fetch_all(
            """
            SELECT
                i.id,
                i.titulo,
                i.status,
                i.etapa_kanban,
                i.data_prevista_entrega,
                c.numero AS contrato_numero,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                cli.cnpj AS cliente_cnpj
            FROM implantacoes i
            INNER JOIN contratos c ON c.id = i.contrato_id
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            WHERE i.ativo = 1 AND i.implantacao_principal_id = %s
            ORDER BY i.updated_at DESC, i.id DESC
            """,
            (implantacao_id,),
        )

    @classmethod
    def vincular_card(cls, implantacao_id, implantacao_principal_id):
        return cls.execute(
            """
            UPDATE implantacoes
            SET implantacao_principal_id = %s
            WHERE id = %s AND ativo = 1
            """,
            (implantacao_principal_id, implantacao_id),
        )

    @classmethod
    def desvincular_card(cls, implantacao_id):
        return cls.execute(
            """
            UPDATE implantacoes
            SET implantacao_principal_id = NULL
            WHERE id = %s AND ativo = 1
            """,
            (implantacao_id,),
        )

    @classmethod
    def atualizar_etapa_kanban(cls, implantacao_id, etapa_kanban):
        return cls.execute(
            """
            UPDATE implantacoes
            SET etapa_kanban=%s,
                status=CASE
                    WHEN %s = 'FINALIZADO' THEN 'ENTREGUE'
                    WHEN %s = 'CANCELADOS' THEN 'CANCELADA'
                    WHEN status IN ('ENTREGUE', 'CANCELADA') AND %s NOT IN ('FINALIZADO', 'CANCELADOS') THEN 'EM_EXECUCAO'
                    ELSE status
                END
            WHERE id=%s AND ativo=1
            """,
            (etapa_kanban, etapa_kanban, etapa_kanban, etapa_kanban, implantacao_id),
        )


    @classmethod
    def listar_historico(cls, implantacao_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_historico
            WHERE implantacao_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (implantacao_id,),
        )

    @classmethod
    def listar_anexos_historico(cls, implantacao_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_historico_anexos
            WHERE implantacao_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (implantacao_id,),
        )

    @classmethod
    def inserir_anexo_historico(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_historico_anexos (
                uuid, historico_id, implantacao_id, arquivo_original, nome_arquivo,
                caminho, url, mime_type, tamanho
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("historico_id"),
                dados.get("implantacao_id"),
                dados.get("arquivo_original"),
                dados.get("nome_arquivo"),
                dados.get("caminho"),
                dados.get("url"),
                dados.get("mime_type"),
                dados.get("tamanho"),
            ),
        )

    @classmethod
    def listar_anexos_por_historico(cls, historico_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_historico_anexos
            WHERE historico_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (historico_id,),
        )

    @classmethod
    def inserir_historico(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_historico (
                uuid, implantacao_id, tipo, etapa_anterior, etapa_nova, autor,
                comentario, email_enviado, email_resultado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("implantacao_id"),
                dados.get("tipo") or "COMENTARIO",
                dados.get("etapa_anterior"),
                dados.get("etapa_nova"),
                dados.get("autor"),
                dados.get("comentario"),
                cls.bool_to_int(dados.get("email_enviado")),
                dados.get("email_resultado"),
            ),
        )

    @classmethod
    def buscar_historico_por_id(cls, historico_id):
        return cls.fetch_one("SELECT * FROM implantacao_historico WHERE id = %s", (historico_id,))

    @classmethod
    def atualizar_comentario_historico(cls, historico_id, comentario):
        return cls.execute(
            """
            UPDATE implantacao_historico
            SET comentario=%s
            WHERE id=%s AND tipo='COMENTARIO'
            """,
            (comentario, historico_id),
        )

    @classmethod
    def excluir_historico(cls, historico_id):
        return cls.execute(
            """
            DELETE FROM implantacao_historico
            WHERE id=%s AND tipo='COMENTARIO'
            """,
            (historico_id,),
        )

    @classmethod
    def listar_checklist(cls, implantacao_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_checklist
            WHERE implantacao_id = %s
            ORDER BY ordem ASC, id ASC
            """,
            (implantacao_id,),
        )


    @classmethod
    def proxima_ordem_checklist(cls, implantacao_id):
        ordem = cls.scalar(
            """
            SELECT COALESCE(MAX(ordem), 0) + 10
            FROM implantacao_checklist
            WHERE implantacao_id = %s
            """,
            (implantacao_id,),
        )
        return ordem or 10

    @classmethod
    def inserir_item_checklist(cls, implantacao_id, item):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_checklist (
                uuid, implantacao_id, ordem, grupo, titulo, descricao, obrigatorio, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDENTE')
            """,
            (
                cls.generate_uuid(),
                implantacao_id,
                item.get("ordem"),
                item.get("grupo"),
                item.get("titulo"),
                item.get("descricao"),
                cls.bool_to_int(item.get("obrigatorio", True)),
            ),
        )

    @classmethod
    def atualizar_item_checklist(cls, item_id, dados):
        return cls.execute(
            """
            UPDATE implantacao_checklist
            SET status=%s,
                responsavel=%s,
                evidencia=%s,
                concluido_em=CASE WHEN %s = 'CONCLUIDO' THEN COALESCE(concluido_em, NOW()) ELSE NULL END
            WHERE id=%s
            """,
            (
                dados.get("status"),
                dados.get("responsavel"),
                dados.get("evidencia"),
                dados.get("status"),
                item_id,
            ),
        )


    @classmethod
    def excluir_item_checklist(cls, item_id):
        return cls.execute(
            "DELETE FROM implantacao_checklist WHERE id = %s",
            (item_id,),
        )

    @classmethod
    def buscar_item_checklist(cls, item_id):
        return cls.fetch_one("SELECT * FROM implantacao_checklist WHERE id = %s", (item_id,))

    @classmethod
    def _filtros(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo=1, agrupamento="principais"):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            where.append(
                """
                (
                    i.titulo LIKE %s
                    OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                    OR COALESCE(cli.cnpj, '') LIKE %s
                    OR COALESCE(c.numero, '') LIKE %s
                    OR COALESCE(i.responsavel, '') LIKE %s
                    OR COALESCE(i.implantador_nome, '') LIKE %s
                    OR COALESCE(exec.nome, '') LIKE %s
                    OR COALESCE(p.nome, '') LIKE %s
                )
                """
            )
            params.extend([termo] * 8)
        if status:
            where.append("i.status = %s")
            params.append(status)
        if responsavel:
            where.append("(i.responsavel LIKE %s OR i.implantador_nome LIKE %s)")
            params.extend([f"%{responsavel}%", f"%{responsavel}%"])
        if prazo == "atrasadas":
            where.append("i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega < CURDATE()")
        elif prazo == "vence_7":
            where.append("i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)")
        elif prazo == "vence_30":
            where.append("i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)")
        elif prazo == "sem_prazo":
            where.append("i.status NOT IN ('ENTREGUE', 'CANCELADA') AND i.data_prevista_entrega IS NULL")
        if agrupamento == "principais":
            where.append("i.implantacao_principal_id IS NULL")
        elif agrupamento == "vinculadas":
            where.append("i.implantacao_principal_id IS NOT NULL")
        if ativo in (0, 1):
            where.append("i.ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params

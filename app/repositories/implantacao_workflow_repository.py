from app.repositories.base_repository import BaseRepository


class ImplantacaoWorkflowRepository(BaseRepository):
    TABLE = "implantacoes"

    @classmethod
    def total(cls, pesquisa=None, status=None, responsavel=None, ativo=1):
        sql = """
            SELECT COUNT(*)
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, status, responsavel, ativo)
        sql += where
        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, status=None, responsavel=None, ativo=1, limit=50, offset=0):
        sql = """
            SELECT
                i.id,
                i.uuid,
                i.contrato_id,
                i.cliente_id,
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
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome,
                exec.nome AS executivo_nome,
                p.nome AS parceiro_nome,
                checklist.total_itens,
                checklist.total_concluidos
            FROM implantacoes i
            INNER JOIN clientes cli ON cli.id = i.cliente_id
            INNER JOIN contratos c ON c.id = i.contrato_id
            LEFT JOIN parceiros_executivos exec ON exec.id = i.executivo_id
            LEFT JOIN parceiros p ON p.id = i.parceiro_id
            LEFT JOIN (
                SELECT implantacao_id,
                       COUNT(*) AS total_itens,
                       SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidos
                FROM implantacao_checklist
                GROUP BY implantacao_id
            ) checklist ON checklist.implantacao_id = i.id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, status, responsavel, ativo)
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
                c.numero AS contrato_numero,
                c.status AS contrato_status,
                c.descricao AS contrato_descricao,
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
            WHERE i.id = %s AND i.ativo = 1
        """
        return cls.fetch_one(sql, (implantacao_id,))

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
            WHERE c.ativo = 1
              AND i.id IS NULL
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
    def dashboard(cls):
        resumo = cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total_implantacoes,
                SUM(CASE WHEN status IN ('AGUARDANDO_INICIO', 'EM_PLANEJAMENTO') THEN 1 ELSE 0 END) AS total_planejamento,
                SUM(CASE WHEN status = 'EM_EXECUCAO' THEN 1 ELSE 0 END) AS total_execucao,
                SUM(CASE WHEN status = 'EM_VALIDACAO' THEN 1 ELSE 0 END) AS total_validacao,
                SUM(CASE WHEN status = 'ENTREGUE' THEN 1 ELSE 0 END) AS total_entregues,
                SUM(CASE WHEN status NOT IN ('ENTREGUE', 'CANCELADA') AND data_prevista_entrega < CURDATE() THEN 1 ELSE 0 END) AS total_atrasadas
            FROM implantacoes
            WHERE ativo = 1
            """
        )
        por_status = cls.fetch_all(
            """
            SELECT status AS nome, COUNT(*) AS total
            FROM implantacoes
            WHERE ativo = 1
            GROUP BY status
            ORDER BY total DESC, status ASC
            """
        )
        por_responsavel = cls.fetch_all(
            """
            SELECT COALESCE(responsavel, 'Sem responsavel') AS nome, COUNT(*) AS total
            FROM implantacoes
            WHERE ativo = 1
            GROUP BY nome
            ORDER BY total DESC, nome ASC
            LIMIT 8
            """
        )
        return {"resumo": resumo, "por_status": por_status, "por_responsavel": por_responsavel}

    @classmethod
    def listar_kanban(cls):
        return cls.fetch_all(
            """
            SELECT
                i.id,
                i.contrato_id,
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
            ORDER BY COALESCE(i.data_prevista_entrega, '2999-12-31') ASC, i.updated_at DESC, i.id DESC
            """
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
    def buscar_item_checklist(cls, item_id):
        return cls.fetch_one("SELECT * FROM implantacao_checklist WHERE id = %s", (item_id,))

    @classmethod
    def _filtros(cls, pesquisa=None, status=None, responsavel=None, ativo=1):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            where.append(
                """
                (
                    i.titulo LIKE %s
                    OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                    OR COALESCE(c.numero, '') LIKE %s
                    OR COALESCE(i.responsavel, '') LIKE %s
                    OR COALESCE(exec.nome, '') LIKE %s
                    OR COALESCE(p.nome, '') LIKE %s
                )
                """
            )
            params.extend([termo] * 6)
        if status:
            where.append("i.status = %s")
            params.append(status)
        if responsavel:
            where.append("i.responsavel LIKE %s")
            params.append(f"%{responsavel}%")
        if ativo in (0, 1):
            where.append("i.ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params

from app.core.constants.origens import ORIGEM_MANUAL
from app.core.constants.origens import ORIGEM_OMIE
from app.repositories.base_repository import BaseRepository


class ContratoRepository(BaseRepository):

    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM contratos
            WHERE codigo_externo=%s
            ORDER BY origem = 'OMIE' DESC, id DESC
            """,
            (codigo_externo,),
        )
        contrato = cursor.fetchone()
        cls.close(conn, cursor)
        return contrato

    @classmethod
    def buscar_manual_por_numero(cls, cliente_id, numero):
        if not numero:
            return None
        return cls.fetch_one(
            """
            SELECT * FROM contratos
            WHERE cliente_id=%s AND numero=%s AND origem=%s AND ativo=1
            ORDER BY id DESC
            LIMIT 1
            """,
            (cliente_id, numero, ORIGEM_MANUAL),
        )

    @classmethod
    def buscar_por_id(cls, contrato_id):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                c.*,
                cli.nome_fantasia AS cliente_nome,
                cli.razao_social AS cliente_razao_social,
                cli.cnpj AS cliente_cnpj,
                cli.email AS cliente_email,
                cli.telefone AS cliente_telefone,
                cli.codigo_externo AS cliente_codigo_externo,
                exec.nome AS executivo_nome,
                exec.email AS executivo_email,
                p.nome AS parceiro_nome
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
            WHERE c.id=%s AND c.ativo=1
            """,
            (contrato_id,),
        )
        contrato = cursor.fetchone()
        cls.close(conn, cursor)
        return contrato

    @classmethod
    def total(cls, pesquisa=None, status=None, origem=None, data_de=None, data_ate=None):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT COUNT(*) AS total
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
        """
        where, parametros = cls._filtros(pesquisa, status, origem, data_de, data_ate)
        if where:
            sql += " WHERE " + " AND ".join(where)
        cursor.execute(sql, tuple(parametros))
        total = cursor.fetchone()["total"]
        cls.close(conn, cursor)
        return total

    @classmethod
    def listar(cls, pesquisa=None, status=None, origem=None, data_de=None, data_ate=None, limit=50, offset=0):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT
                c.id,
                c.uuid,
                c.cliente_id,
                c.codigo_externo,
                c.origem,
                c.numero,
                c.descricao,
                c.status,
                c.valor_mensal,
                c.valor_setup,
                c.valor_projeto,
                c.setup_omie_status,
                c.setup_omie_codigo_os,
                c.setup_omie_numero_os,
                c.setup_omie_valor_total,
                c.setup_omie_parcelas,
                c.setup_omie_faturamento_status,
                c.setup_omie_sincronizado_em,
                c.valor_promocional,
                c.valor_servicos_bruto,
                c.valor_descontos,
                c.valor_servicos_liquido,
                c.vendedor_nome,
                c.projeto_nome,
                c.quantidade_usuarios,
                c.data_fechamento,
                c.inicio_vigencia,
                c.fim_vigencia,
                c.arquivo_assinado,
                c.arquivo_assinado_original,
                c.clicksign_assinado_em,
                cli.nome_fantasia AS cliente_nome,
                cli.razao_social AS cliente_razao_social,
                cli.cnpj AS cliente_cnpj,
                exec.nome AS executivo_nome,
                p.nome AS parceiro_nome
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
        """
        where, parametros = cls._filtros(pesquisa, status, origem, data_de, data_ate)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += """
            ORDER BY COALESCE(c.data_fechamento, c.created_at) DESC, c.id DESC
            LIMIT %s OFFSET %s
        """
        parametros.extend([limit, offset])
        cursor.execute(sql, tuple(parametros))
        contratos = cursor.fetchall()
        cls.close(conn, cursor)
        return contratos

    @classmethod
    def listar_para_ambientes(cls, limit=1000, offset=0):
        return cls.fetch_all(
            """
            SELECT
                c.id,
                c.numero,
                c.descricao,
                c.status,
                c.valor_mensal,
                c.data_fechamento,
                cli.nome_fantasia AS cliente_nome,
                cli.razao_social AS cliente_razao_social,
                cli.cnpj AS cliente_cnpj
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE c.ativo = 1
              AND c.status IN ('ATIVO', 'ENCAMINHADO_PROJETO', 'EM_ELABORACAO')
            ORDER BY FIELD(c.status, 'ENCAMINHADO_PROJETO', 'EM_ELABORACAO', 'ATIVO'),
                     COALESCE(c.data_fechamento, c.created_at) DESC, c.id DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )

    @classmethod
    def dashboard(cls, pesquisa=None, status=None, origem=None, data_de=None, data_ate=None):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        joins = """
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
        """
        where, parametros = cls._filtros(pesquisa, status, origem, data_de, data_ate)
        where_sql = " WHERE " + " AND ".join(where) if where else ""

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS total_recorrencia,
                COALESCE(SUM(COALESCE(c.valor_setup, 0) + COALESCE(c.valor_projeto, 0)), 0) AS total_setup,
                COALESCE(SUM(COALESCE(c.quantidade_usuarios, 0)), 0) AS total_usuarios,
                SUM(CASE WHEN c.status = 'RASCUNHO' THEN 1 ELSE 0 END) AS total_rascunho,
                SUM(CASE WHEN c.status IN ('ENCAMINHADO_PROJETO', 'EM_ELABORACAO') THEN 1 ELSE 0 END) AS total_encaminhado,
                SUM(CASE WHEN c.status = 'ATIVO' THEN 1 ELSE 0 END) AS total_ativos,
                SUM(CASE WHEN c.status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluido
            """ + joins + where_sql,
            tuple(parametros),
        )
        resumo = cursor.fetchone()

        adendo_joins = """
            FROM contratos_adendos a
            INNER JOIN contratos c ON c.id = a.contrato_id
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
            LEFT JOIN parceiros p ON p.id = c.parceiro_id
        """
        adendo_where, adendo_parametros = cls._filtros_adendos_dashboard(pesquisa, status, origem, data_de, data_ate)
        adendo_where_sql = " WHERE " + " AND ".join(adendo_where) if adendo_where else ""
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_adendos,
                COALESCE(SUM(COALESCE(a.valor_recorrente, 0)), 0) AS total_recorrencia_adendos,
                COALESCE(SUM(CASE WHEN a.tipo = 'USUARIOS_ADICIONAIS' THEN COALESCE(a.quantidade_usuarios, 0) ELSE 0 END), 0) AS total_usuarios_adendos
            """ + adendo_joins + adendo_where_sql,
            tuple(adendo_parametros),
        )
        resumo_adendos = cursor.fetchone() or {}

        resumo = cls._combinar_resumo_dashboard(resumo, resumo_adendos)
        executivos = cls._combinar_agrupamento_dashboard(
            cls._agrupar(cursor, joins, where_sql, parametros, "COALESCE(exec.nome, 'Sem executivo')"),
            cls._agrupar_adendos(cursor, adendo_joins, adendo_where_sql, adendo_parametros, "COALESCE(exec.nome, 'Sem executivo')"),
        )
        parceiros = cls._combinar_agrupamento_dashboard(
            cls._agrupar(cursor, joins, where_sql, parametros, "COALESCE(p.nome, 'Sem parceiro')"),
            cls._agrupar_adendos(cursor, adendo_joins, adendo_where_sql, adendo_parametros, "COALESCE(p.nome, 'Sem parceiro')"),
        )

        cls.close(conn, cursor)
        return {
            "resumo": resumo,
            "executivos": executivos,
            "parceiros": parceiros,
        }

    @classmethod
    def contar_encaminhados_sem_arquivo(cls):
        return cls.scalar(
            """
            SELECT COUNT(*)
            FROM contratos
            WHERE ativo = 1
              AND status = 'ENCAMINHADO_PROJETO'
              AND (arquivo_assinado IS NULL OR arquivo_assinado = '')
            """
        ) or 0

    @classmethod
    def buscar_assinado_sem_codigo_por_cliente_valor(cls, cliente_id, valor_mensal):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM contratos
            WHERE cliente_id=%s
              AND origem=%s
              AND codigo_externo IS NULL
              AND arquivo_assinado IS NOT NULL
              AND ativo=1
              AND COALESCE(valor_mensal, 0) = COALESCE(%s, 0)
            ORDER BY data_fechamento DESC, id DESC
            LIMIT 1
            """,
            (cliente_id, ORIGEM_MANUAL, valor_mensal),
        )
        contrato = cursor.fetchone()
        cls.close(conn, cursor)
        return contrato

    @classmethod
    def buscar_omie_ativo_por_cliente(cls, cliente_id, exceto_id=None):
        parametros = [cliente_id, ORIGEM_OMIE]
        filtro_exceto = ""
        if exceto_id:
            filtro_exceto = "AND id <> %s"
            parametros.append(exceto_id)

        return cls.fetch_one(
            f"""
            SELECT *
            FROM contratos
            WHERE cliente_id=%s
              AND origem=%s
              AND ativo=1
              {filtro_exceto}
            ORDER BY synced_at DESC, id DESC
            LIMIT 1
            """,
            tuple(parametros),
        )

    @classmethod
    def desativar_omie_ativos_por_cliente(cls, cliente_id, manter_id):
        return cls.execute_delete_count(
            """
            UPDATE contratos
            SET ativo=0,
                status='CANCELADO',
                synced_at=NOW()
            WHERE cliente_id=%s
              AND origem=%s
              AND ativo=1
              AND id<>%s
            """,
            (cliente_id, ORIGEM_OMIE, manter_id),
        )

    @classmethod
    def desativar_omie_ativos_ausentes(cls, codigos_externos):
        codigos = [codigo for codigo in codigos_externos if codigo not in (None, "")]
        if not codigos:
            return 0

        placeholders = ", ".join(["%s"] * len(codigos))
        parametros = [ORIGEM_OMIE, *codigos]
        return cls.execute_delete_count(
            f"""
            UPDATE contratos
            SET ativo=0,
                status='CANCELADO',
                synced_at=NOW()
            WHERE origem=%s
              AND ativo=1
              AND codigo_externo IS NOT NULL
              AND codigo_externo NOT IN ({placeholders})
            """,
            tuple(parametros),
        )

    @classmethod
    def buscar_por_proposta_id(cls, proposta_id):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM contratos
            WHERE proposta_id=%s AND ativo=1
            ORDER BY id DESC
            LIMIT 1
            """,
            (proposta_id,),
        )
        contrato = cursor.fetchone()
        cls.close(conn, cursor)
        return contrato

    @classmethod
    def inserir_manual(cls, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        uuid = cls.generate_uuid()
        cursor.execute(
            """
            INSERT INTO contratos (
                uuid, cliente_id, contato_id, proposta_id, codigo_externo, origem, numero, descricao, status,
                inicio_vigencia, fim_vigencia, contato_nome, contato_email,
                contato_telefone, data_fechamento, executivo_id, parceiro_id,
                tipo_venda, valor_mensal, valor_setup, valor_projeto,
                valor_promocional, quantidade_usuarios, data_inicio_recorrencia,
                data_ativacao, dia_faturamento, observacoes, arquivo_preparado,
                arquivo_preparado_original, ativo, synced_at
            ) VALUES (
                %s, %s, %s, %s, NULL, 'MANUAL', %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, 1, NULL
            )
            """,
            (
                uuid,
                dados.get("cliente_id"),
                dados.get("contato_id"),
                dados.get("proposta_id"),
                dados.get("numero"),
                dados.get("descricao"),
                dados.get("status"),
                dados.get("inicio_vigencia"),
                dados.get("fim_vigencia"),
                dados.get("contato_nome"),
                dados.get("contato_email"),
                dados.get("contato_telefone"),
                dados.get("data_fechamento"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("tipo_venda"),
                dados.get("valor_mensal"),
                dados.get("valor_setup"),
                dados.get("valor_projeto"),
                dados.get("valor_promocional"),
                dados.get("quantidade_usuarios"),
                dados.get("data_inicio_recorrencia"),
                dados.get("data_ativacao"),
                dados.get("dia_faturamento"),
                dados.get("observacoes"),
                dados.get("arquivo_preparado"),
                dados.get("arquivo_preparado_original"),
            ),
        )
        contrato_id = cursor.lastrowid
        conn.commit()
        cls.close(conn, cursor)
        return contrato_id

    @classmethod
    def inserir(cls, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        uuid = cls.generate_uuid()
        cursor.execute(
            """
            INSERT INTO contratos (
                uuid, cliente_id, executivo_id, parceiro_id, codigo_externo, origem, numero, descricao, status,
                inicio_vigencia, fim_vigencia, observacoes, ativo, synced_at,
                valor_mensal, dia_faturamento, tipo_faturamento, codigo_vendedor,
                vendedor_nome, codigo_projeto, projeto_nome, codigo_cc,
                observacao_contrato, valor_servicos_bruto, valor_descontos, valor_servicos_liquido
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(),
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                uuid,
                dados.get("cliente_id"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("codigo_externo"),
                dados.get("origem"),
                dados.get("numero"),
                dados.get("descricao"),
                dados.get("status"),
                dados.get("inicio_vigencia"),
                dados.get("fim_vigencia"),
                dados.get("observacoes"),
                1 if dados.get("ativo", True) else 0,
                dados.get("valor_mensal"),
                dados.get("dia_faturamento"),
                dados.get("tipo_faturamento"),
                dados.get("codigo_vendedor"),
                dados.get("vendedor_nome"),
                dados.get("codigo_projeto"),
                dados.get("projeto_nome"),
                dados.get("codigo_cc"),
                dados.get("observacao_contrato"),
                dados.get("valor_servicos_bruto"),
                dados.get("valor_descontos"),
                dados.get("valor_servicos_liquido"),
            ),
        )
        contrato_id = cursor.lastrowid
        conn.commit()
        cls.close(conn, cursor)
        return contrato_id

    @classmethod
    def listar_para_setup_omie(cls, limit=1000):
        return cls.fetch_all(
            """
            SELECT
                c.id,
                c.cliente_id,
                c.codigo_externo,
                c.numero,
                c.origem,
                c.status,
                c.data_fechamento,
                c.inicio_vigencia,
                cli.codigo_externo AS cliente_codigo_externo,
                cli.nome_fantasia AS cliente_nome,
                cli.razao_social AS cliente_razao_social
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE c.ativo = 1
              AND cli.codigo_externo IS NOT NULL
              AND cli.codigo_externo <> ''
              AND c.status NOT IN ('CANCELADO', 'ENCERRADO')
            ORDER BY COALESCE(c.setup_omie_sincronizado_em, '1970-01-01'), c.id
            LIMIT %s
            """,
            (limit,),
        )

    @classmethod
    def listar_omie_ativos_para_vinculos_comerciais(cls):
        return cls.fetch_all(
            """
            SELECT id, numero, vendedor_nome, projeto_nome, parceiro_id, executivo_id
            FROM contratos
            WHERE origem = %s
              AND ativo = 1
            """,
            (ORIGEM_OMIE,),
        )

    @classmethod
    def atualizar_vinculos_comerciais_omie_sync(cls, contrato_id, parceiro_id=None, executivo_id=None):
        return cls.execute(
            """
            UPDATE contratos
            SET parceiro_id = COALESCE(%s, parceiro_id),
                executivo_id = COALESCE(%s, executivo_id)
            WHERE id = %s
              AND origem = %s
              AND ativo = 1
            """,
            (parceiro_id, executivo_id, contrato_id, ORIGEM_OMIE),
        )

    @classmethod
    def atualizar_setup_omie(cls, contrato_id, dados):
        return cls.execute(
            """
            UPDATE contratos
            SET valor_setup = COALESCE(%s, valor_setup),
                setup_omie_status = %s,
                setup_omie_codigo_os = %s,
                setup_omie_numero_os = %s,
                setup_omie_valor_total = %s,
                setup_omie_parcelas = %s,
                setup_omie_etapa = %s,
                setup_omie_faturamento_status = %s,
                setup_omie_data_previsao = %s,
                setup_omie_data_faturamento = %s,
                setup_omie_data_cancelamento = %s,
                setup_omie_descricao = %s,
                setup_omie_observacao = %s,
                setup_omie_sincronizado_em = NOW()
            WHERE id = %s
              AND ativo = 1
            """,
            (
                dados.get("valor_setup"),
                dados.get("setup_omie_status"),
                dados.get("setup_omie_codigo_os"),
                dados.get("setup_omie_numero_os"),
                dados.get("setup_omie_valor_total"),
                dados.get("setup_omie_parcelas"),
                dados.get("setup_omie_etapa"),
                dados.get("setup_omie_faturamento_status"),
                dados.get("setup_omie_data_previsao"),
                dados.get("setup_omie_data_faturamento"),
                dados.get("setup_omie_data_cancelamento"),
                dados.get("setup_omie_descricao"),
                dados.get("setup_omie_observacao"),
                contrato_id,
            ),
        )

    @classmethod
    def atualizar_quantidade_usuarios(cls, contrato_id, quantidade_usuarios):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET quantidade_usuarios=%s
            WHERE id=%s
            """,
            (quantidade_usuarios, contrato_id),
        )
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def atualizar_sync(cls, contrato_id, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET
                cliente_id=%s,
                codigo_externo=%s,
                origem=%s,
                executivo_id=COALESCE(%s, executivo_id),
                parceiro_id=COALESCE(%s, parceiro_id),
                numero=%s,
                descricao=%s,
                status=%s,
                inicio_vigencia=%s,
                fim_vigencia=%s,
                valor_mensal=%s,
                dia_faturamento=%s,
                tipo_faturamento=%s,
                codigo_vendedor=%s,
                vendedor_nome=%s,
                codigo_projeto=%s,
                projeto_nome=%s,
                codigo_cc=%s,
                observacao_contrato=%s,
                valor_servicos_bruto=%s,
                valor_descontos=%s,
                valor_servicos_liquido=%s,
                ativo=%s,
                synced_at=NOW()
            WHERE id=%s
            """,
            (
                dados.get("cliente_id"),
                dados.get("codigo_externo"),
                dados.get("origem"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("numero"),
                dados.get("descricao"),
                dados.get("status"),
                dados.get("inicio_vigencia"),
                dados.get("fim_vigencia"),
                dados.get("valor_mensal"),
                dados.get("dia_faturamento"),
                dados.get("tipo_faturamento"),
                dados.get("codigo_vendedor"),
                dados.get("vendedor_nome"),
                dados.get("codigo_projeto"),
                dados.get("projeto_nome"),
                dados.get("codigo_cc"),
                dados.get("observacao_contrato"),
                dados.get("valor_servicos_bruto"),
                dados.get("valor_descontos"),
                dados.get("valor_servicos_liquido"),
                1 if dados.get("ativo", True) else 0,
                contrato_id,
            ),
        )
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def atualizar(cls, contrato_id, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET
                cliente_id=%s,
                contato_id=%s,
                proposta_id=%s,
                numero=%s,
                descricao=%s,
                status=%s,
                inicio_vigencia=%s,
                fim_vigencia=%s,
                contato_nome=%s,
                contato_email=%s,
                contato_telefone=%s,
                data_fechamento=%s,
                executivo_id=%s,
                parceiro_id=%s,
                tipo_venda=%s,
                valor_mensal=%s,
                valor_setup=%s,
                valor_projeto=%s,
                valor_promocional=%s,
                quantidade_usuarios=%s,
                data_inicio_recorrencia=%s,
                data_ativacao=%s,
                dia_faturamento=%s,
                observacoes=%s,
                arquivo_preparado=COALESCE(%s, arquivo_preparado),
                arquivo_preparado_original=COALESCE(%s, arquivo_preparado_original)
            WHERE id=%s AND origem=%s
            """,
            (
                dados.get("cliente_id"),
                dados.get("contato_id"),
                dados.get("proposta_id"),
                dados.get("numero"),
                dados.get("descricao"),
                dados.get("status"),
                dados.get("inicio_vigencia"),
                dados.get("fim_vigencia"),
                dados.get("contato_nome"),
                dados.get("contato_email"),
                dados.get("contato_telefone"),
                dados.get("data_fechamento"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("tipo_venda"),
                dados.get("valor_mensal"),
                dados.get("valor_setup"),
                dados.get("valor_projeto"),
                dados.get("valor_promocional"),
                dados.get("quantidade_usuarios"),
                dados.get("data_inicio_recorrencia"),
                dados.get("data_ativacao"),
                dados.get("dia_faturamento"),
                dados.get("observacoes"),
                dados.get("arquivo_preparado"),
                dados.get("arquivo_preparado_original"),
                contrato_id,
                ORIGEM_MANUAL,
            ),
        )
        conn.commit()
        cls.close(conn, cursor)


    @classmethod
    def atualizar_vinculos_comerciais(cls, contrato_id, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET
                contato_id=%s,
                contato_nome=%s,
                contato_email=%s,
                contato_telefone=%s,
                executivo_id=%s,
                parceiro_id=%s,
                observacoes=%s
            WHERE id=%s AND origem='OMIE' AND ativo=1
            """,
            (
                dados.get("contato_id"),
                dados.get("contato_nome"),
                dados.get("contato_email"),
                dados.get("contato_telefone"),
                dados.get("executivo_id"),
                dados.get("parceiro_id"),
                dados.get("observacoes"),
                contrato_id,
            ),
        )
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def atualizar_arquivo_assinado(cls, contrato_id, arquivo, arquivo_original, assinado_em=None, envelope_id=None, enviado_em=None):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET arquivo_assinado=%s,
                arquivo_assinado_original=%s,
                clicksign_status='ASSINADO',
                clicksign_document_key=COALESCE(%s, clicksign_document_key),
                clicksign_envelope_id=COALESCE(%s, clicksign_envelope_id),
                clicksign_enviado_em=COALESCE(%s, clicksign_enviado_em),
                clicksign_assinado_em=COALESCE(%s, NOW()),
                status=CASE
                    WHEN status IN ('RASCUNHO', 'ENVIADO_CLICKSIGN', 'AGUARDANDO_ASSINATURA') THEN 'CONCLUIDO'
                    ELSE status
                END
            WHERE id=%s AND ativo=1
            """,
            (arquivo, arquivo_original, arquivo, envelope_id, enviado_em, assinado_em, contrato_id),
        )
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def excluir(cls, contrato_id):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET ativo=0
            WHERE id=%s AND origem=%s
            """,
            (contrato_id, ORIGEM_MANUAL),
        )
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def listar_clientes_para_contrato(cls):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nome_fantasia, razao_social, cnpj, email, telefone
            FROM clientes
            WHERE ativo = 1
            ORDER BY nome_fantasia
            """
        )
        clientes = cursor.fetchall()
        cls.close(conn, cursor)
        return clientes

    @classmethod
    def listar_para_select(cls):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, numero, descricao
            FROM contratos
            WHERE ativo = 1
            ORDER BY numero
            """
        )
        contratos = cursor.fetchall()
        cls.close(conn, cursor)
        return contratos

    @staticmethod
    def _filtros(pesquisa=None, status=None, origem=None, data_de=None, data_ate=None):
        condicoes = [] if status == "CANCELADO" else ["c.ativo=1"]
        parametros = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            condicoes.append(
                """
                (
                    c.numero LIKE %s
                    OR c.descricao LIKE %s
                    OR cli.nome_fantasia LIKE %s
                    OR cli.razao_social LIKE %s
                    OR cli.cnpj LIKE %s
                    OR REGEXP_REPLACE(cli.cnpj, '[^0-9A-Za-z]', '') LIKE %s
                    OR exec.nome LIKE %s
                    OR p.nome LIKE %s
                )
                """
            )
            parametros.extend([termo, termo, termo, termo, termo, termo_cnpj, termo, termo])

        if status:
            condicoes.append("c.status = %s")
            parametros.append(status)

        if origem:
            condicoes.append("c.origem = %s")
            parametros.append(origem)

        if data_de:
            condicoes.append("COALESCE(c.inicio_vigencia, c.data_fechamento) >= %s")
            parametros.append(data_de)

        if data_ate:
            condicoes.append("COALESCE(c.inicio_vigencia, c.data_fechamento) <= %s")
            parametros.append(data_ate)

        return condicoes, parametros

    @classmethod
    def _filtros_adendos_dashboard(cls, pesquisa=None, status=None, origem=None, data_de=None, data_ate=None):
        condicoes = ["a.ativo = 1", "c.ativo = 1"]
        parametros = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in pesquisa if ch.isdigit())}%" if any(ch.isdigit() for ch in pesquisa) else termo
            condicoes.append("""
                (
                    COALESCE(cli.nome_fantasia, '') LIKE %s
                    OR COALESCE(cli.razao_social, '') LIKE %s
                    OR COALESCE(cli.cnpj, '') LIKE %s
                    OR COALESCE(c.numero, '') LIKE %s
                    OR COALESCE(exec.nome, '') LIKE %s
                    OR COALESCE(p.nome, '') LIKE %s
                    OR COALESCE(a.titulo, '') LIKE %s
                    OR COALESCE(a.numero_adendo, '') LIKE %s
                )
            """)
            parametros.extend([termo, termo, termo_cnpj, termo, termo, termo, termo, termo])

        if status:
            condicoes.append("c.status = %s")
            parametros.append(status)

        if origem:
            condicoes.append("c.origem = %s")
            parametros.append(origem)

        if data_de:
            condicoes.append("COALESCE(a.data_adendo, DATE(a.created_at)) >= %s")
            parametros.append(data_de)

        if data_ate:
            condicoes.append("COALESCE(a.data_adendo, DATE(a.created_at)) <= %s")
            parametros.append(data_ate)

        return condicoes, parametros

    @staticmethod
    def _combinar_resumo_dashboard(resumo, resumo_adendos):
        resumo = resumo or {}
        resumo_adendos = resumo_adendos or {}
        total_contratos = resumo.get("total_contratos") or 0
        total_adendos = resumo_adendos.get("total_adendos") or 0
        total_recorrencia_contratos = resumo.get("total_recorrencia") or 0
        total_recorrencia_adendos = resumo_adendos.get("total_recorrencia_adendos") or 0
        total_usuarios_contratos = resumo.get("total_usuarios") or 0
        total_usuarios_adendos = resumo_adendos.get("total_usuarios_adendos") or 0
        resumo["total_contratos_principais"] = total_contratos
        resumo["total_adendos"] = total_adendos
        resumo["total_itens_contratos"] = total_contratos + total_adendos
        resumo["total_recorrencia_contratos"] = total_recorrencia_contratos
        resumo["total_recorrencia_adendos"] = total_recorrencia_adendos
        resumo["total_recorrencia"] = total_recorrencia_contratos + total_recorrencia_adendos
        resumo["total_usuarios_contratos"] = total_usuarios_contratos
        resumo["total_usuarios_adendos"] = total_usuarios_adendos
        resumo["total_usuarios"] = total_usuarios_contratos + total_usuarios_adendos
        return resumo

    @staticmethod
    def _combinar_agrupamento_dashboard(contratos, adendos):
        por_nome = {}
        for item in contratos or []:
            nome = item.get("nome") or "Sem dados"
            por_nome[nome] = {
                "nome": nome,
                "total_contratos": item.get("total_contratos") or 0,
                "total_adendos": 0,
                "total_recorrencia_contratos": item.get("total_recorrencia") or 0,
                "total_recorrencia_adendos": 0,
            }
        for item in adendos or []:
            nome = item.get("nome") or "Sem dados"
            atual = por_nome.setdefault(nome, {
                "nome": nome,
                "total_contratos": 0,
                "total_adendos": 0,
                "total_recorrencia_contratos": 0,
                "total_recorrencia_adendos": 0,
            })
            atual["total_adendos"] += item.get("total_adendos") or 0
            atual["total_recorrencia_adendos"] += item.get("total_recorrencia_adendos") or 0
        for item in por_nome.values():
            item["total_itens_contratos"] = item["total_contratos"] + item["total_adendos"]
            item["total_recorrencia"] = item["total_recorrencia_contratos"] + item["total_recorrencia_adendos"]
        return sorted(por_nome.values(), key=lambda item: (-item["total_recorrencia"], -item["total_itens_contratos"], item["nome"]))

    @staticmethod
    def _agrupar(cursor, joins, where_sql, parametros, campo_nome):
        cursor.execute(
            f"""
            SELECT
                {campo_nome} AS nome,
                COUNT(*) AS total_contratos,
                COALESCE(SUM(COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)), 0) AS total_recorrencia
            {joins}
            {where_sql}
            GROUP BY nome
            ORDER BY total_recorrencia DESC, total_contratos DESC, nome
            """,
            tuple(parametros),
        )
        return cursor.fetchall()

    @staticmethod
    def _agrupar_adendos(cursor, joins, where_sql, parametros, campo_nome):
        cursor.execute(
            f"""
            SELECT
                {campo_nome} AS nome,
                COUNT(*) AS total_adendos,
                COALESCE(SUM(COALESCE(a.valor_recorrente, 0)), 0) AS total_recorrencia_adendos
            {joins}
            {where_sql}
            GROUP BY nome
            ORDER BY total_recorrencia_adendos DESC, total_adendos DESC, nome
            """,
            tuple(parametros),
        )
        return cursor.fetchall()

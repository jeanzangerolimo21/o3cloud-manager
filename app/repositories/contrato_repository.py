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

        executivos = cls._agrupar(cursor, joins, where_sql, parametros, "COALESCE(exec.nome, 'Sem executivo')")
        parceiros = cls._agrupar(cursor, joins, where_sql, parametros, "COALESCE(p.nome, 'Sem parceiro')")

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
                uuid, cliente_id, codigo_externo, origem, numero, descricao, status,
                inicio_vigencia, fim_vigencia, observacoes, ativo, synced_at,
                valor_mensal, dia_faturamento, tipo_faturamento, codigo_vendedor,
                vendedor_nome, codigo_projeto, projeto_nome, codigo_cc,
                observacao_contrato, valor_servicos_bruto, valor_descontos, valor_servicos_liquido
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(),
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                uuid,
                dados.get("cliente_id"),
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
    def atualizar_arquivo_assinado(cls, contrato_id, arquivo, arquivo_original, assinado_em=None):
        conn = cls.connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contratos
            SET arquivo_assinado=%s,
                arquivo_assinado_original=%s,
                clicksign_status='ASSINADO',
                clicksign_assinado_em=COALESCE(%s, NOW())
            WHERE id=%s AND ativo=1
            """,
            (arquivo, arquivo_original, assinado_em, contrato_id),
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

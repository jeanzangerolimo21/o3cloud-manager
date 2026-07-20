from app.repositories.base_repository import BaseRepository


class PropostaRepository(BaseRepository):
    TABLE = "crm_propostas"

    @classmethod
    def total(cls, pesquisa=None, status=None, ativo=None, clicksign_status=None):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE} p
            LEFT JOIN crm_oportunidades o ON o.id = p.oportunidade_id
            WHERE 1 = 1
        """
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                COALESCE(p.codigo_proposta, '') LIKE %s
                OR COALESCE(p.titulo, '') LIKE %s
                OR COALESCE(p.cliente_nome, '') LIKE %s
                OR COALESCE(p.contato_nome, '') LIKE %s
                OR COALESCE(p.executivo_nome, '') LIKE %s
                OR COALESCE(o.titulo, '') LIKE %s
            )
            """
            params.extend([termo] * 6)
        if status:
            sql += "\n  AND p.status = %s"
            params.append(status)
        if ativo in (0, 1):
            sql += "\n  AND p.ativo = %s"
            params.append(ativo)
        if clicksign_status:
            sql += "\n  AND p.clicksign_status = %s"
            params.append(clicksign_status)
        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, status=None, ativo=None, clicksign_status=None, limit=50, offset=0):
        sql = f"""
            SELECT
                p.id,
                p.uuid,
                p.oportunidade_id,
                p.cliente_id,
                p.contato_id,
                p.executivo_responsavel_id,
                p.codigo_proposta,
                p.titulo,
                p.versao,
                p.status,
                p.validade,
                p.valor_total,
                p.total_mensal,
                p.total_instalacao,
                p.ativo,
                p.clicksign_status,
                p.created_at,
                p.updated_at,
                p.cliente_nome,
                p.executivo_nome,
                o.titulo AS oportunidade_titulo
            FROM {cls.TABLE} p
            LEFT JOIN crm_oportunidades o ON o.id = p.oportunidade_id
            WHERE 1 = 1
        """
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                COALESCE(p.codigo_proposta, '') LIKE %s
                OR COALESCE(p.titulo, '') LIKE %s
                OR COALESCE(p.cliente_nome, '') LIKE %s
                OR COALESCE(p.contato_nome, '') LIKE %s
                OR COALESCE(p.executivo_nome, '') LIKE %s
                OR COALESCE(o.titulo, '') LIKE %s
            )
            """
            params.extend([termo] * 6)
        if status:
            sql += "\n  AND p.status = %s"
            params.append(status)
        if ativo in (0, 1):
            sql += "\n  AND p.ativo = %s"
            params.append(ativo)
        if clicksign_status:
            sql += "\n  AND p.clicksign_status = %s"
            params.append(clicksign_status)
        sql += """
            ORDER BY p.updated_at DESC, p.versao DESC, p.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def buscar_por_id(cls, proposta_id):
        sql = f"""
            SELECT p.*, o.titulo AS oportunidade_titulo, o.empresa AS oportunidade_empresa
            FROM {cls.TABLE} p
            LEFT JOIN crm_oportunidades o ON o.id = p.oportunidade_id
            WHERE p.id = %s
        """
        return cls.fetch_one(sql, (proposta_id,))

    @classmethod
    def proxima_versao(cls, oportunidade_id):
        if not oportunidade_id:
            return (cls.scalar(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {cls.TABLE}") or 1)
        return cls.scalar(f"SELECT COALESCE(MAX(versao), 0) + 1 FROM {cls.TABLE} WHERE oportunidade_id = %s", (oportunidade_id,)) or 1

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid, oportunidade_id, cliente_id, contato_id, parceiro_id, executivo_responsavel_id,
                codigo_proposta, cliente_nome, contato_nome, contato_email, contato_telefone,
                executivo_nome, executivo_email, executivo_telefone, titulo, versao, status, validade,
                setup_dias, mensalidade_dias, prazo_contratual_meses, detalhes_negociacao,
                valor_total, total_mensal, parametrizacao_sistema, setup_ambiente_cloud, total_instalacao,
                condicoes_comerciais, observacoes, itens_snapshot, licencas_snapshot, servidores_snapshot,
                arquivo, ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        return cls.execute_insert(sql, (
            cls.generate_uuid(), dados.get('oportunidade_id'), dados.get('cliente_id'), dados.get('contato_id'), dados.get('parceiro_id'), dados.get('executivo_responsavel_id'),
            dados.get('codigo_proposta'), dados.get('cliente_nome'), dados.get('contato_nome'), dados.get('contato_email'), dados.get('contato_telefone'),
            dados.get('executivo_nome'), dados.get('executivo_email'), dados.get('executivo_telefone'), dados['titulo'], dados['versao'], dados['status'], dados.get('validade'),
            dados.get('setup_dias'), dados.get('mensalidade_dias'), dados.get('prazo_contratual_meses'), dados.get('detalhes_negociacao'),
            dados.get('valor_total'), dados.get('total_mensal'), dados.get('parametrizacao_sistema'), dados.get('setup_ambiente_cloud'), dados.get('total_instalacao'),
            dados.get('condicoes_comerciais'), dados.get('observacoes'), dados.get('itens_snapshot'), dados.get('licencas_snapshot'), dados.get('servidores_snapshot'),
            dados.get('arquivo'), cls.bool_to_int(dados.get('ativo', True)),
        ))

    @classmethod
    def atualizar(cls, proposta_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET oportunidade_id = %s,
                cliente_id = %s,
                contato_id = %s,
                parceiro_id = %s,
                executivo_responsavel_id = %s,
                codigo_proposta = %s,
                cliente_nome = %s,
                contato_nome = %s,
                contato_email = %s,
                contato_telefone = %s,
                executivo_nome = %s,
                executivo_email = %s,
                executivo_telefone = %s,
                titulo = %s,
                versao = %s,
                status = %s,
                validade = %s,
                setup_dias = %s,
                mensalidade_dias = %s,
                prazo_contratual_meses = %s,
                detalhes_negociacao = %s,
                valor_total = %s,
                total_mensal = %s,
                parametrizacao_sistema = %s,
                setup_ambiente_cloud = %s,
                total_instalacao = %s,
                condicoes_comerciais = %s,
                observacoes = %s,
                itens_snapshot = %s,
                licencas_snapshot = %s,
                servidores_snapshot = %s,
                arquivo = %s,
                ativo = %s
            WHERE id = %s
        """
        return cls.execute(sql, (
            dados.get('oportunidade_id'), dados.get('cliente_id'), dados.get('contato_id'), dados.get('parceiro_id'), dados.get('executivo_responsavel_id'),
            dados.get('codigo_proposta'), dados.get('cliente_nome'), dados.get('contato_nome'), dados.get('contato_email'), dados.get('contato_telefone'),
            dados.get('executivo_nome'), dados.get('executivo_email'), dados.get('executivo_telefone'), dados['titulo'], dados['versao'], dados['status'], dados.get('validade'),
            dados.get('setup_dias'), dados.get('mensalidade_dias'), dados.get('prazo_contratual_meses'), dados.get('detalhes_negociacao'),
            dados.get('valor_total'), dados.get('total_mensal'), dados.get('parametrizacao_sistema'), dados.get('setup_ambiente_cloud'), dados.get('total_instalacao'),
            dados.get('condicoes_comerciais'), dados.get('observacoes'), dados.get('itens_snapshot'), dados.get('licencas_snapshot'), dados.get('servidores_snapshot'),
            dados.get('arquivo'), cls.bool_to_int(dados.get('ativo', True)), proposta_id,
        ))

    @classmethod
    def excluir(cls, proposta_id):
        return cls.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", (proposta_id,))

    @classmethod
    def listar_clicksign_pendentes(cls):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT id, codigo_proposta, clicksign_status, clicksign_envelope_id
            FROM {cls.TABLE}
            WHERE ativo = 1
              AND clicksign_envelope_id IS NOT NULL
              AND clicksign_envelope_id <> ''
              AND clicksign_status IN ('ENVIADO', 'AGUARDANDO_ASSINATURAS')
            ORDER BY clicksign_sent_at ASC, id ASC
            """
        )
        propostas = cursor.fetchall()
        cls.close(conn, cursor)
        return propostas

    @classmethod
    def atualizar_clicksign(cls, proposta_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET clicksign_status = %s,
                clicksign_document_key = COALESCE(%s, clicksign_document_key),
                clicksign_document_url = COALESCE(%s, clicksign_document_url),
                clicksign_envelope_id = COALESCE(%s, clicksign_envelope_id),
                clicksign_sent_at = COALESCE(%s, clicksign_sent_at),
                clicksign_signed_at = COALESCE(%s, clicksign_signed_at),
                clicksign_completed_at = COALESCE(%s, clicksign_completed_at),
                clicksign_last_sync_at = %s,
                clicksign_eventos = %s
            WHERE id = %s
        """
        return cls.execute(sql, (
            dados.get('clicksign_status'),
            dados.get('clicksign_document_key'),
            dados.get('clicksign_document_url'),
            dados.get('clicksign_envelope_id'),
            dados.get('clicksign_sent_at'),
            dados.get('clicksign_signed_at'),
            dados.get('clicksign_completed_at'),
            dados.get('clicksign_last_sync_at'),
            dados.get('clicksign_eventos'),
            proposta_id,
        ))

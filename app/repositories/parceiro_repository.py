from app.repositories.base_repository import BaseRepository


class ParceiroRepository(BaseRepository):

    @classmethod
    def total(cls, pesquisa=None, status_negociacao=None, ativo=None, executivo_id=None):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT COUNT(*) AS total
            FROM parceiros p
        """

        parametros = []

        if pesquisa:
            sql += """
                WHERE
                    (
                    nome LIKE %s
                    OR sigla LIKE %s
                    OR razao_social LIKE %s
                    OR nome_fantasia LIKE %s
                    OR contato_1_nome LIKE %s
                    OR contato_1_telefone LIKE %s
                    OR cnpj LIKE %s
                    OR REGEXP_REPLACE(cnpj, '[^0-9A-Za-z]', '') LIKE %s
                    OR status_negociacao LIKE %s
                    )
            """

            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            parametros.extend([termo, termo, termo, termo, termo, termo, termo, termo_cnpj, termo])

        if status_negociacao:
            sql += " WHERE" if not pesquisa else " AND"
            sql += " status_negociacao = %s"
            parametros.append(status_negociacao)

        if ativo in (0, 1):
            sql += " WHERE" if not pesquisa and not status_negociacao else " AND"
            sql += " ativo = %s"
            parametros.append(ativo)

        if executivo_id:
            sql += " WHERE" if not pesquisa and not status_negociacao and ativo not in (0, 1) else " AND"
            sql += " EXISTS (SELECT 1 FROM parceiros_executivos pe WHERE pe.parceiro_id = p.id AND pe.id = %s)"
            parametros.append(executivo_id)

        cursor.execute(sql, tuple(parametros))
        total = cursor.fetchone()["total"]
        cls.close(conn, cursor)
        return total

    @classmethod
    def listar(cls, pesquisa=None, status_negociacao=None, ativo=None, executivo_id=None, limit=50, offset=0):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                id,
                uuid,
                nome,
                sigla,
                tipo,
                COALESCE(nome_fantasia, nome, razao_social) AS nome_exibicao,
                COALESCE(contato_1_nome, contato) AS contato_exibicao,
                COALESCE(contato_1_telefone, telefone) AS telefone_exibicao,
                email,
                telefone,
                ativo,
                premiacao_ativa,
                COALESCE(status_negociacao, 'PRIMEIRO_CONTATO') AS status_negociacao,
                categoria_parceiro
            FROM parceiros p
        """

        parametros = []
        condicoes = []

        if pesquisa:
            condicoes.append("""
                (
                    nome LIKE %s
                    OR sigla LIKE %s
                    OR razao_social LIKE %s
                    OR nome_fantasia LIKE %s
                    OR contato_1_nome LIKE %s
                    OR contato_1_telefone LIKE %s
                    OR cnpj LIKE %s
                    OR REGEXP_REPLACE(cnpj, '[^0-9A-Za-z]', '') LIKE %s
                    OR status_negociacao LIKE %s
                )
            """)
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            parametros.extend([termo, termo, termo, termo, termo, termo, termo, termo_cnpj, termo])

        if status_negociacao:
            condicoes.append("status_negociacao = %s")
            parametros.append(status_negociacao)

        if ativo in (0, 1):
            condicoes.append("ativo = %s")
            parametros.append(ativo)

        if executivo_id:
            condicoes.append("EXISTS (SELECT 1 FROM parceiros_executivos pe WHERE pe.parceiro_id = p.id AND pe.id = %s)")
            parametros.append(executivo_id)

        if condicoes:
            sql += " WHERE "
            sql += " AND ".join(condicoes)
        sql += """
            ORDER BY COALESCE(nome_fantasia, nome, razao_social), nome
            LIMIT %s OFFSET %s
        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))
        parceiros = cursor.fetchall()
        cls.close(conn, cursor)
        return parceiros

    @classmethod
    def listar_todos_ativos(cls):
        sql = """
            SELECT
                id,
                nome,
                sigla,
                premiacao_ativa,
                COALESCE(nome_fantasia, nome, razao_social) AS nome_exibicao
            FROM parceiros
            WHERE ativo = 1
            ORDER BY COALESCE(nome_fantasia, nome, razao_social), nome
        """
        return cls.fetch_all(sql)

    @classmethod
    def buscar_por_id(cls, parceiro_id):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.id,
                p.uuid,
                p.nome,
                p.sigla,
                p.tipo,
                p.contato,
                p.email,
                p.telefone,
                p.site,
                p.logo,
                p.descricao,
                p.ativo,
                p.created_at,
                p.updated_at,
                p.cnpj,
                p.segmento,
                p.categoria_parceiro,
                p.razao_social,
                p.nome_fantasia,
                p.endereco,
                p.cidade,
                p.uf,
                p.contato_1_nome,
                p.contato_1_email,
                p.contato_1_telefone,
                p.contato_2_nome,
                p.contato_2_email,
                p.contato_2_telefone,
                p.contato_3_nome,
                p.contato_3_email,
                p.contato_3_telefone,
                p.executivo_responsavel_id,
                p.status_negociacao,
                p.informacoes_gerais,
                p.premiacao_ativa,
                pe.nome AS executivo_responsavel_nome
            FROM parceiros p
            LEFT JOIN parceiros_executivos pe
                ON pe.id = p.executivo_responsavel_id
            WHERE p.id = %s
        """, (parceiro_id,))

        parceiro = cursor.fetchone()
        cls.close(conn, cursor)
        return parceiro

    @classmethod
    def inserir(cls, dados):
        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parceiros (
                uuid,
                nome,
                sigla,
                tipo,
                contato,
                email,
                telefone,
                site,
                logo,
                descricao,
                ativo,
                cnpj,
                segmento,
                categoria_parceiro,
                razao_social,
                nome_fantasia,
                endereco,
                cidade,
                uf,
                contato_1_nome,
                contato_1_email,
                contato_1_telefone,
                contato_2_nome,
                contato_2_email,
                contato_2_telefone,
                contato_3_nome,
                contato_3_email,
                contato_3_telefone,
                executivo_responsavel_id,
                status_negociacao,
                informacoes_gerais,
                premiacao_ativa
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
            )
        """, (
            cls.generate_uuid(),
            dados["nome"],
            dados["sigla"],
            dados["tipo"],
            dados["contato"],
            dados["email"],
            dados["telefone"],
            dados["site"],
            dados["logo"],
            dados["descricao"],
            dados["ativo"],
            dados.get("cnpj"),
            dados.get("segmento"),
            dados.get("categoria_parceiro"),
            dados.get("razao_social"),
            dados.get("nome_fantasia"),
            dados.get("endereco"),
            dados.get("cidade"),
            dados.get("uf"),
            dados.get("contato_1_nome"),
            dados.get("contato_1_email"),
            dados.get("contato_1_telefone"),
            dados.get("contato_2_nome"),
            dados.get("contato_2_email"),
            dados.get("contato_2_telefone"),
            dados.get("contato_3_nome"),
            dados.get("contato_3_email"),
            dados.get("contato_3_telefone"),
            dados.get("executivo_responsavel_id"),
            dados.get("status_negociacao"),
            dados.get("informacoes_gerais"),
            cls.bool_to_int(dados.get("premiacao_ativa", False)),
        ))

        conn.commit()
        novo_id = cursor.lastrowid
        cls.close(conn, cursor)
        return novo_id

    @classmethod
    def atualizar(cls, parceiro_id, dados):
        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE parceiros
            SET nome = %s,
                sigla = %s,
                tipo = %s,
                contato = %s,
                email = %s,
                telefone = %s,
                site = %s,
                logo = %s,
                descricao = %s,
                ativo = %s,
                cnpj = %s,
                segmento = %s,
                categoria_parceiro = %s,
                razao_social = %s,
                nome_fantasia = %s,
                endereco = %s,
                cidade = %s,
                uf = %s,
                contato_1_nome = %s,
                contato_1_email = %s,
                contato_1_telefone = %s,
                contato_2_nome = %s,
                contato_2_email = %s,
                contato_2_telefone = %s,
                contato_3_nome = %s,
                contato_3_email = %s,
                contato_3_telefone = %s,
                executivo_responsavel_id = %s,
                status_negociacao = %s,
                informacoes_gerais = %s,
                premiacao_ativa = %s
            WHERE id = %s
        """, (
            dados["nome"],
            dados["sigla"],
            dados["tipo"],
            dados["contato"],
            dados["email"],
            dados["telefone"],
            dados["site"],
            dados["logo"],
            dados["descricao"],
            dados["ativo"],
            dados.get("cnpj"),
            dados.get("segmento"),
            dados.get("categoria_parceiro"),
            dados.get("razao_social"),
            dados.get("nome_fantasia"),
            dados.get("endereco"),
            dados.get("cidade"),
            dados.get("uf"),
            dados.get("contato_1_nome"),
            dados.get("contato_1_email"),
            dados.get("contato_1_telefone"),
            dados.get("contato_2_nome"),
            dados.get("contato_2_email"),
            dados.get("contato_2_telefone"),
            dados.get("contato_3_nome"),
            dados.get("contato_3_email"),
            dados.get("contato_3_telefone"),
            dados.get("executivo_responsavel_id"),
            dados.get("status_negociacao"),
            dados.get("informacoes_gerais"),
            cls.bool_to_int(dados.get("premiacao_ativa", False)),
            parceiro_id,
        ))

        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def excluir(cls, parceiro_id):
        sql = """
            DELETE FROM parceiros
            WHERE id = %s
        """
        return cls.execute(sql, (parceiro_id,))

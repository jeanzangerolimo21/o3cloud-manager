from app.repositories.base_repository import BaseRepository


class ReajusteContratoRepository(BaseRepository):
    @classmethod
    def configuracao(cls):
        return cls.fetch_one("SELECT * FROM reajustes_configuracoes WHERE chave='PADRAO' LIMIT 1") or {}

    @classmethod
    def salvar_configuracao(cls, dados):
        config = cls.configuracao()
        config_id = config.get("id")
        if not config_id:
            config_id = cls.execute_insert(
                """
                INSERT INTO reajustes_configuracoes (uuid, chave, alerta_30_dias, alerta_15_dias, alerta_7_dias, enviar_email, ativo, updated_by)
                VALUES (%s, 'PADRAO', %s, %s, %s, %s, %s, %s)
                """,
                (
                    cls.generate_uuid(), dados.get("alerta_30_dias"), dados.get("alerta_15_dias"),
                    dados.get("alerta_7_dias"), dados.get("enviar_email"), dados.get("ativo"), dados.get("updated_by"),
                ),
            )
        else:
            cls.execute(
                """
                UPDATE reajustes_configuracoes
                SET alerta_30_dias=%s, alerta_15_dias=%s, alerta_7_dias=%s,
                    enviar_email=%s, ativo=%s, updated_by=%s
                WHERE id=%s
                """,
                (
                    dados.get("alerta_30_dias"), dados.get("alerta_15_dias"), dados.get("alerta_7_dias"),
                    dados.get("enviar_email"), dados.get("ativo"), dados.get("updated_by"), config_id,
                ),
            )
        return config_id

    @classmethod
    def substituir_usuarios_configuracao(cls, config_id, usuario_ids):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reajustes_configuracoes_usuarios WHERE configuracao_id=%s", (config_id,))
            valores = [(cls.generate_uuid(), config_id, usuario_id, 1, 1) for usuario_id in usuario_ids]
            if valores:
                cursor.executemany(
                    """
                    INSERT INTO reajustes_configuracoes_usuarios (uuid, configuracao_id, usuario_id, receber_notificacao, receber_email)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    valores,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def usuarios_notificacao(cls, config_id=None):
        params = []
        where_config = ""
        if config_id:
            where_config = "AND cu.configuracao_id=%s"
            params.append(config_id)
        return cls.fetch_all(
            f"""
            SELECT u.id, u.nome, u.email, cu.receber_notificacao, cu.receber_email
            FROM reajustes_configuracoes_usuarios cu
            INNER JOIN auth_usuarios u ON u.id = cu.usuario_id
            WHERE u.status='ATIVO'
              AND u.email IS NOT NULL
              AND u.email <> ''
              {where_config}
            ORDER BY u.nome
            """,
            tuple(params),
        )

    @classmethod
    def usuarios_disponiveis(cls):
        return cls.fetch_all(
            """
            SELECT id, nome, email
            FROM auth_usuarios
            WHERE status='ATIVO'
            ORDER BY nome
            """
        )

    @classmethod
    def listar_contratos_monitoramento(cls, filtros=None, limit=500):
        filtros = filtros or {}
        where = ["c.ativo=1"]
        params = []
        q = filtros.get("q")
        if q:
            like = f"%{q}%"
            where.append("(c.numero LIKE %s OR cli.nome_fantasia LIKE %s OR cli.razao_social LIKE %s OR COALESCE(c.vendedor_nome, '') LIKE %s OR COALESCE(c.projeto_nome, '') LIKE %s)")
            params.extend([like, like, like, like, like])
        if filtros.get("status"):
            where.append("c.status=%s")
            params.append(filtros.get("status"))
        if filtros.get("vendedor"):
            where.append("COALESCE(c.vendedor_nome, c.codigo_vendedor, '') LIKE %s")
            params.append(f"%{filtros.get('vendedor')}%")
        sql = f"""
            SELECT c.id, c.numero, c.status, c.origem, c.inicio_vigencia, c.fim_vigencia,
                   c.valor_mensal, c.valor_servicos_bruto, c.valor_descontos, c.valor_servicos_liquido,
                   c.vendedor_nome, c.codigo_vendedor, c.projeto_nome, c.codigo_projeto,
                   cli.nome_fantasia AS cliente_nome, cli.razao_social AS cliente_razao_social
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE {' AND '.join(where)}
            ORDER BY c.inicio_vigencia IS NULL ASC, c.inicio_vigencia ASC, c.id DESC
            LIMIT %s
        """
        params.append(limit)
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def historico_contrato(cls, contrato_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM contratos_valores_historico
            WHERE contrato_id=%s
            ORDER BY detectado_em ASC, id ASC
            """,
            (contrato_id,),
        )

    @classmethod
    def ultimo_historico(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT *
            FROM contratos_valores_historico
            WHERE contrato_id=%s
            ORDER BY detectado_em DESC, id DESC
            LIMIT 1
            """,
            (contrato_id,),
        )

    @classmethod
    def inserir_historico(cls, contrato_id, dados, origem="SISTEMA"):
        return cls.execute_insert(
            """
            INSERT INTO contratos_valores_historico (
                uuid, contrato_id, valor_mensal, valor_servicos_bruto, valor_descontos,
                valor_servicos_liquido, vigencia_referencia, origem
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), contrato_id, dados.get("valor_mensal"), dados.get("valor_servicos_bruto"),
                dados.get("valor_descontos"), dados.get("valor_servicos_liquido"), dados.get("inicio_vigencia"), origem,
            ),
        )

    @classmethod
    def alerta_existente(cls, contrato_id, aniversario, antecedencia):
        return cls.fetch_one(
            """
            SELECT * FROM contratos_reajustes_alertas
            WHERE contrato_id=%s AND aniversario_referencia=%s AND antecedencia_dias=%s
            """,
            (contrato_id, aniversario, antecedencia),
        )

    @classmethod
    def inserir_alerta(cls, contrato_id, aniversario, antecedencia, status, exibido=True):
        return cls.execute_insert(
            """
            INSERT INTO contratos_reajustes_alertas (uuid, contrato_id, aniversario_referencia, antecedencia_dias, status, exibido_em)
            VALUES (%s, %s, %s, %s, %s, IF(%s=1, NOW(), NULL))
            ON DUPLICATE KEY UPDATE status=VALUES(status)
            """,
            (cls.generate_uuid(), contrato_id, aniversario, antecedencia, status, 1 if exibido else 0),
        )

    @classmethod
    def marcar_email_alerta(cls, contrato_id, aniversario, antecedencia):
        return cls.execute(
            """
            UPDATE contratos_reajustes_alertas
            SET email_enviado_em=COALESCE(email_enviado_em, NOW())
            WHERE contrato_id=%s AND aniversario_referencia=%s AND antecedencia_dias=%s
            """,
            (contrato_id, aniversario, antecedencia),
        )

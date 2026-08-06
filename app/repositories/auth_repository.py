from app.repositories.base_repository import BaseRepository


class AuthRepository(BaseRepository):
    @classmethod
    def listar_perfis(cls):
        return cls.fetch_all(
            """
            SELECT id, uuid, nome, codigo, descricao, ativo, mostrar_valores
            FROM auth_perfis
            WHERE ativo = 1
            ORDER BY codigo = \"ADMIN\" DESC, nome ASC
            """
        )

    @classmethod
    def buscar_perfil(cls, perfil_id):
        return cls.fetch_one(
            """
            SELECT id, uuid, nome, codigo, descricao, ativo, mostrar_valores
            FROM auth_perfis
            WHERE id = %s
            """,
            (perfil_id,),
        )

    @classmethod
    def buscar_perfil_por_codigo(cls, codigo):
        return cls.fetch_one(
            """
            SELECT id, uuid, nome, codigo, descricao, ativo, mostrar_valores
            FROM auth_perfis
            WHERE codigo = %s
            """,
            (codigo,),
        )

    @classmethod
    def contar_admins_ativos(cls):
        return cls.scalar(
            """
            SELECT COUNT(*)
            FROM auth_usuarios u
            INNER JOIN auth_perfis p ON p.id = u.perfil_id
            WHERE p.codigo = "ADMIN" AND u.status = "ATIVO"
            """
        ) or 0

    @classmethod
    def inserir_perfil(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_perfis (uuid, nome, codigo, descricao, ativo, mostrar_valores)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("nome"), dados.get("codigo"), dados.get("descricao"),
                cls.bool_to_int(dados.get("ativo")), cls.bool_to_int(dados.get("mostrar_valores")),
            ),
        )

    @classmethod
    def atualizar_perfil(cls, perfil_id, dados):
        return cls.execute(
            """
            UPDATE auth_perfis
            SET nome=%s, codigo=%s, descricao=%s, ativo=%s, mostrar_valores=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("codigo"), dados.get("descricao"),
                cls.bool_to_int(dados.get("ativo")), cls.bool_to_int(dados.get("mostrar_valores")), perfil_id,
            ),
        )

    @classmethod
    def listar_permissoes_perfil(cls, perfil_id):
        return cls.fetch_all(
            """
            SELECT perfil_id, menu_key, permitido, nivel_acesso
            FROM auth_perfil_permissoes
            WHERE perfil_id = %s
            ORDER BY menu_key ASC
            """,
            (perfil_id,),
        )

    @classmethod
    def substituir_permissoes_perfil(cls, perfil_id, permissoes):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM auth_perfil_permissoes WHERE perfil_id = %s", (perfil_id,))
            if isinstance(permissoes, dict):
                valores = [(perfil_id, menu_key, nivel, 1) for menu_key, nivel in permissoes.items()]
            else:
                valores = [(perfil_id, menu_key, "EDICAO", 1) for menu_key in permissoes]
            if valores:
                cursor.executemany(
                    """
                    INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, nivel_acesso, permitido)
                    VALUES (%s, %s, %s, %s)
                    """,
                    valores,
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def listar_usuarios(cls):
        return cls.fetch_all(
            """
            SELECT u.id, u.uuid, u.nome, u.email, u.login, u.origem, u.status,
                   u.externo_id, u.ultimo_login_em, u.ultima_sincronizacao_em,
                   u.created_at, u.updated_at, p.nome AS perfil_nome, p.codigo AS perfil_codigo,
                   c.status AS convite_status, c.expira_em AS convite_expira_em, c.enviado_em AS convite_enviado_em
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id = u.perfil_id
            LEFT JOIN auth_convites c ON c.id = (
                SELECT c2.id FROM auth_convites c2
                WHERE c2.usuario_id = u.id
                ORDER BY c2.created_at DESC, c2.id DESC
                LIMIT 1
            )
            ORDER BY u.status ASC, u.nome ASC, u.id ASC
            """
        )

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return cls.fetch_one(
            """
            SELECT u.*, p.nome AS perfil_nome, p.codigo AS perfil_codigo
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id = u.perfil_id
            WHERE u.id = %s
            """,
            (usuario_id,),
        )

    @classmethod
    def buscar_usuario_por_email(cls, email):
        return cls.fetch_one("SELECT * FROM auth_usuarios WHERE email = %s", (email,))

    @classmethod
    def buscar_usuario_por_login(cls, identificador):
        return cls.fetch_one(
            """
            SELECT u.*, p.nome AS perfil_nome, p.codigo AS perfil_codigo, p.mostrar_valores
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id = u.perfil_id
            WHERE u.email = %s OR u.login = %s
            LIMIT 1
            """,
            (identificador, identificador),
        )

    @classmethod
    def buscar_usuario_por_email_ou_login(cls, identificador):
        return cls.fetch_one(
            """
            SELECT u.*, p.nome AS perfil_nome, p.codigo AS perfil_codigo, p.mostrar_valores
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id = u.perfil_id
            WHERE u.email = %s OR u.login = %s
            LIMIT 1
            """,
            (identificador, identificador),
        )

    @classmethod
    def buscar_usuario_por_email_com_perfil(cls, email):
        return cls.fetch_one(
            """
            SELECT u.*, p.nome AS perfil_nome, p.codigo AS perfil_codigo, p.mostrar_valores
            FROM auth_usuarios u
            LEFT JOIN auth_perfis p ON p.id = u.perfil_id
            WHERE u.email = %s
            """,
            (email,),
        )

    @classmethod
    def listar_menu_keys_usuario(cls, email):
        return cls.fetch_all(
            """
            SELECT pp.menu_key, pp.nivel_acesso
            FROM auth_usuarios u
            INNER JOIN auth_perfis p ON p.id = u.perfil_id
            INNER JOIN auth_perfil_permissoes pp ON pp.perfil_id = p.id
            WHERE u.email = %s
              AND u.status = "ATIVO"
              AND p.ativo = 1
              AND pp.permitido = 1
            ORDER BY pp.menu_key ASC
            """,
            (email,),
        )

    @classmethod
    def inserir_usuario(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_usuarios (
                uuid, nome, email, login, origem, perfil_id, status,
                externo_id, senha_hash, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("nome"), dados.get("email"), dados.get("login"),
                dados.get("origem"), dados.get("perfil_id"), dados.get("status"),
                dados.get("externo_id"), dados.get("senha_hash"), dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar_usuario(cls, usuario_id, dados):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET nome=%s, email=%s, login=%s, origem=%s, perfil_id=%s,
                status=%s, externo_id=%s, updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("email"), dados.get("login"), dados.get("origem"),
                dados.get("perfil_id"), dados.get("status"), dados.get("externo_id"),
                dados.get("updated_by"), usuario_id,
            ),
        )

    @classmethod
    def atualizar_minha_conta(cls, usuario_id, dados):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET nome=%s, email=%s, login=%s, foto=COALESCE(%s, foto), updated_by=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("email"), dados.get("login"),
                dados.get("foto"), dados.get("updated_by"), usuario_id,
            ),
        )

    @classmethod
    def atualizar_senha_usuario(cls, usuario_id, senha_hash, atualizado_por=None):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET senha_hash=%s, updated_by=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (senha_hash, atualizado_por, usuario_id),
        )

    @classmethod
    def definir_senha(cls, usuario_id, senha_hash):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET senha_hash=%s, status=\"ATIVO\", updated_at=NOW()
            WHERE id=%s
            """,
            (senha_hash, usuario_id),
        )

    @classmethod
    def promover_admin_local(cls, usuario_id, perfil_id, senha_hash, atualizado_por="bootstrap"):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET origem="LOCAL", perfil_id=%s, status="ATIVO", senha_hash=%s,
                updated_by=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (perfil_id, senha_hash, atualizado_por, usuario_id),
        )

    @classmethod
    def registrar_login_usuario(cls, usuario_id):
        return cls.execute(
            "UPDATE auth_usuarios SET ultimo_login_em=NOW(), updated_at=NOW() WHERE id=%s",
            (usuario_id,),
        )

    @classmethod
    def inserir_convite(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_convites (
                uuid, usuario_id, token_hash, email, status, expira_em, enviado_em, created_by
            ) VALUES (%s, %s, %s, %s, \"PENDENTE\", %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("usuario_id"), dados.get("token_hash"), dados.get("email"),
                dados.get("expira_em"), dados.get("enviado_em"), dados.get("created_by"),
            ),
        )

    @classmethod
    def expirar_convites_usuario(cls, usuario_id):
        return cls.execute(
            """
            UPDATE auth_convites
            SET status=\"EXPIRADO\"
            WHERE usuario_id=%s AND status=\"PENDENTE\"
            """,
            (usuario_id,),
        )

    @classmethod
    def buscar_convite_por_hash(cls, token_hash):
        return cls.fetch_one(
            """
            SELECT c.*, u.nome AS usuario_nome, u.email AS usuario_email, u.status AS usuario_status
            FROM auth_convites c
            INNER JOIN auth_usuarios u ON u.id = c.usuario_id
            WHERE c.token_hash = %s
            """,
            (token_hash,),
        )

    @classmethod
    def marcar_convite_usado(cls, convite_id):
        return cls.execute("UPDATE auth_convites SET status=\"USADO\", usado_em=NOW() WHERE id=%s", (convite_id,))

    @classmethod
    def listar_provedores(cls):
        return cls.fetch_all(
            """
            SELECT id, uuid, nome, tipo, host, porta, dominio, base_dn, bind_dn,
                   usar_tls, usar_starttls, ativo, ultimo_teste_status,
                   ultimo_teste_mensagem, ultimo_teste_em, updated_at
            FROM auth_provedores
            ORDER BY ativo DESC, tipo ASC, nome ASC
            """
        )

    @classmethod
    def buscar_provedor(cls, provedor_id):
        return cls.fetch_one("SELECT * FROM auth_provedores WHERE id=%s", (provedor_id,))

    @classmethod
    def inserir_provedor(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_provedores (
                uuid, nome, tipo, host, porta, dominio, base_dn, bind_dn,
                bind_password_encrypted, usar_tls, usar_starttls, filtro_usuarios,
                filtro_grupos, atributo_login, atributo_email, atributo_nome,
                upn_suffix, ativo, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            cls._provedor_params(dados, incluir_auditoria=True),
        )

    @classmethod
    def atualizar_provedor(cls, provedor_id, dados):
        return cls.execute(
            """
            UPDATE auth_provedores
            SET nome=%s, tipo=%s, host=%s, porta=%s, dominio=%s, base_dn=%s,
                bind_dn=%s, bind_password_encrypted=COALESCE(%s, bind_password_encrypted),
                usar_tls=%s, usar_starttls=%s, filtro_usuarios=%s, filtro_grupos=%s,
                atributo_login=%s, atributo_email=%s, atributo_nome=%s, upn_suffix=%s,
                ativo=%s, updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("tipo"), dados.get("host"), dados.get("porta"),
                dados.get("dominio"), dados.get("base_dn"), dados.get("bind_dn"),
                dados.get("bind_password_encrypted"), cls.bool_to_int(dados.get("usar_tls")),
                cls.bool_to_int(dados.get("usar_starttls")), dados.get("filtro_usuarios"),
                dados.get("filtro_grupos"), dados.get("atributo_login"), dados.get("atributo_email"),
                dados.get("atributo_nome"), dados.get("upn_suffix"), cls.bool_to_int(dados.get("ativo")),
                dados.get("updated_by"), provedor_id,
            ),
        )

    @classmethod
    def registrar_teste_provedor(cls, provedor_id, status, mensagem):
        return cls.execute(
            """
            UPDATE auth_provedores
            SET ultimo_teste_status=%s, ultimo_teste_mensagem=%s, ultimo_teste_em=NOW()
            WHERE id=%s
            """,
            (status, mensagem, provedor_id),
        )

    @classmethod
    def registrar_auditoria(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None, ip_origem=None, user_agent=None):
        cls.limpar_auditoria_antiga()
        return cls.execute_insert(
            """
            INSERT INTO auth_auditoria (
                uuid, usuario_email, acao, entidade, entidade_id, detalhes, ip_origem, user_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """ ,
            (cls.generate_uuid(), usuario_email, acao, entidade, entidade_id, detalhes, ip_origem, user_agent),
        )

    @classmethod
    def limpar_auditoria_antiga(cls):
        removidos = cls.execute("DELETE FROM auth_auditoria WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)")
        cls.execute("DELETE FROM implantacao_cofre_senhas_auditoria WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)")
        return removidos

    @classmethod
    def listar_auditoria(cls, filtros=None, limite=100):
        filtros = filtros or {}
        where = ["eventos.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"]
        params = []
        if filtros.get("usuario_email"):
            where.append("eventos.usuario_email LIKE %s")
            params.append("%{}%".format(filtros["usuario_email"]))
        if filtros.get("acao"):
            where.append("eventos.acao = %s")
            params.append(filtros["acao"])
        if filtros.get("entidade"):
            where.append("eventos.entidade = %s")
            params.append(filtros["entidade"])
        if filtros.get("data_inicio"):
            where.append("eventos.created_at >= %s")
            params.append(filtros["data_inicio"])
        if filtros.get("data_fim"):
            where.append("eventos.created_at < DATE_ADD(%s, INTERVAL 1 DAY)")
            params.append(filtros["data_fim"])
        params.append(int(limite or 100))
        sql = """
            SELECT usuario_email, acao, entidade, entidade_id, detalhes, ip_origem, user_agent, created_at
            FROM (
                SELECT usuario_email, acao, entidade, entidade_id, detalhes, ip_origem, user_agent, created_at
                FROM auth_auditoria
                UNION ALL
                SELECT usuario_email,
                       CONCAT('COFRE_', acao) AS acao,
                       'cofre_senhas' AS entidade,
                       cofre_senha_id AS entidade_id,
                       detalhe AS detalhes,
                       ip_origem,
                       NULL AS user_agent,
                       created_at
                FROM implantacao_cofre_senhas_auditoria
            ) eventos
            WHERE {}
            ORDER BY eventos.created_at DESC
            LIMIT %s
        """.format(" AND ".join(where))
        return cls.fetch_all(sql, params)

    @classmethod
    def listar_acoes_auditoria(cls):
        return cls.fetch_all(
            """
            SELECT DISTINCT acao
            FROM (
                SELECT acao, created_at FROM auth_auditoria
                UNION ALL
                SELECT CONCAT('COFRE_', acao) AS acao, created_at FROM implantacao_cofre_senhas_auditoria
            ) eventos
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY acao ASC
            """
        )

    @classmethod
    def listar_entidades_auditoria(cls):
        return cls.fetch_all(
            """
            SELECT DISTINCT entidade
            FROM (
                SELECT entidade, created_at FROM auth_auditoria
                UNION ALL
                SELECT 'cofre_senhas' AS entidade, created_at FROM implantacao_cofre_senhas_auditoria
            ) eventos
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY entidade ASC
            """
        )
    @classmethod
    def listar_integracoes_identidade(cls):
        return cls.fetch_all(
            """
            SELECT id, tipo, nome, base_url, ativo
            FROM implantacao_integracoes_config
            WHERE tipo IN ('freeipa', 'ldap', 'ad')
              AND ativo = 1
            ORDER BY FIELD(tipo, 'freeipa', 'ldap', 'ad'), nome ASC
            """
        )

    @classmethod
    def listar_grupo_perfil_mapas(cls):
        return cls.fetch_all(
            """
            SELECT m.id, m.uuid, m.integracao_id, m.provedor_tipo, m.grupo_externo,
                   m.perfil_id, m.ativo, m.created_by, m.updated_by, m.created_at, m.updated_at,
                   p.nome AS perfil_nome, p.codigo AS perfil_codigo,
                   i.nome AS integracao_nome, i.tipo AS integracao_tipo, i.base_url AS integracao_base_url
            FROM auth_grupo_perfil_mapas m
            INNER JOIN auth_perfis p ON p.id = m.perfil_id
            LEFT JOIN implantacao_integracoes_config i ON i.id = m.integracao_id
            ORDER BY m.ativo DESC, m.provedor_tipo ASC, m.grupo_externo ASC
            """
        )

    @classmethod
    def buscar_grupo_perfil_mapa(cls, mapa_id):
        return cls.fetch_one(
            """
            SELECT m.*, p.nome AS perfil_nome, p.codigo AS perfil_codigo,
                   i.nome AS integracao_nome, i.tipo AS integracao_tipo
            FROM auth_grupo_perfil_mapas m
            INNER JOIN auth_perfis p ON p.id = m.perfil_id
            LEFT JOIN implantacao_integracoes_config i ON i.id = m.integracao_id
            WHERE m.id = %s
            """,
            (mapa_id,),
        )

    @classmethod
    def buscar_grupo_perfil_mapa_existente(cls, provedor_tipo, grupo_externo, integracao_id=None, ignorar_id=None):
        sql = """
            SELECT id
            FROM auth_grupo_perfil_mapas
            WHERE provedor_tipo = %s
              AND grupo_externo = %s
              AND ativo = 1
        """
        params = [provedor_tipo, grupo_externo]
        if integracao_id:
            sql += " AND integracao_id = %s"
            params.append(integracao_id)
        else:
            sql += " AND integracao_id IS NULL"
        if ignorar_id:
            sql += " AND id <> %s"
            params.append(ignorar_id)
        sql += " LIMIT 1"
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def inserir_grupo_perfil_mapa(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_grupo_perfil_mapas (
                uuid, integracao_id, provedor_tipo, grupo_externo, perfil_id,
                ativo, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("integracao_id"), dados.get("provedor_tipo"),
                dados.get("grupo_externo"), dados.get("perfil_id"), cls.bool_to_int(dados.get("ativo", True)),
                dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar_grupo_perfil_mapa(cls, mapa_id, dados):
        return cls.execute(
            """
            UPDATE auth_grupo_perfil_mapas
            SET integracao_id=%s,
                provedor_tipo=%s,
                grupo_externo=%s,
                perfil_id=%s,
                ativo=%s,
                updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("integracao_id"), dados.get("provedor_tipo"), dados.get("grupo_externo"),
                dados.get("perfil_id"), cls.bool_to_int(dados.get("ativo", True)), dados.get("updated_by"), mapa_id,
            ),
        )

    @classmethod
    def inativar_grupo_perfil_mapa(cls, mapa_id, usuario_email="sistema"):
        return cls.execute(
            "UPDATE auth_grupo_perfil_mapas SET ativo=0, updated_by=%s WHERE id=%s",
            (usuario_email or "sistema", mapa_id),
        )

    @classmethod
    def _provedor_params(cls, dados, incluir_auditoria=False):
        params = (
            cls.generate_uuid(), dados.get("nome"), dados.get("tipo"), dados.get("host"), dados.get("porta"),
            dados.get("dominio"), dados.get("base_dn"), dados.get("bind_dn"),
            dados.get("bind_password_encrypted"), cls.bool_to_int(dados.get("usar_tls")),
            cls.bool_to_int(dados.get("usar_starttls")), dados.get("filtro_usuarios"),
            dados.get("filtro_grupos"), dados.get("atributo_login"), dados.get("atributo_email"),
            dados.get("atributo_nome"), dados.get("upn_suffix"), cls.bool_to_int(dados.get("ativo")),
            dados.get("created_by"), dados.get("updated_by"),
        )
        return params if incluir_auditoria else params[1:]

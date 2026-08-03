from app.repositories.base_repository import BaseRepository


class AuthRepository(BaseRepository):
    @classmethod
    def listar_perfis(cls):
        return cls.fetch_all(
            """
            SELECT id, uuid, nome, codigo, descricao, ativo
            FROM auth_perfis
            WHERE ativo = 1
            ORDER BY nome ASC
            """
        )

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
        return cls.fetch_one(
            """
            SELECT * FROM auth_usuarios WHERE email = %s
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
                cls.generate_uuid(), dados.get('nome'), dados.get('email'), dados.get('login'),
                dados.get('origem'), dados.get('perfil_id'), dados.get('status'),
                dados.get('externo_id'), dados.get('senha_hash'), dados.get('created_by'), dados.get('updated_by'),
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
                dados.get('nome'), dados.get('email'), dados.get('login'), dados.get('origem'),
                dados.get('perfil_id'), dados.get('status'), dados.get('externo_id'),
                dados.get('updated_by'), usuario_id,
            ),
        )

    @classmethod
    def definir_senha(cls, usuario_id, senha_hash):
        return cls.execute(
            """
            UPDATE auth_usuarios
            SET senha_hash=%s, status='ATIVO', updated_at=NOW()
            WHERE id=%s
            """,
            (senha_hash, usuario_id),
        )

    @classmethod
    def inserir_convite(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO auth_convites (
                uuid, usuario_id, token_hash, email, status, expira_em, enviado_em, created_by
            ) VALUES (%s, %s, %s, %s, 'PENDENTE', %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get('usuario_id'), dados.get('token_hash'), dados.get('email'),
                dados.get('expira_em'), dados.get('enviado_em'), dados.get('created_by'),
            ),
        )

    @classmethod
    def expirar_convites_usuario(cls, usuario_id):
        return cls.execute(
            """
            UPDATE auth_convites
            SET status='EXPIRADO'
            WHERE usuario_id=%s AND status='PENDENTE'
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
        return cls.execute(
            """
            UPDATE auth_convites
            SET status='USADO', usado_em=NOW()
            WHERE id=%s
            """,
            (convite_id,),
        )

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
        return cls.fetch_one(
            """
            SELECT * FROM auth_provedores WHERE id=%s
            """,
            (provedor_id,),
        )

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
                dados.get('nome'), dados.get('tipo'), dados.get('host'), dados.get('porta'),
                dados.get('dominio'), dados.get('base_dn'), dados.get('bind_dn'),
                dados.get('bind_password_encrypted'), cls.bool_to_int(dados.get('usar_tls')),
                cls.bool_to_int(dados.get('usar_starttls')), dados.get('filtro_usuarios'),
                dados.get('filtro_grupos'), dados.get('atributo_login'), dados.get('atributo_email'),
                dados.get('atributo_nome'), dados.get('upn_suffix'), cls.bool_to_int(dados.get('ativo')),
                dados.get('updated_by'), provedor_id,
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
    def registrar_auditoria(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None):
        return cls.execute_insert(
            """
            INSERT INTO auth_auditoria (uuid, usuario_email, acao, entidade, entidade_id, detalhes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(), usuario_email, acao, entidade, entidade_id, detalhes),
        )

    @classmethod
    def listar_auditoria(cls, limite=30):
        return cls.fetch_all(
            """
            SELECT usuario_email, acao, entidade, entidade_id, detalhes, created_at
            FROM auth_auditoria
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (limite,),
        )

    @classmethod
    def _provedor_params(cls, dados, incluir_auditoria=False):
        params = (
            cls.generate_uuid(), dados.get('nome'), dados.get('tipo'), dados.get('host'), dados.get('porta'),
            dados.get('dominio'), dados.get('base_dn'), dados.get('bind_dn'),
            dados.get('bind_password_encrypted'), cls.bool_to_int(dados.get('usar_tls')),
            cls.bool_to_int(dados.get('usar_starttls')), dados.get('filtro_usuarios'),
            dados.get('filtro_grupos'), dados.get('atributo_login'), dados.get('atributo_email'),
            dados.get('atributo_nome'), dados.get('upn_suffix'), cls.bool_to_int(dados.get('ativo')),
            dados.get('created_by'), dados.get('updated_by'),
        )
        return params if incluir_auditoria else params[1:]

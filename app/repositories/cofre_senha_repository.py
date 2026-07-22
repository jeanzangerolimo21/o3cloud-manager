from app.repositories.base_repository import BaseRepository


class CofreSenhaRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None, limit=50, offset=0):
        sql = """
            SELECT cs.id, cs.uuid, cs.pasta_id, cp.nome AS pasta_nome, cp.tipo AS pasta_tipo,
                   cs.cliente_id, cs.cliente_nome, cs.cliente_cnpj,
                   cs.faixa_rede_id, fr.rede AS faixa_rede,
                   cs.licenca_o3web_id, o3.id_licenca AS licenca_o3web_codigo,
                   cs.categoria, cs.titulo, cs.host, cs.porta, cs.url, cs.usuario,
                   cs.observacoes, cs.proxmox_node_id, cs.proxmox_vm_id,
                   cs.pbs_server_id, cs.zabbix_host_id, cs.ativo,
                   cs.created_by, cs.updated_by, cs.created_at, cs.updated_at
            FROM implantacao_cofre_senhas cs
            JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
            LEFT JOIN o3web_licencas o3 ON o3.id = cs.licenca_o3web_id
            LEFT JOIN implantacao_cofre_pastas cp ON cp.id = cs.pasta_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, categoria, ativo, pasta_id)
        sql += where
        sql += """
            ORDER BY cs.cliente_nome ASC, cs.categoria ASC, cs.titulo ASC, cs.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None):
        sql = """
            SELECT COUNT(*)
            FROM implantacao_cofre_senhas cs
            JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
            LEFT JOIN o3web_licencas o3 ON o3.id = cs.licenca_o3web_id
            LEFT JOIN implantacao_cofre_pastas cp ON cp.id = cs.pasta_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, categoria, ativo, pasta_id)
        return cls.scalar(sql + where, tuple(params)) or 0

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) AS ativas,
                SUM(CASE WHEN ativo = 1 AND categoria = 'firewall' THEN 1 ELSE 0 END) AS firewall,
                SUM(CASE WHEN ativo = 1 AND categoria = 'vpn' THEN 1 ELSE 0 END) AS vpn,
                SUM(CASE WHEN ativo = 1 AND categoria = 'o3web' THEN 1 ELSE 0 END) AS o3web,
                SUM(CASE WHEN ativo = 1 AND categoria IN ('proxmox', 'pbs', 'zabbix') THEN 1 ELSE 0 END) AS integracoes_futuras
            FROM implantacao_cofre_senhas
            """
        )

    @classmethod
    def buscar_por_id(cls, senha_id):
        return cls.fetch_one(
            """
            SELECT cs.*, fr.rede AS faixa_rede, o3.id_licenca AS licenca_o3web_codigo, cp.nome AS pasta_nome, cp.tipo AS pasta_tipo
            FROM implantacao_cofre_senhas cs
            JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
            LEFT JOIN o3web_licencas o3 ON o3.id = cs.licenca_o3web_id
            LEFT JOIN implantacao_cofre_pastas cp ON cp.id = cs.pasta_id
            WHERE cs.id = %s
            """,
            (senha_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_cofre_senhas (
                uuid, pasta_id, cliente_id, cliente_nome, cliente_cnpj, faixa_rede_id, licenca_o3web_id,
                categoria, titulo, host, porta, url, usuario, senha_encrypted, observacoes,
                proxmox_node_id, proxmox_vm_id, pbs_server_id, zabbix_host_id, ativo, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(),) + cls._params(dados, incluir_senha=True),
        )

    @classmethod
    def atualizar(cls, senha_id, dados):
        campos_senha = ""
        params = cls._params(dados, incluir_senha=False)
        if dados.get("senha_encrypted"):
            campos_senha = ", senha_encrypted=%s"
            params = params[:-1] + (dados.get("senha_encrypted"),) + params[-1:]
        return cls.execute(
            f"""
            UPDATE implantacao_cofre_senhas
            SET pasta_id=%s,
                cliente_id=%s,
                cliente_nome=%s,
                cliente_cnpj=%s,
                faixa_rede_id=%s,
                licenca_o3web_id=%s,
                categoria=%s,
                titulo=%s,
                host=%s,
                porta=%s,
                url=%s,
                usuario=%s,
                observacoes=%s,
                proxmox_node_id=%s,
                proxmox_vm_id=%s,
                pbs_server_id=%s,
                zabbix_host_id=%s,
                ativo=%s{campos_senha},
                updated_by=%s
            WHERE id=%s
            """,
            params + (senha_id,),
        )

    @classmethod
    def excluir(cls, senha_id, usuario_email=None):
        return cls.execute(
            "UPDATE implantacao_cofre_senhas SET ativo = 0, updated_by = %s WHERE id = %s",
            (usuario_email or "sistema", senha_id),
        )

    @classmethod
    def registrar_auditoria(cls, senha_id, acao, usuario_email="sistema", detalhe=None, ip_origem=None):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_cofre_senhas_auditoria (
                cofre_senha_id, acao, usuario_email, detalhe, ip_origem
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (senha_id, acao, usuario_email or "sistema", detalhe, ip_origem),
        )

    @classmethod
    def listar_auditoria(cls, senha_id, limit=20):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_cofre_senhas_auditoria
            WHERE cofre_senha_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (senha_id, limit),
        )

    @classmethod
    def listar_faixas_ativas(cls):
        return cls.fetch_all(
            """
            SELECT id, rede, cliente_id, cliente_nome, cliente_cnpj, fw_wan, fw_lan
            FROM implantacao_faixas_rede
            WHERE ativo = 1
            ORDER BY cliente_nome ASC, INET_ATON(SUBSTRING_INDEX(rede, '/', 1)) ASC
            """
        )

    @classmethod
    def listar_licencas_ativas(cls):
        return cls.fetch_all(
            """
            SELECT id, id_licenca, chave_ativacao, cliente_id, cliente_nome, cliente_cnpj, tipo, url_principal, url_secundaria
            FROM o3web_licencas
            WHERE ativo = 1
            ORDER BY cliente_nome ASC, id DESC
            """
        )

    @classmethod
    def _params(cls, dados, incluir_senha=False):
        params = (
            dados.get("pasta_id"),
            dados.get("cliente_id"),
            dados.get("cliente_nome"),
            dados.get("cliente_cnpj"),
            dados.get("faixa_rede_id"),
            dados.get("licenca_o3web_id"),
            dados.get("categoria"),
            dados.get("titulo"),
            dados.get("host"),
            dados.get("porta"),
            dados.get("url"),
            dados.get("usuario"),
        )
        if incluir_senha:
            params += (dados.get("senha_encrypted"),)
        params += (
            dados.get("observacoes"),
            dados.get("proxmox_node_id"),
            dados.get("proxmox_vm_id"),
            dados.get("pbs_server_id"),
            dados.get("zabbix_host_id"),
            dados.get("ativo", 1),
            dados.get("updated_by") or dados.get("created_by") or "sistema",
            dados.get("updated_by") or dados.get("created_by") or "sistema",
        )
        if not incluir_senha:
            params = params[:-2] + (params[-1],)
        return params

    @classmethod
    def _filtros(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            where.append(
                """
                (
                    cs.cliente_nome LIKE %s
                    OR COALESCE(cs.cliente_cnpj, '') LIKE %s
                    OR cs.titulo LIKE %s
                    OR cs.usuario LIKE %s
                    OR COALESCE(cs.host, '') LIKE %s
                    OR COALESCE(cs.url, '') LIKE %s
                    OR fr.rede LIKE %s
                    OR COALESCE(o3.id_licenca, '') LIKE %s
                    OR COALESCE(cs.observacoes, '') LIKE %s
                    OR COALESCE(cp.nome, '') LIKE %s
                )
                """
            )
            params.extend([termo] * 10)
        if categoria:
            where.append("cs.categoria = %s")
            params.append(categoria)
        if pasta_id:
            where.append("cs.pasta_id = %s")
            params.append(pasta_id)
        if ativo in (0, 1):
            where.append("cs.ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params

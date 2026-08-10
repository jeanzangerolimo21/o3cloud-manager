from app.repositories.base_repository import BaseRepository


class CofreSenhaRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None, apenas_clientes=False, limit=50, offset=0):
        sql = """
            SELECT cs.id, cs.uuid, cs.pasta_id, cp.nome AS pasta_nome, cp.tipo AS pasta_tipo,
                   cs.cliente_id, cs.cliente_nome, cs.cliente_cnpj,
                   cs.ambiente_id, amb.nome AS ambiente_nome, amb.ambiente_tipo, amb.prefixo_proxmox,
                   cs.faixa_rede_id, fr.rede AS faixa_rede,
                   cp.owner_email AS pasta_owner_email, cp.compartilhada AS pasta_compartilhada, cp.compartilhada_com AS pasta_compartilhada_com,
                   cs.licenca_o3web_id, o3.id_licenca AS licenca_o3web_codigo,
                   cs.categoria, cs.titulo, cs.host, cs.porta, cs.url, cs.usuario,
                   cs.observacoes, cs.proxmox_node_id, cs.proxmox_vm_id,
                   cs.pbs_server_id, cs.zabbix_host_id, cs.ativo,
                   cs.created_by, cs.updated_by, cs.created_at, cs.updated_at
            FROM implantacao_cofre_senhas cs
            LEFT JOIN ambientes amb ON amb.id = cs.ambiente_id
            LEFT JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
            LEFT JOIN o3web_licencas o3 ON o3.id = cs.licenca_o3web_id
            LEFT JOIN implantacao_cofre_pastas cp ON cp.id = cs.pasta_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, categoria, ativo, pasta_id, apenas_clientes)
        sql += where
        sql += """
            ORDER BY cs.cliente_nome ASC, cs.categoria ASC, cs.titulo ASC, cs.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None, apenas_clientes=False):
        sql = """
            SELECT COUNT(*)
            FROM implantacao_cofre_senhas cs
            LEFT JOIN ambientes amb ON amb.id = cs.ambiente_id
            LEFT JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
            LEFT JOIN o3web_licencas o3 ON o3.id = cs.licenca_o3web_id
            LEFT JOIN implantacao_cofre_pastas cp ON cp.id = cs.pasta_id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, categoria, ativo, pasta_id, apenas_clientes)
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
            SELECT cs.*, amb.nome AS ambiente_nome, amb.ambiente_tipo, amb.prefixo_proxmox, fr.rede AS faixa_rede, o3.id_licenca AS licenca_o3web_codigo, cp.nome AS pasta_nome, cp.tipo AS pasta_tipo, cp.owner_email AS pasta_owner_email, cp.compartilhada AS pasta_compartilhada, cp.compartilhada_com AS pasta_compartilhada_com
            FROM implantacao_cofre_senhas cs
            LEFT JOIN ambientes amb ON amb.id = cs.ambiente_id
            LEFT JOIN implantacao_faixas_rede fr ON fr.id = cs.faixa_rede_id
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
                uuid, pasta_id, cliente_id, cliente_nome, cliente_cnpj, ambiente_id, faixa_rede_id, licenca_o3web_id,
                categoria, titulo, host, porta, url, usuario, senha_encrypted, observacoes,
                proxmox_node_id, proxmox_vm_id, pbs_server_id, zabbix_host_id,
                proxmox_node_inventory_id, proxmox_inventory_id, pbs_backup_snapshot_id,
                zabbix_host_inventory_id, ativo, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                ambiente_id=%s,
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
                proxmox_node_inventory_id=%s,
                proxmox_inventory_id=%s,
                pbs_backup_snapshot_id=%s,
                zabbix_host_inventory_id=%s,
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
    def criar_compartilhamento(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_cofre_compartilhamentos (
                uuid, cofre_senha_id, token_hash, expires_at, created_by, created_ip
            ) VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE), %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("cofre_senha_id"), dados.get("token_hash"),
                dados.get("ttl_minutos", 5), dados.get("created_by") or "sistema",
                dados.get("created_ip"),
            ),
        )

    @classmethod
    def consumir_compartilhamento(cls, token_hash, accessed_ip=None):
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                UPDATE implantacao_cofre_compartilhamentos
                SET accessed_at = NOW(), accessed_ip = %s
                WHERE token_hash = %s AND expires_at > NOW()
                  AND accessed_at IS NULL AND revoked_at IS NULL
                """,
                (accessed_ip, token_hash),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return None
            cursor.execute(
                """
                SELECT cc.cofre_senha_id, cs.titulo, cs.senha_encrypted, cc.expires_at
                FROM implantacao_cofre_compartilhamentos cc
                JOIN implantacao_cofre_senhas cs ON cs.id = cc.cofre_senha_id
                WHERE cc.token_hash = %s AND cs.ativo = 1
                """,
                (token_hash,),
            )
            compartilhamento = cursor.fetchone()
            if not compartilhamento:
                conn.rollback()
                return None
            conn.commit()
            return compartilhamento
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def listar_vinculos_infraestrutura(cls):
        nodes = cls.fetch_all(
            """
            SELECT n.id, n.integracao_id, i.nome AS integracao_nome, n.node, n.status
            FROM proxmox_node_inventory n
            JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            WHERE n.ativo = 1 AND i.tipo = 'proxmox' AND i.ativo = 1
            ORDER BY i.nome, n.node
            """
        )
        vms = cls.fetch_all(
            """
            SELECT p.id, p.integracao_id, p.node, p.vmid, p.tipo, p.nome, p.status,
                   n.id AS node_inventory_id, i.nome AS integracao_nome
            FROM proxmox_vm_inventory p
            JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
            LEFT JOIN proxmox_node_inventory n
              ON n.integracao_id = p.integracao_id AND n.node = p.node AND n.ativo = 1
            WHERE p.ativo = 1 AND i.tipo = 'proxmox' AND i.ativo = 1
            ORDER BY i.nome, p.node, p.vmid
            """
        )
        snapshots = cls.fetch_all(
            """
            SELECT s.id, s.proxmox_inventory_id, s.integracao_id, s.datastore,
                   s.namespace, s.backup_type, s.backup_id, s.backup_time,
                   s.snapshot_name, i.nome AS integracao_nome
            FROM pbs_backup_snapshots s
            JOIN implantacao_integracoes_config i ON i.id = s.integracao_id
            WHERE i.tipo = 'pbs' AND i.ativo = 1
            ORDER BY s.backup_time DESC, s.snapshot_name
            """
        )
        return {
            "proxmox_nodes": nodes,
            "proxmox_vms": vms,
            "pbs_snapshots": snapshots,
            "zabbix_hosts": [],
        }

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
            dados.get("ambiente_id"),
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
            dados.get("proxmox_node_inventory_id"),
            dados.get("proxmox_inventory_id"),
            dados.get("pbs_backup_snapshot_id"),
            dados.get("zabbix_host_inventory_id"),
            dados.get("ativo", 1),
            dados.get("updated_by") or dados.get("created_by") or "sistema",
            dados.get("updated_by") or dados.get("created_by") or "sistema",
        )
        if not incluir_senha:
            params = params[:-2] + (params[-1],)
        return params

    @classmethod
    def _filtros(cls, pesquisa=None, categoria=None, ativo=1, pasta_id=None, apenas_clientes=False):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            where.append(
                """
                (
                    cs.cliente_nome LIKE %s
                    OR COALESCE(cs.cliente_cnpj, '') LIKE %s
                    OR REGEXP_REPLACE(COALESCE(cs.cliente_cnpj, ''), '[^0-9A-Za-z]', '') LIKE %s
                    OR cs.titulo LIKE %s
                    OR cs.usuario LIKE %s
                    OR COALESCE(cs.host, '') LIKE %s
                    OR COALESCE(cs.url, '') LIKE %s
                    OR COALESCE(amb.nome, '') LIKE %s
                    OR COALESCE(amb.prefixo_proxmox, '') LIKE %s
                    OR COALESCE(fr.rede, '') LIKE %s
                    OR COALESCE(o3.id_licenca, '') LIKE %s
                    OR COALESCE(cs.observacoes, '') LIKE %s
                    OR COALESCE(cp.nome, '') LIKE %s
                )
                """
            )
            params.extend([termo, termo, termo_cnpj, termo, termo, termo, termo, termo, termo, termo, termo, termo, termo])
        if apenas_clientes:
            where.append("cp.tipo = %s")
            params.append("cliente")
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

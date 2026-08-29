from app.repositories.base_repository import BaseRepository


STATUS_ATIVOS = ("AGENDADO", "VALIDANDO", "DESLIGANDO", "AGUARDANDO_DESLIGAMENTO", "APLICANDO", "VALIDANDO_CONFIGURACAO", "LIGANDO", "VALIDANDO_INICIALIZACAO")


class ProxmoxAgendamentoRepository(BaseRepository):
    @classmethod
    def listar(cls, filtros=None, limite=100):
        filtros = filtros or {}
        limite = max(1, min(int(limite or 100), 300))
        sql = """
            SELECT a.*, i.nome AS integracao_nome
            FROM proxmox_agendamentos a
            JOIN implantacao_integracoes_config i ON i.id = a.integracao_id
            WHERE 1=1
        """
        params = []
        if filtros.get("status"):
            sql += " AND a.status = %s"
            params.append(filtros.get("status"))
        if filtros.get("integracao_id"):
            sql += " AND a.integracao_id = %s"
            params.append(int(filtros.get("integracao_id")))
        if filtros.get("node"):
            sql += " AND a.node_nome = %s"
            params.append(filtros.get("node"))
        if filtros.get("q"):
            termo = f"%{filtros.get('q')}%"
            sql += " AND (a.vm_nome LIKE %s OR CAST(a.vmid AS CHAR) LIKE %s OR a.motivo LIKE %s)"
            params.extend([termo, termo, termo])
        sql += f" ORDER BY FIELD(a.status, 'ERRO', 'VALIDANDO', 'DESLIGANDO', 'AGUARDANDO_DESLIGAMENTO', 'APLICANDO', 'VALIDANDO_CONFIGURACAO', 'LIGANDO', 'VALIDANDO_INICIALIZACAO', 'AGENDADO', 'CONCLUIDO', 'CANCELADO'), a.executar_em DESC LIMIT {limite}"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN status = 'AGENDADO' THEN 1 ELSE 0 END) AS agendados,
                   SUM(CASE WHEN status IN ('VALIDANDO','DESLIGANDO','AGUARDANDO_DESLIGAMENTO','APLICANDO','VALIDANDO_CONFIGURACAO','LIGANDO','VALIDANDO_INICIALIZACAO') THEN 1 ELSE 0 END) AS em_execucao,
                   SUM(CASE WHEN status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS concluidos,
                   SUM(CASE WHEN status = 'ERRO' THEN 1 ELSE 0 END) AS erros
            FROM proxmox_agendamentos
            """
        ) or {}

    @classmethod
    def buscar_por_id(cls, agendamento_id):
        return cls.fetch_one(
            """
            SELECT a.*, i.nome AS integracao_nome, i.base_url, i.usuario, i.token_nome, i.timeout_seconds, i.verify_ssl
            FROM proxmox_agendamentos a
            JOIN implantacao_integracoes_config i ON i.id = a.integracao_id
            WHERE a.id = %s
            """,
            (agendamento_id,),
        )

    @classmethod
    def listar_eventos(cls, agendamento_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM proxmox_agendamentos_eventos
            WHERE agendamento_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (agendamento_id,),
        )

    @classmethod
    def listar_pendentes(cls, limite=5):
        limite = max(1, min(int(limite or 5), 20))
        return cls.fetch_all(
            f"""
            SELECT id
            FROM proxmox_agendamentos
            WHERE status = 'AGENDADO'
              AND executar_em <= NOW()
            ORDER BY executar_em ASC, id ASC
            LIMIT {limite}
            """
        )

    @classmethod
    def buscar_inventario_qemu(cls, inventario_id):
        return cls.fetch_one(
            """
            SELECT p.id, p.integracao_id, i.nome AS cluster_nome, i.base_url AS cluster_base_url,
                   p.node, p.vmid, p.tipo, p.nome, p.status, p.cpu_cores, p.memoria_mb,
                   p.ativo, p.ultimo_sync_em
            FROM proxmox_vm_inventory p
            JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
            WHERE p.id = %s AND p.ativo = 1 AND p.tipo = 'qemu' AND i.ativo = 1 AND i.tipo = 'proxmox'
            """,
            (inventario_id,),
        )

    @classmethod
    def listar_vms_qemu(cls):
        return cls.fetch_all(
            """
            SELECT p.id, p.integracao_id, i.nome AS cluster_nome, i.base_url AS cluster_base_url,
                   p.node, p.vmid, p.tipo, p.nome, p.status, p.cpu_cores, p.memoria_mb, p.ultimo_sync_em
            FROM proxmox_vm_inventory p
            JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
            WHERE p.ativo = 1 AND p.tipo = 'qemu' AND i.ativo = 1 AND i.tipo = 'proxmox'
            ORDER BY i.nome ASC, p.node ASC, p.vmid ASC
            """
        )

    @classmethod
    def listar_nodes(cls):
        return cls.fetch_all(
            """
            SELECT DISTINCT p.integracao_id, i.nome AS cluster_nome, p.node
            FROM proxmox_vm_inventory p
            JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
            WHERE p.ativo = 1 AND p.tipo = 'qemu' AND i.ativo = 1 AND i.tipo = 'proxmox'
            ORDER BY i.nome ASC, p.node ASC
            """
        )

    @classmethod
    def existe_ativo_vm(cls, integracao_id, node_nome, vmid):
        return bool(cls.scalar(
            f"""
            SELECT id
            FROM proxmox_agendamentos
            WHERE integracao_id = %s
              AND node_nome = %s
              AND vmid = %s
              AND status IN ({','.join(['%s'] * len(STATUS_ATIVOS))})
            LIMIT 1
            """,
            (integracao_id, node_nome, vmid, *STATUS_ATIVOS),
        ))

    @classmethod
    def criar(cls, dados):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO proxmox_agendamentos (
                    uuid, integracao_id, cluster_nome, cluster_base_url, inventario_id, node_nome,
                    vmid, vm_nome, tipo, cpu_original, cpu_nova, memoria_original_mb,
                    memoria_nova_mb, status_original, executar_em, desligar_se_necessario,
                    religar_automaticamente, motivo, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'qemu', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    cls.generate_uuid(), dados["integracao_id"], dados.get("cluster_nome"), dados.get("cluster_base_url"),
                    dados.get("inventario_id"), dados["node_nome"], dados["vmid"], dados.get("vm_nome"),
                    dados.get("cpu_original"), dados.get("cpu_nova"), dados.get("memoria_original_mb"),
                    dados.get("memoria_nova_mb"), dados.get("status_original"), dados["executar_em"],
                    cls.bool_to_int(dados.get("desligar_se_necessario")), cls.bool_to_int(dados.get("religar_automaticamente")),
                    dados.get("motivo"), dados.get("created_by"),
                ),
            )
            agendamento_id = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO proxmox_agendamentos_eventos (uuid, agendamento_id, status, mensagem)
                VALUES (%s, %s, 'AGENDADO', %s)
                """,
                (cls.generate_uuid(), agendamento_id, "Agendamento criado."),
            )
            conn.commit()
            return agendamento_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def cancelar(cls, agendamento_id, usuario_email):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE proxmox_agendamentos
                SET status = 'CANCELADO', cancelado_em = NOW(), cancelled_by = %s, mensagem_erro = NULL
                WHERE id = %s AND status = 'AGENDADO'
                """,
                (usuario_email or "sistema", agendamento_id),
            )
            alteradas = cursor.rowcount
            if alteradas:
                cursor.execute(
                    """
                    INSERT INTO proxmox_agendamentos_eventos (uuid, agendamento_id, status, mensagem)
                    VALUES (%s, %s, 'CANCELADO', %s)
                    """,
                    (cls.generate_uuid(), agendamento_id, f"Cancelado por {usuario_email or 'sistema'}."),
                )
            conn.commit()
            return alteradas > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def claim(cls, agendamento_id, worker_id):
        return cls.execute_delete_count(
            """
            UPDATE proxmox_agendamentos
            SET status = 'VALIDANDO', worker_id = %s, iniciado_em = COALESCE(iniciado_em, NOW())
            WHERE id = %s AND status = 'AGENDADO' AND executar_em <= NOW()
            """,
            (worker_id, agendamento_id),
        ) > 0

    @classmethod
    def registrar_evento(cls, agendamento_id, status, mensagem=None):
        return cls.execute(
            """
            INSERT INTO proxmox_agendamentos_eventos (uuid, agendamento_id, status, mensagem)
            VALUES (%s, %s, %s, %s)
            """,
            (cls.generate_uuid(), agendamento_id, status, mensagem),
        )

    @classmethod
    def atualizar_status(cls, agendamento_id, status, mensagem=None, **campos):
        permitidos = {
            "cpu_original", "cpu_final", "memoria_original_mb", "memoria_final_mb",
            "status_original", "status_final", "mensagem_erro", "finalizado_em",
        }
        sets = ["status = %s"]
        params = [status]
        for campo, valor in campos.items():
            if campo not in permitidos:
                continue
            if campo == "finalizado_em" and valor == "NOW()":
                sets.append("finalizado_em = NOW()")
            else:
                sets.append(f"{campo} = %s")
                params.append(valor)
        params.append(agendamento_id)
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE proxmox_agendamentos SET {', '.join(sets)} WHERE id = %s",
                tuple(params),
            )
            cursor.execute(
                """
                INSERT INTO proxmox_agendamentos_eventos (uuid, agendamento_id, status, mensagem)
                VALUES (%s, %s, %s, %s)
                """,
                (cls.generate_uuid(), agendamento_id, status, mensagem),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

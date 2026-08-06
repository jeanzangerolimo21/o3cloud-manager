import json

from app.repositories.base_repository import BaseRepository


class ZabbixHostRepository(BaseRepository):
    @classmethod
    def listar(cls, integracao_id=None, ativo=1):
        sql = """
            SELECT h.id, h.integracao_id, i.nome AS integracao_nome, h.hostid,
                   h.host, h.nome, h.status, h.interfaces, h.cliente_id,
                   c.nome_fantasia AS cliente_nome, h.ultimo_sync_em, h.ativo
            FROM zabbix_host_inventory h
            JOIN implantacao_integracoes_config i ON i.id = h.integracao_id
            LEFT JOIN clientes c ON c.id = h.cliente_id
            WHERE i.tipo = 'zabbix'
        """
        params = []
        if integracao_id:
            sql += " AND h.integracao_id = %s"
            params.append(integracao_id)
        if ativo in (0, 1):
            sql += " AND h.ativo = %s"
            params.append(ativo)
        sql += " ORDER BY COALESCE(h.nome, h.host) ASC, h.id ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def salvar(cls, integracao_id, hosts):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE zabbix_host_inventory SET ativo = 0 WHERE integracao_id = %s",
                (integracao_id,),
            )
            atualizados = 0
            for item in hosts:
                cursor.execute(
                    """
                    INSERT INTO zabbix_host_inventory (
                        uuid, integracao_id, hostid, host, nome, status, interfaces,
                        ativo, ultimo_sync_em, raw_payload
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1, NOW(), %s)
                    ON DUPLICATE KEY UPDATE
                        host=VALUES(host), nome=VALUES(nome), status=VALUES(status),
                        interfaces=VALUES(interfaces), ativo=1, ultimo_sync_em=NOW(),
                        raw_payload=VALUES(raw_payload)
                    """,
                    (
                        cls.generate_uuid(), integracao_id, item.get("hostid"),
                        item.get("host"), item.get("nome"), item.get("status"),
                        json.dumps(item.get("interfaces") or [], ensure_ascii=False),
                        json.dumps(item.get("raw_payload") or {}, ensure_ascii=False),
                    ),
                )
                atualizados += 1
            conn.commit()
            return atualizados
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

from app.repositories.base_repository import BaseRepository


class ZabbixAlarmRepository(BaseRepository):
    @classmethod
    def listar(cls, integracao_id=None, limite=80):
        sql = """
            SELECT z.*, i.nome AS integracao_nome
            FROM zabbix_alarm_cache z
            JOIN implantacao_integracoes_config i ON i.id = z.integracao_id
            WHERE 1 = 1
        """
        params = []
        if integracao_id:
            sql += " AND z.integracao_id = %s"
            params.append(integracao_id)
        sql += """
            ORDER BY z.aberto DESC, z.severidade DESC, z.clock DESC, z.id DESC
            LIMIT %s
        """
        params.append(max(1, min(int(limite or 80), 200)))
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def ultimo_sync(cls, integracao_id=None):
        sql = """
            SELECT MAX(sincronizado_em) AS sincronizado_em
            FROM zabbix_alarm_cache
            WHERE 1 = 1
        """
        params = []
        if integracao_id:
            sql += " AND integracao_id = %s"
            params.append(integracao_id)
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def salvar(cls, integracao_id, alarmes):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM zabbix_alarm_cache WHERE integracao_id = %s", (integracao_id,))
            for item in alarmes:
                cursor.execute(
                    """
                    INSERT INTO zabbix_alarm_cache (
                        uuid, integracao_id, eventid, clock, data_evento, aberto, status_label,
                        severidade, severidade_label, host, nome, acknowledged, raw_payload, sincronizado_em
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())
                    ON DUPLICATE KEY UPDATE
                        clock=VALUES(clock), data_evento=VALUES(data_evento), aberto=VALUES(aberto),
                        status_label=VALUES(status_label), severidade=VALUES(severidade),
                        severidade_label=VALUES(severidade_label), host=VALUES(host), nome=VALUES(nome),
                        acknowledged=VALUES(acknowledged), raw_payload=VALUES(raw_payload),
                        sincronizado_em=UTC_TIMESTAMP()
                    """,
                    (
                        cls.generate_uuid(), integracao_id, item.get("eventid"), item.get("clock"),
                        item.get("data_evento"), cls.bool_to_int(item.get("aberto")), item.get("status_label"),
                        item.get("severidade"), item.get("severidade_label"), item.get("host"), item.get("nome"),
                        cls.bool_to_int(item.get("acknowledged")), item.get("raw_payload"),
                    ),
                )
            conn.commit()
            return len(alarmes)
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

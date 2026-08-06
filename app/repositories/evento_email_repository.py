from app.repositories.base_repository import BaseRepository
class EventoEmailRepository(BaseRepository):
 @classmethod
 def destinatarios(cls,evento_id):
  rows=cls.fetch_all("SELECT DISTINCT LOWER(TRIM(email)) email FROM crm_evento_participantes WHERE evento_id=%s AND email IS NOT NULL AND TRIM(email)<>'' ORDER BY email",(evento_id,))
  return [r["email"] for r in rows]
 @classmethod
 def enviados_hoje(cls,config_id):
  return cls.scalar("SELECT COALESCE(SUM(total_enviados),0) FROM crm_evento_disparos_email WHERE config_email_id=%s AND status IN ('ENVIADO','PARCIAL') AND created_at>=CURDATE()",(config_id,)) or 0
 @classmethod
 def iniciar(cls,d):
  return cls.execute_insert("INSERT INTO crm_evento_disparos_email(uuid,evento_id,config_email_id,assunto,total_destinatarios,anexo_nome,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s)",(cls.generate_uuid(),d["evento_id"],d["config_email_id"],d["assunto"],d["total_destinatarios"],d.get("anexo_nome"),d.get("created_by")))
 @classmethod
 def finalizar(cls,id,status,enviados,erro=None):
  return cls.execute("UPDATE crm_evento_disparos_email SET status=%s,total_enviados=%s,erro=%s,finished_at=NOW() WHERE id=%s",(status,enviados,erro,id))

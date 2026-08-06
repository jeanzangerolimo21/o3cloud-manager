from app.repositories.base_repository import BaseRepository

class EmailConfigRepository(BaseRepository):
 TABLE="config_email_servicos"
 @classmethod
 def listar(cls):
  return cls.fetch_all("SELECT id,uuid,nome,provedor,smtp_host,smtp_port,smtp_user,smtp_from,brevo_sender_email,brevo_sender_name,brevo_reply_to,brevo_daily_limit,brevo_environment,brevo_api_url,usar_tls,ativo,observacoes,ultimo_teste_status,ultimo_teste_mensagem,ultimo_teste_em,created_by,updated_by,created_at,updated_at FROM config_email_servicos ORDER BY ativo DESC,nome ASC,id ASC")
 @classmethod
 def buscar_ativo(cls,provedor="SMTP"):
  return cls.fetch_one("SELECT * FROM config_email_servicos WHERE ativo=1 AND provedor=%s ORDER BY updated_at DESC,id DESC LIMIT 1",(provedor,))
 @classmethod
 def buscar_por_id(cls,id): return cls.fetch_one("SELECT * FROM config_email_servicos WHERE id=%s",(id,))
 @classmethod
 def inserir(cls,d):
  return cls.execute_insert("INSERT INTO config_email_servicos(uuid,nome,provedor,smtp_host,smtp_port,smtp_user,smtp_password_encrypted,smtp_from,brevo_sender_email,brevo_sender_name,brevo_reply_to,brevo_daily_limit,brevo_environment,brevo_api_url,brevo_api_key_encrypted,usar_tls,ativo,observacoes,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(cls.generate_uuid(),d.get("nome"),d.get("provedor","SMTP"),d.get("smtp_host"),d.get("smtp_port"),d.get("smtp_user"),d.get("smtp_password_encrypted"),d.get("smtp_from"),d.get("brevo_sender_email"),d.get("brevo_sender_name"),d.get("brevo_reply_to"),d.get("brevo_daily_limit"),d.get("brevo_environment"),d.get("brevo_api_url"),d.get("brevo_api_key_encrypted"),cls.bool_to_int(d.get("usar_tls",True)),cls.bool_to_int(d.get("ativo",True)),d.get("observacoes"),d.get("created_by"),d.get("updated_by")))
 @classmethod
 def atualizar(cls,id,d):
  return cls.execute("UPDATE config_email_servicos SET nome=%s,provedor=%s,smtp_host=%s,smtp_port=%s,smtp_user=%s,smtp_password_encrypted=COALESCE(%s,smtp_password_encrypted),smtp_from=%s,brevo_sender_email=%s,brevo_sender_name=%s,brevo_reply_to=%s,brevo_daily_limit=%s,brevo_environment=%s,brevo_api_url=%s,brevo_api_key_encrypted=COALESCE(%s,brevo_api_key_encrypted),usar_tls=%s,ativo=%s,observacoes=%s,updated_by=%s WHERE id=%s",(d.get("nome"),d.get("provedor","SMTP"),d.get("smtp_host"),d.get("smtp_port"),d.get("smtp_user"),d.get("smtp_password_encrypted"),d.get("smtp_from"),d.get("brevo_sender_email"),d.get("brevo_sender_name"),d.get("brevo_reply_to"),d.get("brevo_daily_limit"),d.get("brevo_environment"),d.get("brevo_api_url"),d.get("brevo_api_key_encrypted"),cls.bool_to_int(d.get("usar_tls",True)),cls.bool_to_int(d.get("ativo",True)),d.get("observacoes"),d.get("updated_by"),id))
 @classmethod
 def desativar_outros(cls,id,provedor="SMTP"): return cls.execute("UPDATE config_email_servicos SET ativo=0 WHERE id<>%s AND provedor=%s",(id,provedor))
 @classmethod
 def registrar_teste(cls,id,status,mensagem): return cls.execute("UPDATE config_email_servicos SET ultimo_teste_status=%s,ultimo_teste_mensagem=%s,ultimo_teste_em=NOW() WHERE id=%s",(status,mensagem,id))

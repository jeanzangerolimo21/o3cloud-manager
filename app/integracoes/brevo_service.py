import base64
import requests
from app.configuracoes.email_service import EmailConfigService
class BrevoService:
 @classmethod
 def enviar(cls,config,assunto,html,emails,anexo=None):
  if not emails:return {"enviados":0}
  url=(config.get("brevo_api_url") or "https://api.brevo.com/v3").rstrip("/")+"/smtp/email"
  headers={"accept":"application/json","api-key":config.get("brevo_api_key") or "","content-type":"application/json"}
  if not headers["api-key"]:raise ValueError("BREVO_API_KEY não configurada.")
  sender={"email":config.get("brevo_sender_email"),"name":config.get("brevo_sender_name") or config.get("brevo_sender_email")}
  if not sender["email"]:raise ValueError("BREVO_SENDER_EMAIL não configurado.")
  payload={"sender":sender,"to":[{"email":e} for e in emails],"subject":assunto,"htmlContent":html or ""}
  if config.get("brevo_reply_to"):payload["replyTo"]={"email":config["brevo_reply_to"]}
  if anexo:
   payload["attachment"]=[{"content":base64.b64encode(anexo["content"]).decode("ascii"),"name":anexo["name"]}]
  response=requests.post(url,headers=headers,json=payload,timeout=45)
  if response.status_code>=400:raise ValueError("Brevo retornou HTTP {}: {}".format(response.status_code,response.text[:500]))
  return {"enviados":len(emails),"message_id":(response.json() if response.content else {}).get("messageId")}
 @classmethod
 def config(cls): return EmailConfigService.buscar_ativo(incluir_senha=True,provedor="BREVO")

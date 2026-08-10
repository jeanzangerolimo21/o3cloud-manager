import json
from app.repositories.base_repository import BaseRepository
class EventoRepository(BaseRepository):
 @classmethod
 def listar_eventos(cls):
  return cls.fetch_all("SELECT e.*,(SELECT COUNT(*) FROM crm_evento_participantes p WHERE p.evento_id=e.id) total_participantes,(SELECT COUNT(*) FROM crm_evento_importacoes i WHERE i.evento_id=e.id) total_importacoes FROM crm_eventos e WHERE e.ativo=1 ORDER BY e.data_evento DESC,e.id DESC")
 @classmethod
 def buscar_evento(cls,id): return cls.fetch_one("SELECT * FROM crm_eventos WHERE id=%s AND ativo=1",(id,))
 @classmethod
 def inserir_evento(cls,nome,data,created_by=None): return cls.execute_insert("INSERT INTO crm_eventos(uuid,nome_evento,data_evento,created_by) VALUES(%s,%s,%s,%s)",(cls.generate_uuid(),nome,data,created_by))
 @classmethod
 def atualizar_evento(cls,id,nome,data):
  return cls.execute("UPDATE crm_eventos SET nome_evento=%s,data_evento=%s WHERE id=%s AND ativo=1",(nome,data,id))
 @classmethod
 def inserir_importacao(cls,eid,nome,ext,total,mapping): return cls.execute_insert("INSERT INTO crm_evento_importacoes(uuid,evento_id,nome_arquivo,extensao,total_linhas,mapeamento_json) VALUES(%s,%s,%s,%s,%s,%s)",(cls.generate_uuid(),eid,nome,ext,total,json.dumps(mapping,ensure_ascii=False)))
 @classmethod
 def buscar_importacao(cls,id):
  row=cls.fetch_one("SELECT * FROM crm_evento_importacoes WHERE id=%s",(id,))
  if row:
   try: row["mapeamento"]=json.loads(row.get("mapeamento_json") or "{}")
   except (TypeError,ValueError): row["mapeamento"]={}
  return row
 @classmethod
 def atualizar_importacao(cls,id,status,validas,invalidas,duplicadas,mapping): return cls.execute("UPDATE crm_evento_importacoes SET status=%s,linhas_validas=%s,linhas_invalidas=%s,linhas_duplicadas=%s,mapeamento_json=%s WHERE id=%s",(status,validas,invalidas,duplicadas,json.dumps(mapping,ensure_ascii=False),id))
 @classmethod
 def inserir_participantes(cls,rows):
  if not rows:return 0
  return cls.execute_many("INSERT INTO crm_evento_participantes(uuid,evento_id,importacao_id,nome,telefone,email,empresa,cnpj,chave_deduplicacao) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",[(cls.generate_uuid(),r["evento_id"],r["importacao_id"],r["nome"],r.get("telefone"),r.get("email"),r.get("empresa"),r.get("cnpj"),r["chave_deduplicacao"]) for r in rows])
 @classmethod
 def inserir_participante_manual(cls,eid,d,usuario_email=None):
  import_id=cls.inserir_importacao(eid,"Cadastro manual","manual",1,{"origem":"manual","created_by":usuario_email})
  cls.atualizar_importacao(import_id,"CONFIRMADO",1,0,0,{"origem":"manual","created_by":usuario_email})
  cls.inserir_participantes([{**d,"evento_id":eid,"importacao_id":import_id}])
  return import_id
 @classmethod
 def listar_participantes(cls,eid,q=None,limit=100,offset=0):
  p=[eid]; w=["evento_id=%s"]
  if q:w.append("(nome LIKE %s OR empresa LIKE %s OR email LIKE %s)");t="%"+q+"%";p += [t,t,t]
  p += [limit,offset]
  return cls.fetch_all("SELECT * FROM crm_evento_participantes WHERE "+" AND ".join(w)+" ORDER BY nome LIMIT %s OFFSET %s",p)
 @classmethod
 def total_participantes(cls,eid,q=None):
  p=[eid]; w=["evento_id=%s"]
  if q:w.append("(nome LIKE %s OR empresa LIKE %s OR email LIKE %s)");t="%"+q+"%";p += [t,t,t]
  return cls.scalar("SELECT COUNT(*) FROM crm_evento_participantes WHERE "+" AND ".join(w),p) or 0
 @classmethod
 def listar_chaves(cls,eid): return [r["chave_deduplicacao"] for r in cls.fetch_all("SELECT chave_deduplicacao FROM crm_evento_participantes WHERE evento_id=%s",(eid,))]
 @classmethod
 def participante(cls,eid,pid): return cls.fetch_one("SELECT * FROM crm_evento_participantes WHERE evento_id=%s AND id=%s",(eid,pid))
 @classmethod
 def existe_chave_outro(cls,eid,pid,chave): return cls.fetch_one("SELECT id FROM crm_evento_participantes WHERE evento_id=%s AND id<>%s AND chave_deduplicacao=%s LIMIT 1",(eid,pid,chave))
 @classmethod
 def atualizar_participante(cls,eid,pid,d):
  return cls.execute("UPDATE crm_evento_participantes SET nome=%s,telefone=%s,email=%s,empresa=%s,cnpj=%s,chave_deduplicacao=%s WHERE evento_id=%s AND id=%s",(d["nome"],d.get("telefone"),d.get("email"),d.get("empresa"),d.get("cnpj"),d["chave_deduplicacao"],eid,pid))
 @classmethod
 def excluir_participante(cls,eid,pid): return cls.execute("DELETE FROM crm_evento_participantes WHERE evento_id=%s AND id=%s",(eid,pid))
 @classmethod
 def excluir_participantes(cls,eid,ids):
  ids=[int(i) for i in ids if str(i).isdigit()]
  if not ids:return 0
  marks=",".join(["%s"]*len(ids)); return cls.execute("DELETE FROM crm_evento_participantes WHERE evento_id=%s AND id IN ("+marks+")",[eid]+ids)

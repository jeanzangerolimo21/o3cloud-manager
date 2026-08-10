from app.repositories.base_repository import BaseRepository

class ConhecimentoRepository(BaseRepository):
 @classmethod
 def bases(cls): return cls.fetch_all("SELECT b.*,a.nome ambiente_nome,a.prefixo_proxmox,(SELECT COUNT(*) FROM kb_pastas p WHERE p.base_id=b.id) total_pastas,(SELECT COUNT(*) FROM kb_conhecimentos k WHERE k.base_id=b.id) total_conhecimentos,(SELECT COUNT(*) FROM kb_arquivos arq WHERE arq.base_id=b.id) total_arquivos FROM kb_bases b LEFT JOIN ambientes a ON a.id=b.ambiente_id WHERE b.ativo=1 ORDER BY b.nome")
 @classmethod
 def base(cls,id): return cls.fetch_one("SELECT b.*,a.nome ambiente_nome,a.prefixo_proxmox FROM kb_bases b LEFT JOIN ambientes a ON a.id=b.ambiente_id WHERE b.id=%s AND b.ativo=1",(id,))
 @classmethod
 def inserir_base(cls,nome,descricao,caminho,ambiente_id=None): return cls.execute_insert("INSERT INTO kb_bases(uuid,nome,descricao,caminho_relativo,ambiente_id) VALUES(%s,%s,%s,%s,%s)",(cls.generate_uuid(),nome,descricao,caminho,ambiente_id))
 @classmethod
 def atualizar_base(cls,id,nome,descricao,ambiente_id=None): return cls.execute("UPDATE kb_bases SET nome=%s,descricao=%s,ambiente_id=%s WHERE id=%s AND ativo=1",(nome,descricao,ambiente_id,id))
 @classmethod
 def todas_pastas(cls,base_id): return cls.fetch_all("SELECT * FROM kb_pastas WHERE base_id=%s ORDER BY caminho_relativo",(base_id,))
 @classmethod
 def pastas(cls,base_id,parent_id=None):
  if parent_id is None:return cls.fetch_all("SELECT * FROM kb_pastas WHERE base_id=%s AND parent_id IS NULL ORDER BY nome",(base_id,))
  return cls.fetch_all("SELECT * FROM kb_pastas WHERE base_id=%s AND parent_id=%s ORDER BY nome",(base_id,parent_id))
 @classmethod
 def pasta(cls,id): return cls.fetch_one("SELECT * FROM kb_pastas WHERE id=%s",(id,))
 @classmethod
 def inserir_pasta(cls,base_id,parent_id,nome,caminho): return cls.execute_insert("INSERT INTO kb_pastas(base_id,parent_id,nome,caminho_relativo) VALUES(%s,%s,%s,%s)",(base_id,parent_id,nome,caminho))
 @classmethod
 def conhecimentos(cls,base_id,pasta_id=None,q=None):
  w=["k.base_id=%s"];p=[base_id]
  if pasta_id is None:w.append("k.pasta_id IS NULL")
  else:w.append("k.pasta_id=%s");p.append(pasta_id)
  if q:w.append("(k.titulo LIKE %s OR k.tags LIKE %s OR k.conteudo_html LIKE %s)");t="%"+q+"%";p += [t,t,t]
  return cls.fetch_all("SELECT k.*,p.nome pasta_nome FROM kb_conhecimentos k LEFT JOIN kb_pastas p ON p.id=k.pasta_id WHERE "+" AND ".join(w)+" ORDER BY k.updated_at DESC",p)
 @classmethod
 def conhecimento(cls,id): return cls.fetch_one("SELECT k.*,p.nome pasta_nome,b.nome base_nome FROM kb_conhecimentos k JOIN kb_bases b ON b.id=k.base_id LEFT JOIN kb_pastas p ON p.id=k.pasta_id WHERE k.id=%s",(id,))
 @classmethod
 def inserir_conhecimento(cls,d): return cls.execute_insert("INSERT INTO kb_conhecimentos(uuid,base_id,pasta_id,titulo,conteudo_html,tags,catalogo,compartilhado,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(cls.generate_uuid(),d["base_id"],d.get("pasta_id"),d["titulo"],d.get("conteudo_html"),d.get("tags"),d.get("catalogo","Todos"),1 if d.get("compartilhado") else 0,d.get("created_by")))
 @classmethod
 def atualizar_conhecimento(cls,id,d): return cls.execute("UPDATE kb_conhecimentos SET pasta_id=%s,titulo=%s,conteudo_html=%s,tags=%s,catalogo=%s,compartilhado=%s WHERE id=%s",(d.get("pasta_id"),d["titulo"],d.get("conteudo_html"),d.get("tags"),d.get("catalogo","Todos"),1 if d.get("compartilhado") else 0,id))
 @classmethod
 def arquivos(cls,base_id,pasta_id=None,conhecimento_id=None):
  w=["base_id=%s"];p=[base_id]
  if conhecimento_id is not None:w.append("conhecimento_id=%s");p.append(conhecimento_id)
  elif pasta_id is None:w.append("pasta_id IS NULL AND conhecimento_id IS NULL")
  else:w.append("pasta_id=%s AND conhecimento_id IS NULL");p.append(pasta_id)
  return cls.fetch_all("SELECT * FROM kb_arquivos WHERE "+" AND ".join(w)+" ORDER BY nome_original",p)
 @classmethod
 def inserir_arquivo(cls,d): return cls.execute_insert("INSERT INTO kb_arquivos(base_id,pasta_id,conhecimento_id,nome_original,nome_armazenado,caminho_relativo,mime_type,tamanho) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(d["base_id"],d.get("pasta_id"),d.get("conhecimento_id"),d["nome_original"],d["nome_armazenado"],d["caminho_relativo"],d.get("mime_type"),d.get("tamanho",0)))

import re
import shutil
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from app.repositories.ambiente_repository import AmbienteRepository
from app.repositories.conhecimento_repository import ConhecimentoRepository

ROOT=Path("/opt/o3cloud-manager/storage/conhecimentos")
MAX_SIZE=25*1024*1024
ALLOWED={".pdf",".doc",".docx",".xls",".xlsx",".csv",".txt",".md",".zip",".png",".jpg",".jpeg",".gif",".webp",".svg",".ppt",".pptx"}

class ConhecimentoService:
 @staticmethod
 def contexto_base_form():
  return {"ambientes": AmbienteRepository.listar_ativos_para_select()}
 @classmethod
 def _normalizar_ambiente(cls, ambiente_id):
  try: ambiente_id=int(ambiente_id or 0)
  except (TypeError, ValueError): ambiente_id=0
  if not ambiente_id: return None
  ambiente=AmbienteRepository.buscar_por_id(ambiente_id)
  if not ambiente or not ambiente.get("ativo"):
   raise ValueError("Ambiente selecionado não encontrado ou inativo.")
  return ambiente_id
 @staticmethod
 def _segmento(value,label):
  value=secure_filename(value or "").strip("._-")
  if not value: raise ValueError(label+" inválido.")
  return value[:160]
 @classmethod
 def criar_base(cls,nome,descricao="",ambiente_id=None):
  nome=(nome or "").strip()
  if not nome: raise ValueError("Nome da base é obrigatório.")
  if len(nome)>160: raise ValueError("Nome da base deve possuir no máximo 160 caracteres.")
  ambiente_id=cls._normalizar_ambiente(ambiente_id)
  uid=str(uuid4()); ROOT.joinpath(uid).mkdir(parents=True,exist_ok=True)
  return ConhecimentoRepository.inserir_base(nome,descricao.strip()[:500],uid,ambiente_id)
 @classmethod
 def atualizar_base(cls,base_id,nome,descricao="",ambiente_id=None):
  nome=(nome or "").strip()
  if not nome: raise ValueError("Nome da base é obrigatório.")
  if len(nome)>160: raise ValueError("Nome da base deve possuir no máximo 160 caracteres.")
  ambiente_id=cls._normalizar_ambiente(ambiente_id)
  return ConhecimentoRepository.atualizar_base(base_id,nome,descricao.strip()[:500],ambiente_id)
 @classmethod
 def pasta(cls,base,parent,nome):
  base_row=ConhecimentoRepository.base(base)
  if not base_row: raise ValueError("Base não encontrada.")
  nome=cls._segmento(nome,"Nome da pasta")
  parent_row=ConhecimentoRepository.pasta(parent) if parent else None
  if parent_row and parent_row["base_id"]!=base: raise ValueError("Pasta pai inválida.")
  caminho=str(Path(parent_row["caminho_relativo"]) / nome) if parent_row else nome
  ROOT.joinpath(base_row["caminho_relativo"],caminho).mkdir(parents=True,exist_ok=True)
  return ConhecimentoRepository.inserir_pasta(base,parent or None,nome,caminho)
 @classmethod
 def salvar_arquivo(cls,base,arquivo,pasta=None,conhecimento=None):
  if not arquivo or not arquivo.filename: return None
  base_row=ConhecimentoRepository.base(base)
  if not base_row: raise ValueError("Base não encontrada.")
  nome=secure_filename(arquivo.filename)
  ext=Path(nome).suffix.lower()
  if ext not in ALLOWED: raise ValueError("Tipo de arquivo não permitido.")
  arquivo.seek(0,2);size=arquivo.tell();arquivo.seek(0)
  if size>MAX_SIZE: raise ValueError("Arquivo excede o limite de 25MB.")
  pasta_row=ConhecimentoRepository.pasta(pasta) if pasta else None
  if pasta_row and pasta_row["base_id"]!=base: raise ValueError("Pasta inválida.")
  rel=Path(base_row["caminho_relativo"])/(pasta_row["caminho_relativo"] if pasta_row else "_raiz")
  stored=uuid4().hex+"_"+nome; dest=ROOT/rel;dest.mkdir(parents=True,exist_ok=True);arquivo.save(dest/stored)
  caminho=str(rel/stored)
  return ConhecimentoRepository.inserir_arquivo({"base_id":base,"pasta_id":pasta,"conhecimento_id":conhecimento,"nome_original":arquivo.filename,"nome_armazenado":stored,"caminho_relativo":caminho,"mime_type":arquivo.mimetype,"tamanho":size})
 @staticmethod
 def apagar_arquivo(arquivo):
  path=ROOT/arquivo["caminho_relativo"]
  if path.exists():path.unlink()

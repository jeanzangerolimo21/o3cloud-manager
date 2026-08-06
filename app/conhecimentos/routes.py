import html
import re
from pathlib import Path
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from app.conhecimentos.service import ConhecimentoService, ROOT
from app.repositories.conhecimento_repository import ConhecimentoRepository

conhecimentos_bp=Blueprint("conhecimentos",__name__,url_prefix="/conhecimentos")

def _base_or_redirect(base_id):
 base=ConhecimentoRepository.base(base_id)
 return base

def _limpar_html(value):
 value=re.sub(r"<(script|style)[^>]*>.*?</\1>","",value or "",flags=re.I|re.S)
 return re.sub(r"\s(on[a-z]+|javascript:)[^>]*","",value,flags=re.I)

def _form():
 tags=re.sub(r"[\\r\\n]+",",",request.form.get("tags") or "")
 return {"titulo":(request.form.get("titulo") or "").strip(),"conteudo_html":request.form.get("conteudo_html") or "","tags":tags,"catalogo":request.form.get("catalogo") or "Todos","compartilhado":request.form.get("compartilhado")=="1","pasta_id":request.form.get("pasta_id") or None}

@conhecimentos_bp.route("/")
def index(): return render_template("conhecimentos/index.html",bases=ConhecimentoRepository.bases())

@conhecimentos_bp.route("/nova",methods=["GET","POST"])
def nova_base():
 if request.method=="POST":
  try: ConhecimentoService.criar_base(request.form.get("nome"),request.form.get("descricao",""))
  except ValueError as e: flash(str(e),"danger")
  else: flash("Base de conhecimento criada.","success");return redirect(url_for("conhecimentos.index"))
 return render_template("conhecimentos/base_form.html",base=None)

@conhecimentos_bp.route("/<int:base_id>/editar",methods=["GET","POST"])
def editar_base(base_id):
 base=_base_or_redirect(base_id)
 if not base: flash("Base não encontrada.","danger");return redirect(url_for("conhecimentos.index"))
 if request.method=="POST":
  nome=(request.form.get("nome") or "").strip()
  if not nome: flash("Nome da base é obrigatório.","danger")
  else: ConhecimentoRepository.atualizar_base(base_id,nome,request.form.get("descricao",""));flash("Base atualizada.","success");return redirect(url_for("conhecimentos.base",base_id=base_id))
 return render_template("conhecimentos/base_form.html",base=base)

@conhecimentos_bp.route("/<int:base_id>")
def base(base_id):
 b=_base_or_redirect(base_id)
 if not b: flash("Base não encontrada.","danger");return redirect(url_for("conhecimentos.index"))
 pasta_id=request.args.get("pasta",type=int)
 pasta=ConhecimentoRepository.pasta(pasta_id) if pasta_id else None
 if pasta and pasta["base_id"]!=base_id: pasta=None;pasta_id=None
 return render_template("conhecimentos/base.html",base=b,pasta=pasta,pastas=ConhecimentoRepository.pastas(base_id,pasta_id),conhecimentos=ConhecimentoRepository.conhecimentos(base_id,pasta_id,request.args.get("q")),arquivos=ConhecimentoRepository.arquivos(base_id,pasta_id))

@conhecimentos_bp.route("/<int:base_id>/pastas/nova",methods=["POST"])
def nova_pasta(base_id):
 try: ConhecimentoService.pasta(base_id,request.form.get("parent_id",type=int),request.form.get("nome"))
 except ValueError as e: flash(str(e),"danger")
 else: flash("Pasta criada.","success")
 return redirect(url_for("conhecimentos.base",base_id=base_id,pasta=request.form.get("parent_id",type=int) or None))

@conhecimentos_bp.route("/<int:base_id>/upload",methods=["POST"])
def upload(base_id):
 try: ConhecimentoService.salvar_arquivo(base_id,request.files.get("arquivo"),request.form.get("pasta_id",type=int))
 except ValueError as e: flash(str(e),"danger")
 else: flash("Arquivo enviado.","success")
 return redirect(url_for("conhecimentos.base",base_id=base_id,pasta=request.form.get("pasta_id",type=int) or None))

@conhecimentos_bp.route("/<int:base_id>/novo",methods=["GET","POST"])
def novo(base_id):
 b=_base_or_redirect(base_id)
 if not b: flash("Base não encontrada.","danger");return redirect(url_for("conhecimentos.index"))
 if request.method=="POST":
  d=_form();d["conteudo_html"]=_limpar_html(d["conteudo_html"])
  if not d["titulo"]: flash("Título do conhecimento é obrigatório.","danger")
  else:
   d["base_id"]=base_id;d["created_by"]=None
   kid=ConhecimentoRepository.inserir_conhecimento(d)
   for arquivo in request.files.getlist("anexos"):
    if arquivo.filename:
     try: ConhecimentoService.salvar_arquivo(base_id,arquivo,d.get("pasta_id"),kid)
     except ValueError as e: flash(str(e),"danger")
   flash("Conhecimento criado.","success");return redirect(url_for("conhecimentos.visualizar",knowledge_id=kid))
 return render_template("conhecimentos/form.html",base=b,conhecimento={"pasta_id":request.args.get("pasta_id",type=int)},pastas=ConhecimentoRepository.todas_pastas(base_id),modo="novo")

@conhecimentos_bp.route("/conhecimento/<int:knowledge_id>",methods=["GET"])
def visualizar(knowledge_id):
 k=ConhecimentoRepository.conhecimento(knowledge_id)
 if not k: flash("Conhecimento não encontrado.","danger");return redirect(url_for("conhecimentos.index"))
 return render_template("conhecimentos/view.html",conhecimento=k,arquivos=ConhecimentoRepository.arquivos(k["base_id"],conhecimento_id=knowledge_id))

@conhecimentos_bp.route("/conhecimento/<int:knowledge_id>/editar",methods=["GET","POST"])
def editar(knowledge_id):
 k=ConhecimentoRepository.conhecimento(knowledge_id)
 if not k: flash("Conhecimento não encontrado.","danger");return redirect(url_for("conhecimentos.index"))
 if request.method=="POST":
  d=_form();d["conteudo_html"]=_limpar_html(d["conteudo_html"]);d["base_id"]=k["base_id"];ConhecimentoRepository.atualizar_conhecimento(knowledge_id,d)
  for arquivo in request.files.getlist("anexos"):
   if arquivo.filename:
    try: ConhecimentoService.salvar_arquivo(k["base_id"],arquivo,d.get("pasta_id"),knowledge_id)
    except ValueError as e: flash(str(e),"danger")
  flash("Conhecimento atualizado.","success");return redirect(url_for("conhecimentos.visualizar",knowledge_id=knowledge_id))
 return render_template("conhecimentos/form.html",base=ConhecimentoRepository.base(k["base_id"]),conhecimento=k,pastas=ConhecimentoRepository.todas_pastas(k["base_id"]),modo="editar")

@conhecimentos_bp.route("/arquivo/<int:arquivo_id>")
def arquivo(arquivo_id):
 row=ConhecimentoRepository.fetch_one("SELECT * FROM kb_arquivos WHERE id=%s",(arquivo_id,))
 if not row: flash("Arquivo não encontrado.","danger");return redirect(url_for("conhecimentos.index"))
 path=ROOT/row["caminho_relativo"]
 if not path.is_file(): flash("Arquivo não encontrado no armazenamento.","danger");return redirect(url_for("conhecimentos.index"))
 return send_file(path,download_name=row["nome_original"],as_attachment=False)

@conhecimentos_bp.route("/conhecimento/<int:knowledge_id>/imagem",methods=["POST"])
def imagem(knowledge_id):
 k=ConhecimentoRepository.conhecimento(knowledge_id)
 if not k:return {"erro":"Conhecimento não encontrado"},404
 try:
  aid=ConhecimentoService.salvar_arquivo(k["base_id"],request.files.get("imagem"),None,knowledge_id)
  row=ConhecimentoRepository.fetch_one("SELECT * FROM kb_arquivos WHERE id=%s",(aid,))
  return {"url":url_for("conhecimentos.arquivo",arquivo_id=aid),"nome":row["nome_original"]}
 except ValueError as e:return {"erro":str(e)},400

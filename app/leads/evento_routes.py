import json
import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.leads.evento_importer import FIELD_LABELS, cnpj, digits, key, read_rows, suggest_mapping, validate_rows
from app.repositories.evento_repository import EventoRepository

eventos_bp = Blueprint("eventos", __name__, url_prefix="/leads/eventos")

@eventos_bp.route("/")
def index():
 return render_template("leads/eventos/index.html", eventos=EventoRepository.listar_eventos())

@eventos_bp.route("/novo", methods=["GET","POST"])
def novo():
 if request.method=="POST":
  nome=(request.form.get("nome_evento") or "").strip(); data=request.form.get("data_evento")
  if not nome or not data: flash("Informe o nome e a data do evento.","danger")
  else:
   EventoRepository.inserir_evento(nome,data)
   flash("Evento criado com sucesso.","success")
   return redirect(url_for("eventos.index"))
 return render_template("leads/eventos/form.html")

@eventos_bp.route("/<int:evento_id>/editar",methods=["GET","POST"])
def editar(evento_id):
 evento=EventoRepository.buscar_evento(evento_id)
 if not evento: flash("Evento não encontrado.","danger"); return redirect(url_for("eventos.index"))
 if request.method=="POST":
  nome=(request.form.get("nome_evento") or "").strip(); data=request.form.get("data_evento")
  if not nome or not data:
   flash("Informe o nome e a data do evento.","danger")
  elif len(nome)>180:
   flash("O nome do evento deve possuir no máximo 180 caracteres.","danger")
  else:
   EventoRepository.atualizar_evento(evento_id,nome,data)
   flash("Evento atualizado com sucesso.","success")
   return redirect(url_for("eventos.visualizar",evento_id=evento_id))
 return render_template("leads/eventos/form.html",evento=evento,modo="editar")

@eventos_bp.route("/<int:evento_id>")
def visualizar(evento_id):
 evento=EventoRepository.buscar_evento(evento_id)
 if not evento: flash("Evento não encontrado.","danger"); return redirect(url_for("eventos.index"))
 q=request.args.get("q"); pagina=max(1,request.args.get("page",1,type=int)); total=EventoRepository.total_participantes(evento_id,q); total_paginas=max(1,(total+99)//100); pagina=min(pagina,total_paginas); participantes=EventoRepository.listar_participantes(evento_id,q,100,(pagina-1)*100)
 return render_template("leads/eventos/view.html",evento=evento,participantes=participantes,total_participantes=total,pagina=pagina,total_paginas=total_paginas,pesquisa=q)

@eventos_bp.route("/<int:evento_id>/importar",methods=["GET","POST"])
def importar(evento_id):
 evento=EventoRepository.buscar_evento(evento_id)
 if not evento: flash("Evento não encontrado.","danger"); return redirect(url_for("eventos.index"))
 if request.method=="GET": return render_template("leads/eventos/import.html",evento=evento)
 try:
  ext,rows=read_rows(request.files.get("arquivo"))
  headers=rows[0]; mapping=suggest_mapping(headers)
  import_id=EventoRepository.inserir_importacao(evento_id,request.files["arquivo"].filename,ext,len(rows)-1,{"headers":headers,"rows":rows,"mapping":mapping})
  validacao=validate_rows(rows,mapping,EventoRepository.listar_chaves(evento_id))
  duplicadas=sum("Registro duplicado" in " ".join(r["erros"]) for r in validacao)
  EventoRepository.atualizar_importacao(import_id,"PREVIEW",sum(r["valido"] for r in validacao),sum(not r["valido"] for r in validacao),duplicadas,{"headers":headers,"rows":rows,"mapping":mapping})
  return render_template("leads/eventos/preview.html",evento=evento,import_id=import_id,headers=headers,mapping=mapping,validacao=validacao,labels=FIELD_LABELS)
 except (ValueError, KeyError) as erro:
  flash(str(erro),"danger"); return render_template("leads/eventos/import.html",evento=evento)

@eventos_bp.route("/<int:evento_id>/importar/<int:import_id>/confirmar",methods=["POST"])
def confirmar(evento_id,import_id):
 evento=EventoRepository.buscar_evento(evento_id); imp=EventoRepository.buscar_importacao(import_id)
 if not evento or not imp or imp["evento_id"]!=evento_id: flash("Importação não encontrada.","danger"); return redirect(url_for("eventos.index"))
 dados=imp.get("mapeamento") or {}; rows=dados.get("rows") or []
 mapping={f:request.form.get("map_"+f,"") for f in FIELD_LABELS}
 if not any(mapping.values()): mapping=dados.get("mapping") or {}
 validacao=validate_rows(rows,mapping,EventoRepository.listar_chaves(evento_id)); validos=[r for r in validacao if r["valido"]]
 for r in validos:r.update(evento_id=evento_id,importacao_id=import_id)
 EventoRepository.inserir_participantes(validos)
 dados["mapping"]=mapping
 EventoRepository.atualizar_importacao(import_id,"CONFIRMADO",len(validos),len(validacao)-len(validos),sum("Registro duplicado" in " ".join(r["erros"]) for r in validacao),dados)
 flash(f"{len(validos)} participante(s) importado(s).","success")
 return redirect(url_for("eventos.visualizar",evento_id=evento_id))

from app.core.auditoria import registrar_evento
from app.integracoes.brevo_service import BrevoService
from app.repositories.evento_email_repository import EventoEmailRepository
from werkzeug.utils import secure_filename

@eventos_bp.route("/<int:evento_id>/disparo-email",methods=["GET","POST"])
def preparar_disparo_email(evento_id):
 evento=EventoRepository.buscar_evento(evento_id)
 if not evento: flash("Evento não encontrado.","danger"); return redirect(url_for("eventos.index"))
 config=BrevoService.config()
 emails=EventoEmailRepository.destinatarios(evento_id)
 if request.method=="GET":
  return render_template("leads/eventos/disparo_email.html",evento=evento,config=config,total_destinatarios=len(emails),enviados_hoje=EventoEmailRepository.enviados_hoje(config["id"]) if config else 0)
 if not emails:
  flash("Este evento não possui participantes com e-mail válido.","warning"); return redirect(url_for("eventos.visualizar",evento_id=evento_id))
 assunto=(request.form.get("assunto") or "").strip()
 corpo=request.form.get("corpo_html") or ""
 if not assunto: flash("Informe o assunto do e-mail.","danger"); return render_template("leads/eventos/disparo_email.html",evento=evento,config=config,total_destinatarios=len(emails),enviados_hoje=0,form=request.form)
 if not corpo.strip(): flash("Informe o corpo do e-mail.","danger"); return render_template("leads/eventos/disparo_email.html",evento=evento,config=config,total_destinatarios=len(emails),enviados_hoje=0,form=request.form)
 if not config: flash("Nenhum serviço Brevo ativo foi configurado.","danger"); return render_template("leads/eventos/disparo_email.html",evento=evento,config=None,total_destinatarios=len(emails),enviados_hoje=0,form=request.form)
 limite=config.get("brevo_daily_limit")
 usados=EventoEmailRepository.enviados_hoje(config["id"])
 if limite and usados+len(emails)>limite:
  flash(f"Limite diário da Brevo excedido. Disponível: {max(0,limite-usados)} destinatário(s).","danger")
  return render_template("leads/eventos/disparo_email.html",evento=evento,config=config,total_destinatarios=len(emails),enviados_hoje=usados,form=request.form)
 arquivo=request.files.get("anexo"); anexo=None
 if arquivo and arquivo.filename:
  arquivo.seek(0,2); tamanho=arquivo.tell();arquivo.seek(0)
  if tamanho>10*1024*1024:
   flash("O anexo deve ter no máximo 10MB.","danger"); return render_template("leads/eventos/disparo_email.html",evento=evento,config=config,total_destinatarios=len(emails),enviados_hoje=usados,form=request.form)
  anexo={"name":secure_filename(arquivo.filename),"content":arquivo.read()}
 disparo_id=EventoEmailRepository.iniciar({"evento_id":evento_id,"config_email_id":config["id"],"assunto":assunto,"total_destinatarios":len(emails),"anexo_nome":anexo["name"] if anexo else None,"created_by":"sistema"})
 enviados=0; erro=None
 try:
  for inicio in range(0,len(emails),50):
   enviados+=BrevoService.enviar(config,assunto,corpo,emails[inicio:inicio+50],anexo)["enviados"]
  status="ENVIADO"
 except Exception as exc:
  erro=str(exc)[:1000]; status="PARCIAL" if enviados else "ERRO"
 EventoEmailRepository.finalizar(disparo_id,status,enviados,erro)
 registrar_evento("DISPARO_BREVO_"+status,"crm_eventos",evento_id,{"assunto":assunto,"total_destinatarios":len(emails),"total_enviados":enviados,"erro":erro})
 if erro: flash(f"Disparo interrompido após {enviados} envio(s): {erro}","danger")
 else: flash(f"Disparo enviado pela Brevo para {enviados} contato(s).","success")
 return redirect(url_for("eventos.visualizar",evento_id=evento_id))

@eventos_bp.route("/<int:evento_id>/participantes/<int:participante_id>/editar",methods=["GET","POST"])
def editar_participante(evento_id,participante_id):
 evento=EventoRepository.buscar_evento(evento_id); participante=EventoRepository.participante(evento_id,participante_id)
 if not evento or not participante:
  flash("Participante não encontrado neste evento.","danger"); return redirect(url_for("eventos.visualizar",evento_id=evento_id))
 if request.method=="POST":
  d={"nome":(request.form.get("nome") or "").strip()[:150],"telefone":digits(request.form.get("telefone"))[:30],"email":(request.form.get("email") or "").strip().lower()[:150],"empresa":(request.form.get("empresa") or "").strip()[:150],"cnpj":cnpj(request.form.get("cnpj"))}
  erros=[]
  if not d["nome"]: erros.append("Nome é obrigatório.")
  if not d["email"] and not d["telefone"]: erros.append("Informe e-mail ou telefone.")
  if d["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",d["email"]): erros.append("E-mail inválido.")
  if request.form.get("cnpj") and d["cnpj"] is None: erros.append("CNPJ inválido."); d["cnpj"]=""
  d["chave_deduplicacao"]=key(d)
  if EventoRepository.existe_chave_outro(evento_id,participante_id,d["chave_deduplicacao"]): erros.append("Já existe outro participante com este e-mail/telefone neste evento.")
  if erros:
   flash(" ".join(erros),"danger"); participante={**participante,**d}
  else:
   EventoRepository.atualizar_participante(evento_id,participante_id,d); flash("Participante atualizado.","success"); return redirect(url_for("eventos.visualizar",evento_id=evento_id))
 return render_template("leads/eventos/participante_form.html",evento=evento,participante=participante)

@eventos_bp.route("/<int:evento_id>/participantes/<int:participante_id>/excluir",methods=["POST"])
def excluir_participante(evento_id,participante_id):
 if not EventoRepository.participante(evento_id,participante_id):
  flash("Participante não encontrado neste evento.","danger")
 else:
  EventoRepository.excluir_participante(evento_id,participante_id); flash("Participante removido do evento.","success")
 return redirect(url_for("eventos.visualizar",evento_id=evento_id))

@eventos_bp.route("/<int:evento_id>/participantes/excluir",methods=["POST"])
def excluir_participantes(evento_id):
 evento=EventoRepository.buscar_evento(evento_id)
 ids=request.form.getlist("participante_ids")
 if not evento: flash("Evento não encontrado.","danger")
 elif not ids: flash("Selecione ao menos um participante.","warning")
 else:
  EventoRepository.excluir_participantes(evento_id,ids); flash(f"{len(ids)} participante(s) removido(s) do evento.","success")
 return redirect(url_for("eventos.visualizar",evento_id=evento_id,page=request.form.get("page",1),q=request.form.get("q","")))

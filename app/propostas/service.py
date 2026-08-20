import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from xml.sax.saxutils import escape


from app.catalogo.precos.repository import PrecoCatalogoRepository
from app.catalogo.recursos.repository import ProdutoRecursoRepository
from app.catalogo.produtos.service import ProdutoService
from app.clientes.service import ClienteService
from app.financeiro.inadimplencias_service import InadimplenciaService
from app.contatos.service import ContatoService
from app.core.storage import StorageService
from app.integracoes.clicksign.client import ClicksignClient
from app.integracoes.clicksign.client import ClicksignError
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.repositories.contrato_repository import ContratoRepository
from app.repositories.oportunidade_repository import OportunidadeRepository
from app.core.email import EmailService
from app.core.pdf_assinatura import extrair_data_assinatura_pdf
from app.repositories.proposta_repository import PropostaRepository

STATUS_PROPOSTA = {
    "RASCUNHO": "Rascunho",
    "EM_ANALISE": "Em Análise",
    "ENVIADA": "Enviada",
    "APROVADA": "Aprovada",
    "REJEITADA": "Rejeitada",
    "EXPIRADA": "Expirada",
    "CANCELADA": "Cancelada",
}

STATUS_CLICKSIGN = {
    "NAO_ENVIADO": "Não Enviado",
    "DOCUMENTO_GERADO": "Documento Gerado",
    "ENVIADO": "Enviado",
    "AGUARDANDO_ASSINATURAS": "Aguardando Assinaturas",
    "ASSINADO": "Assinado",
    "CONCLUIDO": "Concluído",
    "CANCELADO": "Cancelado",
    "ERRO": "Erro",
}

ACAO_CLICKSIGN = {
    "preparar": "DOCUMENTO_GERADO",
    "enviar": "ENVIADO",
    "aguardar": "AGUARDANDO_ASSINATURAS",
    "assinado": "ASSINADO",
    "concluir": "CONCLUIDO",
    "cancelar": "CANCELADO",
    "erro": "ERRO",
}


class PropostaService:
    repository = PropostaRepository
    MODELO_CONTRATO_CLICKSIGN = StorageService.BASE_STORAGE / StorageService.CONTRATOS / "Modelo_de_Contrato_O3CLOUD.pdf"
    MODELO_CONTRATO_DOCX = StorageService.BASE_STORAGE / StorageService.CONTRATOS / "Modelo_Contrato_O3Cloud.docx"

    @classmethod
    def listar(cls, pesquisa=None, status=None, ativo=None, clicksign_status=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status_ativo(ativo)
        propostas = cls.repository.listar(pesquisa=pesquisa, status=status, ativo=ativo_normalizado, clicksign_status=clicksign_status, limit=limit, offset=offset)
        pendencias = InadimplenciaService.clientes_com_pendencia([proposta.get("cliente_id") for proposta in propostas])
        for proposta in propostas:
            proposta["total_comentarios_internos"] = cls.repository.total_comentarios_internos(proposta.get("id"))
            proposta["pendencia_financeira"] = bool(pendencias.get(proposta.get("cliente_id")))
        total = cls.repository.total(pesquisa=pesquisa, status=status, ativo=ativo_normalizado, clicksign_status=clicksign_status)
        return propostas, total

    @classmethod
    def buscar_por_id(cls, proposta_id):
        proposta = cls.repository.buscar_por_id(proposta_id)
        if not proposta:
            return None
        return cls._decorar_proposta(proposta)

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def listar_contexto_form(cls, executivo_email=None):
        executivos = ParceiroExecutivoService.listar_todos_ativos()
        return {
            "oportunidades": OportunidadeRepository.listar_todos_ativos(),
            "clientes": ClienteService.listar_para_importacao(),
            "contatos": ContatoService.listar_todos_ativos("COMERCIAL"),
            "representantes_legais": ContatoService.listar_todos_ativos("REPRESENTANTE_LEGAL"),
            "executivos": executivos,
            "produtos_fechados": cls.listar_produtos_fechados(),
            "licencas_catalogo": PrecoCatalogoRepository.listar_licenciamento(),
            "recursos_servidor": ProdutoRecursoRepository.listar(),
            "executivo_padrao_id": cls.identificar_executivo_padrao(executivo_email, executivos),
            "codigo_sugerido": cls.gerar_codigo_proposta(),
            "clicksign_status_options": STATUS_CLICKSIGN,
        }

    @classmethod
    def listar_produtos_fechados(cls):
        produtos = ProdutoService.listar()
        ativos = [produto for produto in produtos if produto.get("ativo")]
        return sorted(ativos, key=lambda item: ((item.get("parceiro") or ""), (item.get("nome") or "")))

    @classmethod
    def identificar_executivo_padrao(cls, executivo_email, executivos=None):
        if not executivo_email:
            return None
        for executivo in executivos or ParceiroExecutivoService.listar_todos_ativos():
            if (executivo.get("email") or "").strip().lower() == executivo_email.strip().lower():
                return executivo.get("id")
        return None

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        InadimplenciaService.validar_operacao_cliente(dados.get("cliente_id"))
        dados["versao"] = cls.repository.proxima_versao(dados.get("oportunidade_id"))
        dados["codigo_proposta"] = dados.get("codigo_proposta") or cls.gerar_codigo_proposta()
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, proposta_id, dados):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        dados = cls.normalizar(dados)
        cls.validar(dados, proposta_id=proposta_id)
        dados["versao"] = proposta.get("versao")
        dados["codigo_proposta"] = proposta.get("codigo_proposta") or dados.get("codigo_proposta") or cls.gerar_codigo_proposta()
        dados["arquivo"] = dados.get("arquivo") or proposta.get("arquivo")
        return cls.repository.atualizar(proposta_id, dados)

    @classmethod
    def atualizar_status(cls, proposta_id, status):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        status = (status or "").strip().upper()
        if status not in STATUS_PROPOSTA:
            raise ValueError("Status da proposta inválido.")
        if status in ("REJEITADA", "EXPIRADA", "CANCELADA"):
            cls._cancelar_clicksign_se_pendente(proposta)
        cls.repository.atualizar_status(proposta_id, status, cls._semaforo_padrao(status))
        return cls.buscar_por_id(proposta_id)

    @classmethod
    def excluir(cls, proposta_id):
        proposta = cls.buscar_por_id(proposta_id)
        if proposta and proposta.get("arquivo"):
            StorageService.excluir(StorageService.PROPOSTAS, proposta.get("arquivo"))
        return cls.repository.excluir(proposta_id)

    @classmethod
    def excluir_em_massa(cls, proposta_ids):
        for proposta_id in proposta_ids:
            cls.excluir(proposta_id)

    @classmethod
    def contexto_comentarios_internos(cls, proposta_id, usuario_id=None, usuario_email=None, perfil_codigo=None):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            return None
        mostrar_todos = (perfil_codigo or "").upper() == "ADMIN"
        return {
            "proposta": proposta,
            "comentarios": cls.repository.listar_comentarios_internos(
                proposta_id,
                autor_email=usuario_email,
                mostrar_todos=mostrar_todos,
            ),
        }

    @classmethod
    def criar_comentario_interno(cls, proposta_id, dados, autor_email=None):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        comentario = cls._texto(dados.get("comentario"))
        if not comentario:
            raise ValueError("Comentário interno é obrigatório.")
        emails = cls._emails_form(dados, "emails_compartilhamento")
        comentario_id = cls.repository.inserir_comentario_interno(proposta_id, comentario, autor_email or "sistema")
        cls.repository.substituir_compartilhamentos_comentario(comentario_id, emails)
        resultado_email = cls._enviar_comentario_interno(proposta, comentario, autor_email, emails) if emails else {"enviado": False, "motivo": "sem_destinatarios"}
        return {"comentario_id": comentario_id, "emails": emails, "email": resultado_email}

    @classmethod
    def _enviar_comentario_interno(cls, proposta, comentario, autor_email, emails):
        assunto = f"Comentário interno da proposta - {proposta.get('codigo_proposta') or proposta.get('titulo') or proposta.get('id')}"
        corpo = "\n".join([
            f"Proposta: {proposta.get('codigo_proposta') or proposta.get('id')} - {proposta.get('titulo') or '-'}",
            f"Cliente: {proposta.get('cliente_nome') or '-'}",
            f"Status: {proposta.get('status_label') or proposta.get('status') or '-'}",
            f"Autor: {autor_email or 'sistema'}",
            "",
            comentario,
        ])
        try:
            return EmailService.enviar(assunto, corpo, emails)
        except Exception as erro:
            return {"enviado": False, "motivo": str(erro), "destinatarios": emails}

    @classmethod
    def _emails_form(cls, dados, chave):
        if hasattr(dados, "getlist"):
            valores = dados.getlist(chave)
        else:
            valor = dados.get(chave) or []
            valores = valor if isinstance(valor, (list, tuple, set)) else [valor]
        emails = []
        for valor in valores:
            partes = re.split(r"[,;\s]+", str(valor or ""))
            emails.extend(cls._normalizar_email(email) for email in partes)
        emails = [email for email in emails if email]
        invalidos = [email for email in emails if not cls._email_valido(email)]
        if invalidos:
            raise ValueError("E-mail(s) inválido(s): " + ", ".join(invalidos))
        return sorted(set(emails))

    @staticmethod
    def _email_valido(email):
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))

    @staticmethod
    def _normalizar_email(valor):
        return (valor or "").strip().lower()

    @staticmethod
    def _texto(valor):
        return (valor or "").strip()

    @classmethod
    def atualizar_status_clicksign(cls, proposta_id, acao, usuario_email=None):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        if acao == "sincronizar":
            return cls.sincronizar_status_clicksign(proposta, usuario_email)
        if acao not in ACAO_CLICKSIGN:
            raise ValueError("Ação de ClickSign inválida.")
        novo_status = ACAO_CLICKSIGN[acao]
        agora = datetime.now()
        eventos = list(proposta.get("clicksign_eventos") or [])
        descricao = {
            "DOCUMENTO_GERADO": "Documento preparado para envio ao ClickSign.",
            "ENVIADO": "Documento enviado ao ClickSign.",
            "AGUARDANDO_ASSINATURAS": "Documento aguardando assinaturas.",
            "ASSINADO": "Documento assinado eletronicamente.",
            "CONCLUIDO": "Fluxo de ClickSign concluído e pronto para contrato.",
            "CANCELADO": "Envelope cancelado na ClickSign.",
            "ERRO": "Fluxo de ClickSign marcado com pendência/erro.",
        }[novo_status]
        eventos.append({
            "status": novo_status,
            "descricao": descricao,
            "autor": usuario_email or "sistema",
            "data": agora.isoformat(timespec="seconds"),
        })
        atualizacao = {
            "clicksign_status": novo_status,
            "clicksign_eventos": json.dumps(eventos, ensure_ascii=False),
            "clicksign_last_sync_at": agora,
        }
        if novo_status == "CANCELADO":
            return cls._cancelar_clicksign_se_pendente(proposta, usuario_email)
        if novo_status == "DOCUMENTO_GERADO":
            if (proposta.get("clicksign_status") or "").upper() in ("ASSINADO", "CONCLUIDO"):
                raise ValueError("Esta proposta já consta como assinada na ClickSign. Não é permitido gerar um novo documento para este fluxo. Cancele a proposta atual e gere uma nova se houver alterações.")
            documento = cls.gerar_contrato_clicksign(proposta)
            atualizacao["clicksign_document_key"] = documento["nome"]
            atualizacao["clicksign_document_url"] = documento["url"]
        if novo_status == "ENVIADO":
            if proposta.get("clicksign_envelope_id"):
                raise ValueError("Esta proposta já foi enviada para a ClickSign. Para alterar dados ou contrato, cancele a proposta atual e gere uma nova proposta para evitar duplicidade de assinatura para o cliente.")
            try:
                documento, envio = cls.enviar_contrato_clicksign(proposta)
            except ClicksignError as erro:
                raise ValueError(str(erro)) from erro
            atualizacao["clicksign_document_key"] = documento["nome"]
            atualizacao["clicksign_document_url"] = documento["url"]
            atualizacao["clicksign_envelope_id"] = envio["envelope_id"]
            atualizacao["clicksign_sent_at"] = agora
            eventos[-1]["descricao"] = f"Documento enviado ao ClickSign. Envelope: {envio['envelope_id']}."
            eventos[-1]["clicksign"] = envio
            atualizacao["clicksign_eventos"] = json.dumps(eventos, ensure_ascii=False)
        if novo_status == "ASSINADO":
            atualizacao["clicksign_signed_at"] = agora
        if novo_status == "CONCLUIDO":
            if not proposta.get("clicksign_document_key"):
                documento = cls.gerar_contrato_clicksign(proposta)
                atualizacao["clicksign_document_key"] = documento["nome"]
                atualizacao["clicksign_document_url"] = documento["url"]
                proposta["clicksign_document_key"] = documento["nome"]
            contrato_id = cls.concluir_contrato_clicksign(proposta)
            atualizacao["clicksign_completed_at"] = agora
            atualizacao["clicksign_envelope_id"] = atualizacao.get("clicksign_envelope_id") or proposta.get("clicksign_envelope_id") or f"env-{proposta_id}-{agora.strftime('%Y%m%d%H%M%S')}"
            eventos[-1]["descricao"] = f"Fluxo concluido e contrato vinculado ao cadastro #{contrato_id}."
            atualizacao["clicksign_eventos"] = json.dumps(eventos, ensure_ascii=False)
        cls.repository.atualizar_clicksign(proposta_id, atualizacao)
        return cls.buscar_por_id(proposta_id)

    @classmethod
    def sincronizar_status_clicksign(cls, proposta, usuario_email=None):
        envelope_id = proposta.get("clicksign_envelope_id")
        if not envelope_id:
            raise ValueError("Envie o contrato para a ClickSign antes de sincronizar.")

        agora = datetime.now()
        client = ClicksignClient()
        try:
            envelope = client.consultar_envelope(envelope_id)
        except ClicksignError as erro:
            raise ValueError(str(erro)) from erro

        atributos = envelope.get("attributes") or {}
        status_api = (atributos.get("status") or "").lower()
        novo_status = cls._status_clicksign_por_envelope(status_api)
        eventos = list(proposta.get("clicksign_eventos") or [])
        arquivo_assinado = None
        data_assinatura_pdf = None
        descricao_evento = f"Status sincronizado com a ClickSign: {status_api or 'nao informado'}."
        if novo_status == "ASSINADO":
            arquivo_assinado = cls._baixar_contrato_assinado_clicksign(proposta, client, envelope_id)
            data_assinatura_pdf = extrair_data_assinatura_pdf(StorageService.BASE_STORAGE / StorageService.CONTRATOS / arquivo_assinado)
            descricao_evento += f" PDF assinado salvo em storage/contratos/{arquivo_assinado}."
        eventos.append({
            "status": novo_status,
            "descricao": descricao_evento,
            "autor": usuario_email or "sistema",
            "data": agora.isoformat(timespec="seconds"),
            "clicksign": {
                "envelope_id": envelope_id,
                "status": status_api,
                "modified": atributos.get("modified"),
                "arquivo_assinado": arquivo_assinado,
            },
        })
        atualizacao = {
            "clicksign_status": novo_status,
            "clicksign_document_key": arquivo_assinado,
            "clicksign_document_url": f"/propostas/{proposta.get('id')}/contrato" if arquivo_assinado else None,
            "clicksign_envelope_id": envelope_id,
            "clicksign_sent_at": None,
            "clicksign_signed_at": (data_assinatura_pdf or agora) if novo_status == "ASSINADO" else None,
            "clicksign_completed_at": None,
            "clicksign_last_sync_at": agora,
            "clicksign_eventos": json.dumps(eventos, ensure_ascii=False),
        }
        cls.repository.atualizar_clicksign(proposta.get("id"), atualizacao)
        return cls.buscar_por_id(proposta.get("id"))

    @classmethod
    def _baixar_contrato_assinado_clicksign(cls, proposta, client, envelope_id):
        download = client.baixar_documento_assinado(envelope_id)
        destino = StorageService.BASE_STORAGE / StorageService.CONTRATOS
        destino.mkdir(parents=True, exist_ok=True)
        nome = cls._nome_arquivo_contrato_assinado(proposta)
        caminho = destino / nome
        caminho.write_bytes(download["content"])
        return nome

    @staticmethod
    def _nome_arquivo_contrato_assinado(proposta):
        base = proposta.get("codigo_proposta") or f"proposta-{proposta.get('id')}"
        base = re.sub(r"[^A-Za-z0-9_-]+", "-", str(base).lower()).strip("-") or f"proposta-{proposta.get('id')}"
        return f"contrato-o3-{base}-assinado.pdf"

    @staticmethod
    def _status_clicksign_por_envelope(status_api):
        if status_api == "closed":
            return "ASSINADO"
        if status_api == "canceled":
            return "CANCELADO"
        if status_api == "running":
            return "AGUARDANDO_ASSINATURAS"
        if status_api in ("draft", "created"):
            return "ENVIADO"
        return "AGUARDANDO_ASSINATURAS"

    @classmethod
    def _cancelar_clicksign_se_pendente(cls, proposta, usuario_email=None):
        envelope_id = proposta.get("clicksign_envelope_id")
        if not envelope_id:
            return cls.buscar_por_id(proposta.get("id"))
        if (proposta.get("clicksign_status") or "").upper() == "CANCELADO":
            return cls.buscar_por_id(proposta.get("id"))
        if (proposta.get("clicksign_status") or "").upper() not in ("ENVIADO", "AGUARDANDO_ASSINATURAS"):
            return cls.buscar_por_id(proposta.get("id"))

        agora = datetime.now()
        client = ClicksignClient()
        try:
            envelope = client.cancelar_envelope(envelope_id)
        except ClicksignError as erro:
            raise ValueError(f"Não foi possível cancelar o envelope na ClickSign: {erro}") from erro

        eventos = list(proposta.get("clicksign_eventos") or [])
        eventos.append({
            "status": "CANCELADO",
            "descricao": f"Envelope cancelado na ClickSign. Envelope: {envelope_id}.",
            "autor": usuario_email or "sistema",
            "data": agora.isoformat(timespec="seconds"),
            "clicksign": {
                "envelope_id": envelope_id,
                "status": ((envelope.get("attributes") or {}).get("status") if isinstance(envelope, dict) else None) or "canceled",
            },
        })
        cls.repository.atualizar_clicksign(proposta.get("id"), {
            "clicksign_status": "CANCELADO",
            "clicksign_last_sync_at": agora,
            "clicksign_eventos": json.dumps(eventos, ensure_ascii=False),
        })
        return cls.buscar_por_id(proposta.get("id"))

    @classmethod
    def sincronizar_clicksign_pendentes(cls, usuario_email="sistema"):
        resultados = []
        for item in cls.repository.listar_clicksign_pendentes():
            proposta = cls.buscar_por_id(item.get("id"))
            if not proposta:
                continue
            try:
                atualizada = cls.sincronizar_status_clicksign(proposta, usuario_email)
                resultados.append({
                    "id": item.get("id"),
                    "codigo_proposta": item.get("codigo_proposta"),
                    "status": "OK",
                    "clicksign_status": atualizada.get("clicksign_status"),
                })
            except Exception as erro:
                resultados.append({
                    "id": item.get("id"),
                    "codigo_proposta": item.get("codigo_proposta"),
                    "status": "ERRO",
                    "erro": str(erro),
                })
        return resultados

    @classmethod
    def gerar_contrato_clicksign(cls, proposta):
        proposta = cls.buscar_por_id(proposta.get("id")) if proposta.get("id") else proposta
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        nome = cls._nome_arquivo_contrato(proposta)
        destino = StorageService.BASE_STORAGE / StorageService.CONTRATOS
        destino.mkdir(parents=True, exist_ok=True)
        caminho = destino / nome
        cls._gerar_contrato_pdf_modelo(proposta, caminho)
        return {
            "nome": nome,
            "url": f"/propostas/{proposta['id']}/contrato",
            "caminho": caminho,
        }

    @classmethod
    def enviar_contrato_clicksign(cls, proposta):
        proposta = cls.buscar_por_id(proposta.get("id")) if proposta.get("id") else proposta
        if not proposta:
            raise ClicksignError("Proposta nao encontrada para envio ao Clicksign.")

        documento = cls._documento_contrato_para_clicksign(proposta)
        cliente_nome = (
            proposta.get("cliente_razao_social")
            or proposta.get("cliente_nome")
            or proposta.get("cliente_nome_fantasia")
            or "Cliente"
        )
        envio = ClicksignClient().enviar_contrato(
            nome_envelope=f"Contrato O3 Cloud - {cliente_nome}"[:255],
            caminho_documento=documento["caminho"],
            nome_documento=documento["nome"],
            signatarios=cls._signatarios_clicksign(proposta),
        )
        return documento, envio

    @classmethod
    def _documento_contrato_para_clicksign(cls, proposta):
        nome = proposta.get("clicksign_document_key")
        if nome:
            caminho = StorageService.caminho(StorageService.CONTRATOS, nome)
            if caminho.exists() and caminho.suffix.lower() == ".pdf":
                return {
                    "nome": nome,
                    "url": f"/propostas/{proposta['id']}/contrato",
                    "caminho": caminho,
                }
        return cls.gerar_contrato_clicksign(proposta)

    @classmethod
    def _signatarios_clicksign(cls, proposta):
        return [
            cls._signatario_cliente_clicksign(proposta),
            cls._signatario_o3cloud_clicksign(),
        ]

    @classmethod
    def _signatario_cliente_clicksign(cls, proposta):
        representante = cls._representante_legal_clicksign(proposta)
        return {
            "name": representante.get("nome"),
            "email": representante.get("email"),
            "phone_number": representante.get("telefone") or representante.get("whatsapp"),
            "documentation": representante.get("cpf"),
        }

    @staticmethod
    def _representante_legal_clicksign(proposta):
        representante_id = PropostaService._normalizar_inteiro(proposta.get("representante_legal_id"))
        if representante_id:
            contato = ContatoService.buscar_por_id(representante_id)
            if not contato or not contato.get("ativo"):
                raise ClicksignError("Selecione um contato ativo do tipo Representante Legal antes de enviar o contrato para a ClickSign.")
            if contato.get("tipo_contato") != "REPRESENTANTE_LEGAL":
                raise ClicksignError("O contato selecionado para assinatura precisa ser do tipo Representante Legal.")
            if not PropostaService._cpf_valido_clicksign(contato.get("cpf")):
                raise ClicksignError("Cadastre o CPF do representante legal antes de enviar o contrato para a ClickSign.")
            return contato

        nomes_cliente = [
            proposta.get("cliente_razao_social"),
            proposta.get("cliente_nome_fantasia"),
            proposta.get("cliente_nome"),
            proposta.get("oportunidade_empresa"),
        ]
        chaves_cliente = {
            re.sub(r"[^a-z0-9]+", "", str(nome).lower())
            for nome in nomes_cliente
            if nome
        }
        for contato in ContatoService.listar_todos_ativos("REPRESENTANTE_LEGAL"):
            empresa = re.sub(r"[^a-z0-9]+", "", str(contato.get("empresa") or "").lower())
            if empresa and any(empresa in chave or chave in empresa for chave in chaves_cliente):
                if not PropostaService._cpf_valido_clicksign(contato.get("cpf")):
                    raise ClicksignError("Cadastre o CPF do representante legal antes de enviar o contrato para a ClickSign.")
                return contato
        raise ClicksignError("Selecione um contato ativo do tipo Representante Legal na proposta antes de enviar o contrato para a ClickSign. Caso ele não exista, cadastre pelo atalho de contato na proposta.")

    @staticmethod
    def _cpf_valido_clicksign(valor):
        return len(re.sub(r"\D+", "", str(valor or ""))) == 11

    @staticmethod
    def _signatario_o3cloud_clicksign():
        return {
            "name": os.getenv("CLICKSIGN_O3_SIGNER_NAME", "Jean Pierri de Carvalho Zangerolimo"),
            "email": os.getenv("CLICKSIGN_O3_SIGNER_EMAIL", "jean@o3cloud.com.br"),
            "phone_number": os.getenv("CLICKSIGN_O3_SIGNER_PHONE", ""),
            "documentation": os.getenv("CLICKSIGN_O3_SIGNER_DOCUMENTATION", ""),
        }

    @classmethod
    def caminho_contrato_clicksign(cls, proposta_id):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta or not proposta.get("clicksign_document_key"):
            return None, None
        caminho = StorageService.caminho(StorageService.CONTRATOS, proposta.get("clicksign_document_key"))
        if caminho.exists() and caminho.suffix.lower() == ".pdf":
            return caminho, proposta.get("clicksign_document_key")
        documento = cls.gerar_contrato_clicksign(proposta)
        cls.repository.atualizar_clicksign(proposta_id, {
            "clicksign_status": proposta.get("clicksign_status") or "DOCUMENTO_GERADO",
            "clicksign_document_key": documento["nome"],
            "clicksign_document_url": documento["url"],
            "clicksign_envelope_id": None,
            "clicksign_sent_at": None,
            "clicksign_signed_at": None,
            "clicksign_completed_at": None,
            "clicksign_last_sync_at": datetime.now(),
            "clicksign_eventos": json.dumps(proposta.get("clicksign_eventos") or [], ensure_ascii=False),
        })
        return documento["caminho"], documento["nome"]

    @classmethod
    def concluir_contrato_clicksign(cls, proposta):
        proposta = cls.buscar_por_id(proposta.get("id")) if proposta.get("id") else proposta
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        documento = proposta.get("clicksign_document_key") or cls.gerar_contrato_clicksign(proposta)["nome"]
        data_assinatura = extrair_data_assinatura_pdf(StorageService.BASE_STORAGE / StorageService.CONTRATOS / documento)
        contrato = ContratoRepository.buscar_por_proposta_id(proposta.get("id"))
        if contrato:
            ContratoRepository.atualizar_arquivo_assinado(contrato["id"], documento, documento, data_assinatura)
            return contrato["id"]
        dados = cls._dados_contrato_da_proposta(proposta, documento)
        contrato_id = ContratoRepository.inserir_manual(dados)
        ContratoRepository.atualizar_arquivo_assinado(contrato_id, documento, documento, data_assinatura)
        return contrato_id

    @classmethod
    def _dados_contrato_da_proposta(cls, proposta, documento):
        representante = cls._representante_legal_clicksign(proposta)
        valor_setup = (proposta.get("setup_ambiente_cloud") or Decimal("0.00")) + (proposta.get("instalacao_servidores") or Decimal("0.00"))
        quantidade_usuarios = sum(cls._normalizar_inteiro(item.get("quantidade")) or 0 for item in proposta.get("licencas_items") or []) or None
        return {
            "cliente_id": proposta.get("cliente_id"),
            "contato_id": representante.get("id"),
            "proposta_id": proposta.get("id"),
            "numero": proposta.get("codigo_proposta") or f"PROP-{proposta.get('id')}",
            "descricao": proposta.get("titulo"),
            "status": "CONCLUIDO",
            "inicio_vigencia": None,
            "fim_vigencia": None,
            "contato_nome": representante.get("nome"),
            "contato_email": representante.get("email"),
            "contato_telefone": representante.get("telefone") or representante.get("whatsapp"),
            "data_fechamento": date.today(),
            "executivo_id": proposta.get("executivo_responsavel_id"),
            "parceiro_id": proposta.get("parceiro_id"),
            "tipo_venda": "USUARIO",
            "valor_mensal": proposta.get("total_mensal"),
            "valor_setup": valor_setup,
            "valor_projeto": proposta.get("parametrizacao_sistema"),
            "valor_promocional": None,
            "quantidade_usuarios": quantidade_usuarios,
            "data_inicio_recorrencia": None,
            "data_ativacao": None,
            "dia_faturamento": None,
            "observacoes": proposta.get("condicoes_comerciais") or proposta.get("observacoes"),
            "arquivo_preparado": documento,
            "arquivo_preparado_original": documento,
        }

    @staticmethod
    def _nome_arquivo_contrato(proposta):
        codigo = proposta.get("codigo_proposta") or f"proposta-{proposta.get('id')}"
        seguro = re.sub(r"[^A-Za-z0-9_.-]+", "-", codigo).strip("-._").lower() or f"proposta-{proposta.get('id')}"
        return f"contrato-{seguro}.pdf"

    @classmethod
    def _gerar_contrato_pdf_modelo(cls, proposta, caminho_pdf):
        if cls.MODELO_CONTRATO_DOCX.exists():
            cls._gerar_contrato_pdf_docx(proposta, caminho_pdf)
            return
        cls._gerar_contrato_pdf_fallback(proposta, caminho_pdf)

    @classmethod
    def _gerar_contrato_pdf_docx(cls, proposta, caminho_pdf):
        libreoffice = shutil.which("libreoffice")
        if not libreoffice:
            raise ValueError("LibreOffice não encontrado no servidor para gerar o PDF do contrato.")
        with tempfile.TemporaryDirectory(prefix="o3-contrato-docx-") as temporario:
            temp_path = Path(temporario)
            home_path = temp_path / "home"
            home_path.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["HOME"] = str(home_path)
            docx_preenchido = temp_path / "contrato-preenchido.docx"
            cls._preencher_docx(cls.MODELO_CONTRATO_DOCX, docx_preenchido, cls._placeholders_contrato_docx(proposta))
            cls._executar_libreoffice(
                [libreoffice, "--headless", "--convert-to", "pdf", "--outdir", str(temp_path), str(docx_preenchido)],
                env,
            )
            pdf_preenchido = docx_preenchido.with_suffix(".pdf")
            if not pdf_preenchido.exists():
                raise ValueError("Não foi possível exportar o contrato DOCX preenchido para PDF.")
            shutil.copyfile(pdf_preenchido, caminho_pdf)

    @classmethod
    def _preencher_docx(cls, modelo, destino, placeholders):
        with ZipFile(modelo, "r") as origem, ZipFile(destino, "w", ZIP_DEFLATED) as saida:
            for item in origem.infolist():
                conteudo = origem.read(item.filename)
                if item.filename.endswith(".xml"):
                    texto = conteudo.decode("utf-8")
                    if item.filename == "word/document.xml":
                        texto = cls._ajustar_logo_docx(texto)
                    for marcador, valor in placeholders.items():
                        texto = texto.replace(marcador, escape(valor or ""))
                    conteudo = texto.encode("utf-8")
                saida.writestr(item, conteudo)

    @staticmethod
    def _ajustar_logo_docx(texto):
        tamanho = "684000"
        texto = re.sub(r'(<wp:inline[^>]*>\s*<wp:extent cx=")[0-9]+(" cy=")[0-9]+("/>)', rf'\g<1>{tamanho}\g<2>{tamanho}\g<3>', texto, count=1)
        texto = re.sub(r'(<a:ext cx=")[0-9]+(" cy=")[0-9]+("/>\s*</a:xfrm>)', rf'\g<1>{tamanho}\g<2>{tamanho}\g<3>', texto, count=1)
        return texto

    @classmethod
    def _gerar_contrato_pdf_fallback(cls, proposta, caminho_pdf):
        modelo = cls.MODELO_CONTRATO_CLICKSIGN
        if not modelo.exists():
            raise ValueError(f"Modelo de contrato não encontrado: {modelo}")
        libreoffice = shutil.which("libreoffice")
        if not libreoffice:
            raise ValueError("LibreOffice não encontrado no servidor para gerar o PDF do contrato.")
        with tempfile.TemporaryDirectory(prefix="o3-contrato-") as temporario:
            temp_path = Path(temporario)
            home_path = temp_path / "home"
            home_path.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["HOME"] = str(home_path)
            cls._executar_libreoffice(
                [libreoffice, "--headless", "--convert-to", "fodg", "--outdir", str(temp_path), str(modelo)],
                env,
            )
            fodg_modelo = temp_path / f"{modelo.stem}.fodg"
            if not fodg_modelo.exists():
                raise ValueError("Não foi possível converter o modelo PDF para edição.")
            conteudo = fodg_modelo.read_text(encoding="utf-8")
            conteudo = cls._ajustar_layout_fodg(conteudo)
            for marcador, valor in cls._placeholders_contrato(proposta).items():
                conteudo = conteudo.replace(marcador, cls._texto_fodg(valor or ""))
            fodg_preenchido = temp_path / "contrato-preenchido.fodg"
            fodg_preenchido.write_text(conteudo, encoding="utf-8")
            cls._executar_libreoffice(
                [libreoffice, "--headless", "--convert-to", "pdf", "--outdir", str(temp_path), str(fodg_preenchido)],
                env,
            )
            pdf_preenchido = fodg_preenchido.with_suffix(".pdf")
            if not pdf_preenchido.exists():
                raise ValueError("Não foi possível exportar o contrato preenchido para PDF.")
            shutil.copyfile(pdf_preenchido, caminho_pdf)

    @staticmethod
    def _executar_libreoffice(comando, env):
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True, timeout=90)
        if resultado.returncode != 0:
            detalhe = (resultado.stderr or resultado.stdout or "").strip()
            raise ValueError(f"Falha ao executar LibreOffice: {detalhe or resultado.returncode}")

    @classmethod
    def _ajustar_layout_fodg(cls, conteudo):
        for marcador, largura, altura in (
            ("[NOME_DO_CLIENTE]", "8.8cm", None),
            ("[SOFTWARE_DO_CLIENTE]", "10.4cm", None),
            ("[ITENS_LICENCA_SERVERS_CUSTOMER_TABLES]", "17.2cm", None),
            ("[NOME_REPRESENTANTE]", "5.4cm", None),
            ("[CARGO_REPRESENTANTE]", "5.4cm", None),
            ("[CPF_REPRESENTANTE]", "5.4cm", None),
        ):
            conteudo = cls._redimensionar_frames_placeholder(conteudo, marcador, largura, altura)
        return conteudo

    @staticmethod
    def _padronizar_margem_esquerda(conteudo):
        def ajustar(match):
            tag = match.group(0)
            x_match = re.search(r'svg:x="([0-9.]+)cm"', tag)
            width_match = re.search(r'svg:width="([0-9.]+)cm"', tag)
            if not x_match or not width_match:
                return tag
            x = float(x_match.group(1))
            width = float(width_match.group(1))
            margem = 1.95
            if x >= margem or width <= 1:
                return tag
            delta = margem - x
            nova_largura = max(width - delta, 1.0)
            tag = re.sub(r'svg:x="[0-9.]+cm"', f'svg:x="{margem:.3f}cm"', tag, count=1)
            tag = re.sub(r'svg:width="[0-9.]+cm"', f'svg:width="{nova_largura:.3f}cm"', tag, count=1)
            return tag
        return re.sub(r'<draw:frame\b[^>]*>', ajustar, conteudo)

    @staticmethod
    def _redimensionar_frames_placeholder(conteudo, marcador, largura, altura=None):
        partes = []
        pos = 0
        abertura = "<draw:frame"
        fechamento = "</draw:frame>"
        while True:
            inicio = conteudo.find(abertura, pos)
            if inicio < 0:
                partes.append(conteudo[pos:])
                break
            fim = conteudo.find(fechamento, inicio)
            if fim < 0:
                partes.append(conteudo[pos:])
                break
            fim += len(fechamento)
            partes.append(conteudo[pos:inicio])
            frame = conteudo[inicio:fim]
            if marcador in frame:
                texto_frame = re.sub(r"<[^>]+>", " ", frame)
                if not any(trecho in texto_frame for trecho in ("de outro lado", "doravante", "neste ato representada", "inscrita no CNPJ")):
                    frame = re.sub(r'svg:width="[^"]+"', f'svg:width="{largura}"', frame, count=1)
                    if altura:
                        frame = re.sub(r'svg:height="[^"]+"', f'svg:height="{altura}"', frame, count=1)
            partes.append(frame)
            pos = fim
        return "".join(partes)

    @classmethod
    def _placeholders_contrato_docx(cls, proposta):
        placeholders = cls._placeholders_contrato(proposta)
        return {marcador: re.sub(r"\s+", " ", str(valor or "")).strip() for marcador, valor in placeholders.items()}

    @classmethod
    def _placeholders_contrato(cls, proposta):
        nome_cliente = proposta.get("cliente_razao_social") or proposta.get("cliente_nome") or proposta.get("cliente_nome_fantasia") or ""
        nome_fantasia = proposta.get("cliente_nome_fantasia") or proposta.get("cliente_nome") or nome_cliente
        contato_nome = proposta.get("representante_legal_nome") or proposta.get("contato_nome") or ""
        cargo = proposta.get("representante_legal_cargo") or proposta.get("contato_cargo") or "Representante legal"
        prazo = cls._normalizar_inteiro(proposta.get("prazo_contratual_meses"), 24) or 24
        software = cls._software_cliente(proposta)
        return {
            "[SOFTWARE_DO_CLIENTE]": cls._quebrar_texto(software, 36, 3),
            "[NUMERO_PROPOSTA]": proposta.get("codigo_proposta") or f"PROP-{proposta.get('id')}",
            "[NOME_DO_CLIENTE]": nome_cliente,
            "[CNPJ_DO_CLIENTE]": proposta.get("cliente_cnpj") or "",
            "[DATA_ASSINATURA]": cls._data_br(date.today()),
            "[VENDEDOR_NOME]": proposta.get("executivo_nome") or "",
            "[VENDEDOR_EMAIL]": proposta.get("executivo_email") or "",
            "[VENDEDOR_TELEFONE]": proposta.get("executivo_telefone") or "",
            "[ENDERECO_DO_CLIENTE]": cls._endereco_cliente(proposta),
            "[NOME_REPRESENTANTE]": contato_nome,
            "[CARGO_REPRESENTANTE]": cargo,
            "[CPF_REPRESENTANTE]": proposta.get("representante_legal_cpf") or proposta.get("contato_cpf") or "",
            "[VALOR_SETUP]": cls._moeda_sem_prefixo(proposta.get("setup_ambiente_cloud")),
            "[VALOR_PROJETO]": cls._moeda_sem_prefixo(proposta.get("parametrizacao_sistema")),
            "[TOTAL_INSTALACAO]": cls._moeda_sem_prefixo(proposta.get("total_instalacao")),
            "[ITENS_LICENCA_SERVERS_CUSTOMER_TABLES]": cls._itens_contrato_texto(proposta),
            "[TOTAL_MENSAL]": cls._moeda_sem_prefixo(proposta.get("total_mensal")),
            "[PAYMENT_DAYS]": str(proposta.get("mensalidade_dias") or 30),
            "[SETUP_DAYS]": str(proposta.get("setup_dias") or 7),
            "[QTD_MESES]": str(prazo),
            "[QTD_MESES_POR_EXTENSO]": cls._numero_por_extenso(prazo),
            "[DETALHES_ADICIONAIS_CLIENTE]": cls._detalhes_adicionais_contrato(proposta),
            "[NOME_FANTASIA]": nome_fantasia,
            "[TOTAL_GERAL]": cls._moeda_sem_prefixo(proposta.get("valor_total")),
        }

    @classmethod
    def _software_cliente(cls, proposta):
        softwares = []
        for item in proposta.get("licencas_items") or []:
            nome = item.get("software") or item.get("produto") or item.get("descricao")
            if nome and nome not in softwares:
                softwares.append(nome)
        if softwares:
            return ", ".join(softwares[:3])
        return proposta.get("titulo") or "Projeto O3 Cloud"

    @classmethod
    def _itens_contrato_texto(cls, proposta):
        itens = []
        for item in proposta.get("licencas_items") or []:
            nome = re.sub(r"\s+", " ", item.get("software") or item.get("produto") or item.get("descricao") or "Licença").strip()
            itens.append(f"{nome} ({item.get('quantidade') or 1})")
        for item in proposta.get("servidores_items") or []:
            nome = re.sub(r"\s+", " ", item.get("nome") or item.get("descricao") or "Servidor").strip()
            itens.append(f"{nome} ({item.get('quantidade') or 1})")
        if not itens:
            return "Não informado"
        if len(itens) > 4:
            return f"{len(itens)} itens recorrentes conforme proposta comercial vinculada."
        return "; ".join(itens)

    @staticmethod
    def _limitar_texto(valor, limite):
        texto = re.sub(r"\s+", " ", str(valor or "")).strip()
        if len(texto) <= limite:
            return texto
        return texto[: max(limite - 3, 0)].rstrip() + "..."

    @staticmethod
    def _quebrar_texto(valor, largura, max_linhas=None):
        palavras = re.sub(r"\s+", " ", str(valor or "")).strip().split(" ")
        linhas = []
        atual = ""
        for palavra in palavras:
            candidato = f"{atual} {palavra}".strip()
            if len(candidato) <= largura:
                atual = candidato
                continue
            if atual:
                linhas.append(atual)
            atual = palavra
        if atual:
            linhas.append(atual)
        if max_linhas and len(linhas) > max_linhas:
            linhas = linhas[:max_linhas]
        return "\n".join(linhas)

    @staticmethod
    def _texto_fodg(valor):
        linhas = str(valor or "").splitlines() or [""]
        return "<text:line-break/>".join(escape(linha) for linha in linhas)

    @staticmethod
    def _detalhes_adicionais_contrato(proposta):
        partes = [
            proposta.get("detalhes_negociacao"),
            proposta.get("condicoes_comerciais"),
            proposta.get("observacoes"),
        ]
        texto = " | ".join(str(parte).strip() for parte in partes if parte and str(parte).strip())
        return texto or "Não informado"

    @staticmethod
    def _endereco_cliente(proposta):
        cidade = proposta.get("cliente_cidade")
        estado = proposta.get("cliente_estado")
        if cidade and estado:
            return f"{cidade}/{estado}"
        return cidade or estado or "Não informado"

    @staticmethod
    def _moeda_sem_prefixo(valor):
        decimal = PropostaService._decimal(valor) or Decimal("0.00")
        texto = f"{decimal:,.2f}"
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _data_br(valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
        return str(valor or "")

    @staticmethod
    def _numero_por_extenso(numero):
        mapa = {
            1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis",
            7: "sete", 8: "oito", 9: "nove", 10: "dez", 11: "onze", 12: "doze",
            13: "treze", 14: "quatorze", 15: "quinze", 16: "dezesseis", 17: "dezessete",
            18: "dezoito", 19: "dezenove", 20: "vinte", 21: "vinte e um", 22: "vinte e dois",
            23: "vinte e três", 24: "vinte e quatro", 25: "vinte e cinco", 26: "vinte e seis",
            27: "vinte e sete", 28: "vinte e oito", 29: "vinte e nove", 30: "trinta",
            31: "trinta e um", 32: "trinta e dois", 33: "trinta e três", 34: "trinta e quatro",
            35: "trinta e cinco", 36: "trinta e seis", 48: "quarenta e oito", 60: "sessenta",
        }
        return mapa.get(numero, str(numero))

    @classmethod
    def preparar_form_payload(cls, dados=None, codigo_sugerido=None):
        dados = dict(dados or {})
        licencas_items = cls._preparar_licencas_form(dados.get("licencas_snapshot"), dados.get("licencas_items"))
        servidores_items = cls._preparar_servidores_form(dados.get("servidores_snapshot"), dados.get("servidores_items"))
        return {
            "id": dados.get("id"),
            "oportunidade_id": dados.get("oportunidade_id"),
            "cliente_id": dados.get("cliente_id"),
            "cliente_razao_social": dados.get("cliente_razao_social") or "",
            "cliente_nome_fantasia": dados.get("cliente_nome_fantasia") or "",
            "cliente_cnpj": dados.get("cliente_cnpj") or "",
            "contato_id": dados.get("contato_id"),
            "representante_legal_id": dados.get("representante_legal_id"),
            "parceiro_id": dados.get("parceiro_id"),
            "executivo_responsavel_id": dados.get("executivo_responsavel_id"),
            "codigo_proposta": dados.get("codigo_proposta") or codigo_sugerido or cls.gerar_codigo_proposta(),
            "titulo": dados.get("titulo") or "",
            "status": dados.get("status") or "RASCUNHO",
            "validade": cls._string_data(dados.get("validade")),
            "setup_dias": dados.get("setup_dias") or 7,
            "mensalidade_dias": dados.get("mensalidade_dias") or 30,
            "prazo_contratual_meses": dados.get("prazo_contratual_meses") or 24,
            "detalhes_negociacao": dados.get("detalhes_negociacao") or "",
            "condicoes_comerciais": dados.get("condicoes_comerciais") or "",
            "observacoes": dados.get("observacoes") or "",
            "comentarios_comerciais": dados.get("comentarios_comerciais") or "",
            "semaforo_fechamento": dados.get("semaforo_fechamento") or cls._semaforo_padrao(dados.get("status")),
            "cliente_nome": dados.get("cliente_nome") or "",
            "contato_nome": dados.get("contato_nome") or "",
            "contato_email": dados.get("contato_email") or "",
            "contato_telefone": dados.get("contato_telefone") or "",
            "executivo_nome": dados.get("executivo_nome") or "",
            "executivo_email": dados.get("executivo_email") or "",
            "executivo_telefone": dados.get("executivo_telefone") or "",
            "parametrizacao_sistema": cls._string_decimal(dados.get("parametrizacao_sistema"), "0.00"),
            "setup_ambiente_cloud": cls._string_decimal(dados.get("setup_ambiente_cloud"), "0.00"),
            "total_mensal": cls._string_decimal(dados.get("total_mensal"), "0.00"),
            "total_instalacao": cls._string_decimal(dados.get("total_instalacao"), "0.00"),
            "valor_total": cls._string_decimal(dados.get("valor_total"), "0.00"),
            "licencas_snapshot": dados.get("licencas_snapshot") or "[]",
            "servidores_snapshot": dados.get("servidores_snapshot") or "[]",
            "arquivo": dados.get("arquivo") or "",
            "clicksign_status": dados.get("clicksign_status") or "NAO_ENVIADO",
            "clicksign_document_key": dados.get("clicksign_document_key") or "",
            "clicksign_document_url": dados.get("clicksign_document_url") or "",
            "clicksign_envelope_id": dados.get("clicksign_envelope_id") or "",
            "clicksign_sent_at": cls._string_datetime(dados.get("clicksign_sent_at")),
            "clicksign_signed_at": cls._string_datetime(dados.get("clicksign_signed_at")),
            "clicksign_completed_at": cls._string_datetime(dados.get("clicksign_completed_at")),
            "clicksign_last_sync_at": cls._string_datetime(dados.get("clicksign_last_sync_at")),
            "clicksign_eventos": cls._carregar_lista_json(dados.get("clicksign_eventos"), dados.get("clicksign_eventos_items")),
            "licencas_items": licencas_items,
            "servidores_items": servidores_items,
            "ativo": str(dados.get("ativo", "1")) in ("1", "true", "True", "on") or dados.get("ativo") is True,
        }

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        for campo in ("oportunidade_id", "cliente_id", "contato_id", "representante_legal_id", "parceiro_id", "executivo_responsavel_id"):
            dados[campo] = cls._normalizar_inteiro(dados.get(campo))
        dados["codigo_proposta"] = (dados.get("codigo_proposta") or "").strip()
        dados["titulo"] = (dados.get("titulo") or "").strip()
        dados["status"] = (dados.get("status") or "RASCUNHO").strip().upper()
        dados["validade"] = cls._normalizar_data(dados.get("validade"))
        dados["setup_dias"] = cls._normalizar_inteiro(dados.get("setup_dias"), 7)
        dados["mensalidade_dias"] = cls._normalizar_inteiro(dados.get("mensalidade_dias"), 30)
        dados["prazo_contratual_meses"] = cls._normalizar_inteiro(dados.get("prazo_contratual_meses"), 24)
        for campo in ("detalhes_negociacao", "condicoes_comerciais", "observacoes", "comentarios_comerciais", "cliente_nome", "contato_nome", "contato_telefone", "executivo_nome", "executivo_telefone"):
            dados[campo] = (dados.get(campo) or "").strip()
        dados["semaforo_fechamento"] = (dados.get("semaforo_fechamento") or cls._semaforo_padrao(dados.get("status"))).strip().upper()
        dados["contato_email"] = (dados.get("contato_email") or "").strip().lower()
        dados["executivo_email"] = (dados.get("executivo_email") or "").strip().lower()
        dados["licencas_items"] = cls._normalizar_licencas(dados.get("licencas_snapshot"))
        dados["servidores_items"] = cls._normalizar_servidores(dados.get("servidores_snapshot"))
        cls._herdar_relacionamentos(dados)
        resumo = cls._calcular_totais(dados["licencas_items"], dados["servidores_items"])
        dados["total_mensal"] = resumo["total_mensal"]
        parametrizacao = cls._decimal(dados.get("parametrizacao_sistema"))
        setup_cloud = cls._decimal(dados.get("setup_ambiente_cloud"))
        dados["parametrizacao_sistema"] = parametrizacao if parametrizacao is not None else resumo["total_mensal"]
        dados["setup_ambiente_cloud"] = setup_cloud if setup_cloud is not None else resumo["total_mensal"]
        dados["total_setup"] = dados["parametrizacao_sistema"] + dados["setup_ambiente_cloud"]
        dados["total_instalacao"] = resumo["instalacao_servidores"] + dados["parametrizacao_sistema"] + dados["setup_ambiente_cloud"]
        dados["valor_total"] = dados["total_mensal"] + dados["total_instalacao"]
        dados["itens_snapshot"] = cls._montar_itens_snapshot(dados["licencas_items"], dados["servidores_items"])
        dados["licencas_snapshot"] = json.dumps(dados["licencas_items"], ensure_ascii=False)
        dados["servidores_snapshot"] = json.dumps(dados["servidores_items"], ensure_ascii=False)
        dados["clicksign_status"] = (dados.get("clicksign_status") or "NAO_ENVIADO").strip().upper()
        dados["clicksign_document_key"] = (dados.get("clicksign_document_key") or "").strip()
        dados["clicksign_document_url"] = (dados.get("clicksign_document_url") or "").strip()
        dados["clicksign_envelope_id"] = (dados.get("clicksign_envelope_id") or "").strip()
        dados["clicksign_eventos"] = dados.get("clicksign_eventos") or "[]"
        dados["ativo"] = str(dados.get("ativo", "1")) == "1" or dados.get("ativo") is True
        return dados

    @classmethod
    def validar(cls, dados, proposta_id=None):
        oportunidade = None
        if dados.get("oportunidade_id"):
            oportunidade = OportunidadeRepository.buscar_por_id(dados["oportunidade_id"])
            if not oportunidade:
                raise ValueError("Oportunidade vinculada não encontrada.")
        if not dados.get("cliente_id") and not dados.get("cliente_nome"):
            raise ValueError("Cliente da proposta é obrigatório.")
        if not dados.get("titulo"):
            raise ValueError("Título da solução é obrigatório.")
        if dados.get("status") not in STATUS_PROPOSTA:
            raise ValueError("Status da proposta inválido.")
        if dados.get("clicksign_status") not in STATUS_CLICKSIGN:
            raise ValueError("Status de ClickSign inválido.")
        if dados.get("semaforo_fechamento") not in ("FRIO", "MORNO", "QUENTE"):
            raise ValueError("Semáforo de fechamento inválido.")
        if not dados["licencas_items"] and not dados["servidores_items"]:
            raise ValueError("Adicione ao menos uma licença ou um servidor na proposta.")
        if dados["prazo_contratual_meses"] <= 0:
            raise ValueError("Prazo contratual deve ser maior que zero.")
        for campo in ("total_mensal", "parametrizacao_sistema", "setup_ambiente_cloud", "total_instalacao", "valor_total"):
            if dados[campo] is not None and dados[campo] < 0:
                raise ValueError("Os valores da proposta não podem ser negativos.")
        if oportunidade and not dados.get("cliente_nome"):
            raise ValueError("Não foi possível resolver o cliente da oportunidade.")
        return True

    @staticmethod
    def _semaforo_padrao(status):
        return {
            "APROVADA": "QUENTE",
            "ENVIADA": "MORNO",
            "EM_ANALISE": "MORNO",
            "RASCUNHO": "FRIO",
            "REJEITADA": "FRIO",
            "EXPIRADA": "FRIO",
            "CANCELADA": "FRIO",
        }.get((status or "").strip().upper(), "FRIO")

    @classmethod
    def gerar_codigo_proposta(cls):
        return datetime.now().strftime("O3-%Y%m%d-%H%M")

    @classmethod
    def gerar_docx(cls, proposta):
        linhas = cls._montar_linhas_documento(proposta)
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as arquivo:
            arquivo.writestr("[Content_Types].xml", cls._docx_content_types())
            arquivo.writestr("_rels/.rels", cls._docx_root_rels())
            arquivo.writestr("word/_rels/document.xml.rels", cls._docx_document_rels())
            arquivo.writestr("word/styles.xml", cls._docx_styles())
            arquivo.writestr("docProps/core.xml", cls._docx_core())
            arquivo.writestr("docProps/app.xml", cls._docx_app())
            arquivo.writestr("word/document.xml", cls._docx_document(linhas))
        buffer.seek(0)
        return buffer

    @classmethod
    def _decorar_proposta(cls, proposta):
        proposta = dict(proposta)
        proposta["licencas_items"] = cls._carregar_lista_json(proposta.get("licencas_snapshot"))
        proposta["servidores_items"] = cls._carregar_lista_json(proposta.get("servidores_snapshot"))
        resumo = cls._calcular_totais(proposta["licencas_items"], proposta["servidores_items"])
        proposta["total_mensal"] = cls._decimal(proposta.get("total_mensal")) or resumo["total_mensal"]
        parametrizacao = cls._decimal(proposta.get("parametrizacao_sistema"))
        setup_cloud = cls._decimal(proposta.get("setup_ambiente_cloud"))
        proposta["parametrizacao_sistema"] = parametrizacao if parametrizacao is not None else resumo["parametrizacao_padrao"]
        proposta["setup_ambiente_cloud"] = setup_cloud if setup_cloud is not None else resumo["setup_cloud_padrao"]
        proposta["total_setup"] = proposta["parametrizacao_sistema"] + proposta["setup_ambiente_cloud"]
        proposta["total_instalacao"] = cls._decimal(proposta.get("total_instalacao")) or (resumo["instalacao_servidores"] + proposta["parametrizacao_sistema"] + proposta["setup_ambiente_cloud"])
        proposta["valor_total"] = cls._decimal(proposta.get("valor_total")) or (proposta["total_mensal"] + proposta["total_instalacao"])
        proposta["instalacao_servidores"] = resumo["instalacao_servidores"]
        proposta["status_label"] = STATUS_PROPOSTA.get(proposta.get("status"), proposta.get("status"))
        proposta["semaforo_fechamento"] = (proposta.get("semaforo_fechamento") or cls._semaforo_padrao(proposta.get("status"))).upper()
        proposta["semaforo_fechamento_label"] = {"FRIO": "Frio", "MORNO": "Morno", "QUENTE": "Quente"}.get(proposta["semaforo_fechamento"], proposta["semaforo_fechamento"])
        proposta["clicksign_status"] = proposta.get("clicksign_status") or "NAO_ENVIADO"
        proposta["clicksign_status_label"] = STATUS_CLICKSIGN.get(proposta.get("clicksign_status"), proposta.get("clicksign_status"))
        proposta["clicksign_eventos"] = cls._carregar_lista_json(proposta.get("clicksign_eventos"))
        proposta["clicksign_sent_at"] = cls._string_datetime(proposta.get("clicksign_sent_at"))
        proposta["clicksign_signed_at"] = cls._string_datetime(proposta.get("clicksign_signed_at"))
        proposta["clicksign_completed_at"] = cls._string_datetime(proposta.get("clicksign_completed_at"))
        proposta["clicksign_last_sync_at"] = cls._string_datetime(proposta.get("clicksign_last_sync_at"))
        proposta["codigo_proposta"] = proposta.get("codigo_proposta") or cls.gerar_codigo_proposta()
        cls._enriquecer_cliente(proposta)
        cls._enriquecer_contato(proposta)
        cls._enriquecer_representante_legal(proposta)
        return proposta

    @classmethod
    def _herdar_relacionamentos(cls, dados):
        oportunidade = OportunidadeRepository.buscar_por_id(dados["oportunidade_id"]) if dados.get("oportunidade_id") else None
        if oportunidade:
            for campo in ("cliente_id", "contato_id", "parceiro_id", "executivo_responsavel_id"):
                if not dados.get(campo):
                    dados[campo] = oportunidade.get(campo)
        if dados.get("cliente_id"):
            for cliente in ClienteService.listar_para_importacao():
                if cliente.get("id") == dados["cliente_id"]:
                    dados["cliente_nome"] = dados.get("cliente_nome") or cliente.get("nome_fantasia") or cliente.get("razao_social") or ""
                    dados["cliente_nome_fantasia"] = cliente.get("nome_fantasia") or dados.get("cliente_nome_fantasia") or ""
                    dados["cliente_razao_social"] = cliente.get("razao_social") or dados.get("cliente_razao_social") or ""
                    dados["cliente_cnpj"] = cliente.get("cnpj") or dados.get("cliente_cnpj") or ""
                    break
        elif oportunidade:
            dados["cliente_nome"] = dados.get("cliente_nome") or oportunidade.get("cliente_exibicao") or oportunidade.get("empresa") or ""
        if dados.get("contato_id"):
            contato = ContatoService.buscar_por_id(dados["contato_id"])
            if contato:
                if contato.get("tipo_contato") != "COMERCIAL":
                    raise ValueError("Selecione um contato do tipo Comercial para a proposta.")
                dados["contato_nome"] = contato.get("nome") or dados.get("contato_nome")
                dados["contato_email"] = contato.get("email") or dados.get("contato_email")
                dados["contato_telefone"] = contato.get("telefone") or contato.get("whatsapp") or dados.get("contato_telefone")
                dados["parceiro_id"] = dados.get("parceiro_id") or contato.get("parceiro_id")
                dados["executivo_responsavel_id"] = dados.get("executivo_responsavel_id") or contato.get("executivo_responsavel_id")
        if dados.get("representante_legal_id"):
            representante = ContatoService.buscar_por_id(dados["representante_legal_id"])
            if not representante or not representante.get("ativo"):
                raise ValueError("Selecione um representante legal ativo para a proposta.")
            if representante.get("tipo_contato") != "REPRESENTANTE_LEGAL":
                raise ValueError("Selecione um contato do tipo Representante Legal para a proposta.")
        if dados.get("executivo_responsavel_id"):
            for executivo in ParceiroExecutivoService.listar_todos_ativos():
                if executivo.get("id") == dados["executivo_responsavel_id"]:
                    dados["executivo_nome"] = executivo.get("nome") or dados.get("executivo_nome")
                    dados["executivo_email"] = executivo.get("email") or dados.get("executivo_email")
                    dados["executivo_telefone"] = executivo.get("telefone") or dados.get("executivo_telefone")
                    dados["parceiro_id"] = dados.get("parceiro_id") or executivo.get("parceiro_id")
                    break

    @classmethod
    def _enriquecer_cliente(cls, dados):
        dados.setdefault("cliente_razao_social", "")
        dados.setdefault("cliente_nome_fantasia", "")
        dados.setdefault("cliente_cnpj", "")
        if not dados.get("cliente_id"):
            return dados
        cliente = ClienteService.buscar_por_id(dados.get("cliente_id"))
        if not cliente:
            return dados
        dados["cliente_razao_social"] = cliente.get("razao_social") or dados.get("cliente_razao_social") or ""
        dados["cliente_nome_fantasia"] = cliente.get("nome_fantasia") or dados.get("cliente_nome_fantasia") or ""
        dados["cliente_cnpj"] = cliente.get("cnpj") or dados.get("cliente_cnpj") or ""
        dados["cliente_cidade"] = cliente.get("cidade") or dados.get("cliente_cidade") or ""
        dados["cliente_estado"] = cliente.get("estado") or dados.get("cliente_estado") or ""
        if not dados.get("cliente_nome"):
            dados["cliente_nome"] = cliente.get("nome_fantasia") or cliente.get("razao_social") or ""
        return dados

    @classmethod
    def _enriquecer_contato(cls, dados):
        dados.setdefault("contato_cargo", "")
        dados.setdefault("contato_cpf", "")
        dados.setdefault("contato_whatsapp", "")
        if not dados.get("contato_id"):
            return dados
        contato = ContatoService.buscar_por_id(dados.get("contato_id"))
        if not contato:
            return dados
        if contato.get("tipo_contato") != "COMERCIAL":
            return dados
        dados["contato_nome"] = contato.get("nome") or dados.get("contato_nome") or ""
        dados["contato_email"] = contato.get("email") or dados.get("contato_email") or ""
        dados["contato_telefone"] = contato.get("telefone") or contato.get("whatsapp") or dados.get("contato_telefone") or ""
        dados["contato_cargo"] = contato.get("cargo") or dados.get("contato_cargo") or ""
        dados["contato_cpf"] = contato.get("cpf") or dados.get("contato_cpf") or ""
        dados["contato_whatsapp"] = contato.get("whatsapp") or dados.get("contato_whatsapp") or ""
        return dados

    @classmethod
    def _enriquecer_representante_legal(cls, dados):
        dados.setdefault("representante_legal_nome", "")
        dados.setdefault("representante_legal_email", "")
        dados.setdefault("representante_legal_telefone", "")
        dados.setdefault("representante_legal_cargo", "")
        dados.setdefault("representante_legal_cpf", "")
        if not dados.get("representante_legal_id"):
            return dados
        contato = ContatoService.buscar_por_id(dados.get("representante_legal_id"))
        if not contato or contato.get("tipo_contato") != "REPRESENTANTE_LEGAL":
            return dados
        dados["representante_legal_nome"] = contato.get("nome") or ""
        dados["representante_legal_email"] = contato.get("email") or ""
        dados["representante_legal_telefone"] = contato.get("telefone") or contato.get("whatsapp") or ""
        dados["representante_legal_cargo"] = contato.get("cargo") or "Representante legal"
        dados["representante_legal_cpf"] = contato.get("cpf") or ""
        return dados

    @classmethod
    def _normalizar_licencas(cls, bruto):
        itens = cls._carregar_lista_json(bruto)
        resposta = []
        for item in itens:
            preco_id = cls._normalizar_inteiro(item.get("preco_id"))
            preco = PrecoCatalogoRepository.buscar_licenciamento(preco_id) if preco_id else None
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            if preco:
                minimo = cls._normalizar_inteiro(preco.get("usuarios_inicio"))
                maximo = cls._normalizar_inteiro(preco.get("usuarios_fim"))
                nome = preco.get("software") or preco.get("produto") or "Licença"
                if minimo and quantidade < minimo:
                    raise ValueError(f"{nome}: quantidade de usuários deve ser no mínimo {minimo}.")
                if maximo and quantidade > maximo:
                    raise ValueError(f"{nome}: quantidade de usuários deve ser no máximo {maximo}.")
                valor_tabela = cls._decimal(preco.get("valor_mensal")) or Decimal("0.00")
                valor_minimo = cls._decimal(preco.get("valor_minimo") or preco.get("valor_setup")) or Decimal("0.00")
                valor_informado = cls._decimal(item.get("valor_unitario"))
                if valor_informado is None:
                    valor_informado = valor_tabela
                if valor_informado < valor_minimo or valor_informado > valor_tabela:
                    raise ValueError(f"{nome}: valor unitario deve ficar entre R$ {valor_minimo} e R$ {valor_tabela}.")
                valor_setup = cls._decimal(preco.get("valor_setup")) or Decimal("0.00")
                valor = valor_informado
                resposta.append({
                    "preco_id": preco_id,
                    "faixa_id": cls._normalizar_inteiro(preco.get("faixa_id")),
                    "produto": (preco.get("produto") or "").strip(),
                    "software": (preco.get("software") or "").strip(),
                    "descricao": (preco.get("descricao") or "").strip(),
                    "quantidade": quantidade,
                    "valor_unitario": cls._string_decimal(valor),
                    "valor_tabela": cls._string_decimal(valor_tabela),
                    "valor_minimo": cls._string_decimal(valor_minimo),
                    "valor_setup": cls._string_decimal(valor_setup),
                    "tem_projeto": str(preco.get("tem_projeto", "0")).lower() in ("1", "true", "sim"),
                    "usuarios_inicio": minimo,
                    "usuarios_fim": maximo,
                    "total_mensal": cls._string_decimal((valor * quantidade).quantize(Decimal("0.01"))),
                })
                continue
            valor = cls._decimal(item.get("valor_unitario")) or Decimal("0.00")
            resposta.append({
                "preco_id": preco_id,
                "faixa_id": cls._normalizar_inteiro(item.get("faixa_id")),
                "produto": (item.get("produto") or "").strip(),
                "software": (item.get("software") or "").strip(),
                "descricao": (item.get("descricao") or "").strip(),
                "quantidade": quantidade,
                "valor_unitario": cls._string_decimal(valor),
                "valor_setup": cls._string_decimal(cls._decimal(item.get("valor_setup")) or Decimal("0.00")),
                "tem_projeto": str(item.get("tem_projeto", "0")).lower() in ("1", "true", "sim"),
                "usuarios_inicio": cls._normalizar_inteiro(item.get("usuarios_inicio")),
                "usuarios_fim": cls._normalizar_inteiro(item.get("usuarios_fim")),
                "total_mensal": cls._string_decimal((valor * quantidade).quantize(Decimal("0.01"))),
            })
        return resposta

    @classmethod
    def _normalizar_servidores(cls, bruto):
        itens = cls._carregar_lista_json(bruto)
        resposta = []
        for item in itens:
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            valor_mensal = cls._decimal(item.get("valor_mensal")) or Decimal("0.00")
            valor_instalacao = cls._decimal(item.get("valor_instalacao")) or Decimal("0.00")
            resposta.append({
                "recurso_id": cls._normalizar_inteiro(item.get("recurso_id")),
                "codigo": (item.get("codigo") or "").strip(),
                "categoria": (item.get("categoria") or "").strip(),
                "nome": (item.get("nome") or "").strip(),
                "descricao": (item.get("descricao") or "").strip(),
                "quantidade": quantidade,
                "valor_mensal": cls._string_decimal(valor_mensal),
                "valor_instalacao": cls._string_decimal(valor_instalacao),
                "total_mensal": cls._string_decimal((valor_mensal * quantidade).quantize(Decimal("0.01"))),
                "total_instalacao": cls._string_decimal((valor_instalacao * quantidade).quantize(Decimal("0.01"))),
            })
        return resposta

    @classmethod
    def _calcular_totais(cls, licencas, servidores):
        total_mensal = Decimal("0.00")
        parametrizacao = Decimal("0.00")
        instalacao_servidores = Decimal("0.00")
        for item in licencas:
            total = cls._decimal(item.get("total_mensal")) or Decimal("0.00")
            total_mensal += total
            if item.get("tem_projeto"):
                parametrizacao += total
        for item in servidores:
            total_mensal += cls._decimal(item.get("total_mensal")) or Decimal("0.00")
            instalacao_servidores += cls._decimal(item.get("total_instalacao")) or Decimal("0.00")
        return {
            "total_mensal": total_mensal.quantize(Decimal("0.01")),
            "parametrizacao_padrao": parametrizacao.quantize(Decimal("0.01")),
            "setup_cloud_padrao": total_mensal.quantize(Decimal("0.01")),
            "instalacao_servidores": instalacao_servidores.quantize(Decimal("0.01")),
        }

    @classmethod
    def _montar_itens_snapshot(cls, licencas, servidores):
        linhas = []
        if licencas:
            linhas.append("Licenciamento por Usuário")
            for item in licencas:
                linhas.append(f"- {item.get('software')}: {item.get('quantidade')} x R$ {item.get('valor_unitario')} = R$ {item.get('total_mensal')}")
        if servidores:
            linhas.append("Recursos de Servidor")
            for item in servidores:
                linhas.append(f"- {item.get('nome')}: {item.get('quantidade')} x R$ {item.get('valor_mensal')} = R$ {item.get('total_mensal')}")
        return "\n".join(linhas)

    @classmethod
    def _montar_linhas_documento(cls, proposta):
        linhas = [
            "SOLUÇÃO",
            proposta.get("titulo") or "",
            proposta.get("cliente_nome") or proposta.get("oportunidade_empresa") or "",
            proposta.get("codigo_proposta") or "",
            "",
            "1. AGRADECIMENTO",
            "Prezado Cliente (a)",
            "Temos o prazer de lhe apresentar a nossa proposta de solução em CLOUD.",
            "Somos uma empresa especializada em hospedagem de servidores em nuvem e tecnologia da informação.",
            "Queremos escrever ao seu lado uma parceria de sucesso oferecendo tecnologia de ponta sob medida.",
            f"{proposta.get('executivo_nome') or 'Executivo de vendas'} - Executivo de vendas",
            f"e-mail - {proposta.get('executivo_email') or '-'}",
            "",
            "2. INVESTIMENTOS CLOUD",
            f"Parametrização do Sistema	R$ {cls._string_decimal(proposta.get('parametrizacao_sistema'))}",
            f"Setup do Ambiente Cloud	R$ {cls._string_decimal(proposta.get('setup_ambiente_cloud'))}",
            f"Recursos adicionais de instalação	R$ {cls._string_decimal(proposta.get('instalacao_servidores'))}",
            f"TOTAL INSTALAÇÃO	R$ {cls._string_decimal(proposta.get('total_instalacao'))}",
            "",
            "Das mensalidades:",
        ]
        for item in proposta.get("licencas_items", []):
            linhas.append(f"{item.get('software')} | {item.get('quantidade')} | R$ {item.get('valor_unitario')} | R$ {item.get('total_mensal')}")
        for item in proposta.get("servidores_items", []):
            linhas.append(f"{item.get('nome')} | {item.get('quantidade')} | R$ {item.get('valor_mensal')} | R$ {item.get('total_mensal')}")
        linhas.extend([
            f"TOTAL MENSAL	R$ {cls._string_decimal(proposta.get('total_mensal'))}",
            f"Setup: {proposta.get('setup_dias')} dias após a entrega do ambiente.",
            f"Mensalidade: {proposta.get('mensalidade_dias')} dias após a entrega do ambiente.",
            f"Prazo contratual: {proposta.get('prazo_contratual_meses')} meses.",
        ])
        return linhas

    @staticmethod
    def _docx_content_types():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'

    @staticmethod
    def _docx_root_rels():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'

    @staticmethod
    def _docx_document_rels():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'

    @staticmethod
    def _docx_styles():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>'

    @staticmethod
    def _docx_core():
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Proposta Comercial O3 Cloud</dc:title><dc:creator>O3Cloud Manager</dc:creator><cp:lastModifiedBy>O3Cloud Manager</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'

    @staticmethod
    def _docx_app():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>O3Cloud Manager</Application></Properties>'

    @classmethod
    def _docx_document(cls, linhas):
        corpo = ''.join(f'<w:p><w:r><w:t xml:space="preserve">{escape(linha or "")}</w:t></w:r></w:p>' for linha in linhas)
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" mc:Ignorable="w14 wp14"><w:body>' + corpo + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>'


    @classmethod
    def _preparar_licencas_form(cls, bruto=None, fallback=None):
        itens = cls._carregar_lista_json(bruto, fallback)
        resposta = []
        for item in itens:
            item = dict(item or {})
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            valor_unitario = cls._decimal_form(item.get("valor_unitario"))
            valor_tabela = cls._decimal_form(item.get("valor_tabela"), valor_unitario)
            valor_minimo = cls._decimal_form(item.get("valor_minimo"), cls._decimal_form(item.get("valor_setup"), Decimal("0.00")))
            total_mensal = cls._decimal_form(item.get("total_mensal"), (valor_unitario * quantidade).quantize(Decimal("0.01")))
            item.update({
                "quantidade": quantidade,
                "valor_unitario": cls._string_decimal(valor_unitario, "0.00"),
                "valor_tabela": cls._string_decimal(valor_tabela, "0.00"),
                "valor_minimo": cls._string_decimal(valor_minimo, "0.00"),
                "valor_setup": cls._string_decimal(cls._decimal_form(item.get("valor_setup"), Decimal("0.00")), "0.00"),
                "total_mensal": cls._string_decimal(total_mensal, "0.00"),
            })
            resposta.append(item)
        return resposta

    @classmethod
    def _preparar_servidores_form(cls, bruto=None, fallback=None):
        itens = cls._carregar_lista_json(bruto, fallback)
        resposta = []
        for item in itens:
            item = dict(item or {})
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            valor_mensal = cls._decimal_form(item.get("valor_mensal"))
            valor_instalacao = cls._decimal_form(item.get("valor_instalacao"))
            total_mensal = cls._decimal_form(item.get("total_mensal"), (valor_mensal * quantidade).quantize(Decimal("0.01")))
            total_instalacao = cls._decimal_form(item.get("total_instalacao"), (valor_instalacao * quantidade).quantize(Decimal("0.01")))
            item.update({
                "quantidade": quantidade,
                "valor_mensal": cls._string_decimal(valor_mensal, "0.00"),
                "valor_instalacao": cls._string_decimal(valor_instalacao, "0.00"),
                "total_mensal": cls._string_decimal(total_mensal, "0.00"),
                "total_instalacao": cls._string_decimal(total_instalacao, "0.00"),
            })
            resposta.append(item)
        return resposta

    @classmethod
    def _decimal_form(cls, valor, default=None):
        if valor in (None, ""):
            return default or Decimal("0.00")
        try:
            return cls._decimal(valor) or default or Decimal("0.00")
        except ValueError:
            return default or Decimal("0.00")

    @staticmethod
    def _carregar_lista_json(bruto=None, fallback=None):
        if isinstance(fallback, list):
            return fallback
        if isinstance(bruto, list):
            return bruto
        if not bruto:
            return []
        try:
            dados = json.loads(bruto)
        except (TypeError, ValueError):
            return []
        return dados if isinstance(dados, list) else []

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default
        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _normalizar_status_ativo(valor):
        if valor in (None, "", "todos"):
            return None
        if str(valor) == "1":
            return 1
        if str(valor) == "0":
            return 0
        return None

    @staticmethod
    def _decimal(valor):
        if isinstance(valor, Decimal):
            return valor.quantize(Decimal("0.01"))
        if valor in (None, ""):
            return None
        try:
            texto = str(valor).replace("R$", "").replace(" ", "").strip()
            if "," in texto:
                texto = texto.replace(".", "").replace(",", ".")
            return Decimal(texto).quantize(Decimal("0.01"))
        except InvalidOperation:
            raise ValueError("Valor monetário inválido na proposta.")

    @staticmethod
    def _normalizar_data(valor):
        if valor in (None, ""):
            return None
        return date.fromisoformat(str(valor))

    @staticmethod
    def _string_data(valor):
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        return valor or ""

    @staticmethod
    def _string_datetime(valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%Y-%m-%d %H:%M:%S")
        return valor or ""

    @staticmethod
    def _string_decimal(valor, default=None):
        if valor in (None, ""):
            return default
        if not isinstance(valor, Decimal):
            valor = PropostaService._decimal(valor)
        if valor is None:
            return default
        return f"{valor:.2f}"

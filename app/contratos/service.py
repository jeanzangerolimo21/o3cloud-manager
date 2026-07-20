from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.contatos.service import ContatoService
from app.core.storage import StorageService
from app.integracoes.omie.client import OmieClient
from app.integracoes.omie.contrato_mapper import ContratoMapper
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.parceiros.service import ParceiroService
from app.propostas.service import PropostaService
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.contrato_repository import ContratoRepository


class ContratoService:
    STATUS_OPTIONS = {
        "RASCUNHO": "Rascunho",
        "ENVIADO_CLICKSIGN": "Enviado ClickSign",
        "AGUARDANDO_ASSINATURA": "Aguardando Assinatura",
        "ENCAMINHADO_PROJETO": "Encaminhado para Projeto",
        "CONCLUIDO": "Concluido",
        "ATIVO": "Contratos Ativos",
        "EM_IMPLANTACAO": "Em Implantacao",
        "SUSPENSO": "Suspenso",
        "ENCERRADO": "Encerrado",
        "CANCELADO": "Cancelado",
    }

    TIPO_VENDA_OPTIONS = {
        "USUARIO": "Usuario",
        "PROJETO": "Projeto",
    }

    @classmethod
    def sincronizar_contrato(cls, contrato_omie):
        dados = ContratoMapper.from_omie(contrato_omie)
        cliente = ClienteRepository.buscar_por_codigo_externo(dados["cliente_codigo_externo"])

        if not cliente:
            return {
                "status": "IGNORADO",
                "numero": dados["numero"],
                "motivo": "Cliente nao encontrado",
            }

        dados["cliente_id"] = cliente["id"]
        contrato = ContratoRepository.buscar_por_codigo_externo(dados["codigo_externo"])

        if not contrato:
            contrato = ContratoRepository.buscar_assinado_sem_codigo_por_cliente_valor(
                cliente["id"],
                dados.get("valor_mensal"),
            )

        if contrato:
            ContratoRepository.atualizar_sync(contrato["id"], dados)
            return {"status": "UPDATE", "numero": dados["numero"]}

        ContratoRepository.inserir(dados)
        return {"status": "INSERT", "numero": dados["numero"]}

    @classmethod
    def sincronizar(cls):
        omie = OmieClient()
        resposta = omie.listar_contratos()
        return [
            cls.sincronizar_contrato(contrato)
            for contrato in resposta.get("contratoCadastro", [])
        ]

    @classmethod
    def listar(cls, filtros, pagina=1, limit=50):
        offset = (pagina - 1) * limit
        contratos = ContratoRepository.listar(limit=limit, offset=offset, **filtros)
        total = ContratoRepository.total(**filtros)
        return contratos, total, (total + limit - 1) // limit

    @classmethod
    def dashboard(cls, filtros):
        return ContratoRepository.dashboard(**filtros)

    @classmethod
    def contexto_form(cls):
        return {
            "clientes": ContratoRepository.listar_clientes_para_contrato(),
            "contatos": cls._contatos_para_form(),
            "propostas": cls._propostas_para_form(),
            "executivos": ParceiroExecutivoService.listar_todos_ativos(),
            "parceiros": ParceiroService.listar_todos_ativos(),
            "status_options": cls.STATUS_OPTIONS,
            "tipo_venda_options": cls.TIPO_VENDA_OPTIONS,
            "modelo_contrato": StorageService.caminho(StorageService.CONTRATOS, "Modelo_Contrato.pdf"),
        }

    @classmethod
    def _contatos_para_form(cls):
        return [
            {
                "id": contato.get("id"),
                "nome": contato.get("nome") or "",
                "empresa": contato.get("empresa") or "",
                "email": contato.get("email") or "",
                "telefone": contato.get("telefone") or contato.get("whatsapp") or "",
                "whatsapp": contato.get("whatsapp") or "",
            }
            for contato in ContatoService.listar_todos_ativos()
        ]

    @classmethod
    def _propostas_para_form(cls):
        propostas, _ = PropostaService.listar(ativo="1")
        return [
            cls._proposta_para_form(proposta.get("id"))
            for proposta in propostas
            if proposta.get("id")
        ]

    @classmethod
    def _proposta_para_form(cls, proposta_id):
        proposta = PropostaService.buscar_por_id(proposta_id)
        if not proposta:
            return {}
        valor_setup = (proposta.get("setup_ambiente_cloud") or Decimal("0.00")) + (proposta.get("instalacao_servidores") or Decimal("0.00"))
        quantidade_usuarios = sum(cls._inteiro(item.get("quantidade")) or 0 for item in proposta.get("licencas_items") or [])
        return {
            "id": proposta.get("id"),
            "codigo": proposta.get("codigo_proposta") or "",
            "titulo": proposta.get("titulo") or "",
            "status": proposta.get("status") or "",
            "cliente_id": proposta.get("cliente_id"),
            "contato_id": proposta.get("contato_id"),
            "parceiro_id": proposta.get("parceiro_id"),
            "executivo_id": proposta.get("executivo_responsavel_id"),
            "contato_nome": proposta.get("contato_nome") or "",
            "contato_email": proposta.get("contato_email") or "",
            "contato_telefone": proposta.get("contato_telefone") or "",
            "valor_mensal": cls._string_decimal(proposta.get("total_mensal")),
            "valor_setup": cls._string_decimal(valor_setup),
            "valor_projeto": cls._string_decimal(proposta.get("parametrizacao_sistema")),
            "quantidade_usuarios": quantidade_usuarios or "",
            "observacoes": proposta.get("detalhes_negociacao") or proposta.get("condicoes_comerciais") or proposta.get("observacoes") or "",
        }

    @classmethod
    def criar(cls, dados, arquivo_preparado=None):
        dados = cls._normalizar(dados)
        cls._validar(dados, arquivo_preparado=arquivo_preparado, exigir_pdf=True)
        cls._aplicar_arquivo_preparado(dados, arquivo_preparado)
        return ContratoRepository.inserir_manual(dados)

    @classmethod
    def atualizar(cls, contrato_id, dados, arquivo_preparado=None):
        contrato = ContratoRepository.buscar_por_id(contrato_id)
        if not contrato:
            raise ValueError("Contrato nao encontrado.")
        if contrato["origem"] != "MANUAL":
            raise ValueError("Contratos sincronizados do Omie so permitem edicao de vinculos comerciais.")

        dados = cls._normalizar(dados)
        cls._validar(dados, arquivo_preparado=arquivo_preparado, exigir_pdf=False)
        cls._aplicar_arquivo_preparado(dados, arquivo_preparado)
        ContratoRepository.atualizar(contrato_id, dados)

    @classmethod
    def atualizar_vinculos_comerciais(cls, contrato_id, dados):
        contrato = ContratoRepository.buscar_por_id(contrato_id)
        if not contrato:
            raise ValueError("Contrato nao encontrado.")
        if contrato["origem"] != "OMIE":
            raise ValueError("Esta edicao restrita e exclusiva para contratos do Omie.")

        dados = cls._normalizar_vinculos_comerciais(dados)
        ContratoRepository.atualizar_vinculos_comerciais(contrato_id, dados)

    @classmethod
    def salvar_assinado(cls, contrato_id, arquivo):
        contrato = ContratoRepository.buscar_por_id(contrato_id)
        if not contrato:
            raise ValueError("Contrato nao encontrado.")
        if not cls._arquivo_pdf(arquivo):
            raise ValueError("Envie um arquivo PDF assinado.")

        salvo = StorageService.salvar(arquivo, StorageService.CONTRATOS)
        ContratoRepository.atualizar_arquivo_assinado(
            contrato_id,
            salvo["nome"],
            salvo["arquivo_original"],
        )

    @classmethod
    def caminho_assinado(cls, contrato_id):
        contrato = ContratoRepository.buscar_por_id(contrato_id)
        if not contrato or not contrato.get("arquivo_assinado"):
            return None, None

        caminho = StorageService.caminho(StorageService.CONTRATOS, contrato["arquivo_assinado"])
        if not Path(caminho).exists():
            return None, None

        return caminho, contrato.get("arquivo_assinado_original") or contrato["arquivo_assinado"]

    @classmethod
    def _normalizar(cls, dados):
        dados = dict(dados)
        cliente = ClienteRepository.buscar_por_id(dados.get("cliente_id")) if dados.get("cliente_id") else None
        numero = (dados.get("numero") or "").strip()
        dados["numero"] = numero or "CTR-" + datetime.now().strftime("%Y%m%d%H%M%S")
        dados["descricao"] = (dados.get("descricao") or "").strip() or None
        dados["status"] = dados.get("status") or "RASCUNHO"
        dados["tipo_venda"] = dados.get("tipo_venda") or "USUARIO"
        dados["cliente"] = cliente

        for campo in (
            "cliente_id",
            "contato_id",
            "proposta_id",
            "executivo_id",
            "parceiro_id",
            "quantidade_usuarios",
            "dia_faturamento",
        ):
            dados[campo] = cls._inteiro(dados.get(campo))

        for campo in ("valor_mensal", "valor_setup", "valor_projeto", "valor_promocional"):
            dados[campo] = cls._decimal(dados.get(campo))

        for campo in (
            "inicio_vigencia",
            "fim_vigencia",
            "data_fechamento",
            "data_inicio_recorrencia",
            "data_ativacao",
        ):
            dados[campo] = dados.get(campo) or None

        cls._preencher_dados_contato(dados)
        for campo in ("contato_nome", "contato_email", "contato_telefone", "observacoes"):
            dados[campo] = (dados.get(campo) or "").strip() or None

        return dados

    @classmethod
    def _normalizar_vinculos_comerciais(cls, dados):
        dados = dict(dados)
        for campo in ("contato_id", "executivo_id", "parceiro_id"):
            dados[campo] = cls._inteiro(dados.get(campo))
        cls._preencher_dados_contato(dados)
        for campo in ("contato_nome", "contato_email", "contato_telefone", "observacoes"):
            dados[campo] = (dados.get(campo) or "").strip() or None
        return dados

    @classmethod
    def _preencher_dados_contato(cls, dados):
        if not dados.get("contato_id"):
            return
        contato = ContatoService.buscar_por_id(dados.get("contato_id"))
        if not contato:
            return
        dados["contato_nome"] = dados.get("contato_nome") or contato.get("nome")
        dados["contato_email"] = dados.get("contato_email") or contato.get("email")
        dados["contato_telefone"] = dados.get("contato_telefone") or contato.get("telefone") or contato.get("whatsapp")

    @classmethod
    def _validar(cls, dados, arquivo_preparado=None, exigir_pdf=False):
        erros = []
        cliente = dados.get("cliente")

        if not cliente:
            erros.append("Informe a empresa/cliente")
        elif not cliente.get("cnpj"):
            erros.append("Informe o CNPJ")
        if not dados.get("contato_nome"):
            erros.append("Informe o nome do contato")
        if not dados.get("contato_email"):
            erros.append("Informe o e-mail do contato")
        if not dados.get("contato_telefone"):
            erros.append("Informe o telefone do contato")
        if not dados.get("data_fechamento"):
            erros.append("Informe a data de fechamento")
        if not dados.get("valor_mensal") or dados["valor_mensal"] <= 0:
            erros.append("Informe o valor recorrente")
        if dados.get("quantidade_usuarios") is not None and dados["quantidade_usuarios"] < 0:
            erros.append("A quantidade de usuarios nao pode ser negativa")
        if exigir_pdf and not cls._arquivo_pdf(arquivo_preparado):
            erros.append("Anexe o contrato em PDF")
        elif arquivo_preparado and arquivo_preparado.filename and not cls._arquivo_pdf(arquivo_preparado):
            erros.append("O contrato deve ser um arquivo PDF")
        if dados.get("status") not in cls.STATUS_OPTIONS:
            erros.append("Status invalido")
        if dados.get("tipo_venda") not in cls.TIPO_VENDA_OPTIONS:
            erros.append("Tipo de venda invalido")

        if erros:
            raise ValueError("|".join(erros))

    @classmethod
    def _aplicar_arquivo_preparado(cls, dados, arquivo):
        dados["arquivo_preparado"] = None
        dados["arquivo_preparado_original"] = None
        if arquivo and arquivo.filename:
            salvo = StorageService.salvar(arquivo, StorageService.CONTRATOS)
            dados["arquivo_preparado"] = salvo["nome"]
            dados["arquivo_preparado_original"] = salvo["arquivo_original"]

    @staticmethod
    def _arquivo_pdf(arquivo):
        return bool(arquivo and arquivo.filename and Path(arquivo.filename).suffix.lower() == ".pdf")


    @staticmethod
    def _string_decimal(valor):
        if valor in (None, ""):
            return ""
        try:
            return str(Decimal(str(valor)).quantize(Decimal("0.01")))
        except (InvalidOperation, ValueError):
            return ""

    @staticmethod
    def _inteiro(valor):
        if valor in (None, ""):
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return None
        texto = str(valor).strip().replace("R$", "").replace(".", "").replace(",", ".")
        try:
            return Decimal(texto)
        except (InvalidOperation, ValueError):
            return None

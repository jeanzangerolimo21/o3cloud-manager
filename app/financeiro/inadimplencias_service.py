import os
from datetime import datetime

from app.core.email import EmailService
from app.core.filters import cnpj_br
from app.financeiro.inadimplencias_repository import InadimplenciaRepository
from app.repositories.contrato_repository import ContratoRepository


class InadimplenciaService:
    STATUS = {"PENDENTE": "Pendente", "LIBERADO": "Liberado"}
    TIPOS_LIBERACAO = {"QUITACAO": "Quitou pendência", "ACORDO": "Realizou acordo"}
    repository = InadimplenciaRepository

    @classmethod
    def listar(cls, filtros=None, pagina=1):
        filtros = cls._normalizar_filtros(filtros or {})
        limit = 50
        offset = (max(1, pagina) - 1) * limit
        return cls.repository.listar(filtros, limit=limit, offset=offset), cls.repository.total(filtros)

    @classmethod
    def buscar_por_id(cls, inadimplencia_id):
        return cls.repository.buscar_por_id(inadimplencia_id)

    @classmethod
    def contexto_form(cls, pesquisa=None):
        return {"contratos": cls.contratos_para_busca(pesquisa)}

    @classmethod
    def contratos_para_busca(cls, pesquisa=None):
        contratos = cls.repository.contratos_para_select(pesquisa=pesquisa, limit=25 if pesquisa else 100)
        return [
            {
                "id": item.get("id"),
                "numero": item.get("numero"),
                "status": item.get("status"),
                "cliente_id": item.get("cliente_id"),
                "cliente_nome": item.get("cliente_nome"),
                "cliente_razao_social": item.get("cliente_razao_social"),
                "cliente_cnpj": item.get("cliente_cnpj"),
                "inadimplencia_ativa": bool(item.get("inadimplencia_ativa")),
            }
            for item in contratos
        ]

    @classmethod
    def registrar(cls, dados, usuario_id=None, usuario_email="sistema"):
        payload = cls._normalizar_registro(dados)
        contrato = ContratoRepository.buscar_por_id(payload["contrato_id"])
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        if cls.repository.buscar_ativa_por_contrato(payload["contrato_id"]):
            raise ValueError("Este contrato já possui pendência financeira ativa.")
        payload["bloqueado_por"] = usuario_id
        payload["bloqueado_por_email"] = usuario_email or "sistema"
        inadimplencia_id = cls.repository.criar(payload)
        inadimplencia = cls.repository.buscar_por_id(inadimplencia_id)
        cls._notificar_registro(inadimplencia)
        return inadimplencia_id

    @classmethod
    def liberar(cls, inadimplencia_id, dados, usuario_id=None, usuario_email="sistema"):
        inadimplencia = cls.repository.buscar_por_id(inadimplencia_id)
        if not inadimplencia:
            raise ValueError("Inadimplência não encontrada.")
        if inadimplencia.get("status") != "PENDENTE":
            raise ValueError("Somente pendências ativas podem ser liberadas.")
        payload = cls._normalizar_liberacao(dados)
        payload["liberado_por"] = usuario_id
        payload["liberado_por_email"] = usuario_email or "sistema"
        atualizado = cls.repository.liberar(inadimplencia_id, payload)
        if not atualizado:
            raise ValueError("Não foi possível liberar a pendência financeira.")
        liberada = cls.repository.buscar_por_id(inadimplencia_id)
        cls._notificar_liberacao(liberada)
        return liberada

    @classmethod
    def excluir_historico(cls, inadimplencia_id):
        inadimplencia = cls.repository.buscar_por_id(inadimplencia_id)
        if not inadimplencia:
            raise ValueError("Inadimplência não encontrada.")
        removido = cls.repository.excluir_historico(inadimplencia_id)
        if not removido:
            raise ValueError("Não foi possível remover o histórico de inadimplência.")
        return inadimplencia

    @classmethod
    def cliente_possui_pendencia(cls, cliente_id):
        if not cliente_id:
            return False
        return cls.repository.cliente_possui_pendencia(cliente_id)

    @classmethod
    def pendencias_cliente(cls, cliente_id):
        if not cliente_id:
            return []
        return cls.repository.listar_ativas_por_cliente(cliente_id)

    @classmethod
    def clientes_com_pendencia(cls, cliente_ids):
        return cls.repository.clientes_com_pendencia(cliente_ids)

    @classmethod
    def validar_operacao_cliente(cls, cliente_id):
        if cls.cliente_possui_pendencia(cliente_id):
            raise ValueError("Não é possível realizar esta operação. O cliente possui pendências financeiras ativas.")

    @classmethod
    def _notificar_registro(cls, inadimplencia):
        campos = {}
        suporte = cls._enviar_email(
            cls._destinatarios_suporte(),
            f"[O3Cloud Manager] Bloqueio por pendência financeira - {inadimplencia.get('cliente_nome')}",
            cls._corpo_suporte_bloqueio(inadimplencia),
        )
        campos["email_suporte_enviado"] = 1 if suporte.get("enviado") else 0
        if not suporte.get("enviado"):
            campos["erro_email_suporte"] = suporte.get("motivo") or suporte.get("erro")

        cliente = cls._enviar_email(
            [inadimplencia.get("cliente_email")],
            "Pendência financeira - O3Cloud",
            cls._corpo_cliente_bloqueio(inadimplencia),
        )
        campos["email_cliente_enviado"] = 1 if cliente.get("enviado") else 0
        if not cliente.get("enviado"):
            campos["erro_email_cliente"] = cliente.get("motivo") or cliente.get("erro")
        cls.repository.atualizar_email_status(inadimplencia["id"], campos)

    @classmethod
    def _notificar_liberacao(cls, inadimplencia):
        campos = {}
        suporte = cls._enviar_email(
            cls._destinatarios_suporte(),
            f"[O3Cloud Manager] Cliente liberado financeiramente - {inadimplencia.get('cliente_nome')}",
            cls._corpo_suporte_liberacao(inadimplencia),
        )
        campos["email_liberacao_suporte_enviado"] = 1 if suporte.get("enviado") else 0
        if not suporte.get("enviado"):
            campos["erro_email_liberacao_suporte"] = suporte.get("motivo") or suporte.get("erro")

        cliente = cls._enviar_email(
            [inadimplencia.get("cliente_email")],
            "Liberação financeira - O3Cloud",
            cls._corpo_cliente_liberacao(inadimplencia),
        )
        campos["email_liberacao_cliente_enviado"] = 1 if cliente.get("enviado") else 0
        if not cliente.get("enviado"):
            campos["erro_email_liberacao_cliente"] = cliente.get("motivo") or cliente.get("erro")
        cls.repository.atualizar_email_status(inadimplencia["id"], campos)

    @staticmethod
    def _enviar_email(destinatarios, assunto, corpo):
        try:
            return EmailService.enviar(assunto, corpo, destinatarios)
        except Exception as erro:
            return {"enviado": False, "erro": str(erro)[:500]}

    @staticmethod
    def _destinatarios_suporte():
        raw = os.getenv("FINANCEIRO_EMAIL_SUPORTE", "sac@o3cloud.com.br,plantao@o3ti.com.br")
        return [item.strip() for item in raw.split(",") if item.strip()]

    @classmethod
    def _normalizar_registro(cls, dados):
        contrato_id = cls._inteiro(dados.get("contrato_id"))
        if not contrato_id:
            raise ValueError("Selecione um contrato.")
        motivo = (dados.get("motivo") or "").strip()
        if not motivo:
            raise ValueError("Informe o motivo da pendência financeira.")
        return {
            "contrato_id": contrato_id,
            "motivo": motivo[:255],
            "observacoes": (dados.get("observacoes") or "").strip() or None,
            "bloqueado_em": cls._data_hora(dados.get("bloqueado_em")),
        }

    @classmethod
    def _normalizar_liberacao(cls, dados):
        tipo = (dados.get("tipo_liberacao") or "").strip().upper()
        if tipo not in cls.TIPOS_LIBERACAO:
            raise ValueError("Selecione Quitação ou Acordo para liberar a pendência.")
        return {
            "tipo_liberacao": tipo,
            "observacao_liberacao": (dados.get("observacao_liberacao") or "").strip() or None,
            "liberado_em": cls._data_hora(dados.get("liberado_em")),
        }

    @staticmethod
    def _normalizar_filtros(dados):
        return {
            "q": (dados.get("q") or "").strip(),
            "status": (dados.get("status") or "").strip().upper(),
            "responsavel_id": InadimplenciaService._inteiro(dados.get("responsavel_id")),
            "data_de": (dados.get("data_de") or "").strip(),
            "data_ate": (dados.get("data_ate") or "").strip(),
        }

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor) if str(valor or "").strip() else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _data_hora(valor):
        valor = (valor or "").strip()
        if not valor:
            return None
        for formato in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(valor, formato)
            except ValueError:
                continue
        raise ValueError("Data informada inválida.")

    @staticmethod
    def _corpo_suporte_bloqueio(item):
        return f"""Cliente: {item.get('cliente_nome')}
Razão Social: {item.get('cliente_razao_social') or item.get('cliente_nome') or '-'}
CNPJ: {cnpj_br(item.get('cliente_cnpj'))}
Contrato: {item.get('contrato_numero')}
Status: Pendência financeira registrada
Solicitação: Realizar o bloqueio operacional do ambiente do cliente devido a pendência financeira.
Registrado por: {item.get('bloqueado_por_email') or item.get('bloqueado_por_nome') or 'sistema'}
Data: {item.get('bloqueado_em')}
Observações: {item.get('observacoes') or item.get('motivo') or '-'}
"""

    @staticmethod
    def _corpo_cliente_bloqueio(item):
        return f"""Identificamos uma pendência financeira relacionada ao contrato {item.get('contrato_numero')}.

Razão Social: {item.get('cliente_razao_social') or item.get('cliente_nome') or '-'}
CNPJ: {cnpj_br(item.get('cliente_cnpj'))}

Favor para regularizar sua situação ligue para o telefone: 19 3142-0232 opção 3, pelo telefone/WhatsApp: 19 99912-4028 ou pelo e-mail: contas@o3cloud.com.br

Atenciosamente,
O3Cloud
"""

    @staticmethod
    def _corpo_suporte_liberacao(item):
        return f"""Cliente: {item.get('cliente_nome')}
Razão Social: {item.get('cliente_razao_social') or item.get('cliente_nome') or '-'}
CNPJ: {cnpj_br(item.get('cliente_cnpj'))}
Contrato: {item.get('contrato_numero')}
Status: Cliente liberado financeiramente
Tipo de liberação: {item.get('tipo_liberacao')}
Responsável: {item.get('liberado_por_email') or item.get('liberado_por_nome') or 'sistema'}
Data: {item.get('liberado_em')}
Observação: {item.get('observacao_liberacao') or '-'}
"""

    @staticmethod
    def _corpo_cliente_liberacao(item):
        return f"""A pendência financeira relacionada ao contrato {item.get('contrato_numero')} foi liberada.

Razão Social: {item.get('cliente_razao_social') or item.get('cliente_nome') or '-'}
CNPJ: {cnpj_br(item.get('cliente_cnpj'))}

Em caso de dúvidas, entre em contato com o setor Financeiro da O3Cloud.

Atenciosamente,
O3Cloud
"""

from datetime import datetime

from app.core.email import EmailService
from app.core.filters import cnpj_br, datetime_br
from app.financeiro.cancelamentos_repository import CancelamentoRepository


class CancelamentoService:
    DESTINATARIO = "sac@o3cloud.com.br"
    repository = CancelamentoRepository

    @classmethod
    def listar(cls, filtros=None, pagina=1):
        filtros = cls._normalizar_filtros(filtros or {})
        limit = 50
        offset = (max(1, pagina) - 1) * limit
        return cls.repository.listar(filtros, limit, offset), cls.repository.total(filtros)

    @classmethod
    def buscar_por_id(cls, cancelamento_id):
        item = cls.repository.buscar_por_id(cancelamento_id)
        if item:
            item["contratos"] = cls.repository.contratos_do_cancelamento(cancelamento_id)
            item["ambientes"] = cls.repository.ambientes_por_contratos(
                [contrato["id"] for contrato in item["contratos"]]
            )
        return item

    @classmethod
    def contexto_form(cls, pesquisa=None):
        return {"contratos": cls.contratos_para_busca(pesquisa)}

    @classmethod
    def contratos_para_busca(cls, pesquisa=None):
        return cls.repository.contratos_para_select(pesquisa, limit=25 if pesquisa else 100)

    @classmethod
    def registrar(cls, dados, usuario_id=None, usuario_email="sistema"):
        payload = cls._normalizar_registro(dados)
        contratos = cls.repository.buscar_contratos_ids(payload["contrato_ids"])
        if len(contratos) != len(payload["contrato_ids"]):
            raise ValueError("Um ou mais contratos selecionados não foram encontrados.")
        clientes = {contrato["cliente_id"] for contrato in contratos}
        if len(clientes) != 1:
            raise ValueError("Selecione somente contratos pertencentes ao mesmo cliente.")
        status_permitidos = {"ATIVO", "ENCAMINHADO_PROJETO"}
        inativos = [contrato.get("numero") for contrato in contratos if contrato.get("status") not in status_permitidos]
        if inativos:
            raise ValueError(
                "Somente contratos ativos ou encaminhados para projeto podem ser cancelados: "
                f"{', '.join(inativos)}."
            )
        existentes = cls.repository.buscar_ativos_por_contratos(payload["contrato_ids"])
        if existentes:
            ids = sorted({str(item["id"]) for item in existentes})
            raise ValueError(f"Um dos contratos já pertence ao cancelamento #{', #'.join(ids)}.")
        payload["cliente_id"] = contratos[0]["cliente_id"]
        payload.update({
            "solicitado_por": usuario_id,
            "solicitado_por_email": usuario_email or "sistema",
            "destinatario_email": cls.DESTINATARIO,
        })
        cancelamento_id = cls.repository.criar(payload)
        item = cls.buscar_por_id(cancelamento_id)
        resultado = cls._enviar(item)
        cls.repository.registrar_resultado_email(cancelamento_id, resultado)
        return {"id": cancelamento_id, "email": resultado}

    @classmethod
    def reenviar(cls, cancelamento_id):
        item = cls.buscar_por_id(cancelamento_id)
        if not item:
            raise ValueError("Cancelamento não encontrado.")
        resultado = cls._enviar(item)
        cls.repository.registrar_resultado_email(cancelamento_id, resultado)
        return resultado

    @classmethod
    def _enviar(cls, item):
        try:
            return EmailService.enviar(
                cls._assunto(item),
                cls._corpo_email(item),
                [cls.DESTINATARIO],
            )
        except Exception as erro:
            return {"enviado": False, "erro": str(erro)[:1000]}

    @classmethod
    def _assunto(cls, item):
        cliente = item.get("cliente_nome") or item.get("cliente_razao_social") or "Cliente não informado"
        return f"Cancelamento - {cliente} - {cnpj_br(item.get('cliente_cnpj'))}"

    @classmethod
    def _corpo_email(cls, item):
        contratos = item.get("contratos") or []
        contratos_texto = "\n".join(
            f"- {contrato.get('numero') or contrato.get('id')} | Status: {contrato.get('status') or '-'}"
            for contrato in contratos
        ) or "- Nenhum contrato vinculado."
        ambientes = item.get("ambientes") or []
        ambientes_texto = "\n".join(
            f"- {amb.get('nome') or ('Ambiente #' + str(amb.get('id')))} | Tipo: {amb.get('ambiente_tipo') or '-'} | Situação: {amb.get('situacao') or '-'} | Prefixo: {amb.get('prefixo_proxmox') or '-'}"
            for amb in ambientes
        ) or "- Nenhum ambiente vinculado foi localizado; validar manualmente."
        return f"""SOLICITAÇÃO DE CANCELAMENTO

Cliente: {item.get('cliente_nome') or '-'}
Razão Social: {item.get('cliente_razao_social') or item.get('cliente_nome') or '-'}
CNPJ: {cnpj_br(item.get('cliente_cnpj'))}
Contratos ativos selecionados:
{contratos_texto}
Data/hora para desligamento: {datetime_br(item.get('data_desligamento'))}
Solicitado por: {item.get('solicitado_por_email') or item.get('solicitado_por_nome') or 'sistema'}

Motivo do cancelamento:
{item.get('motivo') or '-'}

PROVIDÊNCIAS OPERACIONAIS SOLICITADAS

1. Remover as rotinas de monitoramento do cliente.
Detalhes: {item.get('detalhes_monitoramento') or 'Identificar e remover todas as rotinas vinculadas ao cliente.'}

2. Remover as rotinas de backup do cliente.
Detalhes: {item.get('detalhes_backup') or 'Identificar e remover todas as rotinas vinculadas ao cliente, observando a política interna de retenção.'}

3. Desligar o servidor/ambiente a partir de {datetime_br(item.get('data_desligamento'))}.

4. Realizar a remoção total do ambiente conforme o procedimento operacional e as validações internas.
Detalhes: {item.get('detalhes_ambiente') or 'Validar todos os recursos vinculados antes da remoção definitiva.'}

Ambientes encontrados no O3Cloud Manager:
{ambientes_texto}

Observações adicionais:
{item.get('observacoes') or '-'}

Esta mensagem registra uma solicitação operacional. Nenhum recurso foi removido automaticamente pelo O3Cloud Manager.
"""

    @staticmethod
    def _normalizar_registro(dados):
        valores = dados.getlist("contrato_ids") if hasattr(dados, "getlist") else dados.get("contrato_ids", [])
        if isinstance(valores, str):
            valores = [valores]
        contrato_ids = []
        for valor in valores or []:
            contrato_id = CancelamentoService._inteiro(valor)
            if contrato_id and contrato_id not in contrato_ids:
                contrato_ids.append(contrato_id)
        if not contrato_ids:
            raise ValueError("Selecione ao menos um contrato ativo ou encaminhado para projeto.")
        motivo = (dados.get("motivo") or "").strip()
        if not motivo:
            raise ValueError("Informe o motivo do cancelamento.")
        data_desligamento = CancelamentoService._data_hora(dados.get("data_desligamento"))
        if not data_desligamento:
            raise ValueError("Informe a data e hora para o desligamento do servidor.")
        return {
            "contrato_ids": contrato_ids,
            "motivo": motivo[:255],
            "data_desligamento": data_desligamento,
            "detalhes_monitoramento": (dados.get("detalhes_monitoramento") or "").strip() or None,
            "detalhes_backup": (dados.get("detalhes_backup") or "").strip() or None,
            "detalhes_ambiente": (dados.get("detalhes_ambiente") or "").strip() or None,
            "observacoes": (dados.get("observacoes") or "").strip() or None,
        }

    @staticmethod
    def _normalizar_filtros(dados):
        return {
            "q": (dados.get("q") or "").strip(),
            "email_status": (dados.get("email_status") or "").strip().upper(),
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
        raise ValueError("Data de desligamento inválida.")

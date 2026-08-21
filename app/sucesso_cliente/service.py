from app.core.storage import StorageService
from app.repositories.sucesso_cliente_repository import SucessoClienteRepository


STATUS_RELACIONAMENTO = {
    "OTIMO": "Otimo",
    "BOM": "Bom",
    "REGULAR": "Regular",
    "CRITICO": "Critico",
}


class SucessoClienteService:
    repository = SucessoClienteRepository

    @classmethod
    def listar(cls, pesquisa=None, curva=None, status_relacionamento=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        contratos = cls.repository.listar_contratos(pesquisa, curva, status_relacionamento, limit, offset)
        total = cls.repository.total_contratos(pesquisa, curva, status_relacionamento)
        return [cls._decorar_contrato(item) for item in contratos], total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard() or {}

    @classmethod
    def detalhe(cls, contrato_id):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            return None
        contrato = cls._decorar_contrato(contrato)
        contrato["historico"] = cls._historico_com_anexos(contrato_id)
        relacionamento = cls.repository.buscar_relacionamento(contrato_id) or {}
        contrato["relacionamento"] = relacionamento
        contrato["contatos_cliente"] = cls.repository.listar_contatos_cliente([
            contrato.get("cliente_nome_fantasia"),
            contrato.get("cliente_razao_social"),
        ])
        if relacionamento.get("contato_id") and all(str(c.get("id")) != str(relacionamento.get("contato_id")) for c in contrato["contatos_cliente"]):
            contrato["contatos_cliente"].append({
                "id": relacionamento.get("contato_id"),
                "nome": relacionamento.get("contato_nome"),
                "email": relacionamento.get("contato_email"),
                "telefone": relacionamento.get("contato_telefone"),
                "whatsapp": relacionamento.get("contato_whatsapp"),
            })
        return contrato

    @classmethod
    def registrar_relacionamento(cls, contrato_id, dados, arquivos=None, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        status = (dados.get("status_relacionamento") or "").strip().upper()
        if status not in STATUS_RELACIONAMENTO:
            raise ValueError("Status de relacionamento inválido.")
        comentario = (dados.get("comentario") or "").strip()
        if not comentario:
            raise ValueError("Comentário é obrigatório.")
        contato_id = cls._inteiro(dados.get("contato_id"))
        arquivos = [arquivo for arquivo in (arquivos or []) if arquivo and arquivo.filename]
        for arquivo in arquivos:
            StorageService.validar(arquivo)
        cls.repository.salvar_relacionamento(contrato_id, contato_id, status, usuario_email)
        historico_id = cls.repository.inserir_historico({
            "contrato_id": contrato_id,
            "contato_id": contato_id,
            "status_relacionamento": status,
            "comentario": comentario,
            "autor_email": usuario_email,
        })
        cls._salvar_anexos(contrato_id, historico_id, arquivos)
        return historico_id

    @classmethod
    def vincular_contato(cls, contrato_id, contato_id, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        atual = cls.repository.buscar_relacionamento(contrato_id) or {}
        status = atual.get("status_relacionamento") or "BOM"
        cls.repository.salvar_relacionamento(contrato_id, cls._inteiro(contato_id), status, usuario_email)

    @classmethod
    def marcar_critico(cls, contrato_id, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        atual = cls.repository.buscar_relacionamento(contrato_id) or {}
        contato_id = cls._inteiro(atual.get("contato_id"))
        cls.repository.salvar_relacionamento(contrato_id, contato_id, "CRITICO", usuario_email)
        return cls.repository.inserir_historico({
            "contrato_id": contrato_id,
            "contato_id": contato_id,
            "status_relacionamento": "CRITICO",
            "comentario": "Marcado como crítico pela tela principal de Sucesso do Cliente.",
            "autor_email": usuario_email,
        })

    @classmethod
    def _historico_com_anexos(cls, contrato_id):
        historico = cls.repository.listar_historico(contrato_id)
        anexos = cls.repository.listar_anexos(contrato_id)
        por_historico = {}
        for anexo in anexos:
            por_historico.setdefault(anexo.get("historico_id"), []).append(anexo)
        for item in historico:
            item["anexos"] = por_historico.get(item.get("id"), [])
        return historico

    @classmethod
    def _salvar_anexos(cls, contrato_id, historico_id, arquivos):
        pasta = f"sucesso_cliente/{contrato_id}/comentarios"
        for arquivo in arquivos:
            salvo = StorageService.salvar(arquivo, pasta)
            if not salvo:
                continue
            cls.repository.inserir_anexo({
                "historico_id": historico_id,
                "contrato_id": contrato_id,
                "arquivo_original": salvo.get("arquivo_original"),
                "nome_arquivo": salvo.get("nome"),
                "caminho": f"{pasta}/{salvo.get('nome')}",
                "url": salvo.get("url"),
                "mime_type": salvo.get("mime_type"),
                "tamanho": salvo.get("tamanho"),
            })

    @classmethod
    def _decorar_contrato(cls, contrato):
        contrato = dict(contrato)
        valor = cls._decimal(contrato.get("valor_servicos_bruto") or contrato.get("valor_mensal"))
        contrato["valor_bruto_cs"] = valor
        contrato["curva"] = cls._curva(valor)
        contrato["status_relacionamento_label"] = STATUS_RELACIONAMENTO.get(contrato.get("status_relacionamento"), "Sem registro")
        return contrato

    @staticmethod
    def _curva(valor):
        if valor >= 2999.99:
            return "A"
        if valor >= 1000:
            return "B"
        return "C"

    @staticmethod
    def _decimal(valor):
        try:
            return float(valor or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor) if valor not in (None, "") else None
        except (TypeError, ValueError):
            return None

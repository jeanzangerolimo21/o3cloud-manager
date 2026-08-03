from app.clientes.service import ClienteService
from app.parceiros.service import ParceiroService
from app.repositories.cofre_pasta_repository import CofrePastaRepository


TIPOS_COFRE_PASTA = {
    "cliente": "Cliente",
    "parceiro": "Parceiro",
    "usuario": "Usuário logado",
}


class CofrePastaService:
    repository = CofrePastaRepository

    @classmethod
    def listar(cls, pesquisa=None, tipo=None, ativo="1"):
        ativo_normalizado = cls._normalizar_ativo(ativo)
        return cls.repository.listar(pesquisa=pesquisa, tipo=tipo, ativo=ativo_normalizado)

    @classmethod
    def listar_ativas(cls):
        return cls.repository.listar_ativas()

    @classmethod
    def listar_pastas_usuario(cls, usuario_email):
        return cls.repository.listar_pastas_usuario(usuario_email)

    @classmethod
    def listar_pastas_compartilhadas_com_usuario(cls, usuario_email):
        return cls.repository.listar_pastas_compartilhadas_com_usuario(usuario_email)

    @classmethod
    def listar_usuarios_sistema(cls):
        return cls.repository.listar_usuarios_sistema()

    @classmethod
    def buscar_por_id(cls, pasta_id):
        return cls.repository.buscar_por_id(pasta_id)

    @classmethod
    def listar_parceiros_navegacao(cls):
        return cls.repository.listar_parceiros_navegacao()

    @classmethod
    def buscar_parceiro_navegacao(cls, parceiro_id):
        if not parceiro_id:
            return None
        return cls.repository.buscar_parceiro_navegacao(parceiro_id)

    @classmethod
    def listar_pastas_cliente_por_parceiro(cls, parceiro_id):
        if not parceiro_id:
            return []
        return cls.repository.listar_pastas_cliente_por_parceiro(parceiro_id)

    @classmethod
    def contexto_form(cls):
        return {
            "clientes": ClienteService.listar_para_importacao(),
            "parceiros": ParceiroService.listar_todos_ativos(),
            "tipo_options": TIPOS_COFRE_PASTA,
            "usuarios_sistema": cls.listar_usuarios_sistema(),
        }

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar(dados, usuario_email)
        return cls.repository.inserir(payload)

    @classmethod
    def atualizar(cls, pasta_id, dados, usuario_email="sistema"):
        if not cls.repository.buscar_por_id(pasta_id):
            raise ValueError("Pasta não encontrada.")
        payload = cls._normalizar(dados, usuario_email)
        cls.repository.atualizar(pasta_id, payload)

    @classmethod
    def excluir(cls, pasta_id):
        if not cls.repository.buscar_por_id(pasta_id):
            raise ValueError("Pasta não encontrada.")
        cls.repository.excluir(pasta_id)

    @classmethod
    def _normalizar(cls, dados, usuario_email="sistema"):
        nome = cls._texto(dados.get("nome"))
        tipo = cls._texto(dados.get("tipo")) or "usuario"
        if not nome:
            raise ValueError("Nome da pasta é obrigatório.")
        if tipo not in TIPOS_COFRE_PASTA:
            raise ValueError("Tipo de pasta inválido.")

        parceiro_id = None
        parceiro_nome = None
        cliente_id = None
        cliente_nome = None
        if tipo in ("parceiro", "cliente"):
            parceiro_id = cls._inteiro(dados.get("parceiro_id"))
            if not parceiro_id:
                raise ValueError("Parceiro é obrigatório para esta pasta.")
            parceiro = ParceiroService.buscar_por_id(parceiro_id)
            if not parceiro:
                raise ValueError("Parceiro selecionado não encontrado.")
            parceiro_nome = parceiro.get("nome_fantasia") or parceiro.get("nome") or parceiro.get("razao_social")
        if tipo == "cliente":
            cliente_id = cls._inteiro(dados.get("cliente_id"))
            if not cliente_id:
                raise ValueError("Cliente é obrigatório para pasta por cliente.")
            cliente = ClienteService.buscar_por_id(cliente_id)
            if not cliente:
                raise ValueError("Cliente selecionado não encontrado.")
            cliente_nome = cliente.get("nome_fantasia") or cliente.get("razao_social")

        return {
            "nome": nome,
            "tipo": tipo,
            "parceiro_id": parceiro_id,
            "parceiro_nome": parceiro_nome,
            "cliente_id": cliente_id,
            "cliente_nome": cliente_nome,
            "owner_email": cls._texto(dados.get("owner_email")) or usuario_email or "sistema",
            "compartilhada": 1 if str(dados.get("compartilhada", "0")) == "1" else 0,
            "compartilhada_com": cls._texto_longo(dados.get("compartilhada_com")),
            "observacoes": cls._texto_longo(dados.get("observacoes")),
            "ativo": 1 if str(dados.get("ativo", "1")) != "0" else 0,
        }

    @staticmethod
    def _normalizar_ativo(valor):
        if valor == "todos":
            return None
        try:
            return 1 if int(valor) == 1 else 0
        except (TypeError, ValueError):
            return 1

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _texto_longo(valor):
        return (valor or "").strip() or None

import base64
import hashlib
import hmac
import os

from flask import current_app

from app.clientes.service import ClienteService
from app.implantacao.cofre_pastas_service import TIPOS_COFRE_PASTA
from app.repositories.cofre_pasta_repository import CofrePastaRepository
from app.repositories.cofre_senha_repository import CofreSenhaRepository
from app.repositories.faixa_rede_repository import FaixaRedeRepository
from app.repositories.o3web_licenca_repository import O3WebLicencaRepository


CATEGORIAS_COFRE_SENHAS = {
    "firewall": "Firewall",
    "vpn": "VPN",
    "o3web": "O3Web",
    "proxmox": "Proxmox",
    "pbs": "PBS",
    "zabbix": "Zabbix",
    "linux": "Linux",
    "windows": "Windows",
    "banco": "Banco de Dados",
    "outros": "Outros",
}


class CofreSenhaService:
    repository = CofreSenhaRepository

    @classmethod
    def listar(cls, pesquisa=None, categoria=None, ativo="1", pasta_id=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        senhas = cls.repository.listar(
            pesquisa=pesquisa,
            categoria=categoria,
            ativo=ativo_normalizado,
            pasta_id=pasta_id,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(pesquisa=pesquisa, categoria=categoria, ativo=ativo_normalizado, pasta_id=pasta_id)
        return senhas, total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar_por_id(cls, senha_id):
        return cls.repository.buscar_por_id(senha_id)

    @classmethod
    def contexto_form(cls):
        return {
            "clientes": ClienteService.listar_para_importacao(),
            "faixas_rede": cls.repository.listar_faixas_ativas(),
            "licencas_o3web": cls.repository.listar_licencas_ativas(),
            "pastas": CofrePastaRepository.listar_ativas(),
            "pasta_tipo_options": TIPOS_COFRE_PASTA,
            "categoria_options": CATEGORIAS_COFRE_SENHAS,
            "senha_policy": cls.politica_gerador_senha(),
        }

    @classmethod
    def politica_gerador_senha(cls):
        return {
            "tamanho": current_app.config.get("COFRE_SENHA_GERADOR_TAMANHO", 20),
            "maiusculas": bool(current_app.config.get("COFRE_SENHA_GERADOR_MAIUSCULAS", True)),
            "minusculas": bool(current_app.config.get("COFRE_SENHA_GERADOR_MINUSCULAS", True)),
            "numeros": bool(current_app.config.get("COFRE_SENHA_GERADOR_NUMEROS", True)),
            "simbolos": bool(current_app.config.get("COFRE_SENHA_GERADOR_SIMBOLOS", True)),
        }

    @classmethod
    def criar(cls, dados, usuario_email="sistema", ip_origem=None):
        payload = cls._normalizar(dados, exigir_senha=True)
        payload["senha_encrypted"] = cls._encrypt(payload.pop("senha"))
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        senha_id = cls.repository.inserir(payload)
        cls.repository.registrar_auditoria(senha_id, "CRIAR", usuario_email, "Credencial criada", ip_origem)
        return senha_id

    @classmethod
    def atualizar(cls, senha_id, dados, usuario_email="sistema", ip_origem=None):
        existente = cls.repository.buscar_por_id(senha_id)
        if not existente:
            raise ValueError("Credencial não encontrada.")
        payload = cls._normalizar(dados, exigir_senha=False)
        if payload.pop("senha", None):
            payload["senha_encrypted"] = cls._encrypt(dados.get("senha"))
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar(senha_id, payload)
        cls.repository.registrar_auditoria(senha_id, "ATUALIZAR", usuario_email, "Credencial atualizada", ip_origem)

    @classmethod
    def excluir(cls, senha_id, usuario_email="sistema", ip_origem=None):
        if not cls.repository.buscar_por_id(senha_id):
            raise ValueError("Credencial não encontrada.")
        cls.repository.excluir(senha_id, usuario_email)
        cls.repository.registrar_auditoria(senha_id, "INATIVAR", usuario_email, "Credencial inativada", ip_origem)

    @classmethod
    def revelar_senha(cls, senha_id, usuario_email="sistema", ip_origem=None):
        senha = cls.repository.buscar_por_id(senha_id)
        if not senha or not senha.get("ativo"):
            raise ValueError("Credencial não encontrada ou inativa.")
        try:
            valor = cls._decrypt(senha.get("senha_encrypted"))
        except ValueError as erro:
            raise ValueError("Não foi possível descriptografar a senha. Verifique a chave do cofre.") from erro
        cls.repository.registrar_auditoria(senha_id, "REVELAR", usuario_email, "Senha revelada na interface", ip_origem)
        return valor

    @classmethod
    def listar_auditoria(cls, senha_id):
        return cls.repository.listar_auditoria(senha_id)

    @classmethod
    def _normalizar(cls, dados, exigir_senha=False):
        cliente_id = cls._inteiro(dados.get("cliente_id"))
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        cliente = ClienteService.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente selecionado não encontrado.")
        cliente_nome = (cliente.get("nome_fantasia") or cliente.get("razao_social") or "").strip()

        faixa_rede_id = cls._inteiro(dados.get("faixa_rede_id"))
        if not faixa_rede_id:
            raise ValueError("Faixa de rede é obrigatória.")
        faixa = FaixaRedeRepository.buscar_por_id(faixa_rede_id)
        if not faixa or not faixa.get("ativo"):
            raise ValueError("Faixa de rede selecionada não encontrada ou inativa.")
        if int(faixa.get("cliente_id") or 0) != cliente_id:
            raise ValueError("A faixa de rede selecionada não pertence ao cliente informado.")

        pasta_id = cls._inteiro(dados.get("pasta_id")) or None
        if pasta_id:
            pasta = CofrePastaRepository.buscar_por_id(pasta_id)
            if not pasta or not pasta.get("ativo"):
                raise ValueError("Pasta selecionada não encontrada ou inativa.")

        licenca_o3web_id = cls._inteiro(dados.get("licenca_o3web_id")) or None
        if licenca_o3web_id:
            licenca = O3WebLicencaRepository.buscar_por_id(licenca_o3web_id)
            if not licenca or not licenca.get("ativo"):
                raise ValueError("Licença O3Web selecionada não encontrada ou inativa.")
            if licenca.get("cliente_id") and int(licenca.get("cliente_id")) != cliente_id:
                raise ValueError("A licença O3Web selecionada não pertence ao cliente informado.")

        categoria = cls._texto(dados.get("categoria")) or "outros"
        if categoria not in CATEGORIAS_COFRE_SENHAS:
            raise ValueError("Categoria inválida.")
        titulo = cls._texto(dados.get("titulo"))
        usuario = cls._texto(dados.get("usuario"))
        senha = dados.get("senha") or ""
        if not titulo:
            raise ValueError("Título é obrigatório.")
        if not usuario:
            raise ValueError("Usuário é obrigatório.")
        if exigir_senha and not senha:
            raise ValueError("Senha é obrigatória.")

        return {
            "pasta_id": pasta_id,
            "cliente_id": cliente_id,
            "cliente_nome": cliente_nome,
            "cliente_cnpj": cliente.get("cnpj"),
            "faixa_rede_id": faixa_rede_id,
            "licenca_o3web_id": licenca_o3web_id,
            "categoria": categoria,
            "titulo": titulo,
            "host": cls._texto(dados.get("host")),
            "porta": cls._inteiro(dados.get("porta")) or None,
            "url": cls._texto(dados.get("url")),
            "usuario": usuario,
            "senha": senha,
            "observacoes": cls._texto_longo(dados.get("observacoes")),
            "proxmox_node_id": cls._texto(dados.get("proxmox_node_id")),
            "proxmox_vm_id": cls._texto(dados.get("proxmox_vm_id")),
            "pbs_server_id": cls._texto(dados.get("pbs_server_id")),
            "zabbix_host_id": cls._texto(dados.get("zabbix_host_id")),
            "ativo": 1 if str(dados.get("ativo", "1")) != "0" else 0,
        }

    @classmethod
    def _key(cls):
        configured = current_app.config.get("COFRE_SENHAS_KEY")
        secret = configured or current_app.config.get("SECRET_KEY") or "o3cloud-dev"
        return hashlib.sha256(secret.encode("utf-8")).digest()

    @classmethod
    def _encrypt(cls, valor):
        key = cls._key()
        nonce = os.urandom(16)
        plain = valor.encode("utf-8")
        cipher = cls._xor_stream(plain, key, nonce)
        assinatura = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
        return "v1:" + base64.urlsafe_b64encode(nonce + assinatura + cipher).decode("utf-8")

    @classmethod
    def _decrypt(cls, valor):
        if not valor or not str(valor).startswith("v1:"):
            raise ValueError("Formato de senha criptografada inválido.")
        key = cls._key()
        try:
            payload = base64.urlsafe_b64decode(str(valor)[3:].encode("utf-8"))
        except Exception as erro:
            raise ValueError("Payload criptografado inválido.") from erro
        nonce = payload[:16]
        assinatura = payload[16:48]
        cipher = payload[48:]
        esperado = hmac.new(key, nonce + cipher, hashlib.sha256).digest()
        if not hmac.compare_digest(assinatura, esperado):
            raise ValueError("Assinatura da senha criptografada inválida.")
        return cls._xor_stream(cipher, key, nonce).decode("utf-8")

    @staticmethod
    def _xor_stream(payload, key, nonce):
        resultado = bytearray()
        contador = 0
        while len(resultado) < len(payload):
            bloco = hashlib.sha256(key + nonce + contador.to_bytes(4, "big")).digest()
            resultado.extend(bloco)
            contador += 1
        return bytes(valor ^ chave for valor, chave in zip(payload, resultado))

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

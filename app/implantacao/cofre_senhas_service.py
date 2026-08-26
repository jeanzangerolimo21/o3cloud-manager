import base64
import hashlib
import hmac
import os
import secrets
from pathlib import Path

from flask import current_app

from app.core.auditoria import registrar_evento
from app.core.storage import StorageService
from app.clientes.service import ClienteService
from app.ambientes.implantador_service import ImplantadorService
from app.implantacao.cofre_pastas_service import TIPOS_COFRE_PASTA
from app.repositories.ambiente_repository import AmbienteRepository
from app.repositories.cofre_pasta_repository import CofrePastaRepository
from app.repositories.cofre_senha_repository import CofreSenhaRepository
from app.repositories.faixa_rede_repository import FaixaRedeRepository
from app.repositories.o3web_licenca_repository import O3WebLicencaRepository


COFRE_COMPARTILHAMENTO_TTL_MINUTOS_MIN = 5
COFRE_COMPARTILHAMENTO_TTL_MINUTOS_MAX = 60 * 60


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
    def listar(cls, pesquisa=None, categoria=None, ativo="1", pasta_id=None, apenas_clientes=False, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        senhas = cls.repository.listar(
            pesquisa=pesquisa,
            categoria=categoria,
            ativo=ativo_normalizado,
            pasta_id=pasta_id,
            apenas_clientes=apenas_clientes,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(pesquisa=pesquisa, categoria=categoria, ativo=ativo_normalizado, pasta_id=pasta_id, apenas_clientes=apenas_clientes)
        return senhas, total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar_por_id(cls, senha_id, usuario_email=None):
        senha = cls.repository.buscar_por_id(senha_id)
        if senha and usuario_email and not cls._usuario_tem_acesso(senha, usuario_email):
            return None
        return senha

    @classmethod
    def contexto_form(cls, usuario_email=None):
        return {
            "clientes": ClienteService.listar_para_importacao(),
            "ambientes": AmbienteRepository.listar_ativos_para_select(),
            "implantadores": ImplantadorService.listar_para_select(),
            "faixas_rede": cls.repository.listar_faixas_ativas(),
            "licencas_o3web": cls.repository.listar_licencas_ativas(),
            "pastas": CofrePastaRepository.listar_ativas_para_usuario(usuario_email),
            "pasta_tipo_options": TIPOS_COFRE_PASTA,
            "categoria_options": CATEGORIAS_COFRE_SENHAS,
            "senha_policy": cls.politica_gerador_senha(),
            **cls.repository.listar_vinculos_infraestrutura(),
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
    def criar(cls, dados, arquivos=None, usuario_email="sistema", ip_origem=None):
        cls._validar_anexos(arquivos)
        payload = cls._normalizar(dados, exigir_senha=True, usuario_email=usuario_email)
        payload["senha_encrypted"] = cls._encrypt(payload.pop("senha"))
        senha_2 = payload.pop("senha_2", None)
        payload["senha_2_encrypted"] = cls._encrypt(senha_2) if senha_2 else None
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        senha_id = cls.repository.inserir(payload)
        total_anexos = cls._salvar_anexos(senha_id, arquivos, usuario_email)
        registrar_evento("COFRE_CREDENCIAL_CRIADA", "cofre_senhas", senha_id, {"cliente_id": payload.get("cliente_id"), "categoria": payload.get("categoria"), "titulo": payload.get("titulo"), "anexos": total_anexos}, usuario_email)
        return senha_id

    @classmethod
    def atualizar(cls, senha_id, dados, arquivos=None, usuario_email="sistema", ip_origem=None):
        cls._validar_anexos(arquivos)
        existente = cls.buscar_por_id(senha_id, usuario_email)
        if not existente:
            raise ValueError("Credencial não encontrada.")
        payload = cls._normalizar({**existente, **dados}, exigir_senha=False, usuario_email=usuario_email)
        if payload.pop("senha", None):
            payload["senha_encrypted"] = cls._encrypt(dados.get("senha"))
        senha_2 = payload.pop("senha_2", None)
        if senha_2:
            payload["senha_2_encrypted"] = cls._encrypt(senha_2)
        elif not payload.get("usuario_2"):
            payload["senha_2_encrypted"] = None
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar(senha_id, payload)
        total_anexos = cls._salvar_anexos(senha_id, arquivos, usuario_email)
        registrar_evento("COFRE_CREDENCIAL_ATUALIZADA", "cofre_senhas", senha_id, {"cliente_id": payload.get("cliente_id"), "categoria": payload.get("categoria"), "titulo": payload.get("titulo"), "senha_alterada": bool(dados.get("senha")), "senha_2_alterada": bool(senha_2), "anexos_adicionados": total_anexos}, usuario_email)

    @classmethod
    def listar_anexos(cls, senha_id, usuario_email="sistema"):
        if not cls.buscar_por_id(senha_id, usuario_email):
            raise ValueError("Credencial não encontrada.")
        return cls.repository.listar_anexos(senha_id)

    @classmethod
    def buscar_anexo(cls, anexo_id, usuario_email="sistema"):
        anexo = cls.repository.buscar_anexo(anexo_id)
        if not anexo:
            return None
        if not cls.buscar_por_id(anexo.get("cofre_senha_id"), usuario_email):
            return None
        return anexo

    @classmethod
    def excluir_anexo(cls, anexo_id, usuario_email="sistema"):
        anexo = cls.buscar_anexo(anexo_id, usuario_email)
        if not anexo:
            raise ValueError("Anexo não encontrado.")
        cls.repository.excluir_anexo(anexo_id)
        cls._remover_arquivo_storage(anexo.get("caminho"))
        registrar_evento("COFRE_CREDENCIAL_ANEXO_EXCLUIDO", "cofre_senhas", anexo.get("cofre_senha_id"), {"arquivo": anexo.get("arquivo_original")}, usuario_email)
        return anexo

    @classmethod
    def excluir(cls, senha_id, usuario_email="sistema", ip_origem=None):
        if not cls.buscar_por_id(senha_id, usuario_email):
            raise ValueError("Credencial não encontrada.")
        cls.repository.excluir(senha_id, usuario_email)
        registrar_evento("COFRE_CREDENCIAL_INATIVADA", "cofre_senhas", senha_id, None, usuario_email)

    @classmethod
    def revelar_senha(cls, senha_id, usuario_email="sistema", ip_origem=None, credencial=None):
        senha = cls.buscar_por_id(senha_id, usuario_email)
        if not senha or not senha.get("ativo"):
            raise ValueError("Credencial não encontrada ou inativa.")
        credencial = cls._normalizar_credencial(credencial)
        campo = "senha_2_encrypted" if credencial == "secundaria" else "senha_encrypted"
        if credencial == "secundaria" and (not senha.get("usuario_2") or not senha.get("senha_2_encrypted")):
            raise ValueError("Credencial secundaria não cadastrada.")
        try:
            valor = cls._decrypt(senha.get(campo))
        except ValueError as erro:
            raise ValueError("Não foi possível descriptografar a senha. Verifique a chave do cofre.") from erro
        registrar_evento("COFRE_CREDENCIAL_REVELADA", "cofre_senhas", senha_id, {"titulo": senha.get("titulo"), "cliente_id": senha.get("cliente_id"), "credencial": credencial}, usuario_email)
        return valor

    @classmethod
    def criar_compartilhamento(cls, senha_id, usuario_email="sistema", ip_origem=None, credencial=None, ttl_minutos=None):
        senha = cls.buscar_por_id(senha_id, usuario_email)
        if not senha or not senha.get("ativo"):
            raise ValueError("Credencial nao encontrada ou sem acesso.")
        credencial = cls._normalizar_credencial(credencial)
        if credencial == "secundaria" and (not senha.get("usuario_2") or not senha.get("senha_2_encrypted")):
            raise ValueError("Credencial secundaria não cadastrada.")
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        ttl = cls._normalizar_ttl_compartilhamento(ttl_minutos)
        cls.repository.criar_compartilhamento({
            "cofre_senha_id": senha_id, "credencial": credencial, "token_hash": token_hash,
            "ttl_minutos": ttl, "created_by": usuario_email, "created_ip": ip_origem,
        })
        registrar_evento(
            "COFRE_COMPARTILHAMENTO_GERADO", "cofre_senhas", senha_id,
            {"titulo": senha.get("titulo"), "expira_em_minutos": ttl, "credencial": credencial}, usuario_email,
        )
        return token

    @staticmethod
    def _normalizar_ttl_compartilhamento(ttl_minutos=None):
        if ttl_minutos in (None, ""):
            ttl_minutos = current_app.config.get("COFRE_COMPARTILHAMENTO_TTL_MINUTOS", COFRE_COMPARTILHAMENTO_TTL_MINUTOS_MIN)
        try:
            ttl = int(str(ttl_minutos).strip())
        except (TypeError, ValueError) as erro:
            raise ValueError("Informe a validade do link em minutos.") from erro
        if ttl < COFRE_COMPARTILHAMENTO_TTL_MINUTOS_MIN:
            raise ValueError("A validade minima do link temporario e de 5 minutos.")
        if ttl > COFRE_COMPARTILHAMENTO_TTL_MINUTOS_MAX:
            raise ValueError("A validade maxima do link temporario e de 60 horas.")
        return ttl

    @classmethod
    def consumir_compartilhamento(cls, token, ip_origem=None):
        if not token or len(token) > 128:
            return None
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        compartilhamento = cls.repository.consumir_compartilhamento(token_hash, ip_origem)
        if not compartilhamento:
            return None
        campo = "senha_2_encrypted" if compartilhamento.get("credencial") == "secundaria" else "senha_encrypted"
        try:
            valor = cls._decrypt(compartilhamento.get(campo))
        except ValueError:
            return None
        registrar_evento(
            "COFRE_COMPARTILHAMENTO_ACESSADO", "cofre_senhas",
            compartilhamento.get("cofre_senha_id"),
            {"titulo": compartilhamento.get("titulo"), "credencial": compartilhamento.get("credencial") or "principal"}, "link-publico",
        )
        return {
            "titulo": compartilhamento.get("titulo"),
            "senha": valor,
            "expires_at": compartilhamento.get("expires_at"),
        }

    @classmethod
    def _validar_anexos(cls, arquivos):
        for arquivo in arquivos or []:
            if arquivo and arquivo.filename:
                StorageService.validar(arquivo)

    @classmethod
    def _salvar_anexos(cls, senha_id, arquivos, usuario_email="sistema"):
        total = 0
        for arquivo in arquivos or []:
            if not arquivo or not arquivo.filename:
                continue
            salvo = StorageService.salvar(arquivo, f"cofre_senhas/{senha_id}")
            if not salvo:
                continue
            salvo["created_by"] = usuario_email or "sistema"
            cls.repository.inserir_anexo(senha_id, salvo)
            total += 1
        return total

    @staticmethod
    def _remover_arquivo_storage(caminho):
        if not caminho:
            return
        base = StorageService.BASE_STORAGE.resolve()
        arquivo = Path(caminho).resolve()
        try:
            dentro_storage = arquivo.is_relative_to(base)
        except AttributeError:
            dentro_storage = str(arquivo).startswith(str(base) + os.sep)
        if dentro_storage and arquivo.exists() and arquivo.is_file():
            arquivo.unlink()

    @staticmethod
    def _usuario_tem_acesso(senha, usuario_email):
        if (senha.get("pasta_tipo") or "") != "usuario":
            return True
        usuario_email = (usuario_email or "sistema").strip().lower()
        if usuario_email == "sistema":
            return True
        owner = (senha.get("pasta_owner_email") or "").strip().lower()
        if owner == usuario_email:
            return True
        if not senha.get("pasta_compartilhada"):
            return False
        compartilhados = {
            item.strip().lower()
            for item in str(senha.get("pasta_compartilhada_com") or "").replace(";", ",").split(",")
            if item.strip()
        }
        return usuario_email in compartilhados

    @classmethod
    def listar_auditoria(cls, senha_id):
        return cls.repository.listar_auditoria(senha_id)

    @classmethod
    def _normalizar(cls, dados, exigir_senha=False, usuario_email=None):
        cliente_id = cls._inteiro(dados.get("cliente_id"))
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        cliente = ClienteService.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente selecionado não encontrado.")
        cliente_nome = (cliente.get("nome_fantasia") or cliente.get("razao_social") or "").strip()

        ambiente_id = cls._inteiro(dados.get("ambiente_id")) or None
        if ambiente_id and not AmbienteRepository.pertence_ao_cliente(ambiente_id, cliente_id):
            raise ValueError("O ambiente selecionado não pertence ao cliente informado ou está inativo.")

        implantador_id = cls._inteiro(dados.get("implantador_id")) or None
        if implantador_id:
            implantador = ImplantadorService.buscar_por_id(implantador_id)
            if not implantador or not implantador.get("ativo"):
                raise ValueError("Implantador selecionado não encontrado ou inativo.")

        faixa_rede_id = cls._inteiro(dados.get("faixa_rede_id")) or None
        if faixa_rede_id:
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
            if pasta.get("tipo") == "usuario" and not cls._usuario_tem_acesso({
                "pasta_tipo": pasta.get("tipo"),
                "pasta_owner_email": pasta.get("owner_email"),
                "pasta_compartilhada": pasta.get("compartilhada"),
                "pasta_compartilhada_com": pasta.get("compartilhada_com"),
            }, usuario_email):
                raise ValueError("Você não tem acesso a esta pasta particular do cofre.")

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
        usuario_2 = cls._texto(dados.get("usuario_2"))
        senha_2 = dados.get("senha_2") or ""
        if not exigir_senha and senha == "********":
            senha = ""
        if not exigir_senha and senha_2 == "********":
            senha_2 = ""
        if not titulo:
            raise ValueError("Título é obrigatório.")
        if not usuario:
            raise ValueError("Usuário é obrigatório.")
        if exigir_senha and not senha:
            raise ValueError("Senha é obrigatória.")
        if usuario_2 and exigir_senha and not senha_2:
            raise ValueError("Senha da credencial secundaria é obrigatória quando o usuário secundário é informado.")
        if usuario_2 and not senha_2 and not dados.get("senha_2_encrypted"):
            raise ValueError("Senha da credencial secundaria é obrigatória quando o usuário secundário é informado.")
        if senha_2 and not usuario_2:
            raise ValueError("Usuário secundário é obrigatório quando a senha secundaria é informada.")

        return {
            "pasta_id": pasta_id,
            "cliente_id": cliente_id,
            "cliente_nome": cliente_nome,
            "cliente_cnpj": cliente.get("cnpj"),
            "ambiente_id": ambiente_id,
            "implantador_id": implantador_id,
            "faixa_rede_id": faixa_rede_id,
            "licenca_o3web_id": licenca_o3web_id,
            "categoria": categoria,
            "titulo": titulo,
            "host": cls._texto(dados.get("host")),
            "porta": cls._inteiro(dados.get("porta")) or None,
            "url": cls._texto(dados.get("url")),
            "usuario": usuario,
            "senha": senha,
            "usuario_2": usuario_2,
            "senha_2": senha_2,
            "observacoes": cls._texto_longo(dados.get("observacoes")),
            "proxmox_node_id": cls._texto(dados.get("proxmox_node_id")),
            "proxmox_vm_id": cls._texto(dados.get("proxmox_vm_id")),
            "pbs_server_id": cls._texto(dados.get("pbs_server_id")),
            "zabbix_host_id": cls._texto(dados.get("zabbix_host_id")),
            "proxmox_node_inventory_id": cls._inteiro(dados.get("proxmox_node_inventory_id")) or None,
            "proxmox_inventory_id": cls._inteiro(dados.get("proxmox_inventory_id")) or None,
            "pbs_backup_snapshot_id": cls._inteiro(dados.get("pbs_backup_snapshot_id")) or None,
            "zabbix_host_inventory_id": cls._inteiro(dados.get("zabbix_host_inventory_id")) or None,
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
    def _normalizar_credencial(valor):
        return "secundaria" if str(valor or "").strip().lower() in ("2", "secundaria", "usuario_2") else "principal"

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

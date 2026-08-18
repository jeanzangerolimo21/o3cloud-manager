from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests

from app.clientes.service import ClienteService
from app.implantacao.integracoes_service import IntegracaoConfigService
from app.integracoes.proxmox.client import ProxmoxClient
from app.repositories.proxmox_inventory_repository import ProxmoxInventoryRepository


class ProxmoxInventoryService:
    repository = ProxmoxInventoryRepository
    STORAGES_VM_CT_CONTABILIZADOS = {"nvme", "storage2"}

    @classmethod
    def listar(cls, tipo=None, status=None, node=None, pesquisa=None):
        return [
            cls._com_link_recurso(item)
            for item in cls.repository.listar(tipo=tipo, status=status, node=node, pesquisa=pesquisa)
        ]

    @classmethod
    def clientes(cls):
        return ClienteService.listar_para_importacao()

    @classmethod
    def vincular_cliente(cls, inventario_id, cliente_id):
        cliente_id = int(cliente_id or 0) or None
        if cliente_id and not ClienteService.buscar_por_id(cliente_id):
            raise ValueError("Cliente selecionado não encontrado.")
        cls.repository.vincular_cliente(inventario_id, cliente_id)

    @classmethod
    def dashboard(cls, tipo=None):
        return cls.repository.dashboard(tipo=tipo) or {}

    @classmethod
    def nodes(cls):
        return cls.repository.listar_nodes()

    @classmethod
    def execucoes_recentes(cls):
        return cls.repository.listar_execucoes()

    @classmethod
    def clusters(cls):
        return [cls._com_percentuais_cluster(item) for item in cls.repository.listar_clusters_dashboard()]

    @classmethod
    def dashboard_clusters(cls):
        dashboard = cls.repository.dashboard_clusters() or {}
        dashboard["cpu_consumida_percent"] = cls._percentual(
            dashboard.get("cpu_consumida"), dashboard.get("cpu_total")
        )
        dashboard["cpu_alocada_percent"] = cls._percentual(
            dashboard.get("cpu_alocada"), dashboard.get("cpu_total")
        )
        dashboard["memoria_usada_percent"] = cls._percentual(
            dashboard.get("memoria_usada_mb"), dashboard.get("memoria_total_mb")
        )
        dashboard["memoria_alocada_percent"] = cls._percentual(
            dashboard.get("memoria_alocada_mb"), dashboard.get("memoria_total_mb")
        )
        dashboard["disco_usado_percent"] = cls._percentual(
            dashboard.get("disco_usado_gb"), dashboard.get("disco_total_gb")
        )
        dashboard["disco_alocado_percent"] = cls._percentual(
            dashboard.get("disco_alocado_gb"), dashboard.get("disco_total_gb")
        )
        return dashboard

    @classmethod
    def nodes_por_cluster(cls):
        return [cls._com_percentuais_node(item) for item in cls.repository.listar_nodes_por_cluster()]

    @classmethod
    def listar_nodes_dashboard(cls):
        return [cls._com_percentuais_node(item) for item in cls.repository.listar_nodes_dashboard()]

    @classmethod
    def dashboard_nodes(cls):
        dashboard = cls.repository.dashboard_nodes() or {}
        total_memoria = float(dashboard.get("memoria_total_mb") or 0)
        usada_memoria = float(dashboard.get("memoria_usada_mb") or 0)
        total_disco = float(dashboard.get("disco_total_gb") or 0)
        usado_disco = float(dashboard.get("disco_usado_gb") or 0)
        dashboard["memoria_usada_percent"] = cls._percentual(usada_memoria, total_memoria)
        dashboard["disco_usado_percent"] = cls._percentual(usado_disco, total_disco)
        return dashboard

    @classmethod
    def sincronizar(cls, usuario_email="sistema", detalhado=False, integracao_id=None):
        integracao = cls._integracao_proxmox_ativa(integracao_id)
        if not integracao:
            raise ValueError("Nenhuma integração Proxmox ativa encontrada.")
        execucao_id = cls.repository.criar_execucao(integracao["id"], usuario_email)
        try:
            segredo = IntegracaoConfigService.revelar_segredo_config(integracao["id"])
            cliente = ProxmoxClient(
                integracao.get("base_url"),
                IntegracaoConfigService._token_api_nome(integracao),
                segredo,
                timeout=integracao.get("timeout_seconds") or 30,
                verify_ssl=bool(integracao.get("verify_ssl")),
            )
            nodes = cls._coletar_nodes(cliente)
            cls.repository.salvar_nodes(integracao["id"], nodes)

            recursos = []
            for item in cliente.listar_vms_containers():
                config = {}
                if detalhado:
                    try:
                        config = cliente.obter_configuracao(item.get("node"), item.get("type"), item.get("vmid"))
                    except requests.exceptions.RequestException:
                        config = {}
                recursos.append(cls._normalizar_recurso(item, config))
            atualizadas = cls.repository.salvar_inventario(integracao["id"], recursos)
            mensagem = f"Sincronismo Proxmox read-only concluído. Recursos lidos: {len(recursos)}."
            cls.repository.finalizar_execucao(execucao_id, "OK", len(recursos), atualizadas, mensagem)
            return {"status": "OK", "mensagem": mensagem, "lidas": len(recursos), "atualizadas": atualizadas}
        except requests.exceptions.SSLError:
            mensagem = "Falha na validação SSL do certificado Proxmox."
        except requests.exceptions.Timeout:
            mensagem = "Timeout ao consultar inventário Proxmox."
        except requests.exceptions.ConnectionError:
            mensagem = "Falha de conexão ao consultar inventário Proxmox."
        except requests.exceptions.HTTPError as erro:
            codigo = erro.response.status_code if erro.response is not None else "HTTP"
            mensagem = f"Falha HTTP {codigo} ao consultar inventário Proxmox."
        except Exception as erro:
            mensagem = f"Falha ao sincronizar inventário Proxmox: {str(erro)[:160]}"
        cls.repository.finalizar_execucao(execucao_id, "ERRO", 0, 0, mensagem)
        return {"status": "ERRO", "mensagem": mensagem, "lidas": 0, "atualizadas": 0}

    @classmethod
    def _coletar_nodes(cls, cliente):
        nodes_base = cliente.listar_nodes()

        def coletar(node):
            node_nome = node.get("node")
            status_node = {}
            storages_node = []
            conteudos_storage = {}
            falha_conteudo_storage = False
            try:
                status_node = cliente.obter_status_node(node_nome)
            except requests.exceptions.RequestException:
                status_node = {}
            try:
                storages_node = cliente.listar_storage_node(node_nome)
            except requests.exceptions.RequestException:
                storages_node = []
            for storage in storages_node:
                storage_nome = storage.get("storage")
                if not cls._storage_vm_ct_contabilizado(storage_nome):
                    continue
                try:
                    conteudos_storage[storage_nome] = cliente.listar_conteudo_storage(node_nome, storage_nome)
                except requests.exceptions.RequestException:
                    falha_conteudo_storage = True
            if falha_conteudo_storage:
                conteudos_storage = {}
            return cls._normalizar_node(node, status_node, storages_node, conteudos_storage)

        with ThreadPoolExecutor(max_workers=min(6, max(1, len(nodes_base)))) as executor:
            futures = [executor.submit(coletar, node) for node in nodes_base]
            return [future.result() for future in as_completed(futures)]

    @classmethod
    def sincronizar_integracao(cls, integracao_id, usuario_email="sistema", detalhado=False):
        return cls.sincronizar(usuario_email=usuario_email, detalhado=detalhado, integracao_id=integracao_id)

    @classmethod
    def _integracao_proxmox_ativa(cls, integracao_id=None):
        if integracao_id:
            integracao = IntegracaoConfigService.buscar_por_id(integracao_id)
            if integracao and integracao.get("tipo") == "proxmox" and integracao.get("ativo"):
                return integracao
            return None
        integracoes = IntegracaoConfigService.listar(tipo="proxmox", ativo="1", grupo="tecnicas")
        return integracoes[0] if integracoes else None

    @staticmethod
    def _normalizar_recurso(item, config=None):
        config = config or {}
        return {
            "node": item.get("node"),
            "vmid": int(item.get("vmid") or 0),
            "tipo": item.get("type") or "qemu",
            "nome": item.get("name"),
            "status": item.get("status"),
            "cpu_cores": config.get("cores") or item.get("maxcpu"),
            "memoria_mb": config.get("memory") or int((item.get("maxmem") or 0) / 1024 / 1024) or None,
            "disco_gb": round((item.get("maxdisk") or 0) / 1024 / 1024 / 1024, 2) or None,
            "discos_qtd": ProxmoxInventoryService._contar_discos(item.get("type"), config) if config else None,
            "interfaces_qtd": ProxmoxInventoryService._contar_interfaces(config) if config else None,
            "ips": None,
            "tags": config.get("tags") or item.get("tags"),
            "template": bool(item.get("template")),
            "uptime_seconds": item.get("uptime"),
            "raw_payload": {"resource": item, "config": config},
        }

    @staticmethod
    def _contar_discos(tipo, config):
        prefixos_qemu = ("ide", "sata", "scsi", "virtio")
        if tipo == "lxc":
            return len([chave for chave in config if chave == "rootfs" or chave.startswith("mp")])
        return len([
            chave for chave, valor in config.items()
            if chave.startswith(prefixos_qemu) and "media=cdrom" not in str(valor)
        ])

    @staticmethod
    def _contar_interfaces(config):
        return len([chave for chave in config if chave.startswith("net")])

    @staticmethod
    def _normalizar_node(node, status=None, storages=None, conteudos_storage=None):
        status = status or {}
        storages = storages or []
        conteudos_storage = conteudos_storage or {}
        memoria = status.get("memory") or {}
        storage_util = ProxmoxInventoryService._storage_util_vm(storages)
        storage_contabilizado = [
            item for item in storage_util
            if ProxmoxInventoryService._storage_vm_ct_contabilizado(item.get("storage"))
        ]
        cpu_total = node.get("maxcpu") or (status.get("cpuinfo") or {}).get("cpus")
        cpu_percent = round(float(node.get("cpu") or status.get("cpu") or 0) * 100, 2)
        memoria_total = memoria.get("total") or node.get("maxmem")
        memoria_usada = memoria.get("used") or node.get("mem")
        memoria_disponivel = memoria.get("available") or memoria.get("free")
        rootfs = status.get("rootfs") or {}
        disco_total = sum(item.get("total") or 0 for item in storage_contabilizado)
        if conteudos_storage:
            disco_usado = ProxmoxInventoryService._bytes_storage_conteudo(conteudos_storage)
        else:
            disco_usado = sum(item.get("used") or 0 for item in storage_contabilizado)
        disco_disponivel = max(disco_total - disco_usado, 0) if disco_total else 0
        if not disco_total:
            disco_total = rootfs.get("total") or node.get("maxdisk")
            disco_usado = rootfs.get("used") or node.get("disk")
            disco_disponivel = rootfs.get("avail") or rootfs.get("free")
        return {
            "node": node.get("node"),
            "status": node.get("status"),
            "cpu_total": cpu_total,
            "cpu_usado_percent": cpu_percent,
            "memoria_total_mb": ProxmoxInventoryService._bytes_para_mb(memoria_total),
            "memoria_usada_mb": ProxmoxInventoryService._bytes_para_mb(memoria_usada),
            "memoria_disponivel_mb": ProxmoxInventoryService._bytes_para_mb(memoria_disponivel),
            "disco_total_gb": ProxmoxInventoryService._bytes_para_gb(disco_total),
            "disco_usado_gb": ProxmoxInventoryService._bytes_para_gb(disco_usado),
            "disco_disponivel_gb": ProxmoxInventoryService._bytes_para_gb(disco_disponivel),
            "storages_qtd": len(storage_contabilizado),
            "uptime_seconds": status.get("uptime") or node.get("uptime"),
            "pve_version": status.get("pveversion"),
            "raw_payload": {"node": node, "status": status, "storages": storages, "conteudos_storage": conteudos_storage},
        }

    @staticmethod
    def _storage_vm_ct_contabilizado(storage_nome):
        return (storage_nome or "").strip().lower() in ProxmoxInventoryService.STORAGES_VM_CT_CONTABILIZADOS

    @staticmethod
    def _bytes_storage_conteudo(conteudos_storage):
        total = 0
        for volumes in (conteudos_storage or {}).values():
            for volume in volumes or []:
                total += int(volume.get("size") or 0)
        return total

    @staticmethod
    def _storage_util_vm(storages):
        uteis = []
        for item in storages:
            conteudo = item.get("content") or ""
            if not item.get("active") or not item.get("enabled"):
                continue
            if not ({"images", "rootdir"} & set(conteudo.split(","))):
                continue
            uteis.append(item)
        return uteis

    @classmethod
    def _com_percentuais_cluster(cls, cluster):
        item = dict(cluster)
        item["web_gui_url"] = cls._web_gui_url(item.get("base_url"))
        item["cpu_consumida_percent"] = cls._percentual(item.get("cpu_consumida"), item.get("cpu_total"))
        item["cpu_alocada_percent"] = cls._percentual(item.get("cpu_alocada"), item.get("cpu_total"))
        item["memoria_usada_percent"] = cls._percentual(item.get("memoria_usada_mb"), item.get("memoria_total_mb"))
        item["memoria_alocada_percent"] = cls._percentual(item.get("memoria_alocada_mb"), item.get("memoria_total_mb"))
        item["disco_usado_percent"] = cls._percentual(item.get("disco_usado_gb"), item.get("disco_total_gb"))
        item["disco_alocado_percent"] = cls._percentual(item.get("disco_alocado_gb"), item.get("disco_total_gb"))
        return item

    @staticmethod
    def _web_gui_url(base_url):
        parsed = urlparse(base_url or "")
        host = parsed.hostname
        if not host and base_url:
            host = str(base_url).split("/", 1)[0].split(":", 1)[0]
        return f"https://{host}:8006" if host else None

    @classmethod
    def _com_link_recurso(cls, recurso):
        item = dict(recurso)
        gui_url = cls._web_gui_url(item.get("base_url"))
        if gui_url and item.get("tipo") and item.get("vmid"):
            item["web_gui_url"] = f"{gui_url}/#v1:0:={item.get('tipo')}/{item.get('vmid')}:4:::::::"
        else:
            item["web_gui_url"] = gui_url
        return item

    @staticmethod
    def _com_percentuais_node(node):
        item = dict(node)
        item["web_gui_url"] = ProxmoxInventoryService._web_gui_url(item.get("base_url"))
        item["memoria_usada_percent"] = ProxmoxInventoryService._percentual(
            item.get("memoria_usada_mb"), item.get("memoria_total_mb")
        )
        item["disco_usado_percent"] = ProxmoxInventoryService._percentual(
            item.get("disco_usado_gb"), item.get("disco_total_gb")
        )
        item["cpu_alocada_percent"] = ProxmoxInventoryService._percentual(
            item.get("cpu_alocada"), item.get("cpu_total")
        )
        item["memoria_alocada_percent"] = ProxmoxInventoryService._percentual(
            item.get("memoria_alocada_mb"), item.get("memoria_total_mb")
        )
        item["disco_alocado_percent"] = ProxmoxInventoryService._percentual(
            item.get("disco_alocado_gb"), item.get("disco_total_gb")
        )
        return item

    @staticmethod
    def _bytes_para_mb(valor):
        return int((valor or 0) / 1024 / 1024) or None

    @staticmethod
    def _bytes_para_gb(valor):
        return round((valor or 0) / 1024 / 1024 / 1024, 2) or None

    @staticmethod
    def _percentual(valor, total):
        valor = float(valor or 0)
        total = float(total or 0)
        if total <= 0:
            return 0
        return round((valor / total) * 100, 1)

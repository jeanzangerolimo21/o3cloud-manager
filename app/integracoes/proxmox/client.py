import requests
import urllib3


class ProxmoxClient:
    def __init__(self, base_url, token_nome, segredo, timeout=30, verify_ssl=True):
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = int(timeout or 30)
        self.verify_ssl = bool(verify_ssl)
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.headers = {"Authorization": f"PVEAPIToken={token_nome}={segredo}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get(self, path, params=None, timeout=None):
        response = self.session.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=timeout or self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return (response.json() or {}).get("data") or []

    def listar_nodes(self):
        return self._get("/api2/json/nodes")

    def obter_status_node(self, node):
        return self._get(f"/api2/json/nodes/{node}/status", timeout=min(self.timeout, 5))

    def listar_storage_node(self, node):
        return self._get(f"/api2/json/nodes/{node}/storage", timeout=min(self.timeout, 12))

    def listar_vms_containers(self):
        recursos = self._get("/api2/json/cluster/resources", params={"type": "vm"})
        return [item for item in recursos if item.get("type") in ("qemu", "lxc")]

    def obter_configuracao(self, node, tipo, vmid):
        recurso = "qemu" if tipo == "qemu" else "lxc"
        return self._get(
            f"/api2/json/nodes/{node}/{recurso}/{vmid}/config",
            timeout=min(self.timeout, 5),
        )

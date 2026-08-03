import requests
import urllib3


class PBSClient:
    def __init__(self, base_url, token_nome, segredo, timeout=30, verify_ssl=True):
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = int(timeout or 30)
        self.verify_ssl = bool(verify_ssl)
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"PBSAPIToken={token_nome}:{segredo}"})

    def _get(self, path, params=None, timeout=None):
        response = self.session.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=timeout or self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return (response.json() or {}).get("data") or []

    def listar_snapshots(self, datastore, namespace=None):
        params = {}
        if namespace:
            params["ns"] = namespace
        return self._get(
            f"/api2/json/admin/datastore/{datastore}/snapshots",
            params=params,
            timeout=min(self.timeout, 30),
        )

import requests
import urllib3


class TrueNASClient:
    def __init__(self, base_url, token, timeout=30, verify_ssl=True):
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = int(timeout or 30)
        self.verify_ssl = bool(verify_ssl)
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def listar_diretorio(self, path):
        response = self.session.post(
            f"{self.base_url}/api/v2.0/filesystem/listdir",
            json={
                "path": path,
                "query-options": {
                    "relationships": False,
                    "select": ["name", "path", "type", "size"],
                },
            },
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json() or []

    def stat(self, path):
        response = self.session.post(
            f"{self.base_url}/api/v2.0/filesystem/stat",
            json=path,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json() or {}

import time

import requests
import urllib3


class ZabbixClient:
    def __init__(self, base_url, token, timeout=30, verify_ssl=True):
        self.base_url = (base_url or "").rstrip("/")
        self.token = token
        self.timeout = max(60, int(timeout or 30))
        self.verify_ssl = bool(verify_ssl)
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def listar_hosts(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip", "dns", "port", "type", "main", "useip"],
                "sortfield": "name",
                "sortorder": "ASC",
            },
            "auth": self.token,
            "id": 2,
        }
        return self._post(payload)

    def eventos_recentes(self, limite=80):
        payload = {
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "extend",
                "selectHosts": ["hostid", "host", "name"],
                "selectRelatedObject": ["triggerid", "description", "priority", "status"],
                "source": 0,
                "object": 0,
                "time_from": int(time.time()) - (30 * 86400),
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC",
                "limit": max(1, min(int(limite or 80), 200)),
            },
            "auth": self.token,
            "id": 1,
        }
        return self._post(payload)

    def problemas_ativos(self, limite=1000):
        payload = {
            "jsonrpc": "2.0",
            "method": "problem.get",
            "params": {
                "output": "extend",
                "source": 0,
                "object": 0,
                "sortfield": ["eventid"],
                "sortorder": "DESC",
                "limit": max(1, min(int(limite or 1000), 1000)),
            },
            "auth": self.token,
            "id": 3,
        }
        return self._post(payload)

    def triggers_por_ids(self, triggerids):
        ids = [str(item) for item in (triggerids or []) if item]
        if not ids:
            return []
        payload = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "output": ["triggerid", "description", "priority", "status"],
                "triggerids": ids,
                "selectHosts": ["hostid", "host", "name"],
            },
            "auth": self.token,
            "id": 4,
        }
        return self._post(payload)

    def _post(self, payload):
        response = requests.post(
            self._api_url(),
            json=payload,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        body = response.json() if response.text else {}
        if response.ok and isinstance(body, dict) and "result" in body:
            return body.get("result") or []

        payload_sem_auth = dict(payload)
        payload_sem_auth.pop("auth", None)
        response = requests.post(
            self._api_url(),
            json=payload_sem_auth,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        body = response.json() if response.text else {}
        if response.ok and isinstance(body, dict) and "result" in body:
            return body.get("result") or []
        if isinstance(body, dict) and body.get("error"):
            erro = body.get("error") or {}
            mensagem = erro.get("data") or erro.get("message") or "erro API"
            raise requests.exceptions.HTTPError(f"Zabbix recusou a consulta: {mensagem}")
        response.raise_for_status()
        return []

    def _api_url(self):
        if self.base_url.endswith("api_jsonrpc.php"):
            return self.base_url
        return f"{self.base_url}/api_jsonrpc.php"

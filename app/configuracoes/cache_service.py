from pathlib import Path

from app.core.storage import StorageService
from app.repositories.base_repository import BaseRepository


class CacheRetencaoService:
    repository = BaseRepository
    OPCOES_RETENCAO = (30, 60, 90, 180, 240, 365)
    CACHES = {
        "zabbix_alarmes": {
            "nome": "Alarmes Zabbix",
            "tabelas": (
                {"nome": "zabbix_alarm_cache", "data": "COALESCE(data_evento, sincronizado_em, created_at)", "where": ""},
            ),
        },
        "zabbix_hosts": {
            "nome": "Hosts Zabbix inativos",
            "tabelas": (
                {"nome": "zabbix_host_inventory", "data": "COALESCE(ultimo_sync_em, updated_at, created_at)", "where": "ativo = 0"},
            ),
        },
        "pbs_backups": {
            "nome": "Backups PBS",
            "tabelas": (
                {"nome": "pbs_backup_snapshots", "data": "backup_time", "where": ""},
                {"nome": "pbs_backup_sync_execucoes", "data": "COALESCE(finalizada_em, iniciada_em, created_at)", "where": ""},
            ),
        },
        "truenas_backups": {
            "nome": "Backups TrueNAS",
            "tabelas": (
                {"nome": "truenas_backup_cache", "data": "COALESCE(ultimo_mtime, sincronizado_em, created_at)", "where": ""},
            ),
        },
        "proxmox_inventario": {
            "nome": "Inventario Proxmox inativo",
            "tabelas": (
                {"nome": "proxmox_vm_inventory", "data": "COALESCE(ultimo_sync_em, updated_at, created_at)", "where": "ativo = 0"},
                {"nome": "proxmox_node_inventory", "data": "COALESCE(ultimo_sync_em, updated_at, created_at)", "where": "ativo = 0"},
                {"nome": "proxmox_vm_sync_execucoes", "data": "COALESCE(finalizada_em, iniciada_em, created_at)", "where": ""},
            ),
        },
        "relatorios_arquivos": {
            "nome": "Relatorios gerados",
            "tabelas": (
                {"nome": "relatorios_jobs", "data": "created_at", "where": "status IN ('CONCLUIDO','ERRO')"},
                {"nome": "relatorios_execucoes", "data": "created_at", "where": ""},
            ),
        },
    }

    @classmethod
    def contexto(cls):
        configs = {item["cache_key"]: item for item in cls.repository.fetch_all("SELECT * FROM config_cache_retencao")}
        historico = cls.repository.fetch_all(
            """
            SELECT *
            FROM config_cache_limpezas
            ORDER BY created_at DESC, id DESC
            LIMIT 30
            """
        )
        caches = []
        for chave, definicao in cls.CACHES.items():
            retencao = int((configs.get(chave) or {}).get("retencao_dias") or 90)
            caches.append({
                "key": chave,
                "nome": definicao["nome"],
                "retencao_dias": retencao,
                "total": cls._contar(definicao["tabelas"]),
                "expirados": cls._contar(definicao["tabelas"], retencao),
            })
        return {"caches": caches, "historico": historico, "opcoes_retencao": cls.OPCOES_RETENCAO}

    @classmethod
    def salvar_retencao(cls, cache_key, retencao_dias, usuario_email):
        if cache_key not in cls.CACHES:
            raise ValueError("Cache invalido.")
        retencao = int(retencao_dias or 90)
        if retencao not in cls.OPCOES_RETENCAO:
            raise ValueError("Retencao invalida.")
        cls.repository.execute(
            """
            INSERT INTO config_cache_retencao (uuid, cache_key, retencao_dias, ativo, updated_by)
            VALUES (%s, %s, %s, 1, %s)
            ON DUPLICATE KEY UPDATE retencao_dias=VALUES(retencao_dias), ativo=1, updated_by=VALUES(updated_by)
            """,
            (cls.repository.generate_uuid(), cache_key, retencao, usuario_email),
        )

    @classmethod
    def limpar(cls, cache_key, modo, usuario_email):
        if cache_key not in cls.CACHES:
            raise ValueError("Cache invalido.")
        if modo not in ("retencao", "total"):
            raise ValueError("Modo de limpeza invalido.")
        retencao = cls._retencao(cache_key)
        removidos = 0
        for tabela in cls.CACHES[cache_key]["tabelas"]:
            removidos += cls._limpar_tabela(tabela, retencao if modo == "retencao" else None)
        cls.repository.execute(
            """
            INSERT INTO config_cache_limpezas (uuid, cache_key, modo, retencao_dias, registros_removidos, executado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (cls.repository.generate_uuid(), cache_key, modo, retencao if modo == "retencao" else None, removidos, usuario_email),
        )
        return removidos

    @classmethod
    def _retencao(cls, cache_key):
        config = cls.repository.fetch_one("SELECT retencao_dias FROM config_cache_retencao WHERE cache_key=%s", (cache_key,))
        return int((config or {}).get("retencao_dias") or 90)

    @classmethod
    def _contar(cls, tabelas, retencao=None):
        total = 0
        for tabela in tabelas:
            where = cls._where(tabela, retencao)
            total += cls.repository.scalar(f"SELECT COUNT(*) FROM {tabela['nome']} {where}") or 0
        return total

    @classmethod
    def _limpar_tabela(cls, tabela, retencao=None):
        where = cls._where(tabela, retencao)
        if tabela["nome"] == "relatorios_jobs":
            arquivos = cls.repository.fetch_all(f"SELECT arquivo_nome FROM relatorios_jobs {where}")
            for item in arquivos:
                nome = item.get("arquivo_nome")
                if nome:
                    caminho = StorageService.BASE_STORAGE / "relatorios" / nome
                    if caminho.exists():
                        caminho.unlink()
        return cls.repository.execute_delete_count(f"DELETE FROM {tabela['nome']} {where}")

    @staticmethod
    def _where(tabela, retencao=None):
        partes = []
        if tabela.get("where"):
            partes.append(tabela["where"])
        if retencao:
            partes.append(f"{tabela['data']} < DATE_SUB(NOW(), INTERVAL {int(retencao)} DAY)")
        return "WHERE " + " AND ".join(partes) if partes else ""

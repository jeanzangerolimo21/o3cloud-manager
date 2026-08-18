import json
import re
import time
import unicodedata
from datetime import datetime, timezone

import requests

from app.implantacao.integracoes_service import IntegracaoConfigService
from app.integracoes.truenas.client import TrueNASClient
from app.repositories.truenas_backup_repository import TrueNASBackupRepository


MOUNTPOINTS_PADRAO = [f"/mnt/BKP{numero}" for numero in range(1, 8)]
PASTAS_IGNORADAS = {
    "backup",
    "backupestações",
    "backupestacoes",
    "backupestaes",
    "backupbd",
    "backupsbd",
    "ftp",
    "ftpshare",
    "iocage",
    "isos",
    "isospve",
    "postgresbkps",
}
DIRETORIOS_IGNORADOS = {"ssh", "lixeira", "trash", "tmp", "temp"}
ARQUIVOS_IGNORADOS = {"sendemail", "sendemailpl"}



class TrueNASBackupService:
    repository = TrueNASBackupRepository

    @classmethod
    def integracoes_truenas(cls):
        return IntegracaoConfigService.listar(tipo="truenas", ativo="1", grupo="tecnicas")

    @classmethod
    def listar(cls, integracao_id=None):
        integracao = cls._integracao_truenas_ativa(integracao_id)
        if not integracao:
            return {
                "status": "PENDENTE",
                "mensagem": "Cadastre uma integração TrueNAS ativa para monitorar backups NAS.",
                "integracao": None,
                "registros": [],
                "dashboard": {},
            }
        registros = [cls._normalizar_cache(item) for item in cls.repository.listar_cache(integracao.get("id"))]
        dashboard = cls.repository.dashboard(integracao.get("id")) or {}
        status = "OK" if registros else "PENDENTE"
        mensagem = "Status carregado do cache local." if registros else "Nenhum cache TrueNAS encontrado. Clique em Sincronizar TrueNAS."
        return {
            "status": status,
            "mensagem": mensagem,
            "integracao": integracao,
            "registros": registros,
            "dashboard": dashboard,
        }

    @classmethod
    def sincronizar(cls, integracao_id=None, periodo_horas=24):
        integracao = cls._integracao_truenas_ativa(integracao_id)
        if not integracao:
            raise ValueError("Cadastre uma integração TrueNAS ativa para sincronizar backups NAS.")
        if not integracao.get("possui_segredo"):
            raise ValueError("A integração TrueNAS está ativa, mas ainda não possui token/segredo cadastrado.")
        try:
            token = IntegracaoConfigService.revelar_segredo_config(integracao.get("id"))
            cliente = TrueNASClient(
                integracao.get("base_url"),
                token,
                timeout=integracao.get("timeout_seconds"),
                verify_ssl=integracao.get("verify_ssl"),
            )
            registros = cls._coletar_registros(cliente, periodo_horas=periodo_horas)
            atualizados = cls.repository.salvar_cache(integracao.get("id"), registros)
            alertas = len([item for item in registros if item.get("status") == "ALERTA"])
            return {
                "status": "OK",
                "mensagem": f"Sincronismo TrueNAS concluído. {atualizados} pasta(s) atualizada(s), {alertas} alerta(s).",
                "registros": registros,
            }
        except requests.exceptions.SSLError:
            mensagem = "Falha na validação SSL do TrueNAS. Ajuste a CA confiável ou desative Verificar SSL para este endpoint interno."
        except requests.exceptions.Timeout:
            mensagem = "Timeout ao consultar diretórios no TrueNAS."
        except requests.exceptions.ConnectionError:
            mensagem = "Falha de conexão com o TrueNAS. Verifique host, porta, rota e firewall."
        except requests.exceptions.RequestException as erro:
            mensagem = f"Falha HTTP ao consultar TrueNAS: {str(erro)[:180]}"
        return {"status": "ERRO", "mensagem": mensagem, "registros": []}

    @classmethod
    def _coletar_registros(cls, cliente, periodo_horas=24):
        ambientes = cls.repository.listar_prefixos_ambientes()
        mapa_prefixos = cls._mapa_prefixos(ambientes)
        corte = time.time() - (max(1, int(periodo_horas or 24)) * 3600)
        registros = []
        vistos = set()
        for mountpoint in MOUNTPOINTS_PADRAO:
            bases = [mountpoint] + cls._bases_backup_bd(cliente, mountpoint)
            for base_path in bases:
                for pasta in cls._listar_pastas_cliente(cliente, base_path):
                    nome_normalizado = cls._normalizar_nome(pasta.get("name"))
                    if not nome_normalizado or nome_normalizado in PASTAS_IGNORADAS:
                        continue
                    chave = pasta.get("path")
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    ambiente = mapa_prefixos.get(nome_normalizado) or {
                        "ambiente_id": None,
                        "prefixo_proxmox": pasta.get("name"),
                        "cliente_nome": None,
                    }
                    registros.append(cls._analisar_pasta(cliente, pasta, ambiente, mountpoint, corte))
        return registros

    @classmethod
    def _bases_backup_bd(cls, cliente, mountpoint):
        bases = []
        for nome_base in ("Backup-BD", "Backups-BD"):
            for path in (f"{mountpoint}/{nome_base}", f"{mountpoint}/{nome_base}/Postgres-BKPs"):
                try:
                    stat = cliente.stat(path)
                except requests.exceptions.RequestException:
                    continue
                if stat:
                    bases.append(path)
        return bases

    @classmethod
    def _listar_pastas_cliente(cls, cliente, base_path):
        try:
            itens = cliente.listar_diretorio(base_path)
        except requests.exceptions.RequestException:
            return []
        return [item for item in itens if item.get("type") == "DIRECTORY"]

    @classmethod
    def _analisar_pasta(cls, cliente, pasta, ambiente, mountpoint, corte):
        arquivos = cls._listar_arquivos_monitorados(cliente, pasta.get("path"), corte)
        arquivos.sort(key=lambda item: item.get("mtime") or 0, reverse=True)
        recentes = [item for item in arquivos if item.get("recente")]
        ultimo = arquivos[0] if arquivos else {}
        detalhes = [
            {"nome": item["nome"], "size": item["size"], "mtime": item["mtime_label"], "is_backup": item["is_backup"]}
            for item in recentes[:10]
        ]
        return {
            "ambiente_id": ambiente.get("ambiente_id"),
            "prefixo_proxmox": ambiente.get("prefixo_proxmox"),
            "cliente_nome": ambiente.get("cliente_nome"),
            "mountpoint": mountpoint,
            "pasta_path": pasta.get("path"),
            "status": "OK" if recentes else "ALERTA",
            "arquivos_recentes": len(recentes),
            "arquivos_total": len(arquivos),
            "ultimo_arquivo": ultimo.get("nome"),
            "ultimo_mtime": datetime.fromtimestamp(ultimo.get("mtime")) if ultimo.get("mtime") else None,
            "detalhes": json.dumps(detalhes, ensure_ascii=False),
        }

    @classmethod
    def _listar_arquivos_monitorados(cls, cliente, raiz, corte, max_depth=3, max_files=300):
        arquivos = []
        pendentes = [(raiz, 0)]
        while pendentes and len(arquivos) < max_files:
            path, depth = pendentes.pop()
            try:
                itens = cliente.listar_diretorio(path)
            except requests.exceptions.RequestException:
                continue
            for item in itens:
                nome = item.get("name") or ""
                if item.get("type") == "DIRECTORY":
                    if (max_depth is None or depth < max_depth) and cls._diretorio_monitorado(nome):
                        pendentes.append((item.get("path"), depth + 1))
                    continue
                if item.get("type") != "FILE" or not cls._arquivo_monitorado(nome):
                    continue
                try:
                    stat = cliente.stat(item.get("path"))
                except requests.exceptions.RequestException:
                    continue
                mtime = float(stat.get("mtime") or 0)
                arquivos.append({
                    "nome": nome,
                    "path": item.get("path"),
                    "size": int(stat.get("size") or item.get("size") or 0),
                    "mtime": mtime,
                    "mtime_label": datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M") if mtime else None,
                    "recente": mtime >= corte,
                    "is_backup": nome.lower().endswith(".backup"),
                })
        return arquivos

    @staticmethod
    def _diretorio_monitorado(nome):
        texto = str(nome or "").strip()
        if not texto or texto.startswith("."):
            return False
        return TrueNASBackupService._normalizar_nome(texto) not in DIRETORIOS_IGNORADOS

    @staticmethod
    def _arquivo_monitorado(nome):
        texto = str(nome or "").strip()
        if not texto or texto.startswith("."):
            return False
        return TrueNASBackupService._normalizar_nome(texto) not in ARQUIVOS_IGNORADOS

    @classmethod
    def _integracao_truenas_ativa(cls, integracao_id=None):
        if integracao_id:
            integracao = IntegracaoConfigService.buscar_por_id(integracao_id)
            if integracao and integracao.get("tipo") == "truenas" and integracao.get("ativo"):
                integracao["possui_segredo"] = 1 if integracao.get("segredo_encrypted") else 0
                return integracao
            return None
        integracoes = cls.integracoes_truenas()
        return integracoes[0] if integracoes else None

    @staticmethod
    def _mapa_prefixos(ambientes):
        mapa = {}
        for ambiente in ambientes:
            chave = TrueNASBackupService._normalizar_nome(ambiente.get("prefixo_proxmox"))
            if chave and chave not in mapa:
                mapa[chave] = ambiente
        return mapa

    @staticmethod
    def _normalizar_nome(valor):
        texto = unicodedata.normalize("NFKD", str(valor or "").lower())
        texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
        return re.sub(r"[^a-z0-9]+", "", texto)

    @staticmethod
    def _normalizar_cache(item):
        registro = dict(item)
        try:
            registro["detalhes_lista"] = json.loads(registro.get("detalhes") or "[]")
        except (TypeError, ValueError):
            registro["detalhes_lista"] = []
        registro["status_classe"] = "success" if registro.get("status") == "OK" else "warning"
        registro["ultimo_mtime_ago"] = TrueNASBackupService._tempo_desde(registro.get("ultimo_mtime"))
        return registro

    @staticmethod
    def _tempo_desde(valor):
        if not valor:
            return "Nunca"
        agora = datetime.now()
        delta = agora - valor
        horas = int(delta.total_seconds() // 3600)
        if horas < 1:
            minutos = max(0, int(delta.total_seconds() // 60))
            return f"{minutos} min"
        dias = horas // 24
        if dias:
            resto = horas % 24
            return f"{dias}d {resto}h"
        return f"{horas}h"

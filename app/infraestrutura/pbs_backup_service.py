from datetime import datetime, timezone

import requests

from app.implantacao.integracoes_service import IntegracaoConfigService
from app.integracoes.pbs.client import PBSClient
from app.repositories.pbs_backup_repository import PBSBackupRepository


DEFAULT_DATASTORE = "DISCO2"
DEFAULT_NAMESPACES = (
    "EVEO-SP-C1-03",
    "EVEO-SP-C1-04",
    "EVEO-SP-C1-05",
    "EVEO-SP-C1-06",
    "EVEO-SP-C1-07",
    "EVEO-SP-C1-08",
    "EVEO-SP-C1-09",
    "EVEO-SP-C1-10",
    "EVEO-SP-C1-11",
)


class PBSBackupService:
    repository = PBSBackupRepository

    @classmethod
    def listar(cls, pesquisa=None, status=None, tipo=None, node=None):
        agora = datetime.utcnow()
        recursos = []
        for item in cls.repository.listar_recursos(pesquisa=pesquisa, status=status, tipo=tipo, node=node):
            recursos.append(cls._com_status(item, agora))
        return recursos

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard() or {}

    @classmethod
    def nodes(cls):
        return cls.repository.listar_nodes_proxmox()

    @classmethod
    def execucoes_recentes(cls):
        return cls.repository.listar_execucoes()

    @classmethod
    def integracoes_pbs(cls):
        return cls.repository.listar_integracoes_pbs()

    @classmethod
    def escopos(cls, ativo=True):
        return [cls._com_namespaces_lista(item) for item in cls.repository.listar_escopos(ativo=ativo)]

    @classmethod
    def buscar_escopo(cls, escopo_id):
        escopo = cls.repository.buscar_escopo(escopo_id) if escopo_id else None
        return cls._com_namespaces_lista(escopo) if escopo else None

    @classmethod
    def escopo_padrao(cls):
        escopos = cls.escopos(ativo=True)
        return escopos[0] if escopos else None

    @classmethod
    def salvar_escopo(cls, dados, escopo_id=None):
        payload = cls._normalizar_escopo(dados)
        if escopo_id:
            cls.repository.atualizar_escopo(escopo_id, payload)
            return escopo_id
        return cls.repository.inserir_escopo(payload)

    @classmethod
    def inativar_escopo(cls, escopo_id):
        return cls.repository.inativar_escopo(escopo_id)

    @classmethod
    def atualizar_politicas(cls, recurso_ids_semanais):
        return cls.repository.atualizar_politicas(recurso_ids_semanais)

    @classmethod
    def sincronizar_todos(cls, usuario_email="sistema"):
        escopos = cls.escopos(ativo=True)
        if not escopos:
            raise ValueError("Cadastre pelo menos um escopo PBS antes de sincronizar.")
        resultados = []
        for escopo in escopos:
            resultado = cls.sincronizar(escopo_id=escopo.get("id"), usuario_email=usuario_email)
            resultados.append(resultado)
        erros = [item for item in resultados if item.get("status") != "OK"]
        snapshots = sum(int(item.get("snapshots") or 0) for item in resultados)
        atualizados = sum(int(item.get("atualizados") or 0) for item in resultados)
        status = "ERRO" if erros else "OK"
        mensagem = f"Sincronismo PBS concluído em {len(resultados)} escopo(s). Snapshots lidos: {snapshots}."
        if erros:
            mensagem += f" Escopos com erro: {len(erros)}."
        return {"status": status, "mensagem": mensagem, "snapshots": snapshots, "atualizados": atualizados}

    @classmethod
    def sincronizar(cls, escopo_id=None, datastore=None, usuario_email="sistema"):
        escopo = cls.buscar_escopo(escopo_id) if escopo_id else cls.escopo_padrao()
        if not escopo and datastore:
            integracao = cls._integracao_pbs_ativa()
            escopo = {
                "integracao_id": integracao.get("id") if integracao else None,
                "datastore": (datastore or DEFAULT_DATASTORE).strip() or DEFAULT_DATASTORE,
                "namespaces_lista": list(DEFAULT_NAMESPACES),
            }
        if not escopo:
            raise ValueError("Cadastre um escopo PBS com datastore e namespaces antes de sincronizar.")
        datastore = (escopo.get("datastore") or DEFAULT_DATASTORE).strip() or DEFAULT_DATASTORE
        integracao = IntegracaoConfigService.buscar_por_id(escopo.get("integracao_id"))
        if not integracao or integracao.get("tipo") != "pbs" or not integracao.get("ativo"):
            raise ValueError("Nenhuma integração PBS ativa encontrada para o escopo selecionado.")
        execucao_id = cls.repository.criar_execucao(integracao["id"], datastore, usuario_email)
        nodes = [item.get("node") for item in cls.repository.listar_nodes_proxmox() if item.get("node")]
        namespaces = escopo.get("namespaces_lista") or list(DEFAULT_NAMESPACES)
        namespace_nodes = cls._mapear_namespaces_nodes(namespaces, nodes)
        mapa_recursos = cls.repository.mapa_recursos_por_node()
        try:
            segredo = IntegracaoConfigService.revelar_segredo_config(integracao["id"])
            cliente = PBSClient(
                integracao.get("base_url"),
                IntegracaoConfigService._token_api_nome(integracao),
                segredo,
                timeout=integracao.get("timeout_seconds") or 30,
                verify_ssl=bool(integracao.get("verify_ssl")),
            )
            snapshots = []
            namespaces_com_erro = []
            for namespace in namespaces:
                try:
                    snapshots_namespace = cliente.listar_snapshots(datastore, namespace=namespace)
                except requests.exceptions.HTTPError as erro:
                    if erro.response is not None and erro.response.status_code == 400:
                        namespaces_com_erro.append(namespace)
                        continue
                    raise
                for snapshot in snapshots_namespace:
                    normalizado = cls._normalizar_snapshot(
                        snapshot, integracao["id"], datastore, namespace, namespace_nodes.get(namespace, namespace), mapa_recursos
                    )
                    if normalizado:
                        snapshots.append(normalizado)
            atualizados = cls.repository.salvar_snapshots(snapshots)
            mensagem = f"Sincronismo PBS concluído. Namespaces lidos: {len(namespaces)}. Snapshots lidos: {len(snapshots)}."
            if namespaces_com_erro:
                mensagem += f" Namespaces sem resposta no datastore: {len(namespaces_com_erro)}."
            cls.repository.finalizar_execucao(execucao_id, "OK", len(namespaces), len(snapshots), atualizados, mensagem)
            return {"status": "OK", "mensagem": mensagem, "snapshots": len(snapshots), "atualizados": atualizados}
        except requests.exceptions.SSLError:
            mensagem = "Falha na validação SSL do certificado PBS."
        except requests.exceptions.Timeout:
            mensagem = "Timeout ao consultar snapshots no PBS."
        except requests.exceptions.ConnectionError:
            mensagem = "Falha de conexão ao consultar snapshots no PBS."
        except requests.exceptions.HTTPError as erro:
            codigo = erro.response.status_code if erro.response is not None else "HTTP"
            mensagem = f"Falha HTTP {codigo} ao consultar snapshots no PBS."
        except Exception as erro:
            mensagem = f"Falha ao sincronizar backups PBS: {str(erro)[:160]}"
        cls.repository.finalizar_execucao(execucao_id, "ERRO", len(namespaces), 0, 0, mensagem)
        return {"status": "ERRO", "mensagem": mensagem, "snapshots": 0, "atualizados": 0}

    @classmethod
    def _integracao_pbs_ativa(cls):
        integracoes = IntegracaoConfigService.listar(tipo="pbs", ativo="1", grupo="tecnicas")
        return integracoes[0] if integracoes else None

    @classmethod
    def _normalizar_escopo(cls, dados):
        integracao_id = cls._inteiro(dados.get("integracao_id"))
        nome = cls._texto(dados.get("nome"))
        datastore = cls._texto(dados.get("datastore"))
        namespaces = cls._namespaces_texto(dados.get("namespaces"))
        if not integracao_id:
            raise ValueError("Selecione uma integração PBS ativa.")
        integracao = IntegracaoConfigService.buscar_por_id(integracao_id)
        if not integracao or integracao.get("tipo") != "pbs" or not integracao.get("ativo"):
            raise ValueError("Integração PBS selecionada não está ativa.")
        if not nome:
            raise ValueError("Informe o nome do escopo PBS.")
        if not datastore:
            raise ValueError("Informe o datastore PBS.")
        if not namespaces:
            raise ValueError("Informe pelo menos um namespace PBS.")
        return {
            "integracao_id": integracao_id,
            "nome": nome,
            "datastore": datastore,
            "namespaces": namespaces,
            "ativo": 1 if dados.get("ativo") else 0,
            "observacoes": cls._texto(dados.get("observacoes")),
        }

    @classmethod
    def _com_namespaces_lista(cls, escopo):
        item = dict(escopo)
        item["namespaces_lista"] = cls._namespaces_lista(item.get("namespaces"))
        return item

    @staticmethod
    def _namespaces_lista(valor):
        partes = str(valor or "").replace(",", "\n").splitlines()
        return [parte.strip() for parte in partes if parte.strip()]

    @classmethod
    def _namespaces_texto(cls, valor):
        return "\n".join(cls._namespaces_lista(valor))

    @staticmethod
    def _texto(valor):
        return str(valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _normalizar_snapshot(cls, snapshot, integracao_id, datastore, namespace, node, mapa_recursos):
        backup_type = snapshot.get("backup-type") or snapshot.get("backup_type") or snapshot.get("backup-type")
        backup_id = snapshot.get("backup-id") or snapshot.get("backup_id")
        backup_time = snapshot.get("backup-time") or snapshot.get("backup_time")
        snapshot_name = snapshot.get("backup") or snapshot.get("snapshot")
        if snapshot_name and (not backup_type or not backup_id or not backup_time):
            parsed_type, parsed_id, parsed_time = cls._parse_snapshot_name(snapshot_name)
            backup_type = backup_type or parsed_type
            backup_id = backup_id or parsed_id
            backup_time = backup_time or parsed_time
        backup_time_dt = cls._parse_backup_time(backup_time)
        if not backup_type or not backup_id or not backup_time_dt:
            return None
        backup_type = "vm" if backup_type in ("qemu", "vm") else "ct" if backup_type in ("lxc", "ct") else backup_type
        proxmox_inventory_id = mapa_recursos.get((node, backup_type, str(backup_id)))
        snapshot_name = snapshot_name or f"{backup_type}/{backup_id}/{backup_time_dt.isoformat()}"
        return {
            "integracao_id": integracao_id,
            "proxmox_inventory_id": proxmox_inventory_id,
            "datastore": datastore,
            "namespace": namespace or "",
            "backup_type": backup_type,
            "backup_id": str(backup_id),
            "backup_time": backup_time_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "snapshot_name": snapshot_name,
            "size_bytes": snapshot.get("size") or snapshot.get("size-bytes"),
            "protected": snapshot.get("protected"),
            "raw_payload": snapshot,
        }

    @staticmethod
    def _mapear_namespaces_nodes(namespaces, nodes):
        nodes_por_sufixo = {}
        for node in nodes:
            sufixo = str(node or "").rsplit("-", 1)[-1]
            if sufixo:
                nodes_por_sufixo[sufixo] = node
        mapa = {}
        for namespace in namespaces:
            sufixo = str(namespace or "").rsplit("-", 1)[-1]
            mapa[namespace] = nodes_por_sufixo.get(sufixo, namespace)
        return mapa

    @staticmethod
    def _parse_snapshot_name(snapshot_name):
        partes = str(snapshot_name or "").split("/")
        if len(partes) < 3:
            return None, None, None
        return partes[-3], partes[-2], partes[-1]

    @staticmethod
    def _parse_backup_time(valor):
        if valor in (None, ""):
            return None
        if isinstance(valor, (int, float)):
            return datetime.fromtimestamp(valor, tz=timezone.utc).replace(tzinfo=None)
        texto = str(valor).strip()
        if texto.isdigit():
            return datetime.fromtimestamp(int(texto), tz=timezone.utc).replace(tzinfo=None)
        texto = texto.replace("Z", "+00:00")
        try:
            data = datetime.fromisoformat(texto)
        except ValueError:
            return None
        if data.tzinfo:
            data = data.astimezone(timezone.utc).replace(tzinfo=None)
        return data

    @staticmethod
    def _com_status(item, agora):
        item = dict(item)
        frequencia = int(item.get("frequencia_horas") or 24)
        ultimo = item.get("ultimo_backup_em")
        if ultimo:
            atraso_horas = max(0, round((agora - ultimo).total_seconds() / 3600, 1))
            item["horas_desde_backup"] = atraso_horas
            item["backup_ok"] = atraso_horas <= frequencia
            item["backup_status"] = "OK" if item["backup_ok"] else "ALERTA"
        else:
            item["horas_desde_backup"] = None
            item["backup_ok"] = False
            item["backup_status"] = "SEM_BACKUP"
        item["backup_semanal"] = frequencia >= 168
        item["prazo_label"] = "7 dias" if item["backup_semanal"] else "24 horas"
        return item

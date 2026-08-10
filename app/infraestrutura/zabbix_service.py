import json
from datetime import datetime

import requests

from app.implantacao.integracoes_service import IntegracaoConfigService
from app.core.logging_config import get_logger
from app.integracoes.zabbix.client import ZabbixClient
from app.repositories.zabbix_alarm_repository import ZabbixAlarmRepository
from app.repositories.zabbix_host_repository import ZabbixHostRepository


integration_logger = get_logger("integrations")


SEVERIDADES = {
    0: {"label": "Não classificado", "classe": "secondary", "ordem": 0},
    1: {"label": "Informação", "classe": "info", "ordem": 1},
    2: {"label": "Média", "classe": "warning", "ordem": 2},
    3: {"label": "Alta média", "classe": "warning", "ordem": 3},
    4: {"label": "Alta", "classe": "danger", "ordem": 4},
    5: {"label": "Crítica", "classe": "dark", "ordem": 5},
}


class ZabbixMonitoramentoService:
    repository = ZabbixAlarmRepository
    host_repository = ZabbixHostRepository

    @classmethod
    def dashboard(cls, alarmes):
        abertos = [item for item in alarmes if item.get("aberto")]
        resolvidos = [item for item in alarmes if not item.get("aberto")]
        return {
            "total": len(alarmes),
            "abertos": len(abertos),
            "resolvidos": len(resolvidos),
            "media": len([item for item in abertos if item.get("severidade") in (2, 3)]),
            "alta": len([item for item in abertos if item.get("severidade") == 4]),
            "critica": len([item for item in abertos if item.get("severidade") == 5]),
            "desastre": len([item for item in abertos if item.get("severidade") >= 5]),
        }

    @classmethod
    def integracoes_zabbix(cls):
        return IntegracaoConfigService.listar(tipo="zabbix", ativo="1", grupo="tecnicas")

    @classmethod
    def listar_alarmes(cls, integracao_id=None, limite=80):
        integracao = cls._integracao_zabbix_ativa(integracao_id)
        if not integracao:
            return {
                "status": "PENDENTE",
                "mensagem": "Cadastre uma integração Zabbix ativa para consultar alarmes recentes.",
                "integracao": None,
                "alarmes": [],
                "ultimo_sync": None,
            }
        alarmes = [cls._normalizar_cache(item) for item in cls.repository.listar(integracao.get("id"), limite=limite)]
        ultimo_sync = cls.repository.ultimo_sync(integracao.get("id")) or {}
        if not alarmes:
            mensagem = "Nenhum alarme em cache. Clique em Sincronizar Zabbix para carregar os alarmes recentes."
            status = "PENDENTE"
        else:
            mensagem = f"{len(alarmes)} alarme(s) carregado(s) do cache local."
            status = "OK"
        return {
            "status": status,
            "mensagem": mensagem,
            "integracao": integracao,
            "alarmes": alarmes,
            "ultimo_sync": ultimo_sync.get("sincronizado_em"),
        }

    @classmethod
    def sincronizar(cls, integracao_id=None, limite=80):
        integracao = cls._integracao_zabbix_ativa(integracao_id)
        if not integracao:
            raise ValueError("Cadastre uma integração Zabbix ativa para sincronizar alarmes recentes.")
        if not integracao.get("possui_segredo"):
            raise ValueError("A integração Zabbix está ativa, mas ainda não possui token/segredo cadastrado.")
        try:
            token = IntegracaoConfigService.revelar_segredo_config(integracao.get("id"))
            cliente = ZabbixClient(
                integracao.get("base_url"),
                token,
                timeout=integracao.get("timeout_seconds"),
                verify_ssl=integracao.get("verify_ssl"),
            )
            hosts = [cls._normalizar_host(item) for item in cliente.listar_hosts()]
            hosts_atualizados = cls.host_repository.salvar(integracao.get("id"), hosts)
            eventos = cliente.eventos_recentes(limite=limite)
            alarmes = sorted(
                [cls._normalizar_evento(evento, integracao) for evento in eventos],
                key=lambda item: (0 if item.get("aberto") else 1, -item.get("severidade", 0), -int(item.get("clock") or 0)),
            )
            atualizados = cls.repository.salvar(integracao.get("id"), alarmes)
            return {
                "status": "OK",
                "mensagem": f"Sincronismo Zabbix concluido. {hosts_atualizados} host(s) e {atualizados} alarme(s) atualizados.",
                "integracao": integracao,
                "alarmes": alarmes,
            }
        except requests.exceptions.SSLError:
            mensagem = "Falha na validação SSL do Zabbix. Ajuste a CA confiável ou desative Verificar SSL para este endpoint interno."
        except requests.exceptions.Timeout:
            mensagem = "Timeout ao consultar alarmes recentes no Zabbix."
        except requests.exceptions.ConnectionError:
            mensagem = "Falha de conexão com o Zabbix. Verifique host, porta, rota e firewall."
        except requests.exceptions.RequestException as erro:
            mensagem = f"Falha HTTP ao consultar Zabbix: {str(erro)[:180]}"
        except ValueError:
            mensagem = "Resposta inválida do Zabbix. Endpoint respondeu, mas não retornou JSON esperado."
        integration_logger.error("Zabbix synchronization failed", extra={"service": "ZABBIX", "operation": "SYNC"})
        return {
            "status": "ERRO",
            "mensagem": mensagem,
            "integracao": integracao,
            "alarmes": [],
        }

    @classmethod
    def _integracao_zabbix_ativa(cls, integracao_id=None):
        if integracao_id:
            integracao = IntegracaoConfigService.buscar_por_id(integracao_id)
            if integracao and integracao.get("tipo") == "zabbix" and integracao.get("ativo"):
                integracao["possui_segredo"] = 1 if integracao.get("segredo_encrypted") else 0
                return integracao
            return None
        integracoes = cls.integracoes_zabbix()
        return integracoes[0] if integracoes else None

    @staticmethod
    def _normalizar_host(item):
        return {
            "hostid": item.get("hostid"),
            "host": item.get("host"),
            "nome": item.get("name") or item.get("host"),
            "status": item.get("status"),
            "interfaces": item.get("interfaces") or [],
            "raw_payload": item,
        }

    @classmethod
    def _normalizar_cache(cls, item):
        severidade = cls._inteiro(item.get("severidade"), 0)
        severidade_info = SEVERIDADES.get(severidade, SEVERIDADES[0])
        aberto = bool(item.get("aberto"))
        return {
            "eventid": item.get("eventid"),
            "clock": item.get("clock"),
            "data_evento": item.get("data_evento"),
            "aberto": aberto,
            "status_label": "Aberto" if aberto else "Resolvido",
            "status_classe": severidade_info["classe"] if aberto else "success",
            "linha_classe": cls._linha_classe(severidade, aberto),
            "severidade": severidade,
            "severidade_label": item.get("severidade_label") or severidade_info["label"],
            "severidade_classe": severidade_info["classe"],
            "nome": item.get("nome"),
            "host": item.get("host") or "-",
            "integracao_nome": item.get("integracao_nome"),
            "acknowledged": bool(item.get("acknowledged")),
            "sincronizado_em": item.get("sincronizado_em"),
        }

    @classmethod
    def _normalizar_evento(cls, evento, integracao):
        relacionado = evento.get("relatedObject") or {}
        hosts = evento.get("hosts") or []
        severidade = cls._inteiro(evento.get("severity"), cls._inteiro(relacionado.get("priority"), 0))
        severidade_info = SEVERIDADES.get(severidade, SEVERIDADES[0])
        aberto = str(evento.get("value")) == "1"
        clock = cls._inteiro(evento.get("clock"), 0)
        return {
            "eventid": evento.get("eventid"),
            "clock": clock,
            "data_evento": datetime.fromtimestamp(clock) if clock else None,
            "aberto": aberto,
            "status_label": "Aberto" if aberto else "Resolvido",
            "status_classe": severidade_info["classe"] if aberto else "success",
            "linha_classe": cls._linha_classe(severidade, aberto),
            "severidade": severidade,
            "severidade_label": severidade_info["label"],
            "severidade_classe": severidade_info["classe"],
            "nome": evento.get("name") or relacionado.get("description") or "Alarme Zabbix",
            "host": cls._host_label(hosts),
            "integracao_nome": integracao.get("nome"),
            "acknowledged": str(evento.get("acknowledged")) == "1",
            "raw_payload": json.dumps(evento, ensure_ascii=False),
        }

    @staticmethod
    def _linha_classe(severidade, aberto):
        if not aberto:
            return "table-success"
        if severidade >= 5:
            return "table-dark"
        if severidade >= 4:
            return "table-danger"
        if severidade >= 2:
            return "table-warning"
        return ""

    @staticmethod
    def _host_label(hosts):
        if not hosts:
            return "-"
        nomes = []
        for host in hosts:
            nomes.append(host.get("name") or host.get("host") or host.get("hostid"))
        return ", ".join([item for item in nomes if item]) or "-"

    @staticmethod
    def _inteiro(valor, padrao=0):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return padrao

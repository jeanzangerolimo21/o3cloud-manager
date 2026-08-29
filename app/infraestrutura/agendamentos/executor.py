import os
import socket
import time
from decimal import Decimal

from app.core.email import EmailService
from app.infraestrutura.agendamentos.emails import ProxmoxAgendamentoEmailBuilder
from app.implantacao.integracoes_service import IntegracaoConfigService
from app.integracoes.proxmox.client import ProxmoxClient
from app.repositories.proxmox_agendamento_repository import ProxmoxAgendamentoRepository


class ProxmoxAgendamentoExecutor:
    repository = ProxmoxAgendamentoRepository

    @classmethod
    def processar_pendentes(cls, limite=5):
        worker_id = cls._worker_id()
        resultados = []
        for pendente in cls.repository.listar_pendentes(limite):
            agendamento_id = pendente["id"]
            if not cls.repository.claim(agendamento_id, worker_id):
                continue
            try:
                cls.executar(agendamento_id)
                concluido = cls.repository.buscar_por_id(agendamento_id)
                cls._enviar_email_final(concluido, sucesso=True)
                resultados.append(f"Agendamento #{agendamento_id}: CONCLUIDO")
            except Exception as erro:
                mensagem = str(erro)
                cls.repository.atualizar_status(
                    agendamento_id,
                    "ERRO",
                    mensagem,
                    mensagem_erro=mensagem,
                    finalizado_em="NOW()",
                )
                falha = cls.repository.buscar_por_id(agendamento_id)
                cls._enviar_email_final(falha, sucesso=False, mensagem_erro=mensagem)
                resultados.append(f"Agendamento #{agendamento_id}: ERRO - {mensagem}")
        return resultados

    @classmethod
    def executar(cls, agendamento_id):
        agendamento = cls.repository.buscar_por_id(agendamento_id)
        if not agendamento:
            raise ValueError("Agendamento não encontrado.")
        if agendamento.get("status") != "VALIDANDO":
            raise ValueError("Agendamento não está em estado executável.")
        cls._enviar_email_inicio(agendamento)

        client = cls._client(agendamento)
        recurso = cls._localizar_recurso(client, agendamento)
        if recurso.get("node") != agendamento.get("node_nome"):
            raise ValueError("VM localizada em outro node. Sincronize o inventário e crie um novo agendamento.")
        if recurso.get("type") != "qemu":
            raise ValueError("Esta automação aceita apenas VMs QEMU.")

        status_atual = client.obter_status_vm(agendamento["node_nome"], agendamento["vmid"])
        config_atual = client.obter_configuracao(agendamento["node_nome"], "qemu", agendamento["vmid"])
        cls._validar_lock(config_atual, status_atual)

        sockets_atual = cls._int_config(config_atual.get("sockets") or agendamento.get("cpu_sockets_original") or 1) or 1
        cpu_atual = cls._int_config(status_atual.get("cpus") or recurso.get("maxcpu") or agendamento.get("cpu_original"))
        cores_config_atual = cls._int_config(config_atual.get("cores") or agendamento.get("cpu_cores_por_socket_original"))
        cores_por_socket_atual = int(cpu_atual / sockets_atual) if sockets_atual and cpu_atual and cpu_atual % sockets_atual == 0 else cores_config_atual
        memoria_atual = cls._int_config(cls._bytes_para_mb(status_atual.get("maxmem") or recurso.get("maxmem")) or config_atual.get("memory") or agendamento.get("memoria_original_mb"))
        status_original = status_atual.get("status") or recurso.get("status") or agendamento.get("status_original")
        cls.repository.atualizar_status(
            agendamento_id,
            "VALIDANDO",
            "Estado atual validado no Proxmox.",
            cpu_original=cpu_atual,
            cpu_sockets_original=sockets_atual,
            cpu_cores_por_socket_original=cores_por_socket_atual,
            memoria_original_mb=memoria_atual,
            status_original=status_original,
        )

        payload = {}
        cpu_desejada = int(agendamento["cpu_nova"]) if agendamento.get("cpu_nova") else None
        topologia_desejada = None
        if cpu_desejada and cpu_desejada != cpu_atual:
            if cpu_atual and cpu_desejada < cpu_atual:
                raise ValueError("CPU nova é menor que a CPU atual.")
            topologia_desejada = cls._topologia_cpu_desejada(cpu_desejada, sockets_atual)
            payload["cores"] = topologia_desejada["cores_por_socket"]
            if topologia_desejada["sockets"] != sockets_atual:
                payload["sockets"] = topologia_desejada["sockets"]
        if agendamento.get("memoria_nova_mb") and int(agendamento["memoria_nova_mb"]) != memoria_atual:
            if memoria_atual and int(agendamento["memoria_nova_mb"]) < memoria_atual:
                raise ValueError("Memória nova é menor que a memória atual.")
            payload["memory"] = int(agendamento["memoria_nova_mb"])
        if not payload:
            cls.repository.atualizar_status(
                agendamento_id,
                "CONCLUIDO",
                "Configuração já estava nos valores solicitados.",
                cpu_final=cpu_atual,
                cpu_sockets_final=sockets_atual,
                cpu_cores_por_socket_final=cores_por_socket_atual,
                memoria_final_mb=memoria_atual,
                status_final=status_original,
                finalizado_em="NOW()",
            )
            return

        estava_ligada = status_original == "running"
        if estava_ligada:
            if not agendamento.get("desligar_se_necessario"):
                raise ValueError("VM está ligada e o desligamento automático foi desabilitado.")
            cls.repository.atualizar_status(agendamento_id, "DESLIGANDO", "Solicitando shutdown gracioso da VM.")
            upid = client.shutdown_vm(agendamento["node_nome"], agendamento["vmid"])
            cls._aguardar_task(client, agendamento["node_nome"], upid)
            cls.repository.atualizar_status(agendamento_id, "AGUARDANDO_DESLIGAMENTO", "Aguardando VM ficar stopped.")
            cls._aguardar_status(client, agendamento["node_nome"], agendamento["vmid"], "stopped")

        cls.repository.atualizar_status(agendamento_id, "APLICANDO", "Aplicando CPU/RAM no Proxmox.")
        upid = client.alterar_configuracao_vm(agendamento["node_nome"], agendamento["vmid"], payload)
        cls._aguardar_task(client, agendamento["node_nome"], upid)

        cls.repository.atualizar_status(agendamento_id, "VALIDANDO_CONFIGURACAO", "Validando configuração aplicada.")
        config_final = client.obter_configuracao(agendamento["node_nome"], "qemu", agendamento["vmid"])
        status_config_final = client.obter_status_vm(agendamento["node_nome"], agendamento["vmid"])
        sockets_final = cls._int_config(config_final.get("sockets") or payload.get("sockets") or sockets_atual) or 1
        cores_payload_total = payload.get("cores") * sockets_final if payload.get("cores") else None
        cpu_final = cls._int_config(status_config_final.get("cpus") or cores_payload_total or cpu_atual)
        cores_config_final = cls._int_config(config_final.get("cores") or payload.get("cores") or cores_por_socket_atual)
        cores_por_socket_final = int(cpu_final / sockets_final) if sockets_final and cpu_final and cpu_final % sockets_final == 0 else cores_config_final
        memoria_final = cls._int_config(cls._bytes_para_mb(status_config_final.get("maxmem")) or config_final.get("memory") or memoria_atual)
        if cpu_desejada and cpu_final != cpu_desejada:
            raise ValueError("CPU final não confere com o valor solicitado.")
        if payload.get("memory") and memoria_final != payload["memory"]:
            raise ValueError("Memória final não confere com o valor solicitado.")

        status_final = client.obter_status_vm(agendamento["node_nome"], agendamento["vmid"]).get("status")
        if estava_ligada and agendamento.get("religar_automaticamente"):
            cls.repository.atualizar_status(agendamento_id, "LIGANDO", "Religando VM originalmente ligada.")
            upid = client.start_vm(agendamento["node_nome"], agendamento["vmid"])
            cls._aguardar_task(client, agendamento["node_nome"], upid)
            cls.repository.atualizar_status(agendamento_id, "VALIDANDO_INICIALIZACAO", "Validando inicialização da VM.")
            cls._aguardar_status(client, agendamento["node_nome"], agendamento["vmid"], "running")
            status_final = "running"

        cls.repository.atualizar_status(
            agendamento_id,
            "CONCLUIDO",
            "Upgrade concluído e validado.",
            cpu_final=cpu_final,
            cpu_sockets_final=sockets_final,
            cpu_cores_por_socket_final=cores_por_socket_final,
            memoria_final_mb=memoria_final,
            status_final=status_final,
            finalizado_em="NOW()",
        )

    @classmethod
    def _enviar_email_inicio(cls, agendamento):
        destinatario = (agendamento.get("created_by") or "").strip().lower()
        if not destinatario or destinatario == "sistema" or "@" not in destinatario:
            return
        assunto, corpo, corpo_html = ProxmoxAgendamentoEmailBuilder.inicio(agendamento)
        try:
            resultado = EmailService.enviar(assunto, corpo, [destinatario], corpo_html=corpo_html)
            if resultado.get("enviado"):
                cls.repository.registrar_evento(agendamento["id"], "VALIDANDO", f"E-mail de início enviado para {destinatario}.")
            else:
                cls.repository.registrar_evento(agendamento["id"], "VALIDANDO", f"E-mail de início não enviado: {resultado.get('motivo') or 'motivo não informado'}.")
        except Exception as erro:
            cls.repository.registrar_evento(agendamento["id"], "VALIDANDO", f"Falha ao enviar e-mail de início: {erro}")

    @classmethod
    def _enviar_email_final(cls, agendamento, sucesso=True, mensagem_erro=None):
        if not agendamento:
            return
        destinatario = (agendamento.get("created_by") or "").strip().lower()
        if not destinatario or destinatario == "sistema" or "@" not in destinatario:
            return
        status = "CONCLUIDO" if sucesso else "ERRO"
        assunto, corpo, corpo_html = ProxmoxAgendamentoEmailBuilder.final(agendamento, sucesso=sucesso, mensagem_erro=mensagem_erro)
        try:
            resultado = EmailService.enviar(assunto, corpo, [destinatario], corpo_html=corpo_html)
            if resultado.get("enviado"):
                cls.repository.registrar_evento(agendamento["id"], status, f"E-mail final enviado para {destinatario}.")
            else:
                cls.repository.registrar_evento(agendamento["id"], status, f"E-mail final não enviado: {resultado.get('motivo') or 'motivo não informado'}.")
        except Exception as erro:
            cls.repository.registrar_evento(agendamento["id"], status, f"Falha ao enviar e-mail final: {erro}")

    @classmethod
    def _client(cls, agendamento):
        segredo = IntegracaoConfigService.revelar_segredo_config(agendamento["integracao_id"])
        token_nome = cls._token_nome_completo(agendamento)
        return ProxmoxClient(
            agendamento.get("base_url") or agendamento.get("cluster_base_url"),
            token_nome,
            segredo,
            timeout=agendamento.get("timeout_seconds") or 30,
            verify_ssl=bool(agendamento.get("verify_ssl")),
        )

    @staticmethod
    def _token_nome_completo(agendamento):
        token_nome = (agendamento.get("token_nome") or "").strip()
        usuario = (agendamento.get("usuario") or "").strip()
        if token_nome and "!" not in token_nome and usuario:
            return f"{usuario}!{token_nome}"
        return token_nome

    @staticmethod
    def _localizar_recurso(client, agendamento):
        for item in client.listar_vms_containers():
            if item.get("type") == "qemu" and str(item.get("vmid")) == str(agendamento.get("vmid")):
                return item
        raise ValueError("VM não localizada no cluster Proxmox no momento da execução.")

    @staticmethod
    def _topologia_cpu_desejada(cpu_total, sockets_atual):
        sockets_atual = max(int(sockets_atual or 1), 1)
        if cpu_total % sockets_atual == 0:
            return {"sockets": sockets_atual, "cores_por_socket": int(cpu_total / sockets_atual)}
        return {"sockets": 1, "cores_por_socket": int(cpu_total)}

    @staticmethod
    def _validar_lock(config, status):
        lock = (config or {}).get("lock") or (status or {}).get("lock")
        if lock:
            raise ValueError(f"VM possui lock ativo no Proxmox ({lock}).")

    @classmethod
    def _aguardar_task(cls, client, node, upid):
        if not upid:
            return
        timeout = int(os.getenv("PROXMOX_AGENDAMENTO_TASK_TIMEOUT", "600"))
        intervalo = int(os.getenv("PROXMOX_AGENDAMENTO_TASK_INTERVAL", "3"))
        fim = time.time() + timeout
        while time.time() < fim:
            status = client.obter_task_status(node, upid)
            if status.get("status") == "stopped":
                exitstatus = status.get("exitstatus")
                if exitstatus in (None, "OK"):
                    return
                raise ValueError(f"Task Proxmox finalizada com status {exitstatus}.")
            time.sleep(intervalo)
        raise ValueError("Timeout aguardando task do Proxmox.")

    @classmethod
    def _aguardar_status(cls, client, node, vmid, esperado):
        timeout = int(os.getenv("PROXMOX_AGENDAMENTO_VM_TIMEOUT", "600"))
        intervalo = int(os.getenv("PROXMOX_AGENDAMENTO_VM_INTERVAL", "5"))
        fim = time.time() + timeout
        while time.time() < fim:
            status = client.obter_status_vm(node, vmid).get("status")
            if status == esperado:
                return
            time.sleep(intervalo)
        raise ValueError(f"Timeout aguardando VM ficar {esperado}.")

    @staticmethod
    def _int_config(valor):
        if valor is None or valor == "":
            return None
        return int(Decimal(str(valor)))

    @staticmethod
    def _bytes_para_mb(valor):
        if valor is None:
            return None
        return int(Decimal(str(valor)) / Decimal(1024 * 1024))

    @staticmethod
    def _worker_id():
        return f"{socket.gethostname()}:{os.getpid()}"

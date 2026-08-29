from datetime import datetime

from app.core.email import EmailService
from app.repositories.proxmox_agendamento_repository import ProxmoxAgendamentoRepository


STATUS_LABELS = {
    "AGENDADO": "Agendado",
    "VALIDANDO": "Validando",
    "DESLIGANDO": "Desligando",
    "AGUARDANDO_DESLIGAMENTO": "Aguardando desligamento",
    "APLICANDO": "Aplicando",
    "VALIDANDO_CONFIGURACAO": "Validando configuração",
    "LIGANDO": "Ligando",
    "VALIDANDO_INICIALIZACAO": "Validando inicialização",
    "CONCLUIDO": "Concluído",
    "ERRO": "Erro",
    "CANCELADO": "Cancelado",
}

STATUS_CLASSES = {
    "AGENDADO": "primary",
    "VALIDANDO": "info",
    "DESLIGANDO": "warning",
    "AGUARDANDO_DESLIGAMENTO": "warning",
    "APLICANDO": "warning",
    "VALIDANDO_CONFIGURACAO": "info",
    "LIGANDO": "warning",
    "VALIDANDO_INICIALIZACAO": "info",
    "CONCLUIDO": "success",
    "ERRO": "danger",
    "CANCELADO": "secondary",
}


class ProxmoxAgendamentoService:
    repository = ProxmoxAgendamentoRepository

    @classmethod
    def listar(cls, filtros=None):
        agendamentos = cls.repository.listar(filtros or {})
        for item in agendamentos:
            cls._decorar(item)
        return agendamentos

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar(cls, agendamento_id):
        item = cls.repository.buscar_por_id(agendamento_id)
        if item:
            cls._decorar(item)
        return item

    @classmethod
    def eventos(cls, agendamento_id):
        eventos = cls.repository.listar_eventos(agendamento_id)
        for evento in eventos:
            evento["status_label"] = STATUS_LABELS.get(evento.get("status"), evento.get("status"))
            evento["status_classe"] = STATUS_CLASSES.get(evento.get("status"), "secondary")
        return eventos

    @classmethod
    def contexto_form(cls):
        vms = cls.repository.listar_vms_qemu()
        nodes = cls.repository.listar_nodes()
        clusters = []
        vistos = set()
        for vm in vms:
            key = vm.get("integracao_id")
            if key in vistos:
                continue
            vistos.add(key)
            clusters.append({
                "id": vm.get("integracao_id"),
                "nome": vm.get("cluster_nome"),
                "base_url": vm.get("cluster_base_url"),
            })
        return {"clusters": clusters, "nodes": nodes, "vms": vms}

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        inventario_id = cls._int(dados.get("inventario_id"), "Selecione uma VM QEMU.")
        vm = cls.repository.buscar_inventario_qemu(inventario_id)
        if not vm:
            raise ValueError("VM QEMU não encontrada no inventário ativo do Proxmox.")

        cpu_atual = int(float(vm.get("cpu_cores") or 0))
        memoria_atual = int(vm.get("memoria_mb") or 0)
        cpu_nova = cls._int_opcional(dados.get("cpu_nova"), "CPU nova inválida.")
        memoria_nova_mb = cls._memoria_mb(dados.get("memoria_nova_gb"))
        executar_em = cls._parse_datetime(dados.get("executar_em"))
        motivo = (dados.get("motivo") or "").strip()

        if not motivo:
            raise ValueError("Informe o motivo do upgrade.")
        if executar_em <= datetime.now():
            raise ValueError("A data e hora do agendamento precisam estar no futuro.")
        if cpu_nova is None and memoria_nova_mb is None:
            raise ValueError("Informe uma nova CPU, uma nova memória, ou ambos.")
        if cpu_nova is not None and cpu_nova <= 0:
            raise ValueError("CPU nova precisa ser maior que zero.")
        if memoria_nova_mb is not None and memoria_nova_mb <= 0:
            raise ValueError("Memória nova precisa ser maior que zero.")
        if cpu_nova is not None and cpu_atual and cpu_nova == cpu_atual:
            cpu_nova = None
        if memoria_nova_mb is not None and memoria_atual and memoria_nova_mb == memoria_atual:
            memoria_nova_mb = None
        if cpu_nova is None and memoria_nova_mb is None:
            raise ValueError("Os novos valores são iguais aos atuais.")
        if cpu_nova is not None and cpu_atual and cpu_nova < cpu_atual:
            raise ValueError("Esta primeira versão permite apenas upgrade de CPU.")
        if memoria_nova_mb is not None and memoria_atual and memoria_nova_mb < memoria_atual:
            raise ValueError("Esta primeira versão permite apenas upgrade de memória.")
        if cls.repository.existe_ativo_vm(vm["integracao_id"], vm["node"], vm["vmid"]):
            raise ValueError("Já existe um agendamento ativo para esta VM.")

        payload = {
            "integracao_id": vm["integracao_id"],
            "cluster_nome": vm.get("cluster_nome"),
            "cluster_base_url": vm.get("cluster_base_url"),
            "inventario_id": vm.get("id"),
            "node_nome": vm.get("node"),
            "vmid": vm.get("vmid"),
            "vm_nome": vm.get("nome"),
            "cpu_original": cpu_atual or None,
            "cpu_nova": cpu_nova,
            "memoria_original_mb": memoria_atual or None,
            "memoria_nova_mb": memoria_nova_mb,
            "status_original": vm.get("status"),
            "executar_em": executar_em,
            "desligar_se_necessario": dados.get("desligar_se_necessario") == "on" or dados.get("desligar_se_necessario") in (True, "1", 1),
            "religar_automaticamente": dados.get("religar_automaticamente") == "on" or dados.get("religar_automaticamente") in (True, "1", 1),
            "motivo": motivo,
            "created_by": usuario_email or "sistema",
        }
        agendamento_id = cls.repository.criar(payload)
        cls._enviar_email_cadastro(agendamento_id)
        return agendamento_id

    @classmethod
    def _enviar_email_cadastro(cls, agendamento_id):
        agendamento = cls.repository.buscar_por_id(agendamento_id)
        destinatario = (agendamento.get("created_by") or "").strip().lower() if agendamento else ""
        if not destinatario or destinatario == "sistema" or "@" not in destinatario:
            return
        assunto = f"Agendamento Proxmox #{agendamento_id} criado"
        corpo = cls._corpo_email_agendamento(
            agendamento,
            "Agendamento criado",
            "Seu agendamento Proxmox foi registrado e será executado pelo worker no horário programado.",
        )
        try:
            resultado = EmailService.enviar(assunto, corpo, [destinatario])
            if resultado.get("enviado"):
                cls.repository.registrar_evento(agendamento_id, "AGENDADO", f"E-mail de criação enviado para {destinatario}.")
            else:
                cls.repository.registrar_evento(agendamento_id, "AGENDADO", f"E-mail de criação não enviado: {resultado.get('motivo') or 'motivo não informado'}.")
        except Exception as erro:
            cls.repository.registrar_evento(agendamento_id, "AGENDADO", f"Falha ao enviar e-mail de criação: {erro}")

    @classmethod
    def _corpo_email_agendamento(cls, agendamento, titulo, mensagem):
        return "\n".join([
            titulo,
            "",
            mensagem,
            "",
            f"Agendamento: #{agendamento.get('id')}",
            f"Execução: {agendamento.get('executar_em').strftime('%d/%m/%Y %H:%M') if agendamento.get('executar_em') else '-'}",
            f"Cluster: {agendamento.get('integracao_nome') or agendamento.get('cluster_nome') or '-'}",
            f"Node: {agendamento.get('node_nome') or '-'}",
            f"VMID: {agendamento.get('vmid') or '-'}",
            f"VM: {agendamento.get('vm_nome') or '-'}",
            f"CPU atual: {agendamento.get('cpu_original') or '-'}",
            f"CPU total desejada: {agendamento.get('cpu_nova') or 'sem alteração'}",
            f"Memória atual: {round((agendamento.get('memoria_original_mb') or 0) / 1024, 2) if agendamento.get('memoria_original_mb') else '-'} GB",
            f"Memória total desejada: {round((agendamento.get('memoria_nova_mb') or 0) / 1024, 2) if agendamento.get('memoria_nova_mb') else 'sem alteração'} GB",
            f"Motivo: {agendamento.get('motivo') or '-'}",
        ])

    @classmethod
    def cancelar(cls, agendamento_id, usuario_email="sistema"):
        agendamento = cls.repository.buscar_por_id(agendamento_id)
        if not agendamento:
            raise ValueError("Agendamento não encontrado.")
        if agendamento.get("status") != "AGENDADO":
            raise ValueError("Somente agendamentos ainda não iniciados podem ser cancelados.")
        return cls.repository.cancelar(agendamento_id, usuario_email)

    @staticmethod
    def _decorar(item):
        item["status_label"] = STATUS_LABELS.get(item.get("status"), item.get("status"))
        item["status_classe"] = STATUS_CLASSES.get(item.get("status"), "secondary")
        item["memoria_original_gb"] = round((item.get("memoria_original_mb") or 0) / 1024, 2) if item.get("memoria_original_mb") else None
        item["memoria_nova_gb"] = round((item.get("memoria_nova_mb") or 0) / 1024, 2) if item.get("memoria_nova_mb") else None
        item["memoria_final_gb"] = round((item.get("memoria_final_mb") or 0) / 1024, 2) if item.get("memoria_final_mb") else None
        return item

    @staticmethod
    def _int(valor, mensagem):
        try:
            return int(str(valor).strip())
        except (TypeError, ValueError):
            raise ValueError(mensagem)

    @classmethod
    def _int_opcional(cls, valor, mensagem):
        texto = (valor or "").strip()
        if not texto:
            return None
        return cls._int(texto, mensagem)

    @classmethod
    def _memoria_mb(cls, valor):
        texto = (valor or "").strip().replace(",", ".")
        if not texto:
            return None
        try:
            gb = float(texto)
        except ValueError:
            raise ValueError("Memória nova inválida.")
        return int(round(gb * 1024))

    @staticmethod
    def _parse_datetime(valor):
        texto = (valor or "").strip()
        for formato in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue
        raise ValueError("Data e hora do agendamento inválidas.")

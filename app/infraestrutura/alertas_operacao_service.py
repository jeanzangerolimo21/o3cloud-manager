from datetime import datetime, time, timedelta
from html import escape

from flask import current_app

from app.core.email import EmailService
from app.infraestrutura.pbs_backup_service import PBSBackupService
from app.infraestrutura.truenas_backup_service import TrueNASBackupService
from app.infraestrutura.zabbix_service import ZabbixMonitoramentoService
from app.repositories.alertas_operacao_repository import AlertasOperacaoRepository


class AlertasOperacaoService:
    repository = AlertasOperacaoRepository
    TRUE_NAS_DIAS_SEM_MODIFICACAO = 5
    ZABBIX_SEVERIDADE_CRITICA = 5

    @classmethod
    def processar_pendentes(cls, limite=20, forcar=False, agora=None):
        agora = agora or datetime.now()
        resumo = cls.resumo_alertas()
        if resumo["total_alertas"] <= 0:
            return ["Nenhum alerta operacional critico para enviar."]

        usuarios = cls.repository.listar_usuarios_habilitados()
        enviados = []
        for usuario in usuarios:
            if len(enviados) >= max(1, int(limite or 20)):
                break
            if not forcar and not cls._usuario_deve_receber(usuario, agora):
                continue
            resultado = cls.enviar_para_usuario(usuario, resumo)
            status = "OK" if resultado.get("enviado") else "ERRO"
            enviados.append(f"{status} usuario #{usuario.get('id')} {usuario.get('email')}: {resultado.get('motivo') or 'enviado'}")
            if resultado.get("enviado"):
                cls.repository.marcar_envio_usuario(usuario.get("id"))
        return enviados or ["Nenhum usuario habilitado/vencido para receber alertas operacionais."]

    @classmethod
    def enviar_para_usuario(cls, usuario, resumo=None):
        resumo = resumo or cls.resumo_alertas()
        if resumo["total_alertas"] <= 0:
            return {"enviado": False, "motivo": "sem_alertas"}
        assunto = f"[O3Cloud] {resumo['total_alertas']} alerta(s) critico(s) de operacao"
        corpo = cls._corpo_texto(usuario, resumo)
        corpo_html = cls._corpo_html(usuario, resumo)
        try:
            return EmailService.enviar(assunto, corpo, [usuario.get("email")], corpo_html=corpo_html)
        except Exception as erro:
            return {"enviado": False, "motivo": str(erro)[:180], "destinatarios": [usuario.get("email")]}

    @classmethod
    def resumo_alertas(cls):
        zabbix = cls._zabbix_criticos()
        pbs = cls._pbs_pendentes()
        truenas = cls._truenas_sem_modificacao()
        return {
            "zabbix": zabbix,
            "pbs": pbs,
            "truenas": truenas,
            "total_alertas": len(zabbix) + len(pbs) + len(truenas),
            "links": cls._links_dashboard(),
            "gerado_em": datetime.now(),
        }

    @classmethod
    def _zabbix_criticos(cls):
        resultado = ZabbixMonitoramentoService.listar_alarmes(limite=200)
        alarmes = resultado.get("alarmes") or []
        return [item for item in alarmes if item.get("aberto") and int(item.get("severidade") or 0) >= cls.ZABBIX_SEVERIDADE_CRITICA]

    @classmethod
    def _pbs_pendentes(cls):
        return PBSBackupService.listar(status="com_alerta")

    @classmethod
    def _truenas_sem_modificacao(cls):
        resultado = TrueNASBackupService.listar()
        corte = datetime.now() - timedelta(days=cls.TRUE_NAS_DIAS_SEM_MODIFICACAO)
        alertas = []
        for item in resultado.get("registros") or []:
            ultimo = item.get("ultimo_mtime")
            if not ultimo or ultimo < corte:
                alertas.append(item)
        return alertas

    @classmethod
    def _links_dashboard(cls):
        base_url = (current_app.config.get("PUBLIC_BASE_URL") or "").rstrip("/") if current_app else ""
        rotas = {
            "zabbix": "/infraestrutura/monitoramento-zabbix?status=critica",
            "pbs": "/infraestrutura/backups-pbs?status=com_alerta",
            "truenas": "/infraestrutura/backup-nas?aba=alertas",
        }
        if not base_url:
            return rotas
        return {chave: f"{base_url}{valor}" for chave, valor in rotas.items()}

    @classmethod
    def _usuario_deve_receber(cls, usuario, agora):
        horario = cls._parse_horario(usuario.get("alertas_operacao_horario"))
        if agora.time().replace(second=0, microsecond=0) < horario:
            return False
        ultimo = usuario.get("alertas_operacao_ultimo_envio_em")
        if not ultimo:
            return True
        periodicidade = (usuario.get("alertas_operacao_periodicidade") or "DIARIA").upper()
        if periodicidade == "SEMANAL":
            return ultimo <= agora - timedelta(days=7)
        return ultimo.date() < agora.date()

    @staticmethod
    def _parse_horario(valor):
        if isinstance(valor, time):
            return valor.replace(second=0, microsecond=0)
        texto = str(valor or "08:00").strip()
        partes = texto.split(":")
        try:
            return time(hour=int(partes[0]), minute=int(partes[1]) if len(partes) > 1 else 0)
        except (TypeError, ValueError, IndexError):
            return time(hour=8, minute=0)

    @classmethod
    def _corpo_texto(cls, usuario, resumo):
        linhas = [
            f"Ola, {usuario.get('nome') or 'usuario'}.",
            "",
            "Existem alertas criticos de operacao que precisam de conferencia no O3Cloud Manager.",
            "",
            f"Zabbix critico aberto: {len(resumo['zabbix'])}",
            f"Backups PBS nao realizados no prazo: {len(resumo['pbs'])}",
            f"Diretorios TrueNAS sem modificacao ha mais de {cls.TRUE_NAS_DIAS_SEM_MODIFICACAO} dias: {len(resumo['truenas'])}",
            "",
            f"Zabbix: {resumo['links']['zabbix']}",
            f"PBS: {resumo['links']['pbs']}",
            f"TrueNAS: {resumo['links']['truenas']}",
            "",
            "Resumo rapido:",
        ]
        linhas.extend(cls._linhas_texto("Zabbix", resumo["zabbix"], cls._label_zabbix))
        linhas.extend(cls._linhas_texto("PBS", resumo["pbs"], cls._label_pbs))
        linhas.extend(cls._linhas_texto("TrueNAS", resumo["truenas"], cls._label_truenas))
        linhas.append("")
        linhas.append("Acesse o dashboard para os detalhes completos e tratativa operacional.")
        return "\n".join(linhas)

    @classmethod
    def _linhas_texto(cls, titulo, itens, label_fn):
        linhas = [f"- {titulo}:"]
        if not itens:
            linhas.append("  sem itens")
            return linhas
        for item in itens[:5]:
            linhas.append(f"  - {label_fn(item)}")
        if len(itens) > 5:
            linhas.append(f"  - ... mais {len(itens) - 5} item(ns)")
        return linhas

    @classmethod
    def _corpo_html(cls, usuario, resumo):
        cards = "".join([
            cls._card_html("Zabbix critico", len(resumo["zabbix"]), resumo["links"]["zabbix"]),
            cls._card_html("PBS pendente", len(resumo["pbs"]), resumo["links"]["pbs"]),
            cls._card_html(f"TrueNAS > {cls.TRUE_NAS_DIAS_SEM_MODIFICACAO} dias", len(resumo["truenas"]), resumo["links"]["truenas"]),
        ])
        listas = "".join([
            cls._lista_html("Zabbix", resumo["zabbix"], cls._label_zabbix),
            cls._lista_html("PBS", resumo["pbs"], cls._label_pbs),
            cls._lista_html("TrueNAS", resumo["truenas"], cls._label_truenas),
        ])
        nome = escape(usuario.get("nome") or "usuario")
        return f"""
        <div style="font-family:Arial,sans-serif;color:#1f2937;line-height:1.45">
          <p>Ola, {nome}.</p>
          <p>Existem alertas criticos de operacao que precisam de conferencia no O3Cloud Manager.</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin:18px 0">{cards}</div>
          {listas}
          <p style="margin-top:18px;color:#6b7280">Acesse o dashboard para os detalhes completos e tratativa operacional.</p>
        </div>
        """

    @staticmethod
    def _card_html(titulo, total, link):
        return f"""
        <a href="{escape(link)}" style="display:block;text-decoration:none;color:#111827;border:1px solid #e5e7eb;border-radius:8px;padding:14px 16px;min-width:160px;background:#f9fafb">
          <div style="font-size:12px;color:#6b7280;text-transform:uppercase">{escape(titulo)}</div>
          <div style="font-size:28px;font-weight:700;color:#b91c1c">{int(total or 0)}</div>
        </a>
        """

    @staticmethod
    def _lista_html(titulo, itens, label_fn):
        if not itens:
            return f"<h3 style='font-size:16px;margin:18px 0 8px'>{escape(titulo)}</h3><p style='color:#6b7280'>Sem itens.</p>"
        lis = "".join(f"<li>{escape(label_fn(item))}</li>" for item in itens[:5])
        if len(itens) > 5:
            lis += f"<li>... mais {len(itens) - 5} item(ns)</li>"
        return f"<h3 style='font-size:16px;margin:18px 0 8px'>{escape(titulo)}</h3><ul>{lis}</ul>"

    @staticmethod
    def _label_zabbix(item):
        return f"{item.get('host') or '-'} - {item.get('nome') or '-'}"

    @staticmethod
    def _label_pbs(item):
        ultimo = item.get("ultimo_backup_em") or "nunca"
        return f"{item.get('nome') or item.get('vmid') or '-'} ({item.get('node') or '-'}) - ultimo backup: {ultimo}"

    @staticmethod
    def _label_truenas(item):
        ultimo = item.get("ultimo_mtime") or "nunca"
        return f"{item.get('cliente_nome') or item.get('prefixo_proxmox') or '-'} - {item.get('pasta_path') or '-'} - ultimo arquivo: {ultimo}"

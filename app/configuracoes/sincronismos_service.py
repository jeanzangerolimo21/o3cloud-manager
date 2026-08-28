import os
import subprocess
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

from app.repositories.base_repository import BaseRepository


class SincronismosAgendadosService:
    repository = BaseRepository
    REPO_DIR = Path(__file__).resolve().parents[2]
    TIPOS_BACKGROUND = {"OMIE_SETUP_CONTRATOS"}
    OPCOES_FREQUENCIA = (
        (15, "15 minutos"),
        (30, "30 minutos"),
        (60, "1 hora"),
        (120, "2 horas"),
        (360, "6 horas"),
        (720, "12 horas"),
        (1440, "24 horas"),
    )
    TIPOS = {
        "OMIE": {
            "nome": "Omie",
            "descricao": "Clientes, contratos e itens comerciais.",
            "icone": "bi-cloud-check",
        },
        "OMIE_RECEBIMENTOS": {
            "nome": "Omie - Recebimentos",
            "descricao": "Contas a Receber recebidas para cache financeiro e comissoes.",
            "icone": "bi-cash-coin",
        },
        "OMIE_FATURAMENTO_PREVISOES": {
            "nome": "Omie - Faturamento e Previsoes",
            "descricao": "Historico de contas a receber e previsoes vinculadas aos contratos.",
            "icone": "bi-calendar2-check",
        },
        "OMIE_SETUP_CONTRATOS": {
            "nome": "Omie - Setup dos Contratos",
            "descricao": "Ordens de servico de setup/implantacao vinculadas aos contratos.",
            "icone": "bi-cloud-arrow-down",
        },
        "ZABBIX": {
            "nome": "Zabbix",
            "descricao": "Hosts e alarmes recentes para cache operacional.",
            "icone": "bi-activity",
        },
        "PROXMOX": {
            "nome": "Proxmox",
            "descricao": "Inventario de nodes, VMs, containers e consumo.",
            "icone": "bi-hdd-network",
        },
        "CLICKSIGN": {
            "nome": "ClickSign",
            "descricao": "Status de propostas enviadas para assinatura.",
            "icone": "bi-pen",
        },
        "PBS": {
            "nome": "PBS",
            "descricao": "Snapshots dos escopos do Proxmox Backup Server.",
            "icone": "bi-server",
        },
        "TRUENAS": {
            "nome": "TrueNAS",
            "descricao": "Cache de backups NAS e alertas de diretórios.",
            "icone": "bi-device-hdd",
        },
    }

    for _storage in ("BKP1", "BKP2", "BKP3", "BKP4", "BKP5", "BKP6", "BKP7"):
        TIPOS[f"TRUENAS_{_storage}"] = {
            "nome": f"TrueNAS {_storage}",
            "descricao": f"Cache de backups NAS somente do storage {_storage}.",
            "icone": "bi-device-hdd",
        }

    @classmethod
    def contexto(cls):
        agendamentos = cls._agendamentos_com_definicao()
        historico = cls.repository.fetch_all(
            """
            SELECT e.*, a.nome
            FROM config_sincronismos_execucoes e
            INNER JOIN config_sincronismos_agendados a ON a.id = e.agendamento_id
            ORDER BY e.created_at DESC, e.id DESC
            LIMIT 40
            """
        )
        return {
            "agendamentos": agendamentos,
            "historico": historico,
            "opcoes_frequencia": cls.OPCOES_FREQUENCIA,
        }

    @classmethod
    def salvar(cls, tipo, dados, usuario_email):
        tipo = cls._normalizar_tipo(tipo)
        frequencia = int(dados.get("frequencia_minutos") or 1440)
        if frequencia not in {item[0] for item in cls.OPCOES_FREQUENCIA}:
            raise ValueError("Frequencia de sincronismo invalida.")
        horario = cls._normalizar_horario(dados.get("horario_execucao"))
        ativo = 1 if dados.get("ativo") else 0
        cls.repository.execute(
            """
            UPDATE config_sincronismos_agendados
               SET ativo=%s,
                   frequencia_minutos=%s,
                   horario_execucao=%s,
                   proxima_execucao_em=%s,
                   updated_by=%s
             WHERE tipo=%s
            """,
            (ativo, frequencia, horario, cls._proxima_execucao(ativo, frequencia, horario), usuario_email, tipo),
        )

    @classmethod
    def executar_manual(cls, agendamento_id, usuario_email):
        agendamento = cls._buscar_por_id(agendamento_id)
        if not agendamento:
            raise ValueError("Agendamento nao encontrado.")
        if agendamento["tipo"] in cls.TIPOS_BACKGROUND:
            return cls._executar_background(agendamento, usuario_email, manual=True)
        return cls._executar(agendamento, usuario_email, manual=True)

    @classmethod
    def executar_manual_por_tipo(cls, tipo, usuario_email):
        tipo = cls._normalizar_tipo(tipo)
        agendamento = cls._buscar_por_tipo(tipo)
        if not agendamento:
            raise ValueError("Agendamento nao encontrado.")
        if agendamento["tipo"] in cls.TIPOS_BACKGROUND:
            return cls._executar_background(agendamento, usuario_email, manual=True)
        return cls._executar(agendamento, usuario_email, manual=True)

    @classmethod
    def processar_pendentes(cls, limite=5):
        limite = max(1, min(int(limite or 5), 20))
        agendamentos = cls.repository.fetch_all(
            f"""
            SELECT *
            FROM config_sincronismos_agendados
            WHERE ativo = 1
              AND (proxima_execucao_em IS NULL OR proxima_execucao_em <= NOW())
            ORDER BY COALESCE(proxima_execucao_em, created_at), id
            LIMIT {limite}
            """
        )
        resultados = []
        for item in agendamentos:
            if item["tipo"] in cls.TIPOS_BACKGROUND:
                resultados.append(cls._executar_background(item, "sistema-agendador", manual=False))
            else:
                resultados.append(cls._executar(item, "sistema-agendador", manual=False))
        return resultados

    @classmethod
    def executar_worker(cls, execucao_id):
        execucao = cls.repository.fetch_one(
            """
            SELECT e.*, a.ativo, a.frequencia_minutos, a.horario_execucao
            FROM config_sincronismos_execucoes e
            INNER JOIN config_sincronismos_agendados a ON a.id = e.agendamento_id
            WHERE e.id=%s
            """,
            (execucao_id,),
        )
        if not execucao:
            raise ValueError("Execucao de sincronismo nao encontrada.")
        if execucao.get("status") != "EXECUTANDO" or execucao.get("finalizada_em"):
            return f"{execucao['tipo']}: ignorado - execucao ja finalizada."
        return cls._executar_handler_e_finalizar(execucao, execucao.get("executado_por") or "sistema-worker")

    @classmethod
    def _agendamentos_com_definicao(cls):
        existentes = {item["tipo"]: item for item in cls.repository.fetch_all("SELECT * FROM config_sincronismos_agendados ORDER BY id")}
        agendamentos = []
        for tipo, definicao in cls.TIPOS.items():
            item = existentes.get(tipo) or {}
            agendamentos.append({
                **item,
                "tipo": tipo,
                "nome": item.get("nome") or definicao["nome"],
                "descricao": definicao["descricao"],
                "icone": definicao["icone"],
                "ativo": bool(item.get("ativo")),
                "frequencia_minutos": int(item.get("frequencia_minutos") or 1440),
                "horario_execucao": cls._formatar_horario(item.get("horario_execucao")),
            })
        return agendamentos

    @classmethod
    def _buscar_por_id(cls, agendamento_id):
        return cls.repository.fetch_one("SELECT * FROM config_sincronismos_agendados WHERE id=%s", (agendamento_id,))

    @classmethod
    def _buscar_por_tipo(cls, tipo):
        return cls.repository.fetch_one("SELECT * FROM config_sincronismos_agendados WHERE tipo=%s", (tipo,))

    @classmethod
    def _executar(cls, agendamento, usuario_email, manual=False):
        execucao_id = cls.repository.execute_insert(
            """
            INSERT INTO config_sincronismos_execucoes (uuid, agendamento_id, tipo, status, executado_por, manual)
            VALUES (%s, %s, %s, 'EXECUTANDO', %s, %s)
            """,
            (cls.repository.generate_uuid(), agendamento["id"], agendamento["tipo"], usuario_email, 1 if manual else 0),
        )
        execucao = {
            **agendamento,
            "id": execucao_id,
            "agendamento_id": agendamento["id"],
        }
        return cls._executar_handler_e_finalizar(execucao, usuario_email)

    @classmethod
    def _executar_background(cls, agendamento, usuario_email, manual=False):
        em_andamento = cls._execucao_em_andamento(agendamento["tipo"])
        if em_andamento:
            return f"{agendamento['tipo']}: EXECUTANDO - Sincronismo ja esta em andamento desde {em_andamento.get('iniciada_em')}."

        execucao_id = cls.repository.execute_insert(
            """
            INSERT INTO config_sincronismos_execucoes (uuid, agendamento_id, tipo, status, executado_por, manual, mensagem)
            VALUES (%s, %s, %s, 'EXECUTANDO', %s, %s, %s)
            """,
            (
                cls.repository.generate_uuid(),
                agendamento["id"],
                agendamento["tipo"],
                usuario_email,
                1 if manual else 0,
                "Sincronismo iniciado em segundo plano.",
            ),
        )
        cls.repository.execute(
            """
            UPDATE config_sincronismos_agendados
               SET ultima_execucao_em=NOW(),
                   proxima_execucao_em=%s,
                   ultimo_status='EXECUTANDO',
                   ultimo_mensagem=%s,
                   updated_by=%s
             WHERE id=%s
            """,
            (
                cls._proxima_execucao(
                    agendamento.get("ativo"),
                    agendamento.get("frequencia_minutos"),
                    cls._horario_obj(agendamento.get("horario_execucao")),
                ),
                "Sincronismo iniciado em segundo plano.",
                usuario_email,
                agendamento["id"],
            ),
        )
        try:
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "flask",
                    "--app",
                    "app:create_app",
                    "sincronismos-executar-worker",
                    "--execucao-id",
                    str(execucao_id),
                ],
                cwd=str(cls.REPO_DIR),
                env=os.environ.copy(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as erro:
            mensagem = f"Falha ao iniciar sincronismo em segundo plano: {erro}"[:500]
            cls._finalizar_execucao(agendamento, execucao_id, "ERRO", mensagem, usuario_email)
            return f"{agendamento['tipo']}: ERRO - {mensagem}"

        return f"{agendamento['tipo']}: EXECUTANDO - Sincronismo iniciado em segundo plano."

    @classmethod
    def _executar_handler_e_finalizar(cls, execucao, usuario_email):
        agendamento = {
            "id": execucao.get("agendamento_id") or execucao.get("id"),
            "tipo": execucao["tipo"],
            "ativo": execucao.get("ativo"),
            "frequencia_minutos": execucao.get("frequencia_minutos"),
            "horario_execucao": execucao.get("horario_execucao"),
        }
        try:
            resultado = cls._handler(execucao["tipo"])(usuario_email)
            status = "OK" if (resultado.get("status") or "OK") == "OK" else "ERRO"
            mensagem = (resultado.get("mensagem") or "Sincronismo concluido.")[:500]
        except Exception as erro:
            status = "ERRO"
            mensagem = str(erro)[:500]
        cls._finalizar_execucao(agendamento, execucao["id"], status, mensagem, usuario_email)
        return f"{execucao['tipo']}: {status} - {mensagem}"

    @classmethod
    def _finalizar_execucao(cls, agendamento, execucao_id, status, mensagem, usuario_email):
        cls.repository.execute(
            """
            UPDATE config_sincronismos_execucoes
               SET status=%s, finalizada_em=NOW(), mensagem=%s
             WHERE id=%s
            """,
            (status, mensagem, execucao_id),
        )
        cls.repository.execute(
            """
            UPDATE config_sincronismos_agendados
               SET ultima_execucao_em=NOW(),
                   proxima_execucao_em=%s,
                   ultimo_status=%s,
                   ultimo_mensagem=%s,
                   updated_by=%s
             WHERE id=%s
            """,
            (
                cls._proxima_execucao(
                    agendamento.get("ativo"),
                    agendamento.get("frequencia_minutos"),
                    cls._horario_obj(agendamento.get("horario_execucao")),
                ),
                status,
                mensagem,
                usuario_email,
                agendamento["id"],
            ),
        )

    @classmethod
    def _execucao_em_andamento(cls, tipo):
        return cls.repository.fetch_one(
            """
            SELECT id, iniciada_em
            FROM config_sincronismos_execucoes
            WHERE tipo=%s
              AND status='EXECUTANDO'
              AND finalizada_em IS NULL
            ORDER BY iniciada_em DESC, id DESC
            LIMIT 1
            """,
            (tipo,),
        )

    @staticmethod
    def _normalizar_horario(valor):
        texto = str(valor or "").strip()
        if not texto:
            return None
        try:
            partes = texto.split(":")
            if len(partes) not in (2, 3):
                raise ValueError
            hora = int(partes[0])
            minuto = int(partes[1])
            segundo = int(partes[2]) if len(partes) == 3 else 0
            return time(hora, minuto, segundo)
        except (TypeError, ValueError):
            raise ValueError("Horario invalido. Use o formato HH:MM.")

    @staticmethod
    def _horario_obj(valor):
        if isinstance(valor, time):
            return valor
        if isinstance(valor, timedelta):
            total = int(valor.total_seconds()) % 86400
            return time(total // 3600, (total % 3600) // 60, total % 60)
        if valor:
            return SincronismosAgendadosService._normalizar_horario(valor)
        return None

    @classmethod
    def _formatar_horario(cls, valor):
        horario = cls._horario_obj(valor)
        return horario.strftime("%H:%M") if horario else ""

    @staticmethod
    def _proxima_execucao(ativo, frequencia, horario):
        if not ativo:
            return None
        agora = datetime.now()
        if horario:
            proxima = agora.replace(
                hour=horario.hour,
                minute=horario.minute,
                second=horario.second,
                microsecond=0,
            )
            if proxima <= agora:
                proxima += timedelta(days=1)
            return proxima
        return agora + timedelta(minutes=int(frequencia or 1440))

    @classmethod
    def _handler(cls, tipo):
        tipo = cls._normalizar_tipo(tipo)
        if tipo.startswith("TRUENAS_BKP"):
            storage = "/" + tipo.replace("TRUENAS_", "").replace("BKP", "mnt/BKP", 1)
            return lambda usuario_email: cls._sincronizar_truenas(usuario_email, storage=storage)
        handlers = {
            "OMIE": cls._sincronizar_omie,
            "OMIE_RECEBIMENTOS": cls._sincronizar_omie_recebimentos,
            "OMIE_FATURAMENTO_PREVISOES": cls._sincronizar_omie_faturamento_previsoes,
            "OMIE_SETUP_CONTRATOS": cls._sincronizar_omie_setup_contratos,
            "ZABBIX": cls._sincronizar_zabbix,
            "PROXMOX": cls._sincronizar_proxmox,
            "CLICKSIGN": cls._sincronizar_clicksign,
            "PBS": cls._sincronizar_pbs,
            "TRUENAS": cls._sincronizar_truenas,
        }
        return handlers[tipo]

    @classmethod
    def _normalizar_tipo(cls, tipo):
        tipo = (tipo or "").strip().upper()
        if tipo not in cls.TIPOS:
            raise ValueError("Tipo de sincronismo invalido.")
        return tipo

    @staticmethod
    def _sincronizar_omie(usuario_email):
        from app.integracoes.omie.sync import OmieSync

        sync = OmieSync()
        sync.sincronizar_clientes()
        contratos = sync.sincronizar_contratos() or {}
        return {
            "status": "OK",
            "mensagem": "Sincronismo Omie concluido. Contratos processados: {}.".format(contratos.get("processados", 0)),
        }

    @staticmethod
    def _sincronizar_omie_recebimentos(usuario_email):
        from app.integracoes.omie.sync import OmieSync

        recebimentos = OmieSync().sincronizar_recebimentos() or {}
        return {
            "status": "OK",
            "mensagem": (
                "Recebimentos Omie atualizados. "
                "Processados: {processados}. Novos: {novos}. Atualizados: {atualizados}. Ignorados: {ignorados}."
            ).format(
                processados=recebimentos.get("processados", 0),
                novos=recebimentos.get("novos", 0),
                atualizados=recebimentos.get("atualizados", 0),
                ignorados=recebimentos.get("ignorados", 0),
            ),
        }

    @staticmethod
    def _sincronizar_omie_faturamento_previsoes(usuario_email):
        from app.integracoes.omie.sync import OmieSync

        dados = OmieSync().sincronizar_faturamento_previsoes() or {}
        return {
            "status": "OK",
            "mensagem": (
                "Faturamento e Previsoes Omie atualizados. "
                "Processados: {processados}. Novos: {novos}. "
                "Atualizados: {atualizados}. Ignorados: {ignorados}."
            ).format(**{chave: dados.get(chave, 0) for chave in ("processados", "novos", "atualizados", "ignorados")}),
        }

    @staticmethod
    def _sincronizar_omie_setup_contratos(usuario_email):
        from app.contratos.service import ContratoService

        dados = ContratoService.sincronizar_setups_omie() or {}
        return {
            "status": dados.get("status") or "OK",
            "mensagem": dados.get("mensagem") or "Setups Omie sincronizados.",
        }

    @staticmethod
    def _sincronizar_zabbix(usuario_email):
        from app.infraestrutura.zabbix_service import ZabbixMonitoramentoService

        return ZabbixMonitoramentoService.sincronizar(limite=120)

    @staticmethod
    def _sincronizar_proxmox(usuario_email):
        from app.infraestrutura.proxmox_service import ProxmoxInventoryService

        return ProxmoxInventoryService.sincronizar(usuario_email=usuario_email)

    @staticmethod
    def _sincronizar_clicksign(usuario_email):
        from app.propostas.service import PropostaService

        resultados = PropostaService.sincronizar_clicksign_pendentes(usuario_email)
        erros = [item for item in resultados if item.get("status") != "OK"]
        return {
            "status": "ERRO" if erros else "OK",
            "mensagem": "Sincronismo ClickSign concluido. Propostas verificadas: {}. Erros: {}.".format(len(resultados), len(erros)),
        }

    @staticmethod
    def _sincronizar_pbs(usuario_email):
        from app.infraestrutura.pbs_backup_service import PBSBackupService

        return PBSBackupService.sincronizar_todos(usuario_email=usuario_email)

    @staticmethod
    def _sincronizar_truenas(usuario_email, storage=None):
        from app.infraestrutura.truenas_backup_service import TrueNASBackupService

        return TrueNASBackupService.sincronizar(periodo_horas=24, storage=storage)

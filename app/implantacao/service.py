import json
from datetime import date
from datetime import timedelta

from app.core.email import EmailService
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.parceiros.service import ParceiroService
from app.repositories.contrato_repository import ContratoRepository
from app.repositories.implantacao_workflow_repository import ImplantacaoWorkflowRepository


STATUS_IMPLANTACAO = {
    "AGUARDANDO_INICIO": "Aguardando início",
    "EM_PLANEJAMENTO": "Em planejamento",
    "EM_EXECUCAO": "Em execução",
    "EM_VALIDACAO": "Em validação",
    "ENTREGUE": "Entregue",
    "PAUSADA": "Pausada",
    "CANCELADA": "Cancelada",
}

PRIORIDADE_IMPLANTACAO = {
    "BAIXA": "Baixa",
    "NORMAL": "Normal",
    "ALTA": "Alta",
    "CRITICA": "Crítica",
}

STATUS_PROVISIONAMENTO = {
    "NAO_PLANEJADO": "Não planejado",
    "PLANEJADO": "Planejado",
    "AGUARDANDO_EXECUCAO": "Aguardando execução",
    "EXECUTADO": "Executado",
    "BLOQUEADO": "Bloqueado",
}

STATUS_CHECKLIST = {
    "PENDENTE": "Pendente",
    "EM_ANDAMENTO": "Em andamento",
    "CONCLUIDO": "Concluído",
    "BLOQUEADO": "Bloqueado",
    "NAO_APLICAVEL": "Não aplicável",
}
KANBAN_COLUNAS = [
    ("FILA", "Fila"),
    ("CRIACAO_GRUPO", "Criação de Grupo"),
    ("KICKOFF", "Kickoff"),
    ("VPN", "VPN"),
    ("PROVISIONAMENTO_SERVIDORES", "Provisionamento de Servidores"),
    ("PARAMETRIZACAO_SOFTWARE", "Parametrização de Software"),
    ("PARAMETRIZACAO_VR_SOFT", "Parametrização VR Soft"),
    ("PARAMETRIZACAO_LOGUS", "Parametrização Logus"),
    ("PARAMETRIZACAO_DBSCIENCE", "Parametrização DBScience"),
    ("PARAMETRIZACAO_HAARE", "Parametrização Haare"),
    ("PARAMETRIZACAO_TARGET", "Parametrização Target"),
    ("PARAMETRIZACAO_O3_CLOUD", "Parametrização O3 Cloud"),
    ("PARAMETRIZACAO_LJ_SISTEMAS", "Parametrização LJ Sistemas"),
    ("PARAMETRIZACAO_E_GESTORA", "Parametrização E-Gestora"),
    ("HOMOLOGACAO", "Homologação"),
    ("VIRADA", "Virada"),
    ("REVISAO", "Revisão"),
    ("FINALIZADO", "Finalizado"),
    ("CANCELADOS", "Cancelados"),
]
KANBAN_LABELS = dict(KANBAN_COLUNAS)


CHECKLIST_PADRAO = [
    {"ordem": 10, "grupo": "Entrada", "titulo": "Validar contrato encaminhado para projeto", "descricao": "Confirmar contrato, cliente, escopo e encaminhamento para projeto."},
    {"ordem": 20, "grupo": "Entrada", "titulo": "Confirmar dados do cliente", "descricao": "Conferir contatos, CNPJ, responsável técnico e acessos necessários."},
    {"ordem": 30, "grupo": "Planejamento", "titulo": "Revisar escopo técnico", "descricao": "Validar produtos, usuários, recursos e premissas da proposta."},
    {"ordem": 40, "grupo": "Planejamento", "titulo": "Definir cronograma", "descricao": "Registrar datas previstas de início, execução, validação e entrega."},
    {"ordem": 50, "grupo": "Provisionamento", "titulo": "Planejar recursos de infraestrutura", "descricao": "Definir ambiente, cluster, servidores e requisitos antes de provisionar."},
    {"ordem": 60, "grupo": "Provisionamento", "titulo": "Executar provisionamento controlado", "descricao": "Registrar execução e evidências. Integração Proxmox futura deve preservar rastreabilidade."},
    {"ordem": 70, "grupo": "Validação", "titulo": "Validar ambiente com cliente", "descricao": "Confirmar acesso, funcionamento e aceite técnico."},
    {"ordem": 80, "grupo": "Entrega", "titulo": "Formalizar entrega", "descricao": "Registrar conclusão, pendências residuais e transição para operação."},
]


class ImplantacaoService:
    repository = ImplantacaoWorkflowRepository

    @classmethod
    def contexto_form(cls):
        return {
            "executivos": ParceiroExecutivoService.listar_todos_ativos(),
            "parceiros": ParceiroService.listar_todos_ativos(),
        }

    @classmethod
    def listar(cls, pesquisa=None, status=None, responsavel=None, ativo="1", pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        implantacoes = cls.repository.listar(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            ativo=ativo_normalizado,
        )
        return implantacoes, total

    @classmethod
    def kanban(cls):
        cls.sincronizar_contratos_encaminhados()
        colunas = [{"codigo": codigo, "titulo": titulo, "cards": []} for codigo, titulo in KANBAN_COLUNAS]
        por_codigo = {coluna["codigo"]: coluna for coluna in colunas}
        for card in cls.repository.listar_kanban():
            etapa = card.get("etapa_kanban") or "FILA"
            if etapa not in por_codigo:
                etapa = "FILA"
            por_codigo[etapa]["cards"].append(card)
        return colunas

    @classmethod
    def sincronizar_contratos_encaminhados(cls):
        criadas = []
        for contrato in cls.repository.listar_contratos_elegiveis():
            if cls.repository.buscar_por_contrato_id(contrato.get("id")):
                continue
            implantacao_id = cls.criar({"contrato_id": contrato.get("id"), "etapa_kanban": "FILA"})
            criadas.append(implantacao_id)
        return criadas

    @classmethod
    def mover_kanban(cls, implantacao_id, etapa_kanban):
        if etapa_kanban not in KANBAN_LABELS:
            raise ValueError("Etapa do Kanban inválida.")
        implantacao = cls.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        etapa_anterior = implantacao.get("etapa_kanban") or "FILA"
        if etapa_anterior == etapa_kanban:
            return {"alterado": False, "email": None}
        cls.repository.atualizar_etapa_kanban(implantacao_id, etapa_kanban)
        atualizada = cls.buscar_por_id(implantacao_id)
        email = cls._notificar_movimento_kanban(atualizada, etapa_anterior, etapa_kanban)
        cls._registrar_historico(
            implantacao_id,
            tipo="ETAPA",
            comentario=f"Etapa alterada de {KANBAN_LABELS.get(etapa_anterior, etapa_anterior)} para {KANBAN_LABELS.get(etapa_kanban, etapa_kanban)}.",
            etapa_anterior=etapa_anterior,
            etapa_nova=etapa_kanban,
            email=email,
        )
        return {"alterado": True, "email": email}

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar_por_id(cls, implantacao_id):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            return None
        implantacao["checklist"] = cls.repository.listar_checklist(implantacao_id)
        implantacao["historico"] = cls.repository.listar_historico(implantacao_id)
        implantacao["emails_adicionais_lista"] = cls._parse_emails(implantacao.get("emails_adicionais"))
        return implantacao

    @classmethod
    def listar_contratos_elegiveis(cls):
        return cls.repository.listar_contratos_elegiveis()

    @classmethod
    def buscar_contrato_operacional(cls, contrato_id):
        contrato = cls.repository.buscar_contrato_operacional(contrato_id)
        if not contrato:
            return None
        if not cls._contrato_elegivel(contrato):
            raise ValueError("A visualização operacional está disponível apenas para contratos encaminhados para projeto.")
        return contrato

    @classmethod
    def criar(cls, dados):
        contrato_id = cls._inteiro(dados.get("contrato_id"))
        if not contrato_id:
            raise ValueError("Selecione um contrato encaminhado para projeto para iniciar a implantação.")
        contrato = ContratoRepository.buscar_por_id(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        if not cls._contrato_elegivel(contrato):
            raise ValueError("A implantação só pode iniciar a partir de contrato com status Encaminhado para Projeto.")
        if cls.repository.buscar_por_contrato_id(contrato_id):
            raise ValueError("Este contrato já possui uma implantação ativa.")

        payload = cls._normalizar(dados, contrato=contrato)
        implantacao_id = cls.repository.inserir(payload)
        cls._criar_checklist_padrao(implantacao_id)
        cls.repository.atualizar_percentual(implantacao_id)
        return implantacao_id

    @classmethod
    def atualizar(cls, implantacao_id, dados):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        etapa_anterior = implantacao.get("etapa_kanban") or "FILA"
        payload = cls._normalizar(dados, implantacao=implantacao)
        cls.repository.atualizar(implantacao_id, payload)
        cls.repository.atualizar_percentual(implantacao_id)
        etapa_nova = payload.get("etapa_kanban") or "FILA"
        if etapa_anterior != etapa_nova:
            atualizada = cls.buscar_por_id(implantacao_id)
            email = cls._notificar_movimento_kanban(atualizada, etapa_anterior, etapa_nova)
            cls._registrar_historico(
                implantacao_id,
                tipo="ETAPA",
                comentario=f"Etapa alterada de {KANBAN_LABELS.get(etapa_anterior, etapa_anterior)} para {KANBAN_LABELS.get(etapa_nova, etapa_nova)}.",
                etapa_anterior=etapa_anterior,
                etapa_nova=etapa_nova,
                email=email,
            )


    @classmethod
    def adicionar_comentario(cls, implantacao_id, dados):
        implantacao = cls.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        comentario = (dados.get("comentario") or "").strip()
        if not comentario:
            raise ValueError("Informe um comentário para registrar no histórico.")
        autor = (dados.get("autor") or "").strip() or None
        enviar_email = str(dados.get("enviar_email") or "").lower() in ("1", "true", "on", "sim")
        email = None
        if enviar_email:
            email = cls._notificar_comentario(implantacao, comentario, autor)
        cls._registrar_historico(
            implantacao_id,
            tipo="COMENTARIO",
            comentario=comentario,
            autor=autor,
            email=email,
        )
        return email

    @classmethod
    def editar_comentario(cls, historico_id, dados):
        historico = cls.repository.buscar_historico_por_id(historico_id)
        if not historico:
            raise ValueError("Comentário não encontrado.")
        if historico.get("tipo") != "COMENTARIO":
            raise ValueError("Registros de etapa não podem ser editados.")
        comentario = (dados.get("comentario") or "").strip()
        if not comentario:
            raise ValueError("Informe um comentário para salvar.")
        cls.repository.atualizar_comentario_historico(historico_id, comentario)
        return historico.get("implantacao_id")

    @classmethod
    def excluir_comentario(cls, historico_id):
        historico = cls.repository.buscar_historico_por_id(historico_id)
        if not historico:
            raise ValueError("Comentário não encontrado.")
        if historico.get("tipo") != "COMENTARIO":
            raise ValueError("Registros de etapa não podem ser excluídos.")
        cls.repository.excluir_historico(historico_id)
        return historico.get("implantacao_id")

    @classmethod
    def atualizar_item_checklist(cls, item_id, dados):
        item = cls.repository.buscar_item_checklist(item_id)
        if not item:
            raise ValueError("Item de checklist não encontrado.")
        status = dados.get("status") or "PENDENTE"
        if status not in STATUS_CHECKLIST:
            raise ValueError("Status de checklist inválido.")
        cls.repository.atualizar_item_checklist(item_id, {
            "status": status,
            "responsavel": (dados.get("responsavel") or "").strip() or None,
            "evidencia": (dados.get("evidencia") or "").strip() or None,
        })
        cls.repository.atualizar_percentual(item.get("implantacao_id"))
        return item.get("implantacao_id")

    @classmethod
    def _normalizar(cls, dados, contrato=None, implantacao=None):
        base = contrato or implantacao or {}
        base_status = None if contrato else base.get("status")
        status = dados.get("status") or base_status or "AGUARDANDO_INICIO"
        prioridade = dados.get("prioridade") or base.get("prioridade") or "NORMAL"
        provisionamento_status = dados.get("provisionamento_status") or base.get("provisionamento_status") or "NAO_PLANEJADO"
        etapa_kanban = dados.get("etapa_kanban") or base.get("etapa_kanban") or "FILA"
        if status not in STATUS_IMPLANTACAO:
            raise ValueError("Status de implantação inválido.")
        if prioridade not in PRIORIDADE_IMPLANTACAO:
            raise ValueError("Prioridade de implantação inválida.")
        if provisionamento_status not in STATUS_PROVISIONAMENTO:
            raise ValueError("Status de provisionamento inválido.")
        if etapa_kanban not in KANBAN_LABELS:
            raise ValueError("Etapa do Kanban inválida.")

        titulo = (dados.get("titulo") or base.get("titulo") or "").strip()
        if not titulo:
            cliente_nome = base.get("cliente_nome") or "Cliente"
            contrato_numero = base.get("numero") or base.get("contrato_numero") or base.get("id")
            titulo = f"Implantação - {cliente_nome} - Contrato {contrato_numero}"

        data_prevista_inicio = dados.get("data_prevista_inicio") or base.get("data_prevista_inicio") or None
        data_prevista_entrega = dados.get("data_prevista_entrega") or base.get("data_prevista_entrega") or None
        if contrato and not data_prevista_inicio:
            data_prevista_inicio = cls._data_inicio_padrao()
        if contrato and not data_prevista_entrega:
            data_prevista_entrega = cls._data_entrega_padrao(data_prevista_inicio)

        return {
            "contrato_id": base.get("id") if contrato else base.get("contrato_id"),
            "cliente_id": base.get("cliente_id"),
            "proposta_id": base.get("proposta_id"),
            "executivo_id": cls._inteiro(dados.get("executivo_id")) if "executivo_id" in dados else base.get("executivo_id"),
            "parceiro_id": cls._inteiro(dados.get("parceiro_id")) if "parceiro_id" in dados else base.get("parceiro_id"),
            "titulo": titulo,
            "status": status,
            "etapa_kanban": etapa_kanban,
            "prioridade": prioridade,
            "responsavel": (dados.get("responsavel") or base.get("responsavel") or "").strip() or None,
            "implantador_nome": (dados.get("implantador_nome") or base.get("implantador_nome") or "").strip() or None,
            "implantador_email": (dados.get("implantador_email") or base.get("implantador_email") or "").strip().lower() or None,
            "emails_adicionais": cls._normalizar_emails_texto(dados.get("emails_adicionais") if "emails_adicionais" in dados else base.get("emails_adicionais")),
            "data_prevista_inicio": data_prevista_inicio,
            "data_prevista_entrega": data_prevista_entrega,
            "data_inicio": dados.get("data_inicio") or base.get("data_inicio") or None,
            "data_entrega": dados.get("data_entrega") or base.get("data_entrega") or None,
            "observacoes": (dados.get("observacoes") or base.get("observacoes") or "").strip() or None,
            "provisionamento_status": provisionamento_status,
            "provisionamento_notas": (dados.get("provisionamento_notas") or base.get("provisionamento_notas") or "").strip() or None,
        }

    @classmethod
    def _criar_checklist_padrao(cls, implantacao_id):
        for item in CHECKLIST_PADRAO:
            cls.repository.inserir_item_checklist(implantacao_id, item)

    @classmethod
    def _contrato_elegivel(cls, contrato):
        return contrato.get("status") == "ENCAMINHADO_PROJETO"

    @staticmethod
    def _data_inicio_padrao():
        return (date.today() + timedelta(days=7)).isoformat()

    @staticmethod
    def _data_entrega_padrao(data_inicio):
        if hasattr(data_inicio, "isoformat"):
            inicio = data_inicio
        else:
            inicio = date.fromisoformat(str(data_inicio))
        return (inicio + timedelta(days=30)).isoformat()


    @classmethod
    def _notificar_comentario(cls, implantacao, comentario, autor=None):
        assunto = f"Comentário na implantação - {implantacao.get('cliente_nome') or implantacao.get('titulo') or implantacao.get('id')}"
        corpo = "\n".join([
            f"Projeto: {implantacao.get('titulo') or '-'}",
            f"Cliente: {implantacao.get('cliente_nome') or '-'}",
            f"Contrato: {implantacao.get('contrato_numero') or implantacao.get('contrato_id') or '-'}",
            f"Etapa atual: {KANBAN_LABELS.get(implantacao.get('etapa_kanban'), implantacao.get('etapa_kanban') or '-')}",
            f"Autor: {autor or '-'}",
            "",
            comentario,
        ])
        return EmailService.enviar(assunto, corpo, cls._destinatarios_implantacao(implantacao))

    @classmethod
    def _registrar_historico(cls, implantacao_id, tipo, comentario, etapa_anterior=None, etapa_nova=None, autor=None, email=None):
        cls.repository.inserir_historico({
            "implantacao_id": implantacao_id,
            "tipo": tipo,
            "etapa_anterior": etapa_anterior,
            "etapa_nova": etapa_nova,
            "autor": autor,
            "comentario": comentario,
            "email_enviado": bool(email and email.get("enviado")),
            "email_resultado": json.dumps(email, ensure_ascii=False) if email else None,
        })

    @classmethod
    def _destinatarios_implantacao(cls, implantacao):
        destinatarios = [
            implantacao.get("implantador_email"),
            implantacao.get("executivo_email"),
            implantacao.get("parceiro_email"),
            implantacao.get("contato_email"),
            implantacao.get("cliente_email"),
        ]
        destinatarios.extend(cls._parse_emails(implantacao.get("emails_adicionais")))
        return destinatarios

    @staticmethod
    def _normalizar_emails_texto(valor):
        emails = ImplantacaoService._parse_emails(valor)
        return "\n".join(emails) if emails else None

    @staticmethod
    def _parse_emails(valor):
        if not valor:
            return []
        texto = str(valor).replace(",", "\n").replace(";", "\n").replace(" ", "\n")
        emails = []
        vistos = set()
        for item in texto.splitlines():
            email = item.strip().lower()
            if not email or "@" not in email or email in vistos:
                continue
            vistos.add(email)
            emails.append(email)
        return emails

    @classmethod
    def _notificar_movimento_kanban(cls, implantacao, etapa_anterior, etapa_nova):
        destinatarios = cls._destinatarios_implantacao(implantacao)
        assunto = f"Implantação movida para {KANBAN_LABELS.get(etapa_nova, etapa_nova)}"
        corpo = "\n".join([
            f"Projeto: {implantacao.get('titulo') or '-'}",
            f"Cliente: {implantacao.get('cliente_nome') or '-'}",
            f"Contrato: {implantacao.get('contrato_numero') or implantacao.get('contrato_id') or '-'}",
            f"Etapa anterior: {KANBAN_LABELS.get(etapa_anterior, etapa_anterior)}",
            f"Nova etapa: {KANBAN_LABELS.get(etapa_nova, etapa_nova)}",
            f"Implantador: {implantacao.get('implantador_nome') or implantacao.get('responsavel') or '-'}",
        ])
        return EmailService.enviar(assunto, corpo, destinatarios)

    @staticmethod
    def _normalizar_ativo(valor):
        if valor == "todos":
            return None
        if str(valor) == "0":
            return 0
        return 1

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

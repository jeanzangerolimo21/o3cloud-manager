import json
from datetime import date
from datetime import timedelta

from app.core.email import EmailService
from app.core.logging_config import get_logger
from app.core.storage import StorageService
from app.ambientes.implantador_service import ImplantadorService
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.parceiros.service import ParceiroService
from app.repositories.contrato_repository import ContratoRepository
from app.financeiro.inadimplencias_service import InadimplenciaService
from app.repositories.implantacao_workflow_repository import ImplantacaoWorkflowRepository


application_logger = get_logger("application")

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

CHECKLIST_MODELOS = {
    "PADRAO": {
        "nome": "Implantação padrão",
        "itens": CHECKLIST_PADRAO,
    },
    "O3WEB": {
        "nome": "Licenças O3Web",
        "itens": CHECKLIST_PADRAO + [
            {"ordem": 90, "grupo": "O3Web", "titulo": "Validar licença O3Web", "descricao": "Confirmar ID da licença, URL, validade e vínculo com o cliente."},
            {"ordem": 100, "grupo": "O3Web", "titulo": "Registrar credenciais no cofre", "descricao": "Salvar acessos operacionais vinculados à licença, quando aplicável."},
        ],
    },
    "INFRA": {
        "nome": "Infraestrutura e VPN",
        "itens": CHECKLIST_PADRAO + [
            {"ordem": 90, "grupo": "Rede", "titulo": "Reservar faixa de rede", "descricao": "Definir rede, firewall WAN/LAN, PVE e range de portas."},
            {"ordem": 100, "grupo": "VPN", "titulo": "Validar VPN com cliente", "descricao": "Registrar evidência de conectividade e acessos liberados."},
            {"ordem": 110, "grupo": "Provisionamento", "titulo": "Conferir recursos provisionados", "descricao": "Validar CPU, memória, disco, backup e monitoramento planejado."},
        ],
    },
}


class ImplantacaoService:
    repository = ImplantacaoWorkflowRepository

    @classmethod
    def contexto_form(cls):
        return {
            "executivos": ParceiroExecutivoService.listar_todos_ativos(),
            "parceiros": ParceiroService.listar_todos_ativos(),
            "implantadores": ImplantadorService.listar_para_select(),
        }

    @classmethod
    def listar(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo="1", agrupamento="principais", pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        agrupamento = cls._normalizar_agrupamento(agrupamento)
        implantacoes = cls.repository.listar(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            prazo=prazo,
            ativo=ativo_normalizado,
            agrupamento=agrupamento,
            limit=limit,
            offset=offset,
        )
        pendencias = InadimplenciaService.clientes_com_pendencia([item.get("cliente_id") for item in implantacoes])
        for item in implantacoes:
            item["pendencia_financeira"] = bool(pendencias.get(item.get("cliente_id")))

        total = cls.repository.total(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            prazo=prazo,
            ativo=ativo_normalizado,
            agrupamento=agrupamento,
        )
        return implantacoes, total

    @classmethod
    def kanban_colunas(cls, ativo=1):
        try:
            colunas = cls.repository.listar_colunas_kanban(ativo=ativo)
        except Exception:
            if ativo in (None, 1):
                return [{"codigo": codigo, "titulo": titulo, "ordem": (idx + 1) * 10, "ativo": 1, "sistema": 1, "total_cards": 0} for idx, (codigo, titulo) in enumerate(KANBAN_COLUNAS)]
            return []
        return colunas

    @classmethod
    def kanban_labels(cls):
        return {coluna.get("codigo"): coluna.get("titulo") for coluna in cls.kanban_colunas(ativo=None)} or KANBAN_LABELS

    @classmethod
    def kanban_options(cls):
        return [(coluna.get("codigo"), coluna.get("titulo")) for coluna in cls.kanban_colunas(ativo=1)] or KANBAN_COLUNAS

    @classmethod
    def kanban(cls):
        cls.sincronizar_contratos_encaminhados()
        colunas_config = cls.kanban_colunas(ativo=1)
        colunas = [{"codigo": coluna.get("codigo"), "titulo": coluna.get("titulo"), "cards": []} for coluna in colunas_config]
        por_codigo = {coluna["codigo"]: coluna for coluna in colunas}
        for card in cls.repository.listar_kanban():
            etapa = card.get("etapa_kanban") or "FILA"
            if etapa not in por_codigo:
                etapa = "FILA"
            por_codigo.setdefault(etapa, {"codigo": etapa, "titulo": cls.kanban_labels().get(etapa, etapa), "cards": []})["cards"].append(card)
        return colunas


    @classmethod
    def criar_coluna_kanban(cls, dados):
        payload = cls._normalizar_coluna_kanban(dados, nova=True)
        if cls.repository.buscar_coluna_kanban_por_codigo(payload.get("codigo")):
            raise ValueError("Já existe uma coluna do Kanban com este código.")
        return cls.repository.inserir_coluna_kanban(payload)

    @classmethod
    def atualizar_coluna_kanban(cls, coluna_id, dados):
        coluna = cls.repository.buscar_coluna_kanban(coluna_id)
        if not coluna:
            raise ValueError("Coluna do Kanban não encontrada.")
        payload = cls._normalizar_coluna_kanban(dados, coluna=coluna)
        if coluna.get("codigo") in ("FILA", "FINALIZADO", "CANCELADOS") and not payload.get("ativo"):
            raise ValueError("Esta coluna é essencial para o fluxo e não pode ser inativada.")
        if not payload.get("ativo") and cls.repository.contar_cards_por_coluna_kanban(coluna.get("codigo")):
            raise ValueError("Não é possível inativar uma coluna com implantações ativas.")
        cls.repository.atualizar_coluna_kanban(coluna_id, payload)

    @staticmethod
    def _normalizar_coluna_kanban(dados, nova=False, coluna=None):
        titulo = (dados.get("titulo") or "").strip()
        if not titulo:
            raise ValueError("Informe o título da coluna.")
        codigo = (dados.get("codigo") or (coluna or {}).get("codigo") or titulo).strip().upper()
        codigo = "_".join("".join(ch if ch.isalnum() else " " for ch in codigo).split())
        if not codigo:
            raise ValueError("Informe um código válido para a coluna.")
        ordem = ImplantacaoService._inteiro(dados.get("ordem")) or (coluna or {}).get("ordem") or 10
        ativo_valores = dados.getlist("ativo") if hasattr(dados, "getlist") else [dados.get("ativo", "1")]
        ativo = str((ativo_valores or ["0"])[-1]).lower() in ("1", "true", "on", "sim")
        return {"codigo": codigo, "titulo": titulo, "ordem": ordem, "ativo": ativo}

    @classmethod
    def sincronizar_contratos_encaminhados(cls):
        cls.repository.desativar_por_contratos_omie_inativos()
        cls.repository.desativar_duplicadas_por_cliente()

        criadas = []
        for contrato in cls.repository.listar_contratos_elegiveis():
            if cls.repository.buscar_por_contrato_id(contrato.get("id")):
                continue
            if cls.repository.buscar_por_cliente_id(contrato.get("cliente_id")):
                continue
            implantacao_id = cls.criar({"contrato_id": contrato.get("id"), "etapa_kanban": "FILA"})
            criadas.append(implantacao_id)
        return criadas

    @classmethod
    def mover_kanban(cls, implantacao_id, etapa_kanban):
        labels = cls.kanban_labels()
        if etapa_kanban not in labels:
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
        email_financeiro = cls._notificar_financeiro_implantacao_finalizada_segura(atualizada) if etapa_kanban == "FINALIZADO" else None
        if email_financeiro:
            cls._log_envio_financeiro(implantacao_id, email_financeiro, origem="kanban_finalizado")
        comentario = f"Etapa alterada de {labels.get(etapa_anterior, etapa_anterior)} para {labels.get(etapa_kanban, etapa_kanban)}."
        if email_financeiro:
            comentario += " Financeiro notificado para faturamento."
        cls._registrar_historico(
            implantacao_id,
            tipo="ETAPA",
            comentario=comentario,
            etapa_anterior=etapa_anterior,
            etapa_nova=etapa_kanban,
            email={"enviado": bool((email or {}).get("enviado") or (email_financeiro or {}).get("enviado")), "movimento": email, "financeiro": email_financeiro},
        )
        return {"alterado": True, "email": email, "email_financeiro": email_financeiro}

    @classmethod
    def reenviar_notificacao_financeiro(cls, implantacao_id, autor=None):
        implantacao = cls.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        if implantacao.get("etapa_kanban") != "FINALIZADO":
            raise ValueError("A notificação financeira só pode ser reenviada para implantações finalizadas.")

        resultado = cls._notificar_financeiro_implantacao_finalizada_segura(implantacao)
        cls._log_envio_financeiro(implantacao_id, resultado, origem="reenvio_manual")
        comentario = "Notificação financeira reenviada manualmente para contas@o3cloud.com.br."
        if not resultado.get("enviado"):
            motivo = resultado.get("motivo") or "falha_envio"
            comentario = f"{comentario} Resultado: não enviado ({motivo})."
        cls._registrar_historico(
            implantacao_id,
            tipo="EMAIL_FINANCEIRO",
            comentario=comentario,
            autor=autor,
            email={
                "enviado": bool(resultado.get("enviado")),
                "financeiro": resultado,
                "forcado": True,
            },
        )
        return resultado

    @classmethod
    def dashboard(cls, pesquisa=None, status=None, responsavel=None, prazo=None, ativo="1", agrupamento="principais"):
        return cls.repository.dashboard(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            prazo=prazo,
            ativo=cls._normalizar_ativo(ativo),
            agrupamento=cls._normalizar_agrupamento(agrupamento),
        )

    @classmethod
    def listar_principais_para_vinculo(cls):
        return cls.repository.listar_principais_para_vinculo()

    @classmethod
    def vincular_card(cls, implantacao_id, implantacao_principal_id, autor=None):
        implantacao_id = cls._inteiro(implantacao_id)
        implantacao_principal_id = cls._inteiro(implantacao_principal_id)
        if not implantacao_id or not implantacao_principal_id:
            raise ValueError("Selecione o card de implantação principal.")
        if implantacao_id == implantacao_principal_id:
            raise ValueError("O card não pode ser vinculado a ele mesmo.")
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        principal = cls.repository.buscar_por_id(implantacao_principal_id)
        if not implantacao or not principal:
            raise ValueError("Implantação não encontrada.")
        if principal.get("implantacao_principal_id"):
            raise ValueError("Selecione um card principal, não um card já vinculado a outro.")
        if implantacao.get("implantacao_principal_id") == implantacao_principal_id:
            return principal
        cls.repository.vincular_card(implantacao_id, implantacao_principal_id)
        comentario = f"Card vinculado à implantação principal #{implantacao_principal_id} - {principal.get('titulo')}."
        cls._registrar_historico(implantacao_id, tipo="VINCULO", comentario=comentario, autor=autor)
        cls._registrar_historico(
            implantacao_principal_id,
            tipo="VINCULO",
            comentario=f"Card #{implantacao_id} - {implantacao.get('titulo')} vinculado a esta implantação principal.",
            autor=autor,
        )
        return principal

    @classmethod
    def desvincular_card(cls, implantacao_id, autor=None):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        implantacao_principal_id = implantacao.get("implantacao_principal_id")
        if not implantacao_principal_id:
            raise ValueError("Este card não está vinculado a outro card.")
        cls.repository.desvincular_card(implantacao_id)
        cls._registrar_historico(implantacao_id, tipo="VINCULO", comentario=f"Card desvinculado da implantação principal #{implantacao_principal_id}.", autor=autor)
        cls._registrar_historico(implantacao_principal_id, tipo="VINCULO", comentario=f"Card #{implantacao_id} - {implantacao.get('titulo')} desvinculado desta implantação principal.", autor=autor)
        return implantacao_principal_id


    @classmethod
    def rastreabilidade_por_proposta(cls, proposta_id):
        return cls._normalizar_rastreabilidade(cls.repository.rastreabilidade_por_proposta(proposta_id))

    @classmethod
    def rastreabilidade_por_contrato(cls, contrato_id):
        return cls._normalizar_rastreabilidade(cls.repository.rastreabilidade_por_contrato(contrato_id))

    @classmethod
    def rastreabilidade_por_implantacao(cls, implantacao_id):
        return cls._normalizar_rastreabilidade(cls.repository.rastreabilidade_por_implantacao(implantacao_id))

    @classmethod
    def buscar_por_id(cls, implantacao_id):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            return None
        implantacao["checklist"] = cls.repository.listar_checklist(implantacao_id)
        implantacao["historico"] = cls._historico_com_anexos(implantacao_id)
        implantacao["vinculadas"] = cls.repository.listar_vinculadas(implantacao_id)
        implantacao["emails_adicionais_lista"] = cls._parse_emails(implantacao.get("emails_adicionais"))
        return implantacao

    @classmethod
    def diagnostico_pre_beta(cls, implantacao):
        itens = []

        def adicionar(tipo, titulo, detalhe, icone):
            itens.append({
                "tipo": tipo,
                "titulo": titulo,
                "detalhe": detalhe,
                "icone": icone,
                "classe": {
                    "ok": "success",
                    "fluxo": "secondary",
                    "pendencia": "warning",
                    "erro": "danger",
                }.get(tipo, "secondary"),
            })

        if implantacao.get("proposta_id"):
            adicionar("ok", "Proposta vinculada", "Implantacao tem origem comercial rastreavel por proposta.", "bi-link-45deg")
        else:
            adicionar("fluxo", "Contrato direto", "Fluxo valido para implantacao quando o contrato nao nasceu de proposta no sistema.", "bi-signpost-2")

        if implantacao.get("responsavel") or implantacao.get("implantador_nome"):
            adicionar("ok", "Responsavel definido", "Projeto possui responsavel ou implantador para acompanhamento assistido.", "bi-person-check")
        else:
            adicionar("pendencia", "Responsavel pendente", "Definir responsavel ou implantador antes da validacao Beta com Operacoes.", "bi-person-exclamation")

        if implantacao.get("data_prevista_entrega"):
            adicionar("ok", "Prazo registrado", "Data prevista de entrega permite priorizacao operacional.", "bi-calendar-check")
        elif implantacao.get("status") not in ("ENTREGUE", "CANCELADA"):
            adicionar("pendencia", "Prazo pendente", "Registrar entrega prevista para separar fila planejada de pendencia real.", "bi-calendar-event")

        checklist = implantacao.get("checklist") or []
        obrigatorios = [item for item in checklist if item.get("obrigatorio")]
        obrigatorios_pendentes = [
            item for item in obrigatorios
            if item.get("status") not in ("CONCLUIDO", "NAO_APLICAVEL")
        ]
        if checklist and not obrigatorios_pendentes:
            adicionar("ok", "Checklist sem bloqueio obrigatorio", "Itens obrigatorios estao concluidos ou marcados como nao aplicaveis.", "bi-ui-checks")
        elif checklist:
            adicionar("pendencia", "Checklist obrigatorio pendente", f"{len(obrigatorios_pendentes)} item(ns) obrigatorio(s) ainda exigem validacao.", "bi-list-check")
        else:
            adicionar("pendencia", "Checklist nao gerado", "Aplicar um modelo de checklist antes da validacao assistida.", "bi-ui-checks-grid")

        if implantacao.get("provisionamento_status") in ("EXECUTADO", "PLANEJADO", "AGUARDANDO_EXECUCAO"):
            adicionar("ok", "Provisionamento registrado", "Status tecnico esta definido para acompanhamento sem automacao destrutiva.", "bi-hdd-rack")
        else:
            adicionar("pendencia", "Provisionamento nao planejado", "Registrar planejamento tecnico quando houver escopo de infraestrutura.", "bi-hdd-stack")

        if implantacao.get("cliente_email") or implantacao.get("contato_email") or implantacao.get("emails_adicionais"):
            adicionar("ok", "Contatos para comunicacao", "Ha pelo menos um email disponivel para alinhamentos e historico.", "bi-envelope-check")
        else:
            adicionar("pendencia", "Email de comunicacao pendente", "Completar email do cliente, contato ou envolvidos antes da Beta assistida.", "bi-envelope-exclamation")

        if implantacao.get("status") == "ENTREGUE" and (implantacao.get("percentual_conclusao") or 0) < 100:
            adicionar("erro", "Entrega sem checklist completo", "Implantacao entregue deve ter checklist consistente com a conclusao operacional.", "bi-exclamation-octagon")

        return itens

    @classmethod
    def buscar_por_contrato_id(cls, contrato_id):
        return cls.repository.buscar_por_contrato_id(contrato_id)

    @classmethod
    def iniciar_por_contrato(cls, contrato_id):
        existente = cls.repository.buscar_por_contrato_id(contrato_id)
        if existente:
            return existente.get("id"), False
        return cls.criar({"contrato_id": contrato_id, "etapa_kanban": "FILA"}), True

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
        if cls.repository.buscar_por_cliente_id(contrato.get("cliente_id")):
            raise ValueError("Este cliente já possui uma implantação ativa.")
        InadimplenciaService.validar_operacao_cliente(contrato.get("cliente_id"))

        payload = cls._normalizar(dados, contrato=contrato)
        implantacao_id = cls.repository.inserir(payload)
        cls._criar_checklist_padrao(implantacao_id)
        cls.repository.atualizar_percentual(implantacao_id)
        return implantacao_id

    @classmethod
    def excluir(cls, implantacao_id):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        cls.repository.excluir(implantacao_id)

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
            labels = cls.kanban_labels()
            cls._registrar_historico(
                implantacao_id,
                tipo="ETAPA",
                comentario=f"Etapa alterada de {labels.get(etapa_anterior, etapa_anterior)} para {labels.get(etapa_nova, etapa_nova)}.",
                etapa_anterior=etapa_anterior,
                etapa_nova=etapa_nova,
                email=email,
            )


    @classmethod
    def adicionar_comentario(cls, implantacao_id, dados, arquivos=None):
        implantacao = cls.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        comentario = (dados.get("comentario") or "").strip()
        if not comentario:
            raise ValueError("Informe um comentário para registrar no histórico.")
        autor = (dados.get("autor") or "").strip() or None
        enviar_email = str(dados.get("enviar_email") or "").lower() in ("1", "true", "on", "sim")
        anexar_no_email = enviar_email and str(dados.get("anexar_arquivos_email") or "").lower() in ("1", "true", "on", "sim")
        arquivos = arquivos or []
        cls._validar_anexos_comentario(arquivos)
        historico_id = cls._registrar_historico(
            implantacao_id,
            tipo="COMENTARIO",
            comentario=comentario,
            autor=autor,
            email=None,
        )
        anexos_salvos = cls._salvar_anexos_comentario(implantacao_id, historico_id, arquivos or [])
        email = None
        if enviar_email:
            email = cls._notificar_comentario(implantacao, comentario, autor, anexos_salvos if anexar_no_email else [])
            cls.repository.atualizar_email_historico(
                historico_id,
                bool(email and email.get("enviado")),
                json.dumps(email, ensure_ascii=False) if email else None,
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
        anexos = cls.repository.listar_anexos_por_historico(historico_id)
        cls.repository.excluir_historico(historico_id)
        cls._excluir_arquivos_anexos(anexos)
        return historico.get("implantacao_id")


    @classmethod
    def checklist_modelos(cls):
        return CHECKLIST_MODELOS

    @classmethod
    def adicionar_item_checklist(cls, implantacao_id, dados):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        item = cls._normalizar_item_checklist(dados)
        if not item.get("ordem"):
            item["ordem"] = cls.repository.proxima_ordem_checklist(implantacao_id)
        item_id = cls.repository.inserir_item_checklist(implantacao_id, item)
        cls.repository.atualizar_percentual(implantacao_id)
        return item_id

    @classmethod
    def aplicar_modelo_checklist(cls, implantacao_id, modelo_codigo):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        modelo = CHECKLIST_MODELOS.get(modelo_codigo)
        if not modelo:
            raise ValueError("Modelo de checklist inválido.")
        existentes = cls.repository.listar_checklist(implantacao_id)
        existentes_chaves = {(item.get("grupo"), item.get("titulo")) for item in existentes}
        criados = 0
        for item in modelo.get("itens", []):
            chave = (item.get("grupo"), item.get("titulo"))
            if chave in existentes_chaves:
                continue
            cls.repository.inserir_item_checklist(implantacao_id, item)
            existentes_chaves.add(chave)
            criados += 1
        cls.repository.atualizar_percentual(implantacao_id)
        return criados

    @classmethod
    def excluir_item_checklist(cls, item_id):
        item = cls.repository.buscar_item_checklist(item_id)
        if not item:
            raise ValueError("Item de checklist não encontrado.")
        implantacao_id = item.get("implantacao_id")
        cls.repository.excluir_item_checklist(item_id)
        cls.repository.atualizar_percentual(implantacao_id)
        return implantacao_id

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
    def atualizar_itens_checklist(cls, implantacao_id, dados):
        implantacao = cls.repository.buscar_por_id(implantacao_id)
        if not implantacao:
            raise ValueError("Implantação não encontrada.")
        item_ids = dados.getlist("item_ids") if hasattr(dados, "getlist") else dados.get("item_ids", [])
        if isinstance(item_ids, (str, int)):
            item_ids = [item_ids]
        item_ids = [cls._inteiro(item_id) for item_id in item_ids]
        item_ids = [item_id for item_id in item_ids if item_id]
        if not item_ids:
            raise ValueError("Selecione ao menos um item do checklist para salvar.")

        atualizados = 0
        for item_id in item_ids:
            item = cls.repository.buscar_item_checklist(item_id)
            if not item or int(item.get("implantacao_id") or 0) != int(implantacao_id):
                raise ValueError("Item de checklist inválido para esta implantação.")
            status = dados.get(f"status_{item_id}") or "PENDENTE"
            if status not in STATUS_CHECKLIST:
                raise ValueError("Status de checklist inválido.")
            cls.repository.atualizar_item_checklist(item_id, {
                "status": status,
                "responsavel": (dados.get(f"responsavel_{item_id}") or "").strip() or None,
                "evidencia": (dados.get(f"evidencia_{item_id}") or "").strip() or None,
            })
            atualizados += 1

        cls.repository.atualizar_percentual(implantacao_id)
        return atualizados

    @staticmethod
    def _normalizar_agrupamento(agrupamento):
        return agrupamento if agrupamento in ("principais", "vinculadas", "todos") else "principais"

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
        if etapa_kanban not in cls.kanban_labels():
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

        responsavel_implantador = cls._implantador_por_id(dados.get("responsavel_implantador_id"))
        implantador = cls._implantador_por_id(dados.get("implantador_id"))
        responsavel_nome = (responsavel_implantador or {}).get("nome") or (dados.get("responsavel") or base.get("responsavel") or "").strip() or None
        implantador_nome = (implantador or {}).get("nome") or (dados.get("implantador_nome") or base.get("implantador_nome") or "").strip() or None
        implantador_email = (implantador or {}).get("email") or (dados.get("implantador_email") or base.get("implantador_email") or "").strip().lower() or None

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
            "responsavel": responsavel_nome,
            "implantador_nome": implantador_nome,
            "implantador_email": implantador_email,
            "emails_adicionais": cls._normalizar_emails_texto(dados.get("emails_adicionais") if "emails_adicionais" in dados else base.get("emails_adicionais")),
            "data_prevista_inicio": data_prevista_inicio,
            "data_prevista_entrega": data_prevista_entrega,
            "data_inicio": dados.get("data_inicio") or base.get("data_inicio") or None,
            "data_entrega": dados.get("data_entrega") or base.get("data_entrega") or None,
            "observacoes": (dados.get("observacoes") or base.get("observacoes") or "").strip() or None,
            "provisionamento_status": provisionamento_status,
            "provisionamento_notas": (dados.get("provisionamento_notas") or base.get("provisionamento_notas") or "").strip() or None,
        }



    @staticmethod
    def _implantador_por_id(implantador_id):
        implantador_id = ImplantacaoService._inteiro(implantador_id)
        if not implantador_id:
            return None
        implantador = ImplantadorService.buscar_por_id(implantador_id)
        if not implantador or not implantador.get("ativo"):
            raise ValueError("Implantador selecionado não encontrado ou inativo.")
        return implantador



    def _normalizar_rastreabilidade(row):
        if not row:
            return None
        return {
            "proposta": {
                "id": row.get("proposta_id"),
                "codigo": row.get("codigo_proposta"),
                "titulo": row.get("proposta_titulo"),
                "cliente_nome": row.get("proposta_cliente_nome"),
                "status": row.get("proposta_status"),
                "clicksign_status": row.get("clicksign_status"),
                "clicksign_document_key": row.get("clicksign_document_key"),
                "clicksign_envelope_id": row.get("clicksign_envelope_id"),
                "clicksign_sent_at": row.get("clicksign_sent_at"),
                "clicksign_signed_at": row.get("clicksign_signed_at"),
                "clicksign_completed_at": row.get("clicksign_completed_at"),
            } if row.get("proposta_id") else None,
            "contrato": {
                "id": row.get("contrato_id"),
                "numero": row.get("contrato_numero"),
                "origem": row.get("contrato_origem"),
                "status": row.get("contrato_status"),
                "codigo_externo": row.get("contrato_codigo_externo"),
                "data_fechamento": row.get("contrato_data_fechamento"),
            } if row.get("contrato_id") else None,
            "implantacao": {
                "id": row.get("implantacao_id"),
                "titulo": row.get("implantacao_titulo"),
                "status": row.get("implantacao_status"),
                "etapa_kanban": row.get("etapa_kanban"),
                "responsavel": row.get("implantacao_responsavel") or row.get("implantador_nome"),
                "data_prevista_entrega": row.get("data_prevista_entrega"),
                "percentual_conclusao": row.get("percentual_conclusao"),
                "total_itens": row.get("total_itens"),
                "total_concluidos": row.get("total_concluidos"),
            } if row.get("implantacao_id") else None,
        }

    @staticmethod
    def _normalizar_item_checklist(dados):
        titulo = (dados.get("titulo") or "").strip()
        if not titulo:
            raise ValueError("Informe o título do item do checklist.")
        grupo = (dados.get("grupo") or "Geral").strip() or "Geral"
        ordem = ImplantacaoService._inteiro(dados.get("ordem"))
        obrigatorio = str(dados.get("obrigatorio") or "1").lower() in ("1", "true", "on", "sim")
        return {
            "ordem": ordem,
            "grupo": grupo,
            "titulo": titulo,
            "descricao": (dados.get("descricao") or "").strip() or None,
            "obrigatorio": obrigatorio,
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
    def _notificar_comentario(cls, implantacao, comentario, autor=None, anexos=None):
        assunto = f"Comentário na implantação - {implantacao.get('cliente_nome') or implantacao.get('titulo') or implantacao.get('id')}"
        corpo = "\n".join([
            f"Projeto: {implantacao.get('titulo') or '-'}",
            f"Cliente: {implantacao.get('cliente_nome') or '-'}",
            f"Contrato: {implantacao.get('contrato_numero') or implantacao.get('contrato_id') or '-'}",
            f"Etapa atual: {cls.kanban_labels().get(implantacao.get('etapa_kanban'), implantacao.get('etapa_kanban') or '-')}",
            f"Autor: {autor or '-'}",
            "",
            comentario,
        ])
        return EmailService.enviar(assunto, corpo, cls._destinatarios_implantacao(implantacao), anexos=anexos or [])

    @classmethod
    def _notificar_financeiro_implantacao_finalizada(cls, implantacao):
        data_conclusao = date.today().strftime("%d/%m/%Y")
        nome_cliente = implantacao.get("cliente_nome") or implantacao.get("titulo") or "-"
        cnpj = implantacao.get("cliente_cnpj") or "-"
        contrato = implantacao.get("contrato_numero") or implantacao.get("contrato_id") or "-"
        if implantacao.get("codigo_proposta"):
            contrato = f"{contrato} / {implantacao.get('codigo_proposta')}"
        implantador = implantacao.get("implantador_nome") or implantacao.get("responsavel") or "Equipe de Implantacao"
        assunto = f"Implantacao concluida para faturamento - {nome_cliente}"
        corpo = "\n".join([
            "Prezados,",
            "",
            f"Informamos que o processo de implantação do cliente {nome_cliente} foi concluído com sucesso nesta data.",
            "",
            "Solicitamos a gentileza de dar andamento ao faturamento do projeto/serviço, conforme as condições comerciais contratadas.",
            "",
            "Dados para Faturamento:",
            "",
            f"Razão Social / Cliente: {nome_cliente}",
            "",
            f"CNPJ/CPF: {cnpj}",
            "",
            f"Nº do Contrato / Proposta(se houver): {contrato}",
            "",
            f"Data de Conclusão da Implantação: {data_conclusao}",
            "",
            "Caso necessitem de qualquer validação adicional sobre os entregáveis desta etapa, ficamos à disposição.",
            "",
            "Atenciosamente,",
            "",
            implantador,
        ])
        return EmailService.enviar(assunto, corpo, ["contas@o3cloud.com.br"])

    @classmethod
    def _notificar_financeiro_implantacao_finalizada_segura(cls, implantacao):
        try:
            return cls._notificar_financeiro_implantacao_finalizada(implantacao)
        except Exception as erro:
            application_logger.exception(
                "Falha ao enviar notificacao financeira de implantacao %s para contas@o3cloud.com.br",
                implantacao.get("id"),
                extra={"operation": "IMPLANTACAO_EMAIL_FINANCEIRO"},
            )
            return {
                "enviado": False,
                "motivo": str(erro)[:500],
                "destinatarios": ["contas@o3cloud.com.br"],
            }

    @staticmethod
    def _log_envio_financeiro(implantacao_id, resultado, origem):
        application_logger.info(
            "Notificacao financeira de implantacao %s para contas@o3cloud.com.br: enviado=%s motivo=%s origem=%s",
            implantacao_id,
            bool(resultado.get("enviado")),
            resultado.get("motivo") or "-",
            origem,
            extra={"operation": "IMPLANTACAO_EMAIL_FINANCEIRO"},
        )

    @classmethod
    def _registrar_historico(cls, implantacao_id, tipo, comentario, etapa_anterior=None, etapa_nova=None, autor=None, email=None):
        return cls.repository.inserir_historico({
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
    def _historico_com_anexos(cls, implantacao_id):
        historico = cls.repository.listar_historico(implantacao_id)
        anexos = cls.repository.listar_anexos_historico(implantacao_id)
        por_historico = {}
        for anexo in anexos:
            por_historico.setdefault(anexo.get("historico_id"), []).append(anexo)
        for item in historico:
            item["anexos"] = por_historico.get(item.get("id"), [])
        return historico

    @classmethod
    def _validar_anexos_comentario(cls, arquivos):
        for arquivo in arquivos:
            StorageService.validar(arquivo)

    @classmethod
    def _salvar_anexos_comentario(cls, implantacao_id, historico_id, arquivos):
        anexos_salvos = []
        for arquivo in arquivos:
            if not arquivo or not arquivo.filename:
                continue
            pasta = f"{StorageService.IMPLANTACOES}/{implantacao_id}/comentarios"
            salvo = StorageService.salvar(arquivo, pasta)
            if not salvo:
                continue
            caminho_relativo = f"{pasta}/{salvo.get('nome')}"
            cls.repository.inserir_anexo_historico({
                "historico_id": historico_id,
                "implantacao_id": implantacao_id,
                "arquivo_original": salvo.get("arquivo_original"),
                "nome_arquivo": salvo.get("nome"),
                "caminho": caminho_relativo,
                "url": salvo.get("url"),
                "mime_type": salvo.get("mime_type"),
                "tamanho": salvo.get("tamanho"),
            })
            anexos_salvos.append({
                "arquivo_original": salvo.get("arquivo_original"),
                "nome": salvo.get("arquivo_original") or salvo.get("nome"),
                "caminho": StorageService.BASE_STORAGE / caminho_relativo,
                "mime_type": salvo.get("mime_type"),
            })
        return anexos_salvos

    @classmethod
    def _excluir_arquivos_anexos(cls, anexos):
        for anexo in anexos:
            caminho = anexo.get("caminho") or ""
            partes = caminho.split("/")
            if len(partes) < 2:
                continue
            pasta = "/".join(partes[:-1])
            nome = partes[-1]
            StorageService.excluir(pasta, nome)

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
        labels = cls.kanban_labels()
        assunto = f"Implantação movida para {labels.get(etapa_nova, etapa_nova)}"
        corpo = "\n".join([
            f"Projeto: {implantacao.get('titulo') or '-'}",
            f"Cliente: {implantacao.get('cliente_nome') or '-'}",
            f"Contrato: {implantacao.get('contrato_numero') or implantacao.get('contrato_id') or '-'}",
            f"Etapa anterior: {labels.get(etapa_anterior, etapa_anterior)}",
            f"Nova etapa: {labels.get(etapa_nova, etapa_nova)}",
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

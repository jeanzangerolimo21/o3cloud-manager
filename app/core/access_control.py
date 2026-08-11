from flask import abort, flash, has_request_context, redirect, request, session, url_for

from app.core.logging_config import get_logger

ADMINISTRATIVO_GESTOR = "ADMINISTRATIVO_GESTOR"
ADMINISTRATIVO_COLABORADOR = "ADMINISTRATIVO_COLABORADOR"
PERFIS_COM_EXCLUSAO = frozenset(("ADMIN", "DIRETORIA", "ADMINISTRATIVO_GESTOR"))
MARCADORES_ENDPOINT_EXCLUSAO = ("excluir", "desativar", "inativar", "remover")

from app.repositories.auth_repository import AuthRepository


security_logger = get_logger("security")


MENU_PERMISSOES = (
    {"grupo": "Geral", "key": "visao_geral", "label": "Visao Geral"},
    {"grupo": "Administrativo", "key": "administrativo", "label": "Administrativo"},
    {"grupo": "Financeiro", "key": "dashboard_executivo", "label": "Dashboard Executivo"},
    {"grupo": "Financeiro", "key": "produtos_clientes", "label": "Produtos por Cliente"},
    {"grupo": "Financeiro", "key": "faturamento", "label": "Faturamento"},
    {"grupo": "Financeiro", "key": "inadimplentes", "label": "Inadimplentes"},
    {"grupo": "Financeiro", "key": "contratos", "label": "Contratos"},
    {"grupo": "Cadastros", "key": "ambientes", "label": "Ambientes"},
    {"grupo": "Cadastros", "key": "implantadores", "label": "Implantadores"},
    {"grupo": "Cadastros", "key": "clientes", "label": "Clientes"},
    {"grupo": "Cadastros", "key": "catalogo_comercial", "label": "Catalogo Comercial"},
    {"grupo": "Cadastros", "key": "tabela_precos", "label": "Tabela de Precos"},
    {"grupo": "Cadastros", "key": "recursos_servidor", "label": "Recursos de Servidor"},
    {"grupo": "Cadastros", "key": "produtos_fechados", "label": "Produtos Fechados"},
    {"grupo": "Cadastros", "key": "dimensionamento_tecnico", "label": "Dimensionamento Tecnico"},
    {"grupo": "Cadastros", "key": "regras_campanhas", "label": "Regras Campanhas"},
    {"grupo": "CRM Comercial", "key": "leads", "label": "Leads"},
    {"grupo": "CRM Comercial", "key": "eventos_participante_manual", "label": "Eventos - Participante Manual"},
    {"grupo": "CRM Comercial", "key": "contatos", "label": "Contatos"},
    {"grupo": "CRM Comercial", "key": "oportunidades", "label": "Oportunidades"},
    {"grupo": "CRM Comercial", "key": "pipeline_comercial", "label": "Pipeline Comercial"},
    {"grupo": "CRM Comercial", "key": "propostas", "label": "Propostas"},
    {"grupo": "CRM Comercial", "key": "dashboard_comercial", "label": "Dashboard Comercial"},
    {"grupo": "CRM Comercial", "key": "parceiros", "label": "Parceiros"},
    {"grupo": "Operacoes", "key": "implantacao", "label": "Implantacao"},
    {"grupo": "Operacoes", "key": "kanban_implantacao", "label": "Kanban Implantacao"},
    {"grupo": "Operacoes", "key": "licencas_o3web", "label": "Licencas O3Web"},
    {"grupo": "Operacoes", "key": "faixas_rede", "label": "Faixas de Rede"},
    {"grupo": "Operacoes", "key": "cofre_senhas", "label": "Cofre de Senhas"},
    {"grupo": "Infraestrutura", "key": "clusters", "label": "Clusters"},
    {"grupo": "Infraestrutura", "key": "nodes", "label": "Nodes"},
    {"grupo": "Infraestrutura", "key": "maquinas_virtuais", "label": "Maquinas Virtuais"},
    {"grupo": "Infraestrutura", "key": "containers", "label": "Containers"},
    {"grupo": "Infraestrutura", "key": "backups_pbs", "label": "Backups PBS"},
    {"grupo": "Infraestrutura", "key": "monitoramento_zabbix", "label": "Monitoramento Zabbix"},
    {"grupo": "Infraestrutura", "key": "backup_nas", "label": "Backup NAS"},
    {"grupo": "Relatorios", "key": "relatorios", "label": "Relatorios"},
    {"grupo": "Operacoes", "key": "base_conhecimento", "label": "Base de Conhecimento"},
    {"grupo": "Configuracoes", "key": "usuarios_acessos", "label": "Usuarios e Acessos"},
    {"grupo": "Configuracoes", "key": "servicos_email", "label": "Servicos de Email"},
    {"grupo": "Configuracoes", "key": "integracoes_negocio", "label": "Integracoes de Negocio"},
    {"grupo": "Configuracoes", "key": "integracoes_tecnicas", "label": "Integracoes Tecnicas"},
    {"grupo": "Configuracoes", "key": "auditoria", "label": "Auditoria"},
    {"grupo": "Configuracoes", "key": "cache_sistema", "label": "Retencao de Cache"},
    {"grupo": "Configuracoes", "key": "sincronismos_agendados", "label": "Automacoes de Sincronismo"},
    {"grupo": "Configuracoes", "key": "backups_sistema", "label": "Backups do Sistema"},
    {"grupo": "Configuracoes", "key": "atualizacoes_sistema", "label": "Atualizacoes do Sistema"},
)

TODAS_PERMISSOES = frozenset(item["key"] for item in MENU_PERMISSOES)

ENDPOINT_PERMISSOES = {
    "administrativo": "administrativo",
    "financeiro.dashboard": "visao_geral",
    "financeiro.dashboard_executivo": "dashboard_executivo",
    "financeiro.produtos_clientes": "produtos_clientes",
    "financeiro.faturamentos": "faturamento",
    "financeiro.exportar_modelo_faturamentos_csv": "faturamento",
    "financeiro.inadimplentes": "inadimplentes",
    "financeiro.nova_inadimplencia": "inadimplentes",
    "financeiro.pesquisar_contratos_inadimplencia": "inadimplentes",
    "financeiro.visualizar_inadimplencia": "inadimplentes",
    "financeiro.liberar_inadimplencia": "inadimplentes",
    "financeiro.excluir_inadimplencia": "inadimplentes",
    "contratos": "contratos",
    "ambientes.index": "ambientes",
    "ambientes.novo": "ambientes",
    "ambientes.visualizar": "ambientes",
    "ambientes.editar": "ambientes",
    "ambientes.excluir": "ambientes",
    "ambientes.implantadores": "implantadores",
    "ambientes.novo_implantador": "implantadores",
    "ambientes.editar_implantador": "implantadores",
    "ambientes.excluir_implantador": "implantadores",
    "clientes": "clientes",
    "catalogo.index": "catalogo_comercial",
    "catalogo.importar_catalogo": "catalogo_comercial",
    "catalogo.listar_categorias": "catalogo_comercial",
    "catalogo.nova_categoria": "catalogo_comercial",
    "catalogo.visualizar_categoria": "catalogo_comercial",
    "catalogo.editar_categoria": "catalogo_comercial",
    "catalogo.desativar_categoria": "catalogo_comercial",
    "catalogo.listar_modelos": "catalogo_comercial",
    "catalogo.novo_modelo": "catalogo_comercial",
    "catalogo.visualizar_modelo": "catalogo_comercial",
    "catalogo.editar_modelo": "catalogo_comercial",
    "catalogo.desativar_modelo": "catalogo_comercial",
    "catalogo.listar_faixas": "tabela_precos",
    "catalogo.nova_faixa": "tabela_precos",
    "catalogo.visualizar_faixa": "tabela_precos",
    "catalogo.editar_faixa": "tabela_precos",
    "catalogo.desativar_faixa": "tabela_precos",
    "catalogo.listar_tabela_precos": "tabela_precos",
    "catalogo.exportar_tabela_precos_csv": "tabela_precos",
    "catalogo.listar_recursos_servidor": "recursos_servidor",
    "catalogo.novo_recurso_servidor": "recursos_servidor",
    "catalogo.visualizar_recurso_servidor": "recursos_servidor",
    "catalogo.editar_recurso_servidor": "recursos_servidor",
    "catalogo.desativar_recurso_servidor": "recursos_servidor",
    "catalogo.listar_produtos": "produtos_fechados",
    "catalogo.novo_produto": "produtos_fechados",
    "catalogo.visualizar_produto": "produtos_fechados",
    "catalogo.editar_produto": "produtos_fechados",
    "catalogo.desativar_produto": "produtos_fechados",
    "catalogo.custos_produtos": "produtos_fechados",
    "catalogo.exportar_custos_produtos_csv": "produtos_fechados",
    "catalogo.listar_servidores": "dimensionamento_tecnico",
    "catalogo.novo_servidor": "dimensionamento_tecnico",
    "catalogo.visualizar_servidor": "dimensionamento_tecnico",
    "catalogo.editar_servidor": "dimensionamento_tecnico",
    "catalogo.desativar_servidor": "dimensionamento_tecnico",
    "leads": "leads",
    "eventos": "leads",
    "eventos.novo_participante": "eventos_participante_manual",
    "contatos": "contatos",
    "oportunidades": "oportunidades",
    "pipeline": "pipeline_comercial",
    "propostas.dashboard": "dashboard_comercial",
    "propostas": "propostas",
    "parceiros": "parceiros",
    "regras_campanhas": "regras_campanhas",
    "implantacao.index": "implantacao",
    "implantacao.novo": "implantacao",
    "implantacao.visualizar": "implantacao",
    "implantacao.editar": "implantacao",
    "implantacao.visualizar_contrato_operacional": "implantacao",
    "implantacao.adicionar_comentario": "implantacao",
    "implantacao.editar_comentario": "implantacao",
    "implantacao.excluir_comentario": "implantacao",
    "implantacao.adicionar_item_checklist": "implantacao",
    "implantacao.aplicar_modelo_checklist": "implantacao",
    "implantacao.atualizar_checklist": "implantacao",
    "implantacao.excluir_item_checklist": "implantacao",
    "implantacao.kanban": "kanban_implantacao",
    "implantacao.kanban_colunas": "kanban_implantacao",
    "implantacao.criar_coluna_kanban": "kanban_implantacao",
    "implantacao.editar_coluna_kanban": "kanban_implantacao",
    "implantacao.mover_kanban": "kanban_implantacao",
    "implantacao.licencas_o3web": "licencas_o3web",
    "implantacao.importar_licencas_o3web": "licencas_o3web",
    "implantacao.nova_licenca_o3web": "licencas_o3web",
    "implantacao.editar_licenca_o3web": "licencas_o3web",
    "implantacao.excluir_licenca_o3web": "licencas_o3web",
    "implantacao.faixas_rede": "faixas_rede",
    "implantacao.nova_faixa_rede": "faixas_rede",
    "implantacao.editar_faixa_rede": "faixas_rede",
    "implantacao.excluir_faixa_rede": "faixas_rede",
    "implantacao.cofre_senhas": "cofre_senhas",
    "implantacao.nova_pasta_cofre": "cofre_senhas",
    "implantacao.editar_pasta_cofre": "cofre_senhas",
    "implantacao.excluir_pasta_cofre": "cofre_senhas",
    "implantacao.nova_senha_cofre": "cofre_senhas",
    "implantacao.editar_senha_cofre": "cofre_senhas",
    "implantacao.revelar_senha_cofre": "cofre_senhas",
    "implantacao.compartilhar_senha_cofre": "cofre_senhas",
    "implantacao.excluir_senha_cofre": "cofre_senhas",
    "implantacao.integracoes_config": "integracoes_tecnicas",
    "implantacao.integracoes_negocio": "integracoes_negocio",
    "implantacao.integracoes_tecnicas": "integracoes_tecnicas",
    "implantacao.nova_integracao_config": "integracoes_tecnicas",
    "implantacao.editar_integracao_config": "integracoes_tecnicas",
    "implantacao.testar_integracao_config": "integracoes_tecnicas",
    "implantacao.revelar_integracao_config_segredo": "integracoes_tecnicas",
    "implantacao.revelar_integracao_ambiente_segredo": "integracoes_tecnicas",
    "implantacao.excluir_integracao_config": "integracoes_tecnicas",
    "infraestrutura.clusters": "clusters",
    "infraestrutura.sincronizar_cluster_proxmox": "clusters",
    "infraestrutura.nodes": "nodes",
    "infraestrutura.sincronizar_proxmox": "nodes",
    "infraestrutura.vincular_cliente_proxmox": "maquinas_virtuais",
    "infraestrutura.maquinas_virtuais": "maquinas_virtuais",
    "infraestrutura.containers": "containers",
    "infraestrutura.backups_pbs": "backups_pbs",
    "infraestrutura.novo_escopo_pbs": "backups_pbs",
    "infraestrutura.editar_escopo_pbs": "backups_pbs",
    "infraestrutura.excluir_escopo_pbs": "backups_pbs",
    "infraestrutura.sincronizar_pbs": "backups_pbs",
    "infraestrutura.sincronizar_todos_pbs": "backups_pbs",
    "infraestrutura.atualizar_politicas_pbs": "backups_pbs",
    "infraestrutura.monitoramento_zabbix": "monitoramento_zabbix",
    "infraestrutura.sincronizar_zabbix": "monitoramento_zabbix",
    "infraestrutura.backup_nas": "backup_nas",
    "conhecimentos": "base_conhecimento",
    "infraestrutura.sincronizar_backup_nas": "backup_nas",
    "relatorios": "relatorios",
    "configuracoes.usuarios_index": "usuarios_acessos",
    "configuracoes.usuarios_novo": "usuarios_acessos",
    "configuracoes.usuarios_editar": "usuarios_acessos",
    "configuracoes.usuarios_convidar": "usuarios_acessos",
    "configuracoes.usuarios_remover": "usuarios_acessos",
    "configuracoes.usuarios_grupo_mapa_novo": "usuarios_acessos",
    "configuracoes.usuarios_grupo_mapa_editar": "usuarios_acessos",
    "configuracoes.usuarios_grupo_mapa_excluir": "usuarios_acessos",
    "configuracoes.usuarios_perfil_novo": "usuarios_acessos",
    "configuracoes.usuarios_perfil_editar": "usuarios_acessos",
    "configuracoes.usuarios_provedor_novo": "usuarios_acessos",
    "configuracoes.usuarios_provedor_editar": "usuarios_acessos",
    "configuracoes.usuarios_provedor_testar": "usuarios_acessos",
    "configuracoes.email_index": "servicos_email",
    "configuracoes.email_novo": "servicos_email",
    "configuracoes.email_editar": "servicos_email",
    "configuracoes.email_testar": "servicos_email",
    "configuracoes.auditoria": "auditoria",
    "configuracoes.cache_index": "cache_sistema",
    "configuracoes.cache_retencao": "cache_sistema",
    "configuracoes.cache_limpar": "cache_sistema",
    "configuracoes.sincronismos_index": "sincronismos_agendados",
    "configuracoes.sincronismos_salvar": "sincronismos_agendados",
    "configuracoes.sincronismos_executar": "sincronismos_agendados",
    "configuracoes.backups_index": "backups_sistema",
    "configuracoes.backups_salvar": "backups_sistema",
    "configuracoes.backups_executar": "backups_sistema",
    "configuracoes.backups_download": "backups_sistema",
    "configuracoes.atualizacoes_index": "atualizacoes_sistema",
}

PUBLIC_ENDPOINTS = {"static", "storage", "autenticacao.login", "autenticacao.logout", "configuracoes.usuarios_aceitar_convite", "implantacao.acessar_compartilhamento_senha"}

WRITE_ENDPOINT_MARKERS = (
    "adicionar",
    "aplicar",
    "atualizar",
    "convidar",
    "criar",
    "custos",
    "desativar",
    "editar",
    "excluir",
    "importar",
    "iniciar",
    "ler",
    "mover",
    "nova",
    "novo",
    "revelar",
    "sincronizar",
    "testar",
    "upload",
)

def init_access_control(app):
    @app.before_request
    def verificar_permissao():
        if request.endpoint in PUBLIC_ENDPOINTS:
            return None
        if not _email_sessao():
            return redirect(url_for("autenticacao.login", next=request.full_path if request.query_string else request.path))

        permissao = permissao_endpoint(request.endpoint)
        if not permissao:
            return None
        if pode_acessar_endpoint(permissao, request.endpoint, request.method):
            return None

        security_logger.warning("Access denied", extra={"operation": "ACESSO_NEGADO"})
        if request.method == "GET":
            flash("Acesso não autorizado para este perfil.", "warning")
            return redirect(url_for("financeiro.dashboard"))
        abort(403)

    @app.context_processor
    def contexto_acesso():
        return {
            "pode_acessar": pode_acessar,
            "pode_editar": pode_editar,
            "pode_excluir": pode_excluir,
            "permissao_endpoint": permissao_endpoint,
            "usuario_pode_ver_valores": usuario_pode_ver_valores,
            "usuario_logado": usuario_logado,
            "notificacoes_pendentes": notificacoes_pendentes(),
            "demandas_administrativas_atrasadas": demandas_administrativas_atrasadas(),
        }


def permissao_endpoint(endpoint):
    if not endpoint:
        return None
    if endpoint in ENDPOINT_PERMISSOES:
        return ENDPOINT_PERMISSOES[endpoint]
    prefixo = endpoint.split(".", 1)[0]
    return ENDPOINT_PERMISSOES.get(prefixo)


def pode_acessar(menu_key):
    return menu_key in permissoes_niveis_usuario_atual()


def pode_editar(menu_key):
    return permissoes_niveis_usuario_atual().get(menu_key) == "EDICAO"


def pode_acessar_endpoint(menu_key, endpoint, method):
    if menu_key == "administrativo" and session.get("usuario_perfil") == ADMINISTRATIVO_COLABORADOR:
        bloqueados = ("administrativo.nova_demanda", "administrativo.editar", "administrativo.cancelar", "administrativo.reagendar", "administrativo.editar_comentario", "administrativo.excluir_comentario")
        permitidos_especiais = ("administrativo.comentar", "administrativo.ler_notificacao", "administrativo.ler_todas_notificacoes")
        if endpoint in bloqueados:
            return False
        if endpoint in permitidos_especiais:
            return True
    if endpoint_requer_exclusao(endpoint) and not pode_excluir():
        return False
    nivel = permissoes_niveis_usuario_atual().get(menu_key)
    if not nivel:
        return False
    if nivel == "EDICAO":
        return True
    return not endpoint_requer_edicao(endpoint, method)


def endpoint_requer_exclusao(endpoint):
    nome = (endpoint or "").split(".")[-1].lower()
    return any(marcador in nome for marcador in MARCADORES_ENDPOINT_EXCLUSAO)


def pode_excluir():
    return session.get("usuario_perfil") in PERFIS_COM_EXCLUSAO


def endpoint_requer_edicao(endpoint, method):
    if method not in ("GET", "HEAD", "OPTIONS"):
        return True
    nome = (endpoint or "").split(".")[-1]
    return any(marker in nome for marker in WRITE_ENDPOINT_MARKERS)


def usuario_logado():
    email = _email_sessao()
    return _buscar_usuario(email) if email else None


def usuario_pode_ver_valores():
    email = _email_sessao()
    if not email:
        return True
    usuario = _buscar_usuario(email)
    if not usuario or usuario.get("perfil_codigo") == "ADMIN":
        return True
    return bool(usuario.get("mostrar_valores"))


def permissoes_usuario_atual():
    return frozenset(permissoes_niveis_usuario_atual().keys())


def permissoes_niveis_usuario_atual():
    email = _email_sessao()
    if not email:
        return {menu_key: "EDICAO" for menu_key in TODAS_PERMISSOES}

    usuario = _buscar_usuario(email)
    if not usuario or usuario.get("status") != "ATIVO":
        return {}
    if usuario.get("perfil_codigo") == "ADMIN":
        return {menu_key: "EDICAO" for menu_key in TODAS_PERMISSOES}
    return {
        item["menu_key"]: item.get("nivel_acesso") or "LEITURA"
        for item in AuthRepository.listar_menu_keys_usuario(email)
    }


def notificacoes_pendentes():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return 0
    try:
        from app.repositories.administrativo_repository import AdministrativoRepository
        return AdministrativoRepository.contar_notificacoes(usuario_id)
    except Exception:
        return 0


def demandas_administrativas_atrasadas():
    if not has_request_context():
        return 0
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return 0
    try:
        from app.repositories.administrativo_repository import AdministrativoRepository
        return AdministrativoRepository.contar_demandas_atrasadas(usuario_id)
    except Exception:
        return 0


def _email_sessao():
    for chave in ("usuario_email", "email", "user_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return str(valor).strip().lower()
    return None


def _buscar_usuario(email):
    return AuthRepository.buscar_usuario_por_email_com_perfil(email)

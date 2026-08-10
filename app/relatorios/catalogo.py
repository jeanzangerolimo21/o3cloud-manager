from dataclasses import dataclass


TIPO_TEXTO = "TEXTO"
TIPO_INTEIRO = "INTEIRO"
TIPO_DECIMAL = "DECIMAL"
TIPO_MOEDA = "MOEDA"
TIPO_DATA = "DATA"
TIPO_DATETIME = "DATETIME"
TIPO_BOOLEAN = "BOOLEAN"
TIPO_STATUS = "STATUS"
TIPO_PERCENTUAL = "PERCENTUAL"
TIPOS_NUMERICOS = {TIPO_INTEIRO, TIPO_DECIMAL, TIPO_MOEDA}


@dataclass(frozen=True)
class CampoRelatorio:
    codigo: str
    nome: str
    expressao: str
    tipo: str = TIPO_TEXTO
    filtravel: bool = True
    agrupavel: bool = True
    ordenavel: bool = True
    agregavel: bool = False
    formato: str | None = None
    sensibilidade: str = "NORMAL"

    def as_dict(self):
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "tipo": self.tipo,
            "filtravel": self.filtravel,
            "agrupavel": self.agrupavel,
            "ordenavel": self.ordenavel,
            "agregavel": self.agregavel,
            "formato": self.formato,
            "sensibilidade": self.sensibilidade,
        }


@dataclass(frozen=True)
class FonteRelatorio:
    codigo: str
    nome: str
    descricao: str
    from_sql: str
    campos: tuple[CampoRelatorio, ...]
    where_base: str = ""

    def campo(self, codigo):
        return next((campo for campo in self.campos if campo.codigo == codigo), None)

    def as_dict(self):
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "campos": [campo.as_dict() for campo in self.campos],
        }


FONTES = {
    "clientes": FonteRelatorio(
        "clientes",
        "Clientes",
        "Base de clientes cadastrados.",
        "FROM clientes cli",
        (
            CampoRelatorio("id", "ID", "cli.id", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("nome_fantasia", "Nome fantasia", "cli.nome_fantasia"),
            CampoRelatorio("razao_social", "Razao social", "cli.razao_social"),
            CampoRelatorio("cnpj", "CNPJ", "cli.cnpj", formato="cnpj"),
            CampoRelatorio("cidade", "Cidade", "cli.cidade"),
            CampoRelatorio("estado", "Estado", "cli.estado"),
            CampoRelatorio("origem", "Origem", "cli.origem", TIPO_STATUS),
            CampoRelatorio("ativo", "Ativo", "cli.ativo", TIPO_BOOLEAN),
            CampoRelatorio("criado_em", "Criado em", "cli.created_at", TIPO_DATETIME, agrupavel=False),
        ),
        "cli.ativo = 1",
    ),
    "contratos": FonteRelatorio(
        "contratos",
        "Contratos",
        "Contratos comerciais e recorrencia.",
        """
        FROM contratos c
        INNER JOIN clientes cli ON cli.id = c.cliente_id
        LEFT JOIN parceiros_executivos exec ON exec.id = c.executivo_id
        LEFT JOIN parceiros p ON p.id = c.parceiro_id
        """,
        (
            CampoRelatorio("numero", "Numero", "c.numero"),
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("cnpj", "CNPJ", "cli.cnpj", formato="cnpj"),
            CampoRelatorio("status", "Status", "c.status", TIPO_STATUS),
            CampoRelatorio("origem", "Origem", "c.origem", TIPO_STATUS),
            CampoRelatorio("valor_mensal", "Valor mensal", "COALESCE(NULLIF(c.valor_promocional, 0), c.valor_mensal, 0)", TIPO_MOEDA, agregavel=True, formato="moeda"),
            CampoRelatorio("valor_setup", "Setup", "COALESCE(c.valor_setup, 0) + COALESCE(c.valor_projeto, 0)", TIPO_MOEDA, agregavel=True, formato="moeda"),
            CampoRelatorio("usuarios", "Usuarios", "c.quantidade_usuarios", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("inicio_vigencia", "Inicio vigencia", "c.inicio_vigencia", TIPO_DATA, agrupavel=False),
            CampoRelatorio("fim_vigencia", "Fim vigencia", "c.fim_vigencia", TIPO_DATA, agrupavel=False),
            CampoRelatorio("data_fechamento", "Data fechamento", "c.data_fechamento", TIPO_DATA, agrupavel=False),
            CampoRelatorio("executivo", "Executivo", "exec.nome"),
            CampoRelatorio("parceiro", "Parceiro", "p.nome"),
        ),
        "c.ativo = 1",
    ),
    "inadimplencias": FonteRelatorio(
        "inadimplencias",
        "Inadimplencias",
        "Pendencias financeiras por contrato.",
        """
        FROM financeiro_inadimplencias fi
        INNER JOIN contratos c ON c.id = fi.contrato_id
        INNER JOIN clientes cli ON cli.id = c.cliente_id
        """,
        (
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("cnpj", "CNPJ", "cli.cnpj", formato="cnpj"),
            CampoRelatorio("contrato", "Contrato", "c.numero"),
            CampoRelatorio("status", "Status", "fi.status", TIPO_STATUS),
            CampoRelatorio("motivo", "Motivo", "fi.motivo"),
            CampoRelatorio("bloqueado_em", "Bloqueado em", "fi.bloqueado_em", TIPO_DATETIME, agrupavel=False),
            CampoRelatorio("liberado_em", "Liberado em", "fi.liberado_em", TIPO_DATETIME, agrupavel=False),
            CampoRelatorio("tipo_liberacao", "Tipo liberacao", "fi.tipo_liberacao", TIPO_STATUS),
        ),
        "fi.ativo = 1",
    ),
    "faturamentos": FonteRelatorio(
        "faturamentos",
        "Faturamentos",
        "Faturamentos importados por competencia.",
        """
        FROM faturamentos f
        INNER JOIN contratos c ON c.id = f.contrato_id
        INNER JOIN clientes cli ON cli.id = c.cliente_id
        """,
        (
            CampoRelatorio("competencia", "Competencia", "f.competencia", TIPO_DATA, agrupavel=False),
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("contrato", "Contrato", "c.numero"),
            CampoRelatorio("origem", "Origem", "f.origem", TIPO_STATUS),
            CampoRelatorio("valor_bruto", "Valor bruto", "f.valor_bruto", TIPO_MOEDA, agregavel=True, formato="moeda"),
            CampoRelatorio("valor_comissao", "Comissao", "f.valor_comissao", TIPO_MOEDA, agregavel=True, formato="moeda"),
            CampoRelatorio("valor_liquido", "Valor liquido", "f.valor_liquido", TIPO_MOEDA, agregavel=True, formato="moeda"),
        ),
        "f.ativo = 1",
    ),
    "leads": FonteRelatorio(
        "leads",
        "Leads",
        "Leads do CRM comercial.",
        """
        FROM crm_leads l
        LEFT JOIN parceiros p ON p.id = l.parceiro_id
        LEFT JOIN parceiros_executivos exec ON exec.id = l.executivo_responsavel_id
        """,
        (
            CampoRelatorio("empresa", "Empresa", "l.empresa"),
            CampoRelatorio("contato", "Contato", "l.nome_contato"),
            CampoRelatorio("email", "E-mail", "l.email"),
            CampoRelatorio("telefone", "Telefone", "l.telefone"),
            CampoRelatorio("origem", "Origem", "l.origem", TIPO_STATUS),
            CampoRelatorio("status", "Status", "l.status", TIPO_STATUS),
            CampoRelatorio("cidade", "Cidade", "l.cidade"),
            CampoRelatorio("uf", "UF", "l.uf"),
            CampoRelatorio("parceiro", "Parceiro", "p.nome"),
            CampoRelatorio("executivo", "Executivo", "exec.nome"),
            CampoRelatorio("criado_em", "Criado em", "l.created_at", TIPO_DATETIME, agrupavel=False),
        ),
        "l.ativo = 1",
    ),
    "oportunidades": FonteRelatorio(
        "oportunidades",
        "Oportunidades",
        "Oportunidades comerciais.",
        """
        FROM crm_oportunidades o
        LEFT JOIN clientes cli ON cli.id = o.cliente_id
        LEFT JOIN parceiros p ON p.id = o.parceiro_id
        LEFT JOIN parceiros_executivos exec ON exec.id = o.executivo_responsavel_id
        """,
        (
            CampoRelatorio("titulo", "Titulo", "o.titulo"),
            CampoRelatorio("empresa", "Empresa", "COALESCE(o.empresa, cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("status", "Status", "o.status", TIPO_STATUS),
            CampoRelatorio("valor_estimado", "Valor estimado", "o.valor_estimado", TIPO_MOEDA, agregavel=True, formato="moeda"),
            CampoRelatorio("probabilidade", "Probabilidade", "o.probabilidade", TIPO_PERCENTUAL, agregavel=True),
            CampoRelatorio("usuarios", "Usuarios", "o.quantidade_usuarios", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("parceiro", "Parceiro", "p.nome"),
            CampoRelatorio("executivo", "Executivo", "exec.nome"),
            CampoRelatorio("criado_em", "Criado em", "o.created_at", TIPO_DATETIME, agrupavel=False),
        ),
        "o.ativo = 1",
    ),
    "parceiros": FonteRelatorio(
        "parceiros",
        "Parceiros",
        "Parceiros comerciais.",
        "FROM parceiros p",
        (
            CampoRelatorio("nome", "Nome", "p.nome"),
            CampoRelatorio("cnpj", "CNPJ", "p.cnpj", formato="cnpj"),
            CampoRelatorio("cidade", "Cidade", "p.cidade"),
            CampoRelatorio("estado", "Estado", "p.estado"),
            CampoRelatorio("categoria", "Categoria", "p.categoria", TIPO_STATUS),
            CampoRelatorio("ativo", "Ativo", "p.ativo", TIPO_BOOLEAN),
        ),
        "p.ativo = 1",
    ),
    "implantacoes": FonteRelatorio(
        "implantacoes",
        "Implantacoes",
        "Projetos de implantacao.",
        """
        FROM implantacoes i
        INNER JOIN clientes cli ON cli.id = i.cliente_id
        LEFT JOIN contratos c ON c.id = i.contrato_id
        """,
        (
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("contrato", "Contrato", "c.numero"),
            CampoRelatorio("status", "Status", "i.status", TIPO_STATUS),
            CampoRelatorio("responsavel", "Responsavel", "i.responsavel"),
            CampoRelatorio("percentual", "Percentual", "i.percentual_conclusao", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("prazo", "Prazo", "i.data_prevista_entrega", TIPO_DATA, agrupavel=False),
            CampoRelatorio("entregue_em", "Entregue em", "i.data_entrega", TIPO_DATA, agrupavel=False),
        ),
        "i.ativo = 1",
    ),
    "demandas": FonteRelatorio(
        "demandas",
        "Demandas Administrativas",
        "Demandas e agenda administrativa.",
        """
        FROM administrativo_demandas d
        LEFT JOIN auth_usuarios u ON u.id = d.responsavel_id
        LEFT JOIN administrativo_departamentos dep ON dep.id = d.departamento_id
        """,
        (
            CampoRelatorio("titulo", "Titulo", "d.titulo"),
            CampoRelatorio("categoria", "Categoria", "d.categoria", TIPO_STATUS),
            CampoRelatorio("prioridade", "Prioridade", "d.prioridade", TIPO_STATUS),
            CampoRelatorio("status", "Status", "d.status", TIPO_STATUS),
            CampoRelatorio("responsavel", "Responsavel", "u.nome"),
            CampoRelatorio("departamento", "Departamento", "dep.nome"),
            CampoRelatorio("data_inicial", "Data inicial", "d.data_inicial", TIPO_DATA, agrupavel=False),
            CampoRelatorio("data_limite", "Data limite", "d.data_limite", TIPO_DATA, agrupavel=False),
            CampoRelatorio("concluida_em", "Concluida em", "d.concluida_em", TIPO_DATETIME, agrupavel=False),
        ),
    ),

    "zabbix_alarmes": FonteRelatorio(
        "zabbix_alarmes",
        "Alarmes Zabbix",
        "Alarmes sincronizados no cache local do Zabbix.",
        """
        FROM zabbix_alarm_cache z
        INNER JOIN implantacao_integracoes_config i ON i.id = z.integracao_id
        """,
        (
            CampoRelatorio("integracao", "Integracao", "i.nome"),
            CampoRelatorio("eventid", "Event ID", "z.eventid"),
            CampoRelatorio("data_evento", "Data evento", "z.data_evento", TIPO_DATETIME, agrupavel=False),
            CampoRelatorio("aberto", "Aberto", "z.aberto", TIPO_BOOLEAN),
            CampoRelatorio("status", "Status", "z.status_label", TIPO_STATUS),
            CampoRelatorio("severidade", "Severidade", "z.severidade", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("severidade_label", "Severidade label", "z.severidade_label", TIPO_STATUS),
            CampoRelatorio("host", "Host", "z.host"),
            CampoRelatorio("alarme", "Alarme", "z.nome"),
            CampoRelatorio("reconhecido", "Reconhecido", "z.acknowledged", TIPO_BOOLEAN),
            CampoRelatorio("sincronizado_em", "Sincronizado em", "z.sincronizado_em", TIPO_DATETIME, agrupavel=False),
        ),
    ),
    "pbs_backups": FonteRelatorio(
        "pbs_backups",
        "Backups PBS",
        "Snapshots PBS sincronizados no cache local.",
        """
        FROM pbs_backup_snapshots s
        INNER JOIN implantacao_integracoes_config i ON i.id = s.integracao_id
        LEFT JOIN proxmox_vm_inventory p ON p.id = s.proxmox_inventory_id
        LEFT JOIN clientes cli ON cli.id = p.cliente_id
        """,
        (
            CampoRelatorio("integracao", "Integracao", "i.nome"),
            CampoRelatorio("datastore", "Datastore", "s.datastore"),
            CampoRelatorio("namespace", "Namespace", "s.namespace"),
            CampoRelatorio("tipo_backup", "Tipo backup", "s.backup_type", TIPO_STATUS),
            CampoRelatorio("backup_id", "Backup ID", "s.backup_id"),
            CampoRelatorio("snapshot", "Snapshot", "s.snapshot_name"),
            CampoRelatorio("data_backup", "Data backup", "s.backup_time", TIPO_DATETIME, agrupavel=False),
            CampoRelatorio("tamanho_bytes", "Tamanho bytes", "s.size_bytes", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("protegido", "Protegido", "s.protected", TIPO_BOOLEAN),
            CampoRelatorio("node", "Node", "p.node"),
            CampoRelatorio("vmid", "VMID", "p.vmid", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("recurso", "Recurso", "p.nome"),
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("sincronizado_em", "Sincronizado em", "s.ultimo_sync_em", TIPO_DATETIME, agrupavel=False),
        ),
    ),
    "truenas_backups": FonteRelatorio(
        "truenas_backups",
        "Backups TrueNAS",
        "Status de backups NAS em cache local.",
        """
        FROM truenas_backup_cache t
        INNER JOIN implantacao_integracoes_config i ON i.id = t.integracao_id
        """,
        (
            CampoRelatorio("integracao", "Integracao", "i.nome"),
            CampoRelatorio("cliente", "Cliente", "t.cliente_nome"),
            CampoRelatorio("prefixo", "Prefixo Proxmox", "t.prefixo_proxmox"),
            CampoRelatorio("mountpoint", "Mountpoint", "t.mountpoint"),
            CampoRelatorio("pasta", "Pasta", "t.pasta_path"),
            CampoRelatorio("status", "Status", "t.status", TIPO_STATUS),
            CampoRelatorio("arquivos_recentes", "Arquivos recentes", "t.arquivos_recentes", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("arquivos_total", "Arquivos total", "t.arquivos_total", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("ultimo_arquivo", "Ultimo arquivo", "t.ultimo_arquivo"),
            CampoRelatorio("ultimo_mtime", "Ultima modificacao", "t.ultimo_mtime", TIPO_DATETIME, agrupavel=False),
            CampoRelatorio("sincronizado_em", "Sincronizado em", "t.sincronizado_em", TIPO_DATETIME, agrupavel=False),
        ),
    ),
    "proxmox_recursos": FonteRelatorio(
        "proxmox_recursos",
        "VMs e Containers Proxmox",
        "Inventario local de VMs e containers Proxmox.",
        """
        FROM proxmox_vm_inventory p
        INNER JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
        LEFT JOIN clientes cli ON cli.id = p.cliente_id
        LEFT JOIN contratos c ON c.id = p.contrato_id
        LEFT JOIN implantacoes imp ON imp.id = p.implantacao_id
        """,
        (
            CampoRelatorio("cluster", "Cluster", "i.nome"),
            CampoRelatorio("node", "Node", "p.node"),
            CampoRelatorio("vmid", "VMID", "p.vmid", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("tipo", "Tipo", "p.tipo", TIPO_STATUS),
            CampoRelatorio("nome", "Nome", "p.nome"),
            CampoRelatorio("status", "Status", "p.status", TIPO_STATUS),
            CampoRelatorio("cpu_cores", "CPU cores", "p.cpu_cores", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("memoria_mb", "Memoria MB", "p.memoria_mb", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("disco_gb", "Disco GB", "p.disco_gb", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("discos_qtd", "Discos", "p.discos_qtd", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("interfaces_qtd", "Interfaces", "p.interfaces_qtd", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("cliente", "Cliente", "COALESCE(cli.nome_fantasia, cli.razao_social)"),
            CampoRelatorio("contrato", "Contrato", "c.numero"),
            CampoRelatorio("implantacao", "Implantacao", "imp.titulo"),
            CampoRelatorio("ultimo_sync_em", "Ultimo sync", "p.ultimo_sync_em", TIPO_DATETIME, agrupavel=False),
        ),
        "p.ativo = 1",
    ),
    "proxmox_nodes": FonteRelatorio(
        "proxmox_nodes",
        "Nodes Proxmox",
        "Consumo dos nodes Proxmox no cache local.",
        """
        FROM proxmox_node_inventory n
        INNER JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
        """,
        (
            CampoRelatorio("cluster", "Cluster", "i.nome"),
            CampoRelatorio("node", "Node", "n.node"),
            CampoRelatorio("status", "Status", "n.status", TIPO_STATUS),
            CampoRelatorio("cpu_total", "CPU total", "n.cpu_total", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("cpu_usado_percent", "CPU usado %", "n.cpu_usado_percent", TIPO_PERCENTUAL, agregavel=True),
            CampoRelatorio("memoria_total_mb", "Memoria total MB", "n.memoria_total_mb", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("memoria_usada_mb", "Memoria usada MB", "n.memoria_usada_mb", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("memoria_disponivel_mb", "Memoria disponivel MB", "n.memoria_disponivel_mb", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("disco_total_gb", "Disco total GB", "n.disco_total_gb", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("disco_usado_gb", "Disco usado GB", "n.disco_usado_gb", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("disco_disponivel_gb", "Disco disponivel GB", "n.disco_disponivel_gb", TIPO_DECIMAL, agregavel=True),
            CampoRelatorio("storages_qtd", "Storages", "n.storages_qtd", TIPO_INTEIRO, agregavel=True),
            CampoRelatorio("pve_version", "PVE version", "n.pve_version"),
            CampoRelatorio("ultimo_sync_em", "Ultimo sync", "n.ultimo_sync_em", TIPO_DATETIME, agrupavel=False),
        ),
        "n.ativo = 1",
    ),
}


def listar_fontes():
    return [fonte.as_dict() for fonte in FONTES.values()]


def buscar_fonte(codigo):
    return FONTES.get(codigo)

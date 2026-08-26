import ipaddress

from app.clientes.service import ClienteService
from app.repositories.faixa_rede_repository import FaixaRedeRepository


class FaixaRedeService:
    repository = FaixaRedeRepository

    @classmethod
    def listar(cls, pesquisa=None, ativo="1", pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        faixas = cls.repository.listar(
            pesquisa=pesquisa,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        for faixa in faixas:
            faixa["portas_exibicao"] = cls._portas_exibicao(faixa)
        total = cls.repository.total(pesquisa=pesquisa, ativo=ativo_normalizado)
        return faixas, total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar_por_id(cls, faixa_id):
        faixa = cls.repository.buscar_por_id(faixa_id)
        if faixa:
            faixa["portas_adicionais"] = cls.repository.listar_portas_adicionais(faixa_id)
            faixa["portas_exibicao"] = cls._portas_exibicao(faixa)
        return faixa

    @classmethod
    def criar(cls, dados):
        payload = cls._normalizar(dados)
        if cls.repository.buscar_por_rede(payload["rede"]):
            raise ValueError("Faixa de rede já cadastrada.")
        cls._validar_conflito_portas(payload)
        return cls.repository.inserir(payload)

    @classmethod
    def atualizar(cls, faixa_id, dados):
        if not cls.repository.buscar_por_id(faixa_id):
            raise ValueError("Faixa de rede não encontrada.")
        payload = cls._normalizar(dados)
        existente = cls.repository.buscar_por_rede(payload["rede"])
        if existente and int(existente.get("id")) != int(faixa_id):
            raise ValueError("Faixa de rede já cadastrada em outro registro.")
        cls._validar_conflito_portas(payload, ignorar_id=faixa_id)
        cls.repository.atualizar(faixa_id, payload)

    @classmethod
    def excluir(cls, faixa_id):
        if not cls.repository.buscar_por_id(faixa_id):
            raise ValueError("Faixa de rede não encontrada.")
        cls.repository.excluir(faixa_id)

    @classmethod
    def calcular_proxima(cls, rede_base, quantidade_servidores):
        quantidade = cls._inteiro(quantidade_servidores)
        if quantidade <= 0:
            raise ValueError("Informe a quantidade de servidores.")
        mascara = cls.mascara_por_servidores(quantidade)
        try:
            base = ipaddress.ip_network((rede_base or "").strip(), strict=False)
        except ValueError as erro:
            raise ValueError("Rede base inválida. Use o formato 10.0.0.0/16.") from erro
        if base.version != 4:
            raise ValueError("Informe uma rede IPv4.")
        if mascara < base.prefixlen:
            raise ValueError(f"A rede base /{base.prefixlen} não comporta sub-redes /{mascara}.")

        ocupadas = cls._redes_ocupadas()
        for candidata in base.subnets(new_prefix=mascara):
            if not any(candidata.overlaps(ocupada) for ocupada in ocupadas):
                return cls._sugestao(candidata, quantidade)
        raise ValueError("Nenhuma faixa disponível encontrada dentro da rede base informada.")

    @staticmethod
    def mascara_por_servidores(quantidade_servidores):
        quantidade = int(quantidade_servidores or 0)
        if quantidade <= 5:
            return 29
        if quantidade <= 13:
            return 28
        if quantidade <= 29:
            return 27
        raise ValueError("Projetos acima de 29 servidores exigem uma máscara maior que /27.")

    @classmethod
    def _normalizar(cls, dados):
        quantidade = cls._inteiro(dados.get("quantidade_servidores"))
        if quantidade <= 0:
            raise ValueError("Informe a quantidade de servidores.")
        rede = cls._normalizar_rede(dados.get("rede"))
        mascara = int(str(rede).split("/", 1)[1])
        mascara_recomendada = cls.mascara_por_servidores(quantidade)
        if mascara > mascara_recomendada:
            raise ValueError(f"{quantidade} servidor(es) exigem máscara /{mascara_recomendada} ou maior.")
        cliente_id = cls._inteiro(dados.get("cliente_id"))
        cliente_nome = (dados.get("cliente_nome") or "").strip()
        cliente_cnpj = cls._texto(dados.get("cliente_cnpj"))
        if cliente_id:
            cliente = ClienteService.buscar_por_id(cliente_id)
            if not cliente:
                raise ValueError("Cliente selecionado não encontrado.")
            cliente_nome = (cliente.get("nome_fantasia") or cliente.get("razao_social") or "").strip()
            cliente_cnpj = cliente.get("cnpj")
        if not cliente_nome:
            raise ValueError("Cliente é obrigatório.")
        porta_inicio, porta_fim, portas = cls._normalizar_portas(
            dados.get("porta_inicio"),
            dados.get("porta_fim"),
            dados.get("portas"),
        )
        portas_adicionais = cls._normalizar_portas_adicionais(dados)
        ranges_portas = [
            item
            for item in [{"porta_inicio": porta_inicio, "porta_fim": porta_fim, "portas": portas}]
            if item.get("porta_inicio") and item.get("porta_fim")
        ]
        cls._validar_ranges_sem_sobreposicao(ranges_portas + portas_adicionais)
        return {
            "rede": rede,
            "mascara": mascara,
            "quantidade_servidores": quantidade,
            "fw_wan": cls._texto(dados.get("fw_wan")),
            "fw_lan": cls._texto(dados.get("fw_lan")),
            "cliente_id": cliente_id,
            "cliente_nome": cliente_nome,
            "cliente_cnpj": cliente_cnpj,
            "vpn": cls._texto(dados.get("vpn")),
            "porta_inicio": porta_inicio,
            "porta_fim": porta_fim,
            "portas": portas,
            "portas_adicionais": portas_adicionais,
            "pve": cls._texto_longo(dados.get("pve")),
            "observacoes": cls._texto_longo(dados.get("observacoes")),
            "ativo": 1 if str(dados.get("ativo", "1")) != "0" else 0,
        }

    @classmethod
    def _validar_conflito_portas(cls, dados, ignorar_id=None):
        ranges = [
            item for item in [{
                "porta_inicio": dados.get("porta_inicio"),
                "porta_fim": dados.get("porta_fim"),
            }] if item.get("porta_inicio") and item.get("porta_fim")
        ]
        ranges.extend(dados.get("portas_adicionais") or [])
        for item in ranges:
            conflito = cls.repository.buscar_conflito_portas(
                dados.get("fw_wan"),
                item.get("porta_inicio"),
                item.get("porta_fim"),
                ignorar_id=ignorar_id,
            )
            if not conflito:
                continue
            conflito_range = ""
            if conflito.get("conflito_inicio") and conflito.get("conflito_fim"):
                conflito_range = f" ({conflito.get('conflito_inicio')}-{conflito.get('conflito_fim')})"
            raise ValueError(
                "Range de portas "
                f"{item.get('porta_inicio')}-{item.get('porta_fim')} conflita com a faixa "
                f"{conflito.get('rede')}{conflito_range} do cliente {conflito.get('cliente_nome')} "
                f"no mesmo FW - WAN ({conflito.get('fw_wan')})."
            )

    @classmethod
    def _normalizar_portas_adicionais(cls, dados):
        inicios = (
            dados.getlist("porta_inicio_adicional")
            if hasattr(dados, "getlist")
            else dados.get("porta_inicio_adicional", [])
        )
        fins = (
            dados.getlist("porta_fim_adicional")
            if hasattr(dados, "getlist")
            else dados.get("porta_fim_adicional", [])
        )
        if isinstance(inicios, (str, int)):
            inicios = [inicios]
        if isinstance(fins, (str, int)):
            fins = [fins]
        total = max(len(inicios), len(fins))
        portas = []
        for index in range(total):
            inicio_raw = inicios[index] if index < len(inicios) else None
            fim_raw = fins[index] if index < len(fins) else None
            if not str(inicio_raw or "").strip() and not str(fim_raw or "").strip():
                continue
            inicio, fim, texto = cls._normalizar_portas(inicio_raw, fim_raw)
            portas.append({"porta_inicio": inicio, "porta_fim": fim, "portas": texto})
        return portas

    @staticmethod
    def _validar_ranges_sem_sobreposicao(ranges):
        ordenados = sorted(ranges, key=lambda item: (item.get("porta_inicio") or 0, item.get("porta_fim") or 0))
        anterior = None
        for atual in ordenados:
            if anterior and atual.get("porta_inicio") <= anterior.get("porta_fim"):
                raise ValueError(
                    "Ranges de portas informados se sobrepõem: "
                    f"{anterior.get('porta_inicio')}-{anterior.get('porta_fim')} e "
                    f"{atual.get('porta_inicio')}-{atual.get('porta_fim')}."
                )
            anterior = atual

    @staticmethod
    def _portas_exibicao(faixa):
        portas = []
        if faixa.get("porta_inicio") and faixa.get("porta_fim"):
            portas.append(f"{faixa.get('porta_inicio')}-{faixa.get('porta_fim')}")
        elif faixa.get("portas"):
            portas.append(str(faixa.get("portas")))
        adicionais = faixa.get("portas_adicionais") or []
        if isinstance(adicionais, str):
            portas.extend(item.strip() for item in adicionais.split(",") if item.strip())
        else:
            portas.extend(item.get("portas") for item in adicionais if item.get("portas"))
        return ", ".join(portas) if portas else None

    @classmethod
    def _normalizar_portas(cls, porta_inicio, porta_fim, portas_legado=None):
        inicio = cls._inteiro(porta_inicio)
        fim = cls._inteiro(porta_fim)
        if not inicio and not fim and portas_legado:
            texto = str(portas_legado).strip()
            if "-" in texto:
                partes = texto.split("-", 1)
                inicio = cls._inteiro(partes[0])
                fim = cls._inteiro(partes[1])
        if not inicio and not fim:
            return None, None, None
        if not inicio or not fim:
            raise ValueError("Informe porta inicial e porta final.")
        if inicio < 1 or fim < 1 or inicio > 65535 or fim > 65535:
            raise ValueError("Portas devem estar entre 1 e 65535.")
        if inicio > fim:
            raise ValueError("Porta inicial não pode ser maior que a porta final.")
        return inicio, fim, f"{inicio}-{fim}"

    @classmethod
    def _redes_ocupadas(cls):
        redes = []
        for item in cls.repository.listar_ativas():
            try:
                redes.append(ipaddress.ip_network(item.get("rede"), strict=False))
            except ValueError:
                continue
        return redes

    @classmethod
    def _sugestao(cls, rede, quantidade):
        hosts = [str(host) for host in rede.hosts()]
        pve_hosts = hosts[1:1 + quantidade]
        return {
            "rede": str(rede),
            "mascara": rede.prefixlen,
            "quantidade_servidores": quantidade,
            "fw_wan": "",
            "fw_lan": hosts[0] if hosts else "",
            "pve": ", ".join(pve_hosts),
            "hosts_uteis": max(rede.num_addresses - 2, 0),
        }

    @staticmethod
    def _normalizar_rede(valor):
        texto = (valor or "").strip()
        if not texto:
            raise ValueError("Rede é obrigatória.")
        try:
            rede = ipaddress.ip_network(texto, strict=False)
        except ValueError as erro:
            raise ValueError("Rede inválida. Use o formato 10.0.0.0/29.") from erro
        if rede.version != 4:
            raise ValueError("Informe uma rede IPv4.")
        if rede.prefixlen not in (27, 28, 29):
            raise ValueError("A máscara da faixa deve ser /29, /28 ou /27.")
        return str(rede)

    @staticmethod
    def _normalizar_ativo(valor):
        if valor == "todos":
            return None
        try:
            return 1 if int(valor) == 1 else 0
        except (TypeError, ValueError):
            return 1

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _texto_longo(valor):
        return (valor or "").strip() or None

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import current_app, has_app_context, url_for

from app.core.email import EmailService
from app.repositories.reajuste_contrato_repository import ReajusteContratoRepository


class ReajusteContratoService:
    repository = ReajusteContratoRepository
    STATUS_LABELS = {
        "A_VENCER": "A vencer",
        "REAJUSTE_PROXIMO": "Reajuste proximo",
        "REAJUSTE_VENCIDO": "Reajuste vencido",
        "REAJUSTADO": "Alteracao detectada",
        "SEM_REAJUSTE_DETECTADO": "Sem reajuste detectado",
        "SEM_BASE_COMPARACAO": "Sem base de comparacao",
        "SEM_DATA_VIGENCIA": "Sem data de vigencia",
        "IGNORADO": "Ignorado",
    }
    STATUS_CLASSES = {
        "A_VENCER": "secondary",
        "REAJUSTE_PROXIMO": "warning",
        "REAJUSTE_VENCIDO": "danger",
        "REAJUSTADO": "success",
        "SEM_REAJUSTE_DETECTADO": "danger",
        "SEM_BASE_COMPARACAO": "info",
        "SEM_DATA_VIGENCIA": "secondary",
        "IGNORADO": "secondary",
    }
    STATUS_ALERTA = {"REAJUSTE_PROXIMO", "REAJUSTE_VENCIDO"}

    @classmethod
    def filtros(cls, dados):
        return {
            "q": cls._texto(dados.get("q")),
            "status": cls._texto(dados.get("status")),
            "vendedor": cls._texto(dados.get("vendedor")),
            "situacao": cls._texto(dados.get("situacao")),
            "ano": cls._inteiro(dados.get("ano")),
            "janela": cls._inteiro(dados.get("janela")),
        }

    @classmethod
    def contexto(cls, filtros=None, hoje=None):
        filtros = filtros or {}
        hoje = hoje or date.today()
        config = cls.configuracao()
        contratos = cls.repository.listar_contratos_monitoramento(filtros)
        itens = []
        for contrato in contratos:
            item = cls.analisar_contrato(contrato, hoje=hoje, config=config)
            if cls._filtra_item(item, filtros):
                itens.append(item)
        return {
            "itens": itens,
            "resumo": cls.resumo(itens),
            "total_monitorados": cls.repository.total_contratos_monitoramento(),
            "config": config,
            "usuarios": cls.repository.usuarios_disponiveis(),
            "usuarios_configurados": {u["id"] for u in cls.repository.usuarios_notificacao(config.get("id"))},
            "status_labels": cls.STATUS_LABELS,
            "status_classes": cls.STATUS_CLASSES,
        }

    @classmethod
    def detalhe_contrato(cls, contrato, hoje=None):
        if not contrato:
            return {}
        hoje = hoje or date.today()
        item = cls.analisar_contrato(contrato, hoje=hoje, config=cls.configuracao())
        item["historico"] = cls.historico_com_variacao(contrato.get("id"))
        return item

    @classmethod
    def salvar_configuracao(cls, dados, usuario_email="sistema"):
        payload = {
            "alerta_30_dias": cls._flag(dados, "alerta_30_dias"),
            "alerta_15_dias": cls._flag(dados, "alerta_15_dias"),
            "alerta_7_dias": cls._flag(dados, "alerta_7_dias"),
            "enviar_email": cls._flag(dados, "enviar_email"),
            "ativo": cls._flag(dados, "ativo", default=True),
            "updated_by": usuario_email,
        }
        config_id = cls.repository.salvar_configuracao(payload)
        usuario_ids = []
        valores = dados.getlist("usuario_ids") if hasattr(dados, "getlist") else dados.get("usuario_ids", [])
        for valor in valores:
            inteiro = cls._inteiro(valor)
            if inteiro:
                usuario_ids.append(inteiro)
        cls.repository.substituir_usuarios_configuracao(config_id, sorted(set(usuario_ids)))
        return config_id

    @classmethod
    def processar_alertas(cls, usuario_email="sistema", hoje=None):
        hoje = hoje or date.today()
        config = cls.configuracao()
        if not config.get("ativo"):
            return {"criados": 0, "emails": 0, "mensagens": ["Monitoramento de reajustes inativo."]}
        criados = 0
        emails = 0
        mensagens = []
        for contrato in cls.repository.listar_contratos_monitoramento({}, limit=2000):
            cls.registrar_historico_valor_se_necessario(contrato.get("id"), contrato, origem="MONITORAMENTO")
            item = cls.analisar_contrato(contrato, hoje=hoje, config=config)
            antecedencia = cls.antecedencia_alerta(item, config)
            if antecedencia is None:
                continue
            existente = cls.repository.alerta_existente(contrato.get("id"), item.get("proximo_aniversario"), antecedencia)
            if not existente:
                cls.repository.inserir_alerta(contrato.get("id"), item.get("proximo_aniversario"), antecedencia, item.get("situacao"))
                criados += 1
            if config.get("enviar_email") and not (existente or {}).get("email_enviado_em"):
                enviados = cls._enviar_email_alerta(item, antecedencia, config)
                if enviados:
                    cls.repository.marcar_email_alerta(contrato.get("id"), item.get("proximo_aniversario"), antecedencia)
                    emails += enviados
            mensagens.append(f"{item.get('contrato_numero')}: {cls.STATUS_LABELS.get(item.get('situacao'), item.get('situacao'))}")
        return {"criados": criados, "emails": emails, "mensagens": mensagens}

    @classmethod
    def registrar_historico_valor_se_necessario(cls, contrato_id, dados, origem="SISTEMA"):
        if not contrato_id:
            return None
        ultimo = cls.repository.ultimo_historico(contrato_id)
        atual = cls._valores_historico(dados)
        if not any(atual.get(campo) is not None for campo in ("valor_mensal", "valor_servicos_bruto", "valor_servicos_liquido")):
            return None
        if not ultimo or any(cls._decimal(ultimo.get(campo)) != atual.get(campo) for campo in ("valor_mensal", "valor_servicos_bruto", "valor_descontos", "valor_servicos_liquido")):
            return cls.repository.inserir_historico(contrato_id, {**dados, **atual}, origem=origem)
        return None

    @classmethod
    def analisar_contrato(cls, contrato, hoje=None, config=None):
        hoje = hoje or date.today()
        config = config or cls.configuracao()
        inicio = cls._data(contrato.get("inicio_vigencia"))
        valor_atual = cls._valor_referencia(contrato)
        historico = cls.repository.historico_contrato(contrato.get("id")) if contrato.get("id") else []
        primeiro_faturamento = cls.repository.primeiro_faturamento_contrato(contrato.get("id")) if contrato.get("id") else None
        item = dict(contrato)
        item.update({
            "contrato_id": contrato.get("id"),
            "contrato_numero": contrato.get("numero"),
            "valor_atual": valor_atual,
            "valor_referencia": None,
            "valor_referencia_origem": None,
            "valor_referencia_data": None,
            "valor_pos_aniversario": None,
            "diferenca_valor": None,
            "percentual_variacao": None,
            "idade_meses": None,
            "idade_label": "-",
            "tempo_sem_alteracao_meses": None,
            "tempo_sem_alteracao_label": "-",
            "sem_base_investigar": False,
            "situacao_label": cls.STATUS_LABELS["SEM_DATA_VIGENCIA"],
            "situacao_class": cls.STATUS_CLASSES["SEM_DATA_VIGENCIA"],
            "proximo_aniversario": None,
            "aniversario_anterior": None,
            "dias_para_reajuste": None,
            "situacao": "SEM_DATA_VIGENCIA",
        })
        if not inicio:
            return cls._aplicar_status_visual(item)
        if contrato.get("status") in ("CANCELADO", "ENCERRADO", "SUSPENSO"):
            item.update({"situacao": "IGNORADO", "idade_meses": cls.calcular_idade_meses(inicio, hoje)})
            item["idade_label"] = cls.idade_label(item["idade_meses"])
            return cls._aplicar_status_visual(item)
        proximo = cls.calcular_proximo_aniversario(inicio, hoje)
        anterior = cls._add_years(proximo, -1)
        idade_meses = cls.calcular_idade_meses(inicio, hoje)
        dias = (proximo - hoje).days
        item.update({
            "idade_meses": idade_meses,
            "idade_label": cls.idade_label(idade_meses),
            "proximo_aniversario": proximo,
            "aniversario_anterior": anterior if idade_meses >= 12 else None,
            "dias_para_reajuste": dias,
        })
        comparacao = cls._comparar_faturamento_inicial(primeiro_faturamento, valor_atual) or cls._comparar_historico(historico, anterior)
        item.update(comparacao)
        if valor_atual is None or valor_atual <= 0:
            item["situacao"] = "SEM_BASE_COMPARACAO"
        elif comparacao.get("percentual_variacao") is not None and comparacao.get("diferenca_valor") != 0:
            item["situacao"] = "REAJUSTADO"
        elif idade_meses >= 12 and comparacao.get("valor_referencia") and comparacao.get("valor_pos_aniversario") and comparacao.get("diferenca_valor") == 0:
            item["situacao"] = "SEM_REAJUSTE_DETECTADO"
        elif idade_meses >= 12 and (not historico and not primeiro_faturamento or not comparacao.get("valor_referencia") or not comparacao.get("valor_pos_aniversario")):
            item["situacao"] = "SEM_BASE_COMPARACAO"
        elif dias <= 0:
            item["situacao"] = "REAJUSTE_VENCIDO"
        elif cls.antecedencia_alerta(item, config) is not None:
            item["situacao"] = "REAJUSTE_PROXIMO"
        else:
            item["situacao"] = "A_VENCER"
        if item["situacao"] == "SEM_BASE_COMPARACAO":
            item["tempo_sem_alteracao_meses"] = idade_meses
            item["tempo_sem_alteracao_label"] = cls.idade_label(idade_meses)
            item["sem_base_investigar"] = idade_meses >= 12
        return cls._aplicar_status_visual(item)

    @classmethod
    def antecedencia_alerta(cls, item, config=None):
        config = config or cls.configuracao()
        dias = item.get("dias_para_reajuste")
        if dias is None:
            return None
        if dias <= 0 and item.get("situacao") != "REAJUSTADO":
            return 0
        janelas = []
        if config.get("alerta_30_dias"):
            janelas.append(30)
        if config.get("alerta_15_dias"):
            janelas.append(15)
        if config.get("alerta_7_dias"):
            janelas.append(7)
        for janela in sorted(janelas):
            if dias <= janela:
                return janela
        return None

    @classmethod
    def resumo(cls, itens):
        return {
            "total": len(itens),
            "proximos_30": len([i for i in itens if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 30]),
            "proximos_15": len([i for i in itens if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 15]),
            "proximos_7": len([i for i in itens if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 7]),
            "vencidos": len([i for i in itens if i.get("situacao") == "REAJUSTE_VENCIDO"]),
            "reajustados": len([i for i in itens if i.get("situacao") == "REAJUSTADO"]),
            "sem_base": len([i for i in itens if i.get("situacao") == "SEM_BASE_COMPARACAO"]),
            "sem_base_investigar": len([i for i in itens if i.get("sem_base_investigar")]),
        }

    @classmethod
    def _aplicar_status_visual(cls, item):
        if item.get("sem_base_investigar"):
            item["situacao_label"] = "Sem base - investigar"
            item["situacao_class"] = "danger"
        else:
            item["situacao_label"] = cls.STATUS_LABELS.get(item.get("situacao"), item.get("situacao"))
            item["situacao_class"] = cls.STATUS_CLASSES.get(item.get("situacao"), "secondary")
        return item

    @staticmethod
    def calcular_proximo_aniversario(inicio, hoje=None):
        hoje = hoje or date.today()
        proximo = ReajusteContratoService._add_years(inicio, 1)
        while proximo < hoje:
            proximo = ReajusteContratoService._add_years(proximo, 1)
        return proximo

    @staticmethod
    def calcular_idade_meses(inicio, hoje=None):
        hoje = hoje or date.today()
        meses = (hoje.year - inicio.year) * 12 + hoje.month - inicio.month
        if hoje.day < inicio.day:
            meses -= 1
        return max(0, meses)

    @staticmethod
    def idade_label(meses):
        anos = int((meses or 0) // 12)
        resto = int((meses or 0) % 12)
        if anos and resto:
            return f"{anos} ano(s) e {resto} mes(es)"
        if anos:
            return f"{anos} ano(s)"
        return f"{resto} mes(es)"

    @classmethod
    def historico_com_variacao(cls, contrato_id):
        historico = cls.repository.historico_contrato(contrato_id)
        anterior = None
        linhas = []
        for item in historico:
            valor = cls._valor_referencia(item)
            percentual = None
            if anterior and anterior > 0 and valor is not None:
                percentual = ((valor - anterior) / anterior * Decimal("100")).quantize(Decimal("0.01"))
            linhas.append({**item, "valor_referencia": valor, "percentual_variacao": percentual})
            if valor is not None:
                anterior = valor
        return linhas

    @classmethod
    def configuracao(cls):
        config = cls.repository.configuracao()
        return {
            **config,
            "alerta_30_dias": bool(config.get("alerta_30_dias", True)),
            "alerta_15_dias": bool(config.get("alerta_15_dias", True)),
            "alerta_7_dias": bool(config.get("alerta_7_dias", True)),
            "enviar_email": bool(config.get("enviar_email")),
            "ativo": bool(config.get("ativo", True)),
        }

    @classmethod
    def _comparar_faturamento_inicial(cls, faturamento, valor_atual):
        if not faturamento or valor_atual is None:
            return None
        valor_base = cls._decimal(faturamento.get("valor_original")) or cls._decimal(faturamento.get("valor_recebido"))
        if valor_base is None or valor_base <= 0:
            return None
        diferenca = valor_atual - valor_base
        percentual = (diferenca / valor_base * Decimal("100")).quantize(Decimal("0.01"))
        data_base = cls._data(faturamento.get("data_recebimento")) or cls._data(faturamento.get("data_vencimento")) or cls._data(faturamento.get("data_emissao"))
        return {
            "valor_referencia": valor_base,
            "valor_referencia_origem": "FATURAMENTO_INICIAL",
            "valor_referencia_data": data_base,
            "valor_pos_aniversario": valor_atual,
            "diferenca_valor": diferenca,
            "percentual_variacao": percentual,
        }

    @classmethod
    def _comparar_historico(cls, historico, aniversario):
        if not aniversario:
            return {}
        antes = None
        depois = None
        for item in historico:
            detectado = cls._data(item.get("detectado_em"))
            valor = cls._valor_referencia(item)
            if valor is None:
                continue
            data_ref = detectado or cls._data(item.get("created_at")) or aniversario
            if data_ref <= aniversario:
                antes = valor
            elif depois is None:
                depois = valor
        if antes is None or depois is None:
            return {"valor_referencia": antes, "valor_pos_aniversario": depois}
        diferenca = depois - antes
        percentual = None
        if antes > 0:
            percentual = (diferenca / antes * Decimal("100")).quantize(Decimal("0.01"))
        return {"valor_referencia": antes, "valor_pos_aniversario": depois, "diferenca_valor": diferenca, "percentual_variacao": percentual}

    @classmethod
    def _filtra_item(cls, item, filtros):
        if filtros.get("situacao") and item.get("situacao") != filtros.get("situacao"):
            return False
        if filtros.get("ano") and (not item.get("proximo_aniversario") or item["proximo_aniversario"].year != filtros.get("ano")):
            return False
        if filtros.get("janela"):
            dias = item.get("dias_para_reajuste")
            janela = filtros.get("janela")
            if janela == -1:
                return dias is not None and dias <= 0
            return dias is not None and 0 < dias <= janela
        return True

    @classmethod
    def _enviar_email_alerta(cls, item, antecedencia, config):
        usuarios = [u for u in cls.repository.usuarios_notificacao(config.get("id")) if u.get("receber_email")]
        destinatarios = [u.get("email") for u in usuarios]
        if not destinatarios:
            return 0
        assunto = f"[O3Cloud Manager] Reajuste contratual em {item.get('dias_para_reajuste')} dias - {item.get('cliente_nome') or item.get('cliente_razao_social') or '-'}"
        link = cls._link_contrato(item.get("contrato_id"))
        corpo = "\n".join([
            f"Cliente: {item.get('cliente_nome') or item.get('cliente_razao_social') or '-'}",
            f"Contrato: {item.get('contrato_numero') or '-'}",
            f"Inicio da vigencia: {item.get('inicio_vigencia') or '-'}",
            f"Proximo aniversario: {item.get('proximo_aniversario') or '-'}",
            f"Dias restantes: {item.get('dias_para_reajuste')}",
            f"Valor atual: {item.get('valor_atual') or '-'}",
            f"Vendedor: {item.get('vendedor_nome') or item.get('codigo_vendedor') or '-'}",
            f"Link: {link}",
        ])
        resultado = EmailService.enviar(assunto, corpo, destinatarios)
        return len(resultado.get("destinatarios") or destinatarios) if resultado.get("enviado") else 0

    @staticmethod
    def _link_contrato(contrato_id):
        if not contrato_id or not has_app_context():
            return ""
        base = current_app.config.get("PUBLIC_BASE_URL", "").rstrip("/")
        path = url_for("contratos.view", contrato_id=contrato_id)
        return f"{base}{path}" if base else path

    @staticmethod
    def _add_years(valor, anos):
        try:
            return valor.replace(year=valor.year + anos)
        except ValueError:
            return valor.replace(month=2, day=28, year=valor.year + anos)

    @staticmethod
    def _data(valor):
        if not valor:
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(valor), formato).date()
            except ValueError:
                pass
        return None

    @staticmethod
    def _valor_referencia(dados):
        for campo in ("valor_mensal", "valor_servicos_liquido", "valor_servicos_bruto"):
            valor = ReajusteContratoService._decimal(dados.get(campo))
            if valor is not None:
                return valor
        return None

    @staticmethod
    def _valores_historico(dados):
        return {
            "valor_mensal": ReajusteContratoService._decimal(dados.get("valor_mensal")),
            "valor_servicos_bruto": ReajusteContratoService._decimal(dados.get("valor_servicos_bruto")),
            "valor_descontos": ReajusteContratoService._decimal(dados.get("valor_descontos")),
            "valor_servicos_liquido": ReajusteContratoService._decimal(dados.get("valor_servicos_liquido")),
        }

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return None
        try:
            return Decimal(str(valor)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor or 0)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _flag(dados, chave, default=False):
        if hasattr(dados, "getlist"):
            return 1 if dados.get(chave) else 0
        if chave not in dados:
            return 1 if default else 0
        return 1 if dados.get(chave) else 0

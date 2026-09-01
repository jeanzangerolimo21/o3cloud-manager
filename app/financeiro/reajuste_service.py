import csv
import os
import tempfile
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
    STATUS_INATIVOS = {"CANCELADO", "ENCERRADO", "SUSPENSO"}
    DATA_CORTE_CALCULO = date(2026, 3, 1)
    # INPC anual fechado; aplicado pelo ano anterior ao aniversario contratual.
    INPC_ANUAL = {
        2012: Decimal("6.20"),
        2013: Decimal("5.56"),
        2014: Decimal("6.23"),
        2015: Decimal("11.28"),
        2016: Decimal("6.58"),
        2017: Decimal("2.07"),
        2018: Decimal("3.43"),
        2019: Decimal("4.48"),
        2020: Decimal("5.45"),
        2021: Decimal("10.16"),
        2022: Decimal("5.93"),
        2023: Decimal("3.71"),
        2024: Decimal("4.77"),
        2025: Decimal("3.90"),
    }

    @classmethod
    def filtros(cls, dados):
        return {
            "q": cls._texto(dados.get("q")),
            "status": cls._texto(dados.get("status")),
            "vendedor": cls._texto(dados.get("vendedor")),
            "situacao": cls._texto(dados.get("situacao")),
            "integracao_id": cls._inteiro(dados.get("integracao_id")),
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
        ativos = [i for i in itens if i.get("carteira") == "ATIVA"]
        inativos = [i for i in itens if i.get("carteira") != "ATIVA"]
        return {
            "itens": itens,
            "itens_ativos": ativos,
            "itens_inativos": inativos,
            "resumo": cls.resumo(itens),
            "total_monitorados": cls._total_contratos_monitoramento(filtros),
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
    def processar_alertas(cls, usuario_email="sistema", hoje=None, forcar_relatorio_email=False):
        hoje = hoje or date.today()
        config = cls.configuracao()
        if not config.get("ativo"):
            return {"criados": 0, "emails": 0, "mensagens": ["Monitoramento de reajustes inativo."]}
        criados = 0
        emails = 0
        mensagens = []
        alertas_email = []
        relatorio_email = []
        for contrato in cls.repository.listar_contratos_monitoramento({}, limit=2000):
            cls.registrar_historico_valor_se_necessario(contrato.get("id"), contrato, origem="MONITORAMENTO")
            item = cls.analisar_contrato(contrato, hoje=hoje, config=config)
            if item.get("carteira") != "ATIVA":
                continue
            antecedencia = cls.antecedencia_alerta(item, config)
            if cls._incluir_relatorio_reajuste(item):
                relatorio_email.append({"item": item, "antecedencia": antecedencia})
            if antecedencia is None:
                if item.get("situacao") == "SEM_REAJUSTE_DETECTADO":
                    mensagens.append(f"{item.get('contrato_numero')}: {cls.STATUS_LABELS.get(item.get('situacao'), item.get('situacao'))}")
                continue
            existente = cls.repository.alerta_existente(contrato.get("id"), item.get("proximo_aniversario"), antecedencia)
            if not existente:
                cls.repository.inserir_alerta(contrato.get("id"), item.get("proximo_aniversario"), antecedencia, item.get("situacao"))
                criados += 1
            if config.get("enviar_email") and not (existente or {}).get("email_enviado_em"):
                alertas_email.append({"item": item, "antecedencia": antecedencia})
            mensagens.append(f"{item.get('contrato_numero')}: {cls.STATUS_LABELS.get(item.get('situacao'), item.get('situacao'))}")
        if config.get("enviar_email"):
            envios_email = relatorio_email if forcar_relatorio_email else alertas_email
            if envios_email:
                emails = cls._enviar_email_alertas_lote(envios_email, config, hoje)
                if emails:
                    for alerta in alertas_email:
                        item = alerta["item"]
                        cls.repository.marcar_email_alerta(
                            item.get("contrato_id"),
                            item.get("proximo_aniversario"),
                            alerta.get("antecedencia"),
                        )
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
        contrato_id = contrato.get("id")
        faturamentos = cls._faturamentos_contrato(contrato_id)
        faturamentos = [
            f for f in faturamentos
            if (cls._data_faturamento(f) or date.min) >= cls.DATA_CORTE_CALCULO
        ]
        historico = cls.repository.historico_contrato(contrato_id) if contrato_id else []
        primeiro_faturamento = cls._primeiro_faturamento_por_vigencia(faturamentos, inicio)
        carteira = cls._carteira_contrato(contrato)
        item = dict(contrato)
        item.update({
            "contrato_id": contrato_id,
            "contrato_numero": contrato.get("numero"),
            "carteira": carteira,
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
            "tempo_sem_reajuste_label": "-",
            "prejuizo_estimado": Decimal("0.00"),
            "valor_inpc_estimado": None,
            "inpc_acumulado_percentual": Decimal("0.00"),
            "ciclos_reajuste": [],
            "ciclos_sem_reajuste": 0,
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

        proximo = cls.calcular_proximo_aniversario(inicio, hoje)
        anterior = cls._add_years(proximo, -1)
        idade_meses = cls.calcular_idade_meses(inicio, hoje)
        dias = (proximo - hoje).days
        valor_base_contrato = cls._valor_referencia(contrato)
        analise = cls._analisar_ciclos_faturamento(
            inicio, faturamentos, valor_atual, hoje,
            valor_base=valor_base_contrato,
            data_base=inicio,
        ) if primeiro_faturamento else {}
        item.update({
            "idade_meses": idade_meses,
            "idade_label": cls.idade_label(idade_meses),
            "proximo_aniversario": proximo,
            "aniversario_anterior": anterior if idade_meses >= 12 else None,
            "dias_para_reajuste": dias,
            **analise,
        })

        if primeiro_faturamento:
            valor_base = cls._valor_faturamento(primeiro_faturamento)
            data_base = cls._data_faturamento(primeiro_faturamento)
            item.update({
                "valor_referencia": valor_base,
                "valor_referencia_origem": "FATURAMENTO_INICIAL",
                "valor_referencia_data": data_base,
                "valor_pos_aniversario": valor_atual,
            })
            if valor_base and valor_atual is not None:
                item["diferenca_valor"] = valor_atual - valor_base
                item["percentual_variacao"] = ((valor_atual - valor_base) / valor_base * Decimal("100")).quantize(Decimal("0.01"))
        elif valor_base_contrato and valor_base_contrato > 0 and not historico:
            item.update({
                "valor_referencia": valor_base_contrato,
                "valor_referencia_origem": "VALOR_CONTRATO_INICIAL",
                "valor_referencia_data": max(inicio, cls.DATA_CORTE_CALCULO),
                "valor_pos_aniversario": valor_atual,
            })

        comparacao_historico = cls._comparar_historico(historico, anterior) if historico and not primeiro_faturamento else None
        if comparacao_historico and comparacao_historico.get("percentual_variacao") is not None:
            item.update(comparacao_historico)

        if carteira != "ATIVA":
            item["situacao"] = "IGNORADO"
        elif valor_atual is None or valor_atual <= 0:
            item["situacao"] = "SEM_BASE_COMPARACAO"
        elif not primeiro_faturamento and not historico and idade_meses >= 12:
            item["situacao"] = "SEM_BASE_COMPARACAO"
        elif not primeiro_faturamento and (valor_base_contrato is None or valor_base_contrato <= 0):
            item["situacao"] = "SEM_BASE_COMPARACAO"
        elif item.get("percentual_variacao") is not None and item.get("diferenca_valor") != 0:
            item["situacao"] = "REAJUSTADO"
        elif item.get("ciclos_sem_reajuste"):
            item["situacao"] = "SEM_REAJUSTE_DETECTADO"
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
        ativos = [i for i in itens if i.get("carteira") == "ATIVA"]
        inativos = [i for i in itens if i.get("carteira") != "ATIVA"]
        return {
            "total": len(itens),
            "ativos": len(ativos),
            "inativos": len(inativos),
            "prejuizo_estimado": sum((i.get("prejuizo_estimado") or Decimal("0.00")) for i in itens),
            "prejuizo_estimado_ativos": sum((i.get("prejuizo_estimado") or Decimal("0.00")) for i in ativos),
            "prejuizo_estimado_inativos": sum((i.get("prejuizo_estimado") or Decimal("0.00")) for i in inativos),
            "sem_reajuste": len([i for i in ativos if i.get("situacao") == "SEM_REAJUSTE_DETECTADO"]),
            "proximos_30": len([i for i in ativos if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 30]),
            "proximos_15": len([i for i in ativos if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 15]),
            "proximos_7": len([i for i in ativos if i.get("dias_para_reajuste") is not None and 0 < i.get("dias_para_reajuste") <= 7]),
            "vencidos": len([i for i in ativos if i.get("situacao") == "REAJUSTE_VENCIDO"]),
            "reajustados": len([i for i in ativos if i.get("situacao") == "REAJUSTADO"]),
            "sem_base": len([i for i in ativos if i.get("situacao") == "SEM_BASE_COMPARACAO"]),
            "sem_base_investigar": len([i for i in ativos if i.get("sem_base_investigar")]),
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
    def _total_contratos_monitoramento(cls, filtros):
        try:
            return cls.repository.total_contratos_monitoramento(filtros)
        except TypeError:
            return cls.repository.total_contratos_monitoramento()

    @classmethod
    def _faturamentos_contrato(cls, contrato_id):
        if not contrato_id:
            return []
        if hasattr(cls.repository, "faturamentos_contrato"):
            return cls.repository.faturamentos_contrato(contrato_id) or []
        primeiro = cls.repository.primeiro_faturamento_contrato(contrato_id) if hasattr(cls.repository, "primeiro_faturamento_contrato") else None
        return [primeiro] if primeiro else []

    @classmethod
    def _analisar_ciclos_faturamento(cls, inicio, faturamentos, valor_atual, hoje, valor_base=None, data_base=None):
        primeiro = cls._primeiro_faturamento_por_vigencia(faturamentos, inicio)
        valor_base = cls._valor_faturamento(primeiro) if primeiro else valor_base
        data_base = cls._data_faturamento(primeiro) if primeiro else data_base
        if not inicio or valor_base is None or valor_base <= 0:
            return {}

        faturamentos_normalizados = []
        for faturamento in faturamentos:
            data = cls._data_faturamento(faturamento)
            valor = cls._valor_faturamento(faturamento)
            if data and valor is not None:
                faturamentos_normalizados.append({"data": data, "valor": valor})

        ciclos = []
        valor_anterior = valor_base
        ultima_alteracao = data_base or inicio
        prejuizo = Decimal("0.00")
        anos_sem_reajuste = []
        tem_alteracao = False
        ano = 1
        while cls._add_years(inicio, ano) <= hoje:
            inicio_ciclo = cls._add_years(inicio, ano)
            fim_ciclo = min(cls._add_years(inicio, ano + 1), hoje)
            if inicio_ciclo < cls.DATA_CORTE_CALCULO:
                ano += 1
                continue
            meses_ciclo = cls.calcular_idade_meses(inicio_ciclo, fim_ciclo)
            indice_ano = inicio_ciclo.year - 1
            inpc = cls.INPC_ANUAL.get(indice_ano)
            esperado = cls._aplicar_percentual(valor_anterior, inpc) if inpc is not None else valor_anterior
            valor_ciclo = cls._valor_no_ciclo(faturamentos_normalizados, inicio_ciclo, fim_ciclo, valor_anterior, valor_atual)
            alterado = valor_ciclo is not None and valor_ciclo != valor_anterior
            sem_reajuste = meses_ciclo > 0 and valor_ciclo is not None and not alterado
            diferenca_mensal = Decimal("0.00")
            perda_ciclo = Decimal("0.00")

            if alterado:
                tem_alteracao = True
                ultima_alteracao = inicio_ciclo
            elif sem_reajuste and inpc is not None and esperado > valor_ciclo:
                diferenca_mensal = esperado - valor_ciclo
                perda_ciclo = (diferenca_mensal * Decimal(meses_ciclo)).quantize(Decimal("0.01"))
                prejuizo += perda_ciclo
                anos_sem_reajuste.append({
                    "ano": inicio_ciclo.year,
                    "inpc": inpc,
                    "diferenca_mensal": diferenca_mensal.quantize(Decimal("0.01")),
                    "prejuizo": perda_ciclo,
                })

            ciclos.append({
                "aniversario": inicio_ciclo,
                "ano_inpc": indice_ano,
                "inpc_percentual": inpc,
                "valor_anterior": valor_anterior,
                "valor_faturado": valor_ciclo,
                "valor_estimado_inpc": esperado,
                "alterado": alterado,
                "sem_reajuste": sem_reajuste,
                "meses": meses_ciclo,
                "diferenca_mensal": diferenca_mensal.quantize(Decimal("0.01")),
                "prejuizo": perda_ciclo,
            })
            if valor_ciclo is not None:
                valor_anterior = valor_ciclo
            ano += 1

        if not tem_alteracao and anos_sem_reajuste:
            acumulado = Decimal("1.00")
            for ano_sem_reajuste in anos_sem_reajuste:
                acumulado *= Decimal("1.00") + ano_sem_reajuste["inpc"] / Decimal("100")
            inpc_acumulado = (acumulado - Decimal("1.00")) * Decimal("100")
        else:
            inpc_acumulado = sum((item["inpc"] for item in anos_sem_reajuste), Decimal("0.00"))

        tempo_sem_reajuste = cls.calcular_idade_meses(ultima_alteracao, hoje) if ultima_alteracao else None
        return {
            "tempo_sem_alteracao_meses": tempo_sem_reajuste,
            "tempo_sem_alteracao_label": cls.idade_label(tempo_sem_reajuste),
            "tempo_sem_reajuste_label": cls.idade_label(tempo_sem_reajuste),
            "prejuizo_estimado": prejuizo.quantize(Decimal("0.01")),
            "valor_inpc_estimado": ciclos[-1]["valor_estimado_inpc"] if ciclos else valor_base,
            "inpc_acumulado_percentual": inpc_acumulado.quantize(Decimal("0.01")),
            "ciclos_reajuste": ciclos,
            "ciclos_sem_reajuste": len([c for c in ciclos if c.get("sem_reajuste")]),
            "anos_sem_reajuste": anos_sem_reajuste,
        }

    @classmethod
    def _primeiro_faturamento_por_vigencia(cls, faturamentos, inicio):
        if not faturamentos:
            return None
        if not inicio:
            return faturamentos[0]
        posteriores = [f for f in faturamentos if (cls._data_faturamento(f) or date.min) >= inicio]
        return posteriores[0] if posteriores else faturamentos[0]

    @classmethod
    def _valor_no_ciclo(cls, faturamentos, inicio, fim, valor_anterior, valor_atual):
        for faturamento in faturamentos:
            if inicio <= faturamento["data"] < fim:
                return faturamento["valor"]
        anteriores = [f for f in faturamentos if f["data"] < fim]
        if anteriores:
            return anteriores[-1]["valor"]
        return valor_atual if valor_atual is not None else valor_anterior

    @staticmethod
    def _aplicar_percentual(valor, percentual):
        if percentual is None:
            return valor
        return (valor * (Decimal("1.00") + percentual / Decimal("100"))).quantize(Decimal("0.01"))

    @classmethod
    def _carteira_contrato(cls, contrato):
        ativo = contrato.get("ativo")
        if ativo is not None and not ativo:
            return "INATIVA_CANCELADA"
        if contrato.get("status") in cls.STATUS_INATIVOS:
            return "INATIVA_CANCELADA"
        return "ATIVA"

    @classmethod
    def _valor_faturamento(cls, faturamento):
        return cls._decimal(faturamento.get("valor_original")) or cls._decimal(faturamento.get("valor_recebido"))

    @classmethod
    def _data_faturamento(cls, faturamento):
        return cls._data(faturamento.get("data_recebimento")) or cls._data(faturamento.get("data_vencimento")) or cls._data(faturamento.get("data_emissao"))

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
    def _incluir_relatorio_reajuste(cls, item):
        if item.get("situacao") in ("REAJUSTE_VENCIDO", "SEM_REAJUSTE_DETECTADO"):
            return True
        dias = item.get("dias_para_reajuste")
        return dias is not None and 0 < dias <= 30

    @classmethod
    def _enviar_email_alertas_lote(cls, alertas, config, hoje=None):
        usuarios = [u for u in cls.repository.usuarios_notificacao(config.get("id")) if u.get("receber_email")]
        destinatarios = [u.get("email") for u in usuarios]
        if not destinatarios:
            return 0
        hoje = hoje or date.today()
        vencidos = [a["item"] for a in alertas if a["item"].get("situacao") == "REAJUSTE_VENCIDO"]
        proximos = [a["item"] for a in alertas if 0 < (a["item"].get("dias_para_reajuste") or 0) <= 30]
        sem_reajuste = [a["item"] for a in alertas if a["item"].get("situacao") == "SEM_REAJUSTE_DETECTADO"]
        caminho = cls._gerar_csv_alertas_reajuste(alertas)
        try:
            assunto = f"[O3Cloud Manager] Reajustes contratuais - {len(vencidos)} vencido(s), {len(proximos)} nos proximos 30 dias"
            corpo = "\n".join([
                "Verificacao de reajustes contratuais concluida.",
                "",
                f"Data da verificacao: {hoje}",
                f"Contratos vencidos: {len(vencidos)}",
                f"Contratos a vencer nos proximos 30 dias: {len(proximos)}",
                f"Contratos sem reajuste detectado: {len(sem_reajuste)}",
                f"Total no arquivo: {len(alertas)}",
                "",
                "O detalhamento esta no arquivo CSV anexo.",
                "O monitoramento apenas alerta para analise humana; nao aplica reajustes automaticamente.",
            ])
            resultado = EmailService.enviar(
                assunto,
                corpo,
                destinatarios,
                anexos=[{
                    "nome": f"reajustes-contratuais-{hoje}.csv",
                    "caminho": caminho,
                    "mime_type": "text/csv",
                }],
            )
            return 1 if resultado.get("enviado") else 0
        finally:
            try:
                os.unlink(caminho)
            except OSError:
                pass

    @classmethod
    def _gerar_csv_alertas_reajuste(cls, alertas):
        arquivo = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        with arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow([
                "Grupo",
                "Contrato",
                "Cliente",
                "Inicio da vigencia",
                "Proximo aniversario",
                "Dias restantes",
                "Situacao",
                "Valor atual",
                "Valor INPC estimado",
                "Prejuizo estimado",
                "Vendedor",
                "Link",
            ])
            for alerta in sorted(alertas, key=lambda a: ((a["item"].get("dias_para_reajuste") or 0), a["item"].get("cliente_nome") or "")):
                item = alerta["item"]
                dias = item.get("dias_para_reajuste")
                if item.get("situacao") == "SEM_REAJUSTE_DETECTADO":
                    grupo = "Sem reajuste detectado"
                elif item.get("situacao") == "REAJUSTE_VENCIDO" or (dias is not None and dias <= 0):
                    grupo = "Vencidos"
                else:
                    grupo = "Proximos 30 dias"
                writer.writerow([
                    grupo,
                    item.get("contrato_numero") or "-",
                    item.get("cliente_nome") or item.get("cliente_razao_social") or "-",
                    item.get("inicio_vigencia") or "-",
                    item.get("proximo_aniversario") or "-",
                    dias if dias is not None else "-",
                    item.get("situacao_label") or cls.STATUS_LABELS.get(item.get("situacao"), item.get("situacao")) or "-",
                    cls._formatar_decimal(item.get("valor_atual")),
                    cls._formatar_decimal(item.get("valor_inpc_estimado")),
                    cls._formatar_decimal(item.get("prejuizo_estimado")),
                    item.get("vendedor_nome") or item.get("codigo_vendedor") or "-",
                    cls._link_contrato(item.get("contrato_id")),
                ])
        return arquivo.name

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
    def _formatar_decimal(valor):
        if valor in (None, ""):
            return "-"
        decimal = ReajusteContratoService._decimal(valor)
        return str(decimal) if decimal is not None else "-"

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

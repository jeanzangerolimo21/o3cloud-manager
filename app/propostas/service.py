import json
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from io import BytesIO
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from xml.sax.saxutils import escape

from app.catalogo.precos.repository import PrecoCatalogoRepository
from app.catalogo.recursos.repository import ProdutoRecursoRepository
from app.catalogo.produtos.service import ProdutoService
from app.clientes.service import ClienteService
from app.contatos.service import ContatoService
from app.core.storage import StorageService
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.repositories.oportunidade_repository import OportunidadeRepository
from app.repositories.proposta_repository import PropostaRepository

STATUS_PROPOSTA = {
    "RASCUNHO": "Rascunho",
    "EM_ANALISE": "Em Análise",
    "ENVIADA": "Enviada",
    "APROVADA": "Aprovada",
    "REJEITADA": "Rejeitada",
    "EXPIRADA": "Expirada",
}


class PropostaService:
    repository = PropostaRepository

    @classmethod
    def listar(cls, pesquisa=None, status=None, ativo=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status_ativo(ativo)
        propostas = cls.repository.listar(pesquisa=pesquisa, status=status, ativo=ativo_normalizado, limit=limit, offset=offset)
        total = cls.repository.total(pesquisa=pesquisa, status=status, ativo=ativo_normalizado)
        return propostas, total

    @classmethod
    def buscar_por_id(cls, proposta_id):
        proposta = cls.repository.buscar_por_id(proposta_id)
        if not proposta:
            return None
        return cls._decorar_proposta(proposta)

    @classmethod
    def listar_contexto_form(cls, executivo_email=None):
        executivos = ParceiroExecutivoService.listar_todos_ativos()
        return {
            "oportunidades": OportunidadeRepository.listar_todos_ativos(),
            "clientes": ClienteService.listar_para_importacao(),
            "contatos": ContatoService.listar_todos_ativos(),
            "executivos": executivos,
            "produtos_fechados": cls.listar_produtos_fechados(),
            "licencas_catalogo": PrecoCatalogoRepository.listar_licenciamento(),
            "recursos_servidor": ProdutoRecursoRepository.listar(),
            "executivo_padrao_id": cls.identificar_executivo_padrao(executivo_email, executivos),
            "codigo_sugerido": cls.gerar_codigo_proposta(),
        }

    @classmethod
    def listar_produtos_fechados(cls):
        produtos = ProdutoService.listar()
        ativos = [produto for produto in produtos if produto.get("ativo")]
        return sorted(ativos, key=lambda item: ((item.get("parceiro") or ""), (item.get("nome") or "")))

    @classmethod
    def identificar_executivo_padrao(cls, executivo_email, executivos=None):
        if not executivo_email:
            return None
        for executivo in executivos or ParceiroExecutivoService.listar_todos_ativos():
            if (executivo.get("email") or "").strip().lower() == executivo_email.strip().lower():
                return executivo.get("id")
        return None

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        dados["versao"] = cls.repository.proxima_versao(dados.get("oportunidade_id"))
        dados["codigo_proposta"] = dados.get("codigo_proposta") or cls.gerar_codigo_proposta()
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, proposta_id, dados):
        proposta = cls.buscar_por_id(proposta_id)
        if not proposta:
            raise ValueError("Proposta não encontrada.")
        dados = cls.normalizar(dados)
        cls.validar(dados, proposta_id=proposta_id)
        dados["versao"] = proposta.get("versao")
        dados["codigo_proposta"] = proposta.get("codigo_proposta") or dados.get("codigo_proposta") or cls.gerar_codigo_proposta()
        dados["arquivo"] = dados.get("arquivo") or proposta.get("arquivo")
        return cls.repository.atualizar(proposta_id, dados)

    @classmethod
    def excluir(cls, proposta_id):
        proposta = cls.buscar_por_id(proposta_id)
        if proposta and proposta.get("arquivo"):
            StorageService.excluir(StorageService.PROPOSTAS, proposta.get("arquivo"))
        return cls.repository.excluir(proposta_id)

    @classmethod
    def preparar_form_payload(cls, dados=None, codigo_sugerido=None):
        dados = dict(dados or {})
        return {
            "id": dados.get("id"),
            "oportunidade_id": dados.get("oportunidade_id"),
            "cliente_id": dados.get("cliente_id"),
            "cliente_razao_social": dados.get("cliente_razao_social") or "",
            "cliente_nome_fantasia": dados.get("cliente_nome_fantasia") or "",
            "cliente_cnpj": dados.get("cliente_cnpj") or "",
            "contato_id": dados.get("contato_id"),
            "parceiro_id": dados.get("parceiro_id"),
            "executivo_responsavel_id": dados.get("executivo_responsavel_id"),
            "codigo_proposta": dados.get("codigo_proposta") or codigo_sugerido or cls.gerar_codigo_proposta(),
            "titulo": dados.get("titulo") or "",
            "status": dados.get("status") or "RASCUNHO",
            "validade": cls._string_data(dados.get("validade")),
            "setup_dias": dados.get("setup_dias") or 7,
            "mensalidade_dias": dados.get("mensalidade_dias") or 30,
            "prazo_contratual_meses": dados.get("prazo_contratual_meses") or 24,
            "detalhes_negociacao": dados.get("detalhes_negociacao") or "",
            "condicoes_comerciais": dados.get("condicoes_comerciais") or "",
            "observacoes": dados.get("observacoes") or "",
            "cliente_nome": dados.get("cliente_nome") or "",
            "contato_nome": dados.get("contato_nome") or "",
            "contato_email": dados.get("contato_email") or "",
            "contato_telefone": dados.get("contato_telefone") or "",
            "executivo_nome": dados.get("executivo_nome") or "",
            "executivo_email": dados.get("executivo_email") or "",
            "executivo_telefone": dados.get("executivo_telefone") or "",
            "parametrizacao_sistema": cls._string_decimal(dados.get("parametrizacao_sistema"), "0.00"),
            "setup_ambiente_cloud": cls._string_decimal(dados.get("setup_ambiente_cloud"), "0.00"),
            "total_mensal": cls._string_decimal(dados.get("total_mensal"), "0.00"),
            "total_instalacao": cls._string_decimal(dados.get("total_instalacao"), "0.00"),
            "valor_total": cls._string_decimal(dados.get("valor_total"), "0.00"),
            "licencas_snapshot": dados.get("licencas_snapshot") or "[]",
            "servidores_snapshot": dados.get("servidores_snapshot") or "[]",
            "licencas_items": cls._carregar_lista_json(dados.get("licencas_snapshot"), dados.get("licencas_items")),
            "servidores_items": cls._carregar_lista_json(dados.get("servidores_snapshot"), dados.get("servidores_items")),
            "ativo": str(dados.get("ativo", "1")) in ("1", "true", "True", "on") or dados.get("ativo") is True,
        }

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        for campo in ("oportunidade_id", "cliente_id", "contato_id", "parceiro_id", "executivo_responsavel_id"):
            dados[campo] = cls._normalizar_inteiro(dados.get(campo))
        dados["codigo_proposta"] = (dados.get("codigo_proposta") or "").strip()
        dados["titulo"] = (dados.get("titulo") or "").strip()
        dados["status"] = (dados.get("status") or "RASCUNHO").strip().upper()
        dados["validade"] = cls._normalizar_data(dados.get("validade"))
        dados["setup_dias"] = cls._normalizar_inteiro(dados.get("setup_dias"), 7)
        dados["mensalidade_dias"] = cls._normalizar_inteiro(dados.get("mensalidade_dias"), 30)
        dados["prazo_contratual_meses"] = cls._normalizar_inteiro(dados.get("prazo_contratual_meses"), 24)
        for campo in ("detalhes_negociacao", "condicoes_comerciais", "observacoes", "cliente_nome", "contato_nome", "contato_telefone", "executivo_nome", "executivo_telefone"):
            dados[campo] = (dados.get(campo) or "").strip()
        dados["contato_email"] = (dados.get("contato_email") or "").strip().lower()
        dados["executivo_email"] = (dados.get("executivo_email") or "").strip().lower()
        dados["licencas_items"] = cls._normalizar_licencas(dados.get("licencas_snapshot"))
        dados["servidores_items"] = cls._normalizar_servidores(dados.get("servidores_snapshot"))
        cls._herdar_relacionamentos(dados)
        resumo = cls._calcular_totais(dados["licencas_items"], dados["servidores_items"])
        dados["total_mensal"] = cls._decimal(dados.get("total_mensal")) or resumo["total_mensal"]
        dados["parametrizacao_sistema"] = cls._decimal(dados.get("parametrizacao_sistema"))
        if dados["parametrizacao_sistema"] is None:
            dados["parametrizacao_sistema"] = resumo["parametrizacao_padrao"]
        dados["setup_ambiente_cloud"] = cls._decimal(dados.get("setup_ambiente_cloud"))
        if dados["setup_ambiente_cloud"] is None:
            dados["setup_ambiente_cloud"] = resumo["setup_cloud_padrao"]
        dados["total_instalacao"] = resumo["instalacao_servidores"] + dados["parametrizacao_sistema"] + dados["setup_ambiente_cloud"]
        dados["valor_total"] = dados["total_mensal"] + dados["total_instalacao"]
        dados["itens_snapshot"] = cls._montar_itens_snapshot(dados["licencas_items"], dados["servidores_items"])
        dados["licencas_snapshot"] = json.dumps(dados["licencas_items"], ensure_ascii=False)
        dados["servidores_snapshot"] = json.dumps(dados["servidores_items"], ensure_ascii=False)
        dados["ativo"] = str(dados.get("ativo", "1")) == "1" or dados.get("ativo") is True
        return dados

    @classmethod
    def validar(cls, dados, proposta_id=None):
        oportunidade = None
        if dados.get("oportunidade_id"):
            oportunidade = OportunidadeRepository.buscar_por_id(dados["oportunidade_id"])
            if not oportunidade:
                raise ValueError("Oportunidade vinculada não encontrada.")
        if not dados.get("cliente_id") and not dados.get("cliente_nome"):
            raise ValueError("Cliente da proposta é obrigatório.")
        if not dados.get("titulo"):
            raise ValueError("Título da solução é obrigatório.")
        if dados.get("status") not in STATUS_PROPOSTA:
            raise ValueError("Status da proposta inválido.")
        if not dados["licencas_items"] and not dados["servidores_items"]:
            raise ValueError("Adicione ao menos uma licença ou um servidor na proposta.")
        if dados["prazo_contratual_meses"] <= 0:
            raise ValueError("Prazo contratual deve ser maior que zero.")
        for campo in ("total_mensal", "parametrizacao_sistema", "setup_ambiente_cloud", "total_instalacao", "valor_total"):
            if dados[campo] is not None and dados[campo] < 0:
                raise ValueError("Os valores da proposta não podem ser negativos.")
        if oportunidade and not dados.get("cliente_nome"):
            raise ValueError("Não foi possível resolver o cliente da oportunidade.")
        return True

    @classmethod
    def gerar_codigo_proposta(cls):
        return datetime.now().strftime("O3-%Y%m%d-%H%M")

    @classmethod
    def gerar_docx(cls, proposta):
        linhas = cls._montar_linhas_documento(proposta)
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as arquivo:
            arquivo.writestr("[Content_Types].xml", cls._docx_content_types())
            arquivo.writestr("_rels/.rels", cls._docx_root_rels())
            arquivo.writestr("word/_rels/document.xml.rels", cls._docx_document_rels())
            arquivo.writestr("word/styles.xml", cls._docx_styles())
            arquivo.writestr("docProps/core.xml", cls._docx_core())
            arquivo.writestr("docProps/app.xml", cls._docx_app())
            arquivo.writestr("word/document.xml", cls._docx_document(linhas))
        buffer.seek(0)
        return buffer

    @classmethod
    def _decorar_proposta(cls, proposta):
        proposta = dict(proposta)
        proposta["licencas_items"] = cls._carregar_lista_json(proposta.get("licencas_snapshot"))
        proposta["servidores_items"] = cls._carregar_lista_json(proposta.get("servidores_snapshot"))
        resumo = cls._calcular_totais(proposta["licencas_items"], proposta["servidores_items"])
        proposta["total_mensal"] = cls._decimal(proposta.get("total_mensal")) or resumo["total_mensal"]
        proposta["parametrizacao_sistema"] = cls._decimal(proposta.get("parametrizacao_sistema")) or resumo["parametrizacao_padrao"]
        proposta["setup_ambiente_cloud"] = cls._decimal(proposta.get("setup_ambiente_cloud")) or resumo["setup_cloud_padrao"]
        proposta["total_instalacao"] = cls._decimal(proposta.get("total_instalacao")) or (resumo["instalacao_servidores"] + proposta["parametrizacao_sistema"] + proposta["setup_ambiente_cloud"])
        proposta["valor_total"] = cls._decimal(proposta.get("valor_total")) or (proposta["total_mensal"] + proposta["total_instalacao"])
        proposta["instalacao_servidores"] = resumo["instalacao_servidores"]
        proposta["status_label"] = STATUS_PROPOSTA.get(proposta.get("status"), proposta.get("status"))
        proposta["codigo_proposta"] = proposta.get("codigo_proposta") or cls.gerar_codigo_proposta()
        cls._enriquecer_cliente(proposta)
        return proposta

    @classmethod
    def _herdar_relacionamentos(cls, dados):
        oportunidade = OportunidadeRepository.buscar_por_id(dados["oportunidade_id"]) if dados.get("oportunidade_id") else None
        if oportunidade:
            for campo in ("cliente_id", "contato_id", "parceiro_id", "executivo_responsavel_id"):
                if not dados.get(campo):
                    dados[campo] = oportunidade.get(campo)
        if dados.get("cliente_id"):
            for cliente in ClienteService.listar_para_importacao():
                if cliente.get("id") == dados["cliente_id"]:
                    dados["cliente_nome"] = dados.get("cliente_nome") or cliente.get("nome_fantasia") or cliente.get("razao_social") or ""
                    dados["cliente_nome_fantasia"] = cliente.get("nome_fantasia") or dados.get("cliente_nome_fantasia") or ""
                    dados["cliente_razao_social"] = cliente.get("razao_social") or dados.get("cliente_razao_social") or ""
                    dados["cliente_cnpj"] = cliente.get("cnpj") or dados.get("cliente_cnpj") or ""
                    break
        elif oportunidade:
            dados["cliente_nome"] = dados.get("cliente_nome") or oportunidade.get("cliente_exibicao") or oportunidade.get("empresa") or ""
        if dados.get("contato_id"):
            contato = ContatoService.buscar_por_id(dados["contato_id"])
            if contato:
                dados["contato_nome"] = contato.get("nome") or dados.get("contato_nome")
                dados["contato_email"] = contato.get("email") or dados.get("contato_email")
                dados["contato_telefone"] = contato.get("telefone") or contato.get("whatsapp") or dados.get("contato_telefone")
                dados["parceiro_id"] = dados.get("parceiro_id") or contato.get("parceiro_id")
                dados["executivo_responsavel_id"] = dados.get("executivo_responsavel_id") or contato.get("executivo_responsavel_id")
        if dados.get("executivo_responsavel_id"):
            for executivo in ParceiroExecutivoService.listar_todos_ativos():
                if executivo.get("id") == dados["executivo_responsavel_id"]:
                    dados["executivo_nome"] = executivo.get("nome") or dados.get("executivo_nome")
                    dados["executivo_email"] = executivo.get("email") or dados.get("executivo_email")
                    dados["executivo_telefone"] = executivo.get("telefone") or dados.get("executivo_telefone")
                    dados["parceiro_id"] = dados.get("parceiro_id") or executivo.get("parceiro_id")
                    break

    @classmethod
    def _enriquecer_cliente(cls, dados):
        dados.setdefault("cliente_razao_social", "")
        dados.setdefault("cliente_nome_fantasia", "")
        dados.setdefault("cliente_cnpj", "")
        if not dados.get("cliente_id"):
            return dados
        cliente = ClienteService.buscar_por_id(dados.get("cliente_id"))
        if not cliente:
            return dados
        dados["cliente_razao_social"] = cliente.get("razao_social") or dados.get("cliente_razao_social") or ""
        dados["cliente_nome_fantasia"] = cliente.get("nome_fantasia") or dados.get("cliente_nome_fantasia") or ""
        dados["cliente_cnpj"] = cliente.get("cnpj") or dados.get("cliente_cnpj") or ""
        if not dados.get("cliente_nome"):
            dados["cliente_nome"] = cliente.get("nome_fantasia") or cliente.get("razao_social") or ""
        return dados

    @classmethod
    def _normalizar_licencas(cls, bruto):
        itens = cls._carregar_lista_json(bruto)
        resposta = []
        for item in itens:
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            valor = cls._decimal(item.get("valor_unitario")) or Decimal("0.00")
            resposta.append({
                "preco_id": cls._normalizar_inteiro(item.get("preco_id")),
                "faixa_id": cls._normalizar_inteiro(item.get("faixa_id")),
                "produto": (item.get("produto") or "").strip(),
                "software": (item.get("software") or "").strip(),
                "descricao": (item.get("descricao") or "").strip(),
                "quantidade": quantidade,
                "valor_unitario": cls._string_decimal(valor),
                "valor_setup": cls._string_decimal(cls._decimal(item.get("valor_setup")) or Decimal("0.00")),
                "tem_projeto": str(item.get("tem_projeto", "0")).lower() in ("1", "true", "sim"),
                "usuarios_inicio": cls._normalizar_inteiro(item.get("usuarios_inicio")),
                "usuarios_fim": cls._normalizar_inteiro(item.get("usuarios_fim")),
                "total_mensal": cls._string_decimal((valor * quantidade).quantize(Decimal("0.01"))),
            })
        return resposta

    @classmethod
    def _normalizar_servidores(cls, bruto):
        itens = cls._carregar_lista_json(bruto)
        resposta = []
        for item in itens:
            quantidade = cls._normalizar_inteiro(item.get("quantidade"), 1) or 1
            valor_mensal = cls._decimal(item.get("valor_mensal")) or Decimal("0.00")
            valor_instalacao = cls._decimal(item.get("valor_instalacao")) or Decimal("0.00")
            resposta.append({
                "recurso_id": cls._normalizar_inteiro(item.get("recurso_id")),
                "codigo": (item.get("codigo") or "").strip(),
                "categoria": (item.get("categoria") or "").strip(),
                "nome": (item.get("nome") or "").strip(),
                "descricao": (item.get("descricao") or "").strip(),
                "quantidade": quantidade,
                "valor_mensal": cls._string_decimal(valor_mensal),
                "valor_instalacao": cls._string_decimal(valor_instalacao),
                "total_mensal": cls._string_decimal((valor_mensal * quantidade).quantize(Decimal("0.01"))),
                "total_instalacao": cls._string_decimal((valor_instalacao * quantidade).quantize(Decimal("0.01"))),
            })
        return resposta

    @classmethod
    def _calcular_totais(cls, licencas, servidores):
        total_mensal = Decimal("0.00")
        parametrizacao = Decimal("0.00")
        instalacao_servidores = Decimal("0.00")
        for item in licencas:
            total = cls._decimal(item.get("total_mensal")) or Decimal("0.00")
            total_mensal += total
            if item.get("tem_projeto"):
                parametrizacao += total
        for item in servidores:
            total_mensal += cls._decimal(item.get("total_mensal")) or Decimal("0.00")
            instalacao_servidores += cls._decimal(item.get("total_instalacao")) or Decimal("0.00")
        return {
            "total_mensal": total_mensal.quantize(Decimal("0.01")),
            "parametrizacao_padrao": parametrizacao.quantize(Decimal("0.01")),
            "setup_cloud_padrao": total_mensal.quantize(Decimal("0.01")),
            "instalacao_servidores": instalacao_servidores.quantize(Decimal("0.01")),
        }

    @classmethod
    def _montar_itens_snapshot(cls, licencas, servidores):
        linhas = []
        if licencas:
            linhas.append("Licenciamento por Usuário")
            for item in licencas:
                linhas.append(f"- {item.get('software')}: {item.get('quantidade')} x R$ {item.get('valor_unitario')} = R$ {item.get('total_mensal')}")
        if servidores:
            linhas.append("Recursos de Servidor")
            for item in servidores:
                linhas.append(f"- {item.get('nome')}: {item.get('quantidade')} x R$ {item.get('valor_mensal')} = R$ {item.get('total_mensal')}")
        return "\n".join(linhas)

    @classmethod
    def _montar_linhas_documento(cls, proposta):
        linhas = [
            "SOLUÇÃO",
            proposta.get("titulo") or "",
            proposta.get("cliente_nome") or proposta.get("oportunidade_empresa") or "",
            proposta.get("codigo_proposta") or "",
            "",
            "1. AGRADECIMENTO",
            "Prezado Cliente (a)",
            "Temos o prazer de lhe apresentar a nossa proposta de solução em CLOUD.",
            "Somos uma empresa especializada em hospedagem de servidores em nuvem e tecnologia da informação.",
            "Queremos escrever ao seu lado uma parceria de sucesso oferecendo tecnologia de ponta sob medida.",
            f"{proposta.get('executivo_nome') or 'Executivo de vendas'} - Executivo de vendas",
            f"e-mail - {proposta.get('executivo_email') or '-'}",
            "",
            "2. INVESTIMENTOS CLOUD",
            f"Parametrização do Sistema	R$ {cls._string_decimal(proposta.get('parametrizacao_sistema'))}",
            f"Setup do Ambiente Cloud	R$ {cls._string_decimal(proposta.get('setup_ambiente_cloud'))}",
            f"Recursos adicionais de instalação	R$ {cls._string_decimal(proposta.get('instalacao_servidores'))}",
            f"TOTAL INSTALAÇÃO	R$ {cls._string_decimal(proposta.get('total_instalacao'))}",
            "",
            "Das mensalidades:",
        ]
        for item in proposta.get("licencas_items", []):
            linhas.append(f"{item.get('software')} | {item.get('quantidade')} | R$ {item.get('valor_unitario')} | R$ {item.get('total_mensal')}")
        for item in proposta.get("servidores_items", []):
            linhas.append(f"{item.get('nome')} | {item.get('quantidade')} | R$ {item.get('valor_mensal')} | R$ {item.get('total_mensal')}")
        linhas.extend([
            f"TOTAL MENSAL	R$ {cls._string_decimal(proposta.get('total_mensal'))}",
            f"Setup: {proposta.get('setup_dias')} dias após a entrega do ambiente.",
            f"Mensalidade: {proposta.get('mensalidade_dias')} dias após a entrega do ambiente.",
            f"Prazo contratual: {proposta.get('prazo_contratual_meses')} meses.",
        ])
        return linhas

    @staticmethod
    def _docx_content_types():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'

    @staticmethod
    def _docx_root_rels():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'

    @staticmethod
    def _docx_document_rels():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'

    @staticmethod
    def _docx_styles():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>'

    @staticmethod
    def _docx_core():
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Proposta Comercial O3 Cloud</dc:title><dc:creator>O3Cloud Manager</dc:creator><cp:lastModifiedBy>O3Cloud Manager</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'

    @staticmethod
    def _docx_app():
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>O3Cloud Manager</Application></Properties>'

    @classmethod
    def _docx_document(cls, linhas):
        corpo = ''.join(f'<w:p><w:r><w:t xml:space="preserve">{escape(linha or "")}</w:t></w:r></w:p>' for linha in linhas)
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" mc:Ignorable="w14 wp14"><w:body>' + corpo + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>'

    @staticmethod
    def _carregar_lista_json(bruto=None, fallback=None):
        if isinstance(fallback, list):
            return fallback
        if isinstance(bruto, list):
            return bruto
        if not bruto:
            return []
        try:
            dados = json.loads(bruto)
        except (TypeError, ValueError):
            return []
        return dados if isinstance(dados, list) else []

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default
        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _normalizar_status_ativo(valor):
        if valor in (None, "", "todos"):
            return None
        if str(valor) == "1":
            return 1
        if str(valor) == "0":
            return 0
        return None

    @staticmethod
    def _decimal(valor):
        if isinstance(valor, Decimal):
            return valor.quantize(Decimal("0.01"))
        if valor in (None, ""):
            return None
        try:
            texto = str(valor).replace("R$", "").replace(" ", "").strip()
            if "," in texto:
                texto = texto.replace(".", "").replace(",", ".")
            return Decimal(texto).quantize(Decimal("0.01"))
        except InvalidOperation:
            raise ValueError("Valor monetário inválido na proposta.")

    @staticmethod
    def _normalizar_data(valor):
        if valor in (None, ""):
            return None
        return date.fromisoformat(str(valor))

    @staticmethod
    def _string_data(valor):
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        return valor or ""

    @staticmethod
    def _string_decimal(valor, default=None):
        if valor in (None, ""):
            return default
        if not isinstance(valor, Decimal):
            valor = PropostaService._decimal(valor)
        if valor is None:
            return default
        return f"{valor:.2f}"

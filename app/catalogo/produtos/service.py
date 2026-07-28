"""
Service de Produtos do Catálogo Técnico.

Responsável pelas regras de negócio.

Não conhece banco de dados.
Não conhece Flask.
Não conhece HTML.

Toda persistência é feita pelo ProdutoRepository.
"""

import csv
import io

from app.catalogo.produtos.repository import ProdutoRepository


class ProdutoService:

    repository = ProdutoRepository

    TIPOS_RECURSO = (
        "VM",
        "LXC",
        "CPU",
        "RAM",
        "DISCO",
        "STORAGE",
        "BACKUP",
        "LICENCA",
        "SERVICO",
        "OUTRO",
    )

    ####################################################################
    # CONSULTAS
    ####################################################################

    @classmethod
    def listar(cls):

        return cls.repository.listar()

    @classmethod
    def buscar(cls, produto_id):

        return cls.repository.buscar(produto_id)

    @classmethod
    def buscar_por_codigo(cls, codigo):

        return cls.repository.buscar_por_codigo(codigo)

    @classmethod
    def buscar_por_nome(cls, nome):

        return cls.repository.buscar_por_nome(nome)

    @classmethod
    def contar(cls):

        return cls.repository.contar()

    @classmethod
    def listar_custos_pendentes(cls):

        return cls.repository.listar_custos_pendentes()

    @classmethod
    def importar_custos_csv(cls, arquivo):

        if not arquivo or not arquivo.filename:
            raise ValueError("Selecione um arquivo CSV para importar.")

        conteudo = arquivo.read().decode("utf-8-sig", errors="replace")
        if not conteudo.strip():
            raise ValueError("Arquivo CSV vazio.")

        linhas = cls._ler_csv(conteudo)
        if not linhas:
            raise ValueError("Nenhuma linha encontrada no CSV.")

        resumo = {"processadas": 0, "atualizadas": 0, "ignoradas": 0, "erros": []}

        for numero, linha in enumerate(linhas, start=2):
            try:
                normalizada = {cls._normalizar_header(chave): valor for chave, valor in linha.items()}
                codigo = cls._valor(normalizada, "codigo", "produto_codigo").strip().upper()
                valor_raw = cls._valor(normalizada, "valor_custo", "custo")

                if not codigo and not str(valor_raw or "").strip():
                    resumo["ignoradas"] += 1
                    continue
                if not codigo:
                    raise ValueError("Codigo do produto e obrigatorio.")

                produto = cls.buscar_por_codigo(codigo)
                if not produto or not produto.get("ativo"):
                    raise ValueError("Produto ativo nao encontrado.")

                valor_custo = cls._normalizar_decimal(valor_raw)
                if valor_custo <= 0:
                    raise ValueError("Valor de custo deve ser maior que zero.")

                cls.repository.atualizar_custo_por_codigo(codigo, valor_custo)
                resumo["atualizadas"] += 1
                resumo["processadas"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Linha {numero}: {erro}")

        return resumo

    @staticmethod
    def linhas_exportacao_custos(produtos):

        linhas = []
        for produto in produtos:
            linhas.append([
                produto.get("codigo"),
                produto.get("codigo_externo") or "",
                produto.get("nome"),
                produto.get("categoria"),
                produto.get("tipo_recurso"),
                produto.get("itens_vinculados") or 0,
                produto.get("clientes_total") or 0,
                produto.get("valor_total_itens") or 0,
                "",
            ])
        return linhas

    ####################################################################
    # CADASTRO
    ####################################################################

    @classmethod
    def criar(cls, dados):

        dados = cls.normalizar(dados)

        cls.validar(dados)

        if cls.repository.existe(dados["codigo"]):

            raise ValueError(
                "Já existe um produto com este código."
            )

        produto = cls.buscar_por_nome(dados["nome"])

        if produto:

            raise ValueError(
                "Já existe um produto com este nome."
            )

        return cls.repository.inserir(dados)

    ####################################################################
    # ALTERAÇÃO
    ####################################################################

    @classmethod
    def atualizar(cls, produto_id, dados):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        dados = cls.normalizar(dados)

        cls.validar(dados)

        produto_codigo = cls.buscar_por_codigo(
            dados["codigo"]
        )

        if produto_codigo and produto_codigo["id"] != produto_id:

            raise ValueError(
                "Já existe outro produto com este código."
            )

        produto_nome = cls.buscar_por_nome(
            dados["nome"]
        )

        if produto_nome and produto_nome["id"] != produto_id:

            raise ValueError(
                "Já existe outro produto com este nome."
            )

        return cls.repository.atualizar(
            produto_id,
            dados
        )

    ####################################################################
    # DESATIVAÇÃO
    ####################################################################

    @classmethod
    def desativar(cls, produto_id):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        return cls.repository.desativar(produto_id)

    ####################################################################
    # REATIVAÇÃO
    ####################################################################

    @classmethod
    def reativar(cls, produto_id):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        return cls.repository.reativar(produto_id)

    ####################################################################
    # LISTAS AUXILIARES
    ####################################################################

    @classmethod
    def listar_categorias(cls):

        return cls.repository.listar_categorias()

    @classmethod
    def listar_parceiros(cls):

        return cls.repository.listar_parceiros()

    @classmethod
    def listar_tipos_recurso(cls):

        return cls.repository.listar_tipos_recurso()

    ####################################################################
    # NORMALIZAÇÃO
    ####################################################################

    @classmethod
    def normalizar(cls, dados):

        dados = dict(dados)

        dados["categoria_id"] = int(dados["categoria_id"])
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))

        dados["codigo"] = dados["codigo"].strip().upper()

        dados["nome"] = dados["nome"].strip()

        dados["descricao"] = (
            dados.get("descricao") or ""
        ).strip()

        dados["codigo_externo"] = (
            dados.get("codigo_externo") or ""
        ).strip()

        dados["unidade"] = dados["unidade"].strip().upper()

        dados["tipo_recurso"] = (
            dados.get("tipo_recurso") or "SERVICO"
        ).strip().upper()

        dados["origem"] = (
            dados.get("origem") or "MANUAL"
        ).strip().upper()

        dados["valor_venda"] = float(
            str(
                dados.get("valor_venda", 0)
            ).replace(",", ".")
        )

        dados["valor_custo"] = float(
            str(
                dados.get("valor_custo", 0)
            ).replace(",", ".")
        )

        dados["ativo"] = bool(
            dados.get("ativo", True)
        )

        return dados

    ####################################################################
    # VALIDAÇÕES
    ####################################################################

    @classmethod
    def validar(cls, dados):

        if not dados["categoria_id"]:

            raise ValueError(
                "Categoria é obrigatória."
            )

        if not dados["codigo"]:

            raise ValueError(
                "Código é obrigatório."
            )

        if not dados["nome"]:

            raise ValueError(
                "Nome é obrigatório."
            )

        if not dados["unidade"]:

            raise ValueError(
                "Unidade é obrigatória."
            )

        if dados["tipo_recurso"] not in cls.TIPOS_RECURSO:

            raise ValueError(
                "Tipo de recurso inválido."
            )

        if len(dados["codigo"]) > 30:

            raise ValueError(
                "Código deve possuir no máximo 30 caracteres."
            )

        if len(dados["nome"]) > 150:

            raise ValueError(
                "Nome deve possuir no máximo 150 caracteres."
            )

        return True

    @staticmethod
    def _ler_csv(conteudo):

        amostra = conteudo[:4096]
        try:
            dialect = csv.Sniffer().sniff(amostra, delimiters="	;,|")
        except csv.Error:
            dialect = csv.excel_tab if "	" in amostra else csv.excel

        reader = csv.reader(io.StringIO(conteudo), dialect)
        rows = [row for row in reader if any((coluna or "").strip() for coluna in row)]
        if not rows:
            return []

        headers = ProdutoService._headers_unicos(rows[0])
        resultado = []
        for row in rows[1:]:
            if len(row) < len(headers):
                row = row + [""] * (len(headers) - len(row))
            if len(row) > len(headers):
                row = row[:len(headers)]
            resultado.append(dict(zip(headers, row)))
        return resultado

    @staticmethod
    def _headers_unicos(headers):

        resultado = []
        vistos = {}
        for index, header in enumerate(headers):
            nome = (header or "").strip() or f"coluna_{index + 1}"
            vistos[nome] = vistos.get(nome, 0) + 1
            if vistos[nome] > 1:
                nome = f"{nome}_{vistos[nome]}"
            resultado.append(nome)
        return resultado

    @staticmethod
    def _normalizar_header(valor):

        texto = (valor or "").strip().lower()
        substituicoes = {
            "ç": "c", "ã": "a", "á": "a", "à": "a", "â": "a", "é": "e", "ê": "e",
            "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", ":": "", "/": "_",
        }
        for origem, destino in substituicoes.items():
            texto = texto.replace(origem, destino)
        return "_".join(parte for parte in texto.replace("-", " ").split() if parte)

    @staticmethod
    def _valor(dados, *nomes):

        for nome in nomes:
            chave = ProdutoService._normalizar_header(nome)
            if chave in dados:
                return dados.get(chave) or ""
        return ""

    @staticmethod
    def _normalizar_decimal(valor):

        texto = str(valor or "").strip()
        if not texto:
            raise ValueError("Valor de custo e obrigatorio.")
        texto = texto.replace("R$", "").replace(" ", "")
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", ".")
        try:
            valor_decimal = float(texto)
        except ValueError as erro:
            raise ValueError("Valor de custo invalido.") from erro
        return round(valor_decimal, 2)

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default

        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

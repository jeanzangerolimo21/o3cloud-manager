import csv
import io
from datetime import datetime

from app.repositories.o3web_licenca_repository import O3WebLicencaRepository


TIPOS_LICENCA_O3WEB = {
    "permanent": "Permanente",
    "trial": "Trial",
}


class O3WebLicencaService:
    repository = O3WebLicencaRepository

    @classmethod
    def listar(cls, pesquisa=None, tipo=None, ativo="1", pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_ativo(ativo)
        licencas = cls.repository.listar(
            pesquisa=pesquisa,
            tipo=tipo,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(pesquisa=pesquisa, tipo=tipo, ativo=ativo_normalizado)
        return licencas, total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

    @classmethod
    def buscar_por_id(cls, licenca_id):
        return cls.repository.buscar_por_id(licenca_id)

    @classmethod
    def criar(cls, dados):
        payload = cls._normalizar(dados)
        return cls.repository.inserir(payload)

    @classmethod
    def atualizar(cls, licenca_id, dados):
        if not cls.repository.buscar_por_id(licenca_id):
            raise ValueError("Licença O3Web não encontrada.")
        payload = cls._normalizar(dados)
        cls.repository.atualizar(licenca_id, payload)

    @classmethod
    def excluir(cls, licenca_id):
        if not cls.repository.buscar_por_id(licenca_id):
            raise ValueError("Licença O3Web não encontrada.")
        cls.repository.excluir(licenca_id)

    @classmethod
    def importar_csv(cls, arquivo):
        if not arquivo or not arquivo.filename:
            raise ValueError("Selecione um arquivo CSV para importar.")
        conteudo = arquivo.read().decode("utf-8-sig", errors="replace")
        if not conteudo.strip():
            raise ValueError("Arquivo CSV vazio.")

        linhas = cls._ler_csv(conteudo)
        if not linhas:
            raise ValueError("Nenhuma linha encontrada no CSV.")

        resumo = {"processadas": 0, "criadas": 0, "atualizadas": 0, "ignoradas": 0, "erros": []}
        for numero, linha in enumerate(linhas, start=2):
            try:
                dados = cls._linha_para_payload(linha)
                if not dados.get("cliente_nome"):
                    resumo["ignoradas"] += 1
                    continue
                existente = cls.repository.buscar_por_id_licenca(dados.get("id_licenca"))
                if not existente:
                    existente = cls.repository.buscar_por_chave_cliente_url(
                        dados.get("chave_ativacao"),
                        dados.get("cliente_nome"),
                        dados.get("url_principal"),
                    )
                if existente:
                    cls.repository.atualizar(existente.get("id"), dados)
                    resumo["atualizadas"] += 1
                else:
                    cls.repository.inserir(dados)
                    resumo["criadas"] += 1
                resumo["processadas"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Linha {numero}: {erro}")
        return resumo

    @classmethod
    def _normalizar(cls, dados):
        data_ativacao, data_ativacao_raw = cls._normalizar_data(dados.get("data_ativacao") or dados.get("data_ativacao_raw"))
        data_expiracao, data_expiracao_raw = cls._normalizar_data(dados.get("data_expiracao") or dados.get("data_expiracao_raw"))
        cliente_nome = (dados.get("cliente_nome") or dados.get("cliente") or "").strip()
        if not cliente_nome:
            raise ValueError("Cliente é obrigatório.")
        return {
            "chave_ativacao": cls._texto(dados.get("chave_ativacao")),
            "id_licenca": cls._texto(dados.get("id_licenca")),
            "tipo": cls._texto(dados.get("tipo")),
            "bkp": cls._bool(dados.get("bkp")),
            "dias": cls._inteiro(dados.get("dias")),
            "usuarios": cls._inteiro(dados.get("usuarios")),
            "edicao": cls._texto(dados.get("edicao")),
            "data_ativacao": data_ativacao,
            "data_ativacao_raw": data_ativacao_raw,
            "data_expiracao": data_expiracao,
            "data_expiracao_raw": data_expiracao_raw,
            "cliente_nome": cliente_nome,
            "url_principal": cls._texto(dados.get("url_principal")),
            "url_secundaria": cls._texto(dados.get("url_secundaria")),
            "comments": cls._texto_longo(dados.get("comments")),
            "observacao": cls._texto_longo(dados.get("observacao")),
            "origem": dados.get("origem") or "MANUAL",
            "ativo": 1 if str(dados.get("ativo", "1")) != "0" else 0,
        }

    @classmethod
    def _linha_para_payload(cls, linha):
        normalizada = {cls._normalizar_header(chave): valor for chave, valor in linha.items()}
        return cls._normalizar({
            "chave_ativacao": cls._valor(normalizada, "chave_ativacao", "chave", "ativacao"),
            "id_licenca": cls._valor(normalizada, "id_licenca", "id", "licenca"),
            "tipo": cls._valor(normalizada, "tipo"),
            "bkp": cls._valor(normalizada, "bkp", "backup"),
            "dias": cls._valor(normalizada, "dias"),
            "usuarios": cls._valor(normalizada, "usuarios", "usuario", "users"),
            "edicao": cls._valor(normalizada, "edicao", "edição", "edition"),
            "data_ativacao": cls._valor(normalizada, "data_ativacao", "ativacao_data"),
            "data_expiracao": cls._valor(normalizada, "data_de_expiracao", "data_expiracao", "expiracao"),
            "cliente_nome": cls._valor(normalizada, "cliente", "cliente_nome"),
            "url_principal": cls._valor(normalizada, "url", "url_principal", "url_1"),
            "url_secundaria": cls._valor(normalizada, "url_2", "url_secundaria"),
            "comments": cls._valor(normalizada, "comments", "comentarios", "comentario"),
            "observacao": cls._valor(normalizada, "observacao", "observação"),
            "origem": "CSV",
            "ativo": 1,
        })

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
        headers = rows[0]
        headers = O3WebLicencaService._headers_unicos(headers)
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
        fallback = [
            "chave_ativacao", "id_licenca", "tipo", "bkp", "dias", "usuarios", "edicao",
            "data_ativacao", "data_expiracao", "cliente", "url", "url_2", "comments", "observacao",
        ]
        resultado = []
        vistos = {}
        for index, header in enumerate(headers):
            nome = (header or "").strip() or (fallback[index] if index < len(fallback) else f"coluna_{index + 1}")
            base = nome
            vistos[base] = vistos.get(base, 0) + 1
            if vistos[base] > 1:
                nome = f"{base}_{vistos[base]}"
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
            chave = O3WebLicencaService._normalizar_header(nome)
            if chave in dados:
                return dados.get(chave)
        return None

    @staticmethod
    def _normalizar_data(valor):
        raw = O3WebLicencaService._texto(valor)
        if not raw or raw in ("-", "null", "Null", "NULL"):
            return None, raw
        formatos = [
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
            "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
        ]
        for formato in formatos:
            try:
                data = datetime.strptime(raw, formato)
                if data.year < 1900:
                    return None, raw
                return data.strftime("%Y-%m-%d %H:%M:%S"), raw
            except ValueError:
                continue
        return None, raw

    @staticmethod
    def _bool(valor):
        return str(valor or "").strip().lower() in ("1", "true", "sim", "yes", "s", "y")

    @staticmethod
    def _inteiro(valor):
        texto = str(valor or "").strip()
        if not texto:
            return None
        try:
            return int(float(texto.replace(",", ".")))
        except ValueError:
            return None

    @staticmethod
    def _texto(valor):
        texto = str(valor or "").strip()
        return texto or None

    @staticmethod
    def _texto_longo(valor):
        return O3WebLicencaService._texto(valor)

    @staticmethod
    def _normalizar_ativo(valor):
        if valor == "todos":
            return None
        if str(valor) == "0":
            return 0
        return 1

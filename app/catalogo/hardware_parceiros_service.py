import csv
import io
import unicodedata

from app.repositories.hardware_parceiros_repository import HardwareParceirosRepository


class HardwareParceirosService:
    repository = HardwareParceirosRepository
    ORIGEM_CSV = "CSV_TABELA_HARDWARE_PARCEIROS"

    @classmethod
    def listar(cls, parceiro=None):
        return cls.repository.listar(parceiro=parceiro)

    @classmethod
    def listar_parceiros(cls):
        return cls.repository.listar_parceiros()


    @classmethod
    def buscar(cls, item_id):
        return cls.repository.buscar(item_id)

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, item_id, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.atualizar(item_id, dados)

    @classmethod
    def excluir(cls, item_id):
        return cls.repository.excluir(item_id)

    @classmethod
    def importar_csv(cls, arquivo):
        conteudo = arquivo.read()
        if isinstance(conteudo, bytes):
            conteudo = conteudo.decode("utf-8-sig")
        linhas = list(csv.reader(io.StringIO(conteudo)))
        if len(linhas) < 4:
            raise ValueError("O CSV não possui linhas suficientes para importação.")

        grupos = []
        largura = max(len(linha) for linha in linhas)
        for inicio in range(0, largura, 5):
            titulo = (linhas[0][inicio] if inicio < len(linhas[0]) else "").strip()
            if not titulo:
                continue
            parceiro = cls._normalizar_parceiro(titulo)
            grupos.append((inicio, parceiro))

        registros = []
        ordem = 0
        for inicio, parceiro in grupos:
            secao = ""
            for linha in linhas[2:]:
                bloco = [(linha[i].strip() if i < len(linha) else "") for i in range(inicio, inicio + 5)]
                if not any(bloco):
                    continue
                primeira = bloco[0]
                cabecalho = " ".join(bloco).upper()
                if "MEMÓRIA" in cabecalho or "MEMORIA" in cabecalho:
                    secao = primeira or secao
                    continue
                if not primeira or not any(bloco[1:]):
                    continue
                if not secao:
                    secao = "Hardware"
                registros.append({
                    "parceiro": parceiro,
                    "secao": secao,
                    "faixa_usuarios": primeira,
                    "memoria": bloco[1],
                    "processador": bloco[2],
                    "disco": bloco[3],
                    "origem": cls.ORIGEM_CSV,
                    "ordem": ordem,
                    "ativo": True,
                })
                ordem += 1

        if not registros:
            raise ValueError("Nenhum item de hardware válido foi encontrado no CSV.")

        cls.repository.limpar_importados()
        for registro in registros:
            cls.repository.inserir(registro)
        return len(registros)

    @staticmethod
    def _normalizar_parceiro(titulo):
        texto = titulo.strip()
        simples = "".join(
            char for char in unicodedata.normalize("NFKD", texto)
            if not unicodedata.combining(char)
        )
        simples = simples.upper()
        for prefixo in (
            "TABELA DE HARDWARE POR USUARIOS - ",
            "TABELA DE HARDWARE POR USUAROS - ",
            "TABELA DE HARDWARE ",
        ):
            if simples.startswith(prefixo):
                return simples[len(prefixo):].strip()
        return texto

    @staticmethod
    def normalizar(dados):
        dados = dict(dados)
        for campo in ("parceiro", "secao", "faixa_usuarios", "memoria", "processador", "disco"):
            dados[campo] = (dados.get(campo) or "").strip()
        try:
            dados["ordem"] = int(dados.get("ordem") or 0)
        except (TypeError, ValueError):
            dados["ordem"] = 0
        dados["ativo"] = bool(dados.get("ativo"))
        return dados

    @staticmethod
    def validar(dados):
        for campo, rotulo in (
            ("parceiro", "Parceiro"),
            ("secao", "Seção"),
            ("faixa_usuarios", "Faixa de usuários"),
        ):
            if not dados[campo]:
                raise ValueError(f"{rotulo} é obrigatório.")
        if dados["ordem"] < 0:
            raise ValueError("Ordem não pode ser negativa.")

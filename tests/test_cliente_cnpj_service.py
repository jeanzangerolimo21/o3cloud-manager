import requests
from flask import Flask

from app.clientes.cnpj_service import CnpjService
from app.clientes.routes import clientes_bp


class RespostaFake:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "razao_social": "EMPRESA TESTE LTDA",
            "nome_fantasia": "EMPRESA TESTE",
            "email": "contato@empresa.test",
            "ddd_telefone_1": "1133334444",
            "municipio": "SAO PAULO",
            "uf": "SP",
        }


class RespostaLimitadaFake:
    status_code = 429


class RespostaReceitaWsFake:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "status": "OK",
            "nome": "EMPRESA FALLBACK LTDA",
            "fantasia": "EMPRESA FALLBACK",
            "email": "fallback@empresa.test",
            "telefone": "(11) 2222-3333",
            "municipio": "CAMPINAS",
            "uf": "SP",
        }


def test_consulta_cnpj_normaliza_e_mapeia_resposta(monkeypatch):
    chamadas = []

    def get(url, **kwargs):
        chamadas.append((url, kwargs))
        return RespostaFake()

    monkeypatch.setattr(requests, "get", get)

    dados = CnpjService.consultar("19.131.243/0001-97")

    assert dados["cnpj"] == "19131243000197"
    assert dados["razao_social"] == "EMPRESA TESTE LTDA"
    assert dados["nome_fantasia"] == "EMPRESA TESTE"
    assert dados["cidade"] == "SAO PAULO"
    assert chamadas[0][0].endswith("/19131243000197")
    assert chamadas[0][1]["timeout"] == 10


def test_consulta_cnpj_rejeita_documento_incompleto():
    try:
        CnpjService.consultar("123")
    except ValueError as erro:
        assert "14 dígitos" in str(erro)
    else:
        raise AssertionError("CNPJ incompleto deveria ser rejeitado")


def test_consulta_cnpj_converte_indisponibilidade(monkeypatch):
    def get(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", get)

    try:
        CnpjService.consultar("19131243000197")
    except RuntimeError as erro:
        assert "indisponíveis" in str(erro)
    else:
        raise AssertionError("Timeout deveria ser convertido em erro de serviço")


def test_consulta_cnpj_usa_receita_ws_quando_brasil_api_limita(monkeypatch):
    respostas = iter([RespostaLimitadaFake(), RespostaReceitaWsFake()])
    chamadas = []

    def get(url, **kwargs):
        chamadas.append(url)
        return next(respostas)

    monkeypatch.setattr(requests, "get", get)

    dados = CnpjService.consultar("19131243000197")

    assert dados["razao_social"] == "EMPRESA FALLBACK LTDA"
    assert dados["nome_fantasia"] == "EMPRESA FALLBACK"
    assert dados["cidade"] == "CAMPINAS"
    assert "brasilapi.com.br" in chamadas[0]
    assert "receitaws.com.br" in chamadas[1]


def test_consulta_cnpj_remove_pontuacao_invalida_do_email(monkeypatch):
    resposta = RespostaFake()
    monkeypatch.setattr(resposta, "json", lambda: {"razao_social": "EMPRESA", "email": "contato@empresa.test."})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: resposta)

    dados = CnpjService.consultar("19131243000197")

    assert dados["email"] == "contato@empresa.test"


def test_rota_consulta_cnpj_retorna_dados_para_o_formulario(monkeypatch):
    monkeypatch.setattr(
        CnpjService,
        "consultar",
        classmethod(lambda cls, cnpj: {"cnpj": cnpj, "razao_social": "EMPRESA TESTE"}),
    )
    app = Flask(__name__)
    app.register_blueprint(clientes_bp)

    resposta = app.test_client().get("/clientes/consulta-cnpj?cnpj=19131243000197")

    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "ok": True,
        "cnpj": "19131243000197",
        "razao_social": "EMPRESA TESTE",
    }

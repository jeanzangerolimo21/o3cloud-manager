from app.repositories.cliente_repository import ClienteRepository


def test_upsert_omie_atualiza_cliente_encontrado_pelo_codigo(monkeypatch):
    atualizacoes = []

    monkeypatch.setattr(
        ClienteRepository,
        "buscar_por_codigo_externo",
        classmethod(lambda cls, codigo: {"id": 10}),
    )
    monkeypatch.setattr(
        ClienteRepository,
        "buscar_por_cnpj",
        classmethod(lambda cls, cnpj: {"id": 10}),
    )
    monkeypatch.setattr(
        ClienteRepository,
        "atualizar_sync",
        classmethod(lambda cls, cliente_id, dados: atualizacoes.append(cliente_id)),
    )

    resultado = ClienteRepository.upsert_omie(
        {"codigo_externo": 123, "cnpj": "68566477000172"}
    )

    assert resultado == "UPDATE"
    assert atualizacoes == [10]


def test_upsert_omie_concilia_conflito_entre_codigo_e_cnpj(monkeypatch):
    conciliacoes = []

    monkeypatch.setattr(
        ClienteRepository,
        "buscar_por_codigo_externo",
        classmethod(lambda cls, codigo: {"id": 10}),
    )
    monkeypatch.setattr(
        ClienteRepository,
        "buscar_por_cnpj",
        classmethod(lambda cls, cnpj: {"id": 20}),
    )
    monkeypatch.setattr(
        ClienteRepository,
        "conciliar_omie",
        classmethod(
            lambda cls, codigo_id, cnpj_id, dados: conciliacoes.append(
                (codigo_id, cnpj_id, dados["codigo_externo"])
            )
        ),
    )

    resultado = ClienteRepository.upsert_omie(
        {"codigo_externo": 123, "cnpj": "68566477000172"}
    )

    assert resultado == "UPDATE"
    assert conciliacoes == [(10, 20, 123)]

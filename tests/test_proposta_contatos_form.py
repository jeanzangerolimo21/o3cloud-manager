from app.propostas.service import PropostaService


def test_contato_comercial_aceita_comercial_e_representante_legal():
    contatos = [
        {"id": 1, "tipo_contato": "COMERCIAL"},
        {"id": 2, "tipo_contato": "REPRESENTANTE_LEGAL"},
        {"id": 3, "tipo_contato": "FINANCEIRO"},
    ]

    resultado = PropostaService._filtrar_contatos_por_tipos(
        contatos, "COMERCIAL", "REPRESENTANTE_LEGAL"
    )

    assert [contato["id"] for contato in resultado] == [1, 2]


def test_representante_legal_continua_restrito_ao_tipo_correto():
    contatos = [
        {"id": 1, "tipo_contato": "COMERCIAL"},
        {"id": 2, "tipo_contato": "REPRESENTANTE_LEGAL"},
    ]

    resultado = PropostaService._filtrar_contatos_por_tipos(contatos, "REPRESENTANTE_LEGAL")

    assert resultado == [contatos[1]]

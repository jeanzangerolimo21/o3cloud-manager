import pytest

from app.implantacao.faixas_rede_service import FaixaRedeService
from app.repositories.faixa_rede_repository import FaixaRedeRepository


def test_listagem_ordena_por_fw_wan_crescente_e_deixa_nulos_no_final(monkeypatch):
    consulta = {}

    def fetch_all(sql, params):
        consulta["sql"] = sql
        consulta["params"] = params
        return []

    monkeypatch.setattr(FaixaRedeRepository, "fetch_all", fetch_all)

    FaixaRedeRepository.listar(limit=50, offset=0)

    sql = " ".join(consulta["sql"].split())
    assert "fr.fw_wan IS NULL ASC" in sql
    assert "INET_ATON(fr.fw_wan) ASC" in sql
    assert "SUBSTRING_INDEX(fr.rede" not in sql


def test_criar_recusa_fw_wan_ja_cadastrado(monkeypatch):
    payload = {"rede": "10.10.10.0/29", "fw_wan": "192.0.2.10"}
    monkeypatch.setattr(FaixaRedeService, "_normalizar", lambda dados: payload)
    monkeypatch.setattr(FaixaRedeService.repository, "buscar_por_rede", lambda rede: None)
    monkeypatch.setattr(
        FaixaRedeService.repository,
        "buscar_por_fw_wan",
        lambda fw_wan, ignorar_id=None: {"id": 7, "fw_wan": fw_wan},
    )

    with pytest.raises(ValueError, match="IP FW - WAN 192.0.2.10 já está cadastrado"):
        FaixaRedeService.criar({})


def test_atualizar_permite_manter_fw_wan_do_proprio_cadastro(monkeypatch):
    payload = {"rede": "10.10.10.0/29", "fw_wan": "192.0.2.10"}
    atualizado = {}
    monkeypatch.setattr(FaixaRedeService, "_normalizar", lambda dados: payload)
    monkeypatch.setattr(FaixaRedeService.repository, "buscar_por_id", lambda faixa_id: {"id": faixa_id})
    monkeypatch.setattr(FaixaRedeService.repository, "buscar_por_rede", lambda rede: {"id": 7})
    monkeypatch.setattr(
        FaixaRedeService.repository,
        "buscar_por_fw_wan",
        lambda fw_wan, ignorar_id=None: None,
    )
    monkeypatch.setattr(FaixaRedeService, "_validar_conflito_portas", lambda dados, ignorar_id=None: None)
    monkeypatch.setattr(
        FaixaRedeService.repository,
        "atualizar",
        lambda faixa_id, dados: atualizado.update({"id": faixa_id, "dados": dados}),
    )

    FaixaRedeService.atualizar(7, {})

    assert atualizado == {"id": 7, "dados": payload}

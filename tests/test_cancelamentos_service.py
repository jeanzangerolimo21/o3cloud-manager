from datetime import datetime

import pytest

from app.financeiro.cancelamentos_service import CancelamentoService
from app.financeiro.cancelamentos_repository import CancelamentoRepository
from app.core.access_control import ENDPOINT_PERMISSOES, MENU_PERMISSOES


class DadosMultiplos(dict):
    def getlist(self, chave):
        valor = self.get(chave, [])
        return valor if isinstance(valor, list) else [valor]


def _contratos():
    return [
        {"id": 10, "numero": "2026/010", "status": "ATIVO", "cliente_id": 7},
        {"id": 11, "numero": "2026/011", "status": "ENCAMINHADO_PROJETO", "cliente_id": 7},
    ]


def test_registrar_cancelamento_com_multiplos_contratos_e_observacoes(monkeypatch):
    gravado = {}
    item = {
        "id": 44,
        "cliente_nome": "Cliente Exemplo",
        "cliente_razao_social": "Cliente Exemplo Ltda",
        "cliente_cnpj": "12345678000190",
        "data_desligamento": datetime(2026, 11, 1, 18, 0),
        "motivo": "Encerramento contratual",
        "observacoes": "Preservar uma cópia até autorização do jurídico.",
        "solicitado_por_email": "usuario@o3cloud.com.br",
        "contratos": _contratos(),
        "ambientes": [],
    }

    monkeypatch.setattr(CancelamentoService.repository, "buscar_contratos_ids", lambda ids: _contratos())
    monkeypatch.setattr(CancelamentoService.repository, "buscar_ativos_por_contratos", lambda ids: [])
    monkeypatch.setattr(CancelamentoService.repository, "criar", lambda dados: gravado.update(dados) or 44)
    monkeypatch.setattr(CancelamentoService, "buscar_por_id", classmethod(lambda cls, cancelamento_id: item))
    monkeypatch.setattr(CancelamentoService.repository, "registrar_resultado_email", lambda cancelamento_id, resultado: True)
    envios = []
    monkeypatch.setattr(
        "app.financeiro.cancelamentos_service.EmailService.enviar",
        lambda assunto, corpo, destinatarios: envios.append((assunto, corpo, destinatarios)) or {"enviado": True},
    )

    resultado = CancelamentoService.registrar(
        DadosMultiplos({
            "contrato_ids": ["10", "11"],
            "motivo": "Encerramento contratual",
            "data_desligamento": "2026-11-01T18:00",
            "observacoes": "Preservar uma cópia até autorização do jurídico.",
        }),
        usuario_id=3,
        usuario_email="usuario@o3cloud.com.br",
    )

    assert resultado["id"] == 44
    assert gravado["contrato_ids"] == [10, 11]
    assert gravado["cliente_id"] == 7
    assert envios[0][0] == "Cancelamento - Cliente Exemplo - 12.345.678/0001-90"
    assert "2026/010" in envios[0][1]
    assert "2026/011" in envios[0][1]
    assert "Preservar uma cópia" in envios[0][1]
    assert envios[0][2] == ["sac@o3cloud.com.br"]


def test_registrar_rejeita_contratos_de_clientes_diferentes(monkeypatch):
    contratos = _contratos()
    contratos[1] = {**contratos[1], "cliente_id": 8}
    monkeypatch.setattr(CancelamentoService.repository, "buscar_contratos_ids", lambda ids: contratos)

    with pytest.raises(ValueError, match="mesmo cliente"):
        CancelamentoService.registrar(DadosMultiplos({
            "contrato_ids": ["10", "11"],
            "motivo": "Cancelamento",
            "data_desligamento": "2026-11-01T18:00",
        }))


def test_falha_smtp_nao_descarta_cancelamento(monkeypatch):
    resultados = []
    item = {
        "id": 45, "cliente_nome": "Cliente", "cliente_cnpj": "12345678000190",
        "data_desligamento": datetime(2026, 11, 1, 18, 0), "motivo": "Cancelamento",
        "contratos": _contratos()[:1], "ambientes": [],
    }
    monkeypatch.setattr(CancelamentoService.repository, "buscar_contratos_ids", lambda ids: _contratos()[:1])
    monkeypatch.setattr(CancelamentoService.repository, "buscar_ativos_por_contratos", lambda ids: [])
    monkeypatch.setattr(CancelamentoService.repository, "criar", lambda dados: 45)
    monkeypatch.setattr(CancelamentoService, "buscar_por_id", classmethod(lambda cls, cancelamento_id: item))
    monkeypatch.setattr(CancelamentoService.repository, "registrar_resultado_email", lambda cancelamento_id, resultado: resultados.append(resultado))
    monkeypatch.setattr("app.financeiro.cancelamentos_service.EmailService.enviar", lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError("SMTP timeout")))

    retorno = CancelamentoService.registrar(DadosMultiplos({
        "contrato_ids": ["10"], "motivo": "Cancelamento", "data_desligamento": "2026-11-01T18:00",
    }))

    assert retorno["id"] == 45
    assert retorno["email"]["enviado"] is False
    assert "SMTP timeout" in retorno["email"]["erro"]
    assert resultados == [retorno["email"]]


def test_migration_cria_relacao_multiplos_contratos():
    sql = open("database/migrations/137_create_financeiro_cancelamentos.sql", encoding="utf-8").read()

    assert "CREATE TABLE IF NOT EXISTS financeiro_cancelamentos" in sql
    assert "CREATE TABLE IF NOT EXISTS financeiro_cancelamento_contratos" in sql
    assert "UNIQUE KEY uk_cancelamento_contrato" in sql
    assert "'cancelamentos'" in sql


def test_consulta_disponibiliza_contratos_ativos_e_encaminhados_para_projeto():
    sql = CancelamentoRepository.contratos_para_select.__func__.__code__.co_consts
    texto = " ".join(item for item in sql if isinstance(item, str))

    assert "c.ativo=1" in texto
    assert "c.status IN ('ATIVO', 'ENCAMINHADO_PROJETO')" in texto


def test_menu_e_endpoints_usam_permissao_cancelamentos():
    assert any(item["key"] == "cancelamentos" for item in MENU_PERMISSOES)
    assert ENDPOINT_PERMISSOES["financeiro.cancelamentos"] == "cancelamentos"
    assert ENDPOINT_PERMISSOES["financeiro.novo_cancelamento"] == "cancelamentos"
    assert ENDPOINT_PERMISSOES["financeiro.reenviar_cancelamento"] == "cancelamentos"

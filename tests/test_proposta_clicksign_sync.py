from datetime import datetime

from app.propostas.service import PropostaService
from app.repositories.proposta_repository import PropostaRepository


def test_concluir_contrato_preserva_pdf_assinado_antes_de_persistir_proposta(monkeypatch):
    atualizado = {}
    assinatura = datetime(2026, 10, 7, 14, 30)

    monkeypatch.setattr(
        PropostaService,
        "buscar_por_id",
        classmethod(lambda cls, proposta_id: {
            "id": proposta_id,
            "clicksign_document_key": "contrato-proposta-001.pdf",
            "clicksign_envelope_id": "envelope-antigo",
            "clicksign_sent_at": datetime(2026, 10, 1, 9, 0),
        }),
    )
    monkeypatch.setattr(
        "app.propostas.service.extrair_data_assinatura_pdf",
        lambda caminho: assinatura,
    )
    monkeypatch.setattr(
        "app.propostas.service.ContratoRepository.buscar_por_proposta_id",
        lambda proposta_id: {"id": 77},
    )

    def atualizar_arquivo(contrato_id, arquivo, arquivo_original, assinado_em=None, envelope_id=None, enviado_em=None):
        atualizado.update({
            "contrato_id": contrato_id,
            "arquivo": arquivo,
            "arquivo_original": arquivo_original,
            "assinado_em": assinado_em,
            "envelope_id": envelope_id,
            "enviado_em": enviado_em,
        })

    monkeypatch.setattr(
        "app.propostas.service.ContratoRepository.atualizar_arquivo_assinado",
        atualizar_arquivo,
    )

    contrato_id = PropostaService.concluir_contrato_clicksign({
        "id": 10,
        "clicksign_document_key": "contrato-o3-proposta-001-assinado.pdf",
        "clicksign_envelope_id": "envelope-final",
        "clicksign_sent_at": datetime(2026, 10, 2, 10, 0),
        "clicksign_signed_at": assinatura,
    })

    assert contrato_id == 77
    assert atualizado["arquivo"] == "contrato-o3-proposta-001-assinado.pdf"
    assert atualizado["arquivo_original"] == "contrato-o3-proposta-001-assinado.pdf"
    assert atualizado["envelope_id"] == "envelope-final"
    assert atualizado["assinado_em"] == assinatura


def test_listagem_desalinhada_compara_arquivo_do_contrato_com_proposta(monkeypatch):
    executado = {}

    class CursorFake:
        def execute(self, sql):
            executado["sql"] = sql

        def fetchall(self):
            return []

        def close(self):
            pass

    class ConnectionFake:
        def cursor(self, dictionary=False):
            return CursorFake()

        def close(self):
            pass

    monkeypatch.setattr(PropostaRepository, "connection", classmethod(lambda cls: ConnectionFake()))

    PropostaRepository.listar_clicksign_assinados_desalinhados()

    assert "c.arquivo_assinado" in executado["sql"]
    assert "p.clicksign_document_key" in executado["sql"]

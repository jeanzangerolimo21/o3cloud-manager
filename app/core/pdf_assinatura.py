import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PDF_SIGNATURE_DATE_RE = re.compile(
    rb"/M\s*\(D:(\d{14})(?:([+-])(\d{2})'?((?:\d{2})?)'?)?\)"
)


def extrair_datas_assinatura_pdf(caminho, timezone_destino="America/Sao_Paulo"):
    caminho = Path(caminho)
    if not caminho.exists() or caminho.suffix.lower() != ".pdf":
        return []
    dados = caminho.read_bytes()
    datas = []
    for match in PDF_SIGNATURE_DATE_RE.finditer(dados):
        data = _parse_pdf_date(match, timezone_destino)
        if data:
            datas.append(data)
    return sorted(set(datas))


def extrair_data_assinatura_pdf(caminho, timezone_destino="America/Sao_Paulo"):
    datas = extrair_datas_assinatura_pdf(caminho, timezone_destino)
    return datas[-1] if datas else None


def _parse_pdf_date(match, timezone_destino):
    try:
        base = datetime.strptime(match.group(1).decode("ascii"), "%Y%m%d%H%M%S")
    except ValueError:
        return None

    sinal = match.group(2)
    if sinal:
        horas = int(match.group(3) or 0)
        minutos = int(match.group(4) or 0)
        offset_minutos = horas * 60 + minutos
        if sinal == b"-":
            offset_minutos = -offset_minutos
        origem = timezone.utc if offset_minutos == 0 else timezone(timedelta(minutes=offset_minutos))
        base = base.replace(tzinfo=origem)
    else:
        base = base.replace(tzinfo=timezone.utc)

    return base.astimezone(ZoneInfo(timezone_destino)).replace(tzinfo=None)

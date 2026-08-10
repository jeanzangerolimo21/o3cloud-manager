from datetime import date, datetime
from app.utils.telefone import formatar_telefone


def date_br(value):

    if not value:
        return "-"

    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")

    return str(value)


def datetime_br(value):

    if not value:
        return "-"

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    return str(value)


def telefone_br(value):
    return formatar_telefone(value)


def cnpj_br(value):
    if not value:
        return "-"

    texto = str(value).strip()
    digitos = "".join(ch for ch in texto if ch.isdigit())
    if len(digitos) != 14:
        return texto

    return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


def moeda(value):

    if value is None:
        value = 0

    valor = f"{float(value):,.2f}"

    return "R$ " + valor.replace(",", "X").replace(".", ",").replace("X", ".")

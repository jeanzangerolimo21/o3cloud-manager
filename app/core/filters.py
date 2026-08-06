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


def moeda(value):

    if value is None:
        value = 0

    valor = f"{float(value):,.2f}"

    return "R$ " + valor.replace(",", "X").replace(".", ",").replace("X", ".")

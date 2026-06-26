from datetime import date, datetime


def date_br(value):

    if not value:
        return "-"

    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")

    return str(value)


def moeda(value):

    if value is None:
        value = 0

    valor = f"{float(value):,.2f}"

    return "R$ " + valor.replace(",", "X").replace(".", ",").replace("X", ".")

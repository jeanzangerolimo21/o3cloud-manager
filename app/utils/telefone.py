import re


def formatar_telefone(valor):
    telefone = (valor or "").strip()
    if not telefone:
        return ""

    digitos = re.sub(r"\D", "", telefone)

    if len(digitos) in (12, 13) and digitos.startswith("55"):
        digitos = digitos[2:]

    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"

    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"

    return telefone

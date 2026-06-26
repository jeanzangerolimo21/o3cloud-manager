import re


def limpar_documento(valor):

    if not valor:
        return ""

    return re.sub(r"\D", "", valor)


def limpar_telefone(valor):

    if not valor:
        return ""

    return re.sub(r"\D", "", valor)

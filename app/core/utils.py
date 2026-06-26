from datetime import datetime


def now():

    return datetime.now()


def bool_to_status(valor):

    return "Ativo" if valor else "Inativo"

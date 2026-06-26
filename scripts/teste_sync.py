import os
import requests
from dotenv import load_dotenv

load_dotenv()

payload = {
    "call": "ListarClientes",
    "app_key": os.getenv("OMIE_APP_KEY"),
    "app_secret": os.getenv("OMIE_APP_SECRET"),
    "param": [{
        "pagina": 1,
        "registros_por_pagina": 1
    }]
}

r = requests.post(
    "https://app.omie.com.br/api/v1/geral/clientes/",
    json=payload,
    timeout=30
)

print(r.status_code)
print(r.text[:500])

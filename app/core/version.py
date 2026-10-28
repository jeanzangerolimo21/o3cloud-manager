import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def obter_versao_aplicacao():
    versao_configurada = (os.getenv("APP_VERSION") or "").strip()
    if versao_configurada:
        return versao_configurada

    try:
        resultado = subprocess.run(
            ["git", "describe", "--tags", "--always", "--abbrev=7"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        versao = resultado.stdout.strip()
        if versao:
            return versao
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        pass

    return "versão não identificada"

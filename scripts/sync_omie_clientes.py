import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.integracoes.omie.sync import OmieSync

if __name__ == "__main__":
    OmieSync().sincronizar_clientes()

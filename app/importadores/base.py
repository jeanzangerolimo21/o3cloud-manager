from abc import ABC, abstractmethod


class BaseImporter(ABC):

    def __init__(self):

        self.logs = []

        self.errors = []

    @abstractmethod
    def executar(self, arquivo):

        pass

    def info(self, mensagem):

        self.logs.append(mensagem)

        print(f"[INFO] {mensagem}")

    def adicionar_erro(self, mensagem):

        self.errors.append(mensagem)

        print(f"[ERRO] {mensagem}")

    def possui_erros(self):

        return len(self.errors) > 0

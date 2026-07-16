import csv


class CSVReader:

    def __init__(self, arquivo):

        self.arquivo = arquivo

    def ler(self):

        with open(

            self.arquivo,

            encoding="utf-8-sig"

        ) as csvfile:

            return list(

                csv.DictReader(csvfile)

            )

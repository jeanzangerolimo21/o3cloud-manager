"""Regras de negocio para precos comerciais do Catalogo Tecnico."""

from app.catalogo.precos.repository import PrecoCatalogoRepository


class PrecoCatalogoService:
    """Coordena persistencia de precos por faixa."""

    repository = PrecoCatalogoRepository

    @classmethod
    def buscar_por_faixa(cls, faixa_id):
        return cls.repository.buscar_por_faixa(faixa_id)

    @classmethod
    def listar_licenciamento(cls):
        return cls.repository.listar_licenciamento()

    @classmethod
    def salvar_por_faixa(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)

        existente = cls.buscar_por_faixa(dados['faixa_id'])
        if existente:
            cls.repository.atualizar_por_faixa(dados['faixa_id'], dados)
            return existente['id']

        return cls.repository.inserir(dados)

    @staticmethod
    def normalizar(dados):
        dados = dict(dados)
        dados['faixa_id'] = int(dados['faixa_id'])
        dados['valor_mensal'] = float(dados.get('valor_mensal') or 0)
        dados['valor_setup'] = float(dados.get('valor_setup') or 0)
        dados['tem_projeto'] = bool(dados.get('tem_projeto', False))
        dados['ativo'] = bool(dados.get('ativo', True))
        return dados

    @staticmethod
    def validar(dados):
        if not dados['faixa_id']:
            raise ValueError('Faixa e obrigatoria para o preco.')

        if dados['valor_mensal'] < 0:
            raise ValueError('Valor mensal nao pode ser negativo.')

        if dados['valor_setup'] < 0:
            raise ValueError('Valor setup/minimo nao pode ser negativo.')

        return True

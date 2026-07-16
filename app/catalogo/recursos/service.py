"""Regras de negocio para recursos comerciais de servidor."""

from app.catalogo.recursos.repository import ProdutoRecursoRepository


class ProdutoRecursoService:
    """Coordena validacoes e persistencia de catalogo_recursos_servidor."""

    repository = ProdutoRecursoRepository
    CATEGORIAS = (
        'Outro',
        'Disco',
        'Processador',
        'Memoria',
        'Backup',
        'IP Fixo',
        'Suporte Premium',
        'Sistema Operacional',
        'Call de Acesso',
        'VPN',
    )
    TIPOS_RECURSO = (
        'CPU',
        'RAM',
        'DISCO',
        'STORAGE',
        'BACKUP',
        'LICENCA',
        'SERVICO',
        'OUTRO',
    )

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar(cls, recurso_id):
        return cls.repository.buscar(recurso_id)

    @classmethod
    def buscar_por_codigo(cls, codigo):
        return cls.repository.buscar_por_codigo(codigo)

    @classmethod
    def buscar_por_nome(cls, nome):
        return cls.repository.buscar_por_nome(nome)

    @classmethod
    def contar(cls):
        return cls.repository.contar()

    @classmethod
    def listar_tipos_recurso(cls):
        return cls.repository.listar_tipos_recurso()

    @classmethod
    def listar_categorias(cls):
        return cls.CATEGORIAS

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)

        if cls.buscar_por_codigo(dados['codigo']):
            raise ValueError('Já existe um recurso com este código.')

        existente = cls.buscar_por_nome(dados['nome'])
        if existente:
            raise ValueError('Já existe um recurso com este nome.')

        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, recurso_id, dados):
        recurso = cls.buscar(recurso_id)
        if not recurso:
            raise ValueError('Recurso não encontrado.')

        dados = cls.normalizar(dados)
        cls.validar(dados)

        codigo = cls.buscar_por_codigo(dados['codigo'])
        if codigo and codigo['id'] != recurso_id:
            raise ValueError('Já existe outro recurso com este código.')

        nome = cls.buscar_por_nome(dados['nome'])
        if nome and nome['id'] != recurso_id:
            raise ValueError('Já existe outro recurso com este nome.')

        return cls.repository.atualizar(recurso_id, dados)

    @classmethod
    def desativar(cls, recurso_id):
        recurso = cls.buscar(recurso_id)
        if not recurso:
            raise ValueError('Recurso não encontrado.')

        return cls.repository.desativar(recurso_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        dados['codigo'] = (dados.get('codigo') or '').strip().upper()
        dados['categoria'] = (dados.get('categoria') or '').strip()
        dados['nome'] = (dados.get('nome') or '').strip()
        dados['descricao'] = (dados.get('descricao') or '').strip()
        dados['tipo_recurso'] = (dados.get('tipo_recurso') or 'SERVICO').strip().upper()
        dados['ordem'] = cls._normalizar_inteiro(dados.get('ordem'), default=0)
        dados['valor_mensal'] = float(str(dados.get('valor_mensal', 0)).replace(',', '.') or 0)
        dados['valor_instalacao'] = float(str(dados.get('valor_instalacao', 0)).replace(',', '.') or 0)
        dados['ativo'] = bool(dados.get('ativo', True))
        return dados

    @classmethod
    def validar(cls, dados):
        if not dados['codigo']:
            raise ValueError('Código é obrigatório.')
        if not dados['categoria']:
            raise ValueError('Categoria é obrigatória.')
        if not dados['nome']:
            raise ValueError('Nome é obrigatório.')
        if dados['categoria'] not in cls.CATEGORIAS:
            raise ValueError('Categoria inválida.')
        if dados['tipo_recurso'] not in cls.TIPOS_RECURSO:
            raise ValueError('Tipo de recurso inválido.')
        if dados['valor_mensal'] < 0:
            raise ValueError('Valor mensal não pode ser negativo.')
        if dados['valor_instalacao'] < 0:
            raise ValueError('Valor de instalação não pode ser negativo.')
        if dados['ordem'] is None or dados['ordem'] < 0:
            raise ValueError('Ordem não pode ser negativa.')
        if len(dados['codigo']) > 30:
            raise ValueError('Código deve possuir no máximo 30 caracteres.')
        if len(dados['categoria']) > 100:
            raise ValueError('Categoria deve possuir no máximo 100 caracteres.')
        if len(dados['nome']) > 150:
            raise ValueError('Nome deve possuir no máximo 150 caracteres.')
        return True

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ''):
            return default
        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

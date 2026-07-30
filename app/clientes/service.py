from app.repositories.cliente_repository import ClienteRepository
from app.utils.telefone import formatar_telefone


class ClienteService:

    @staticmethod
    def listar(pesquisa=None, ativo=None, origem=None, pagina=1):

        limite = 50

        offset = (pagina - 1) * limite

        clientes = ClienteRepository.listar(

            pesquisa=pesquisa,
            limit=limite,
            origem=origem,
            ativo=ativo,
            offset=offset

        )

        clientes = [ClienteService._formatar_telefone(cliente) for cliente in clientes]

        total = ClienteRepository.total(
            pesquisa=pesquisa,
            ativo=ativo,
            origem=origem
        )

        return clientes,total

    @staticmethod
    def buscar(codigo_externo):

        return ClienteRepository.buscar_por_codigo_externo(
            codigo_externo
        )

    @staticmethod
    def criar(dados):

        return ClienteRepository.inserir(
            ClienteService._normalizar_dados(dados)
        )


    @staticmethod
    def excluir(cliente_id):

        ClienteRepository.excluir(cliente_id)


    @staticmethod
    def buscar_por_id(cliente_id):

        cliente = ClienteRepository.buscar_por_id(cliente_id)
        return ClienteService._formatar_telefone(cliente)


    @staticmethod
    def atualizar(cliente_id, dados):

        ClienteRepository.atualizar(
            cliente_id,
            ClienteService._normalizar_dados(dados)
        )

        cliente = ClienteRepository.buscar_por_id(
            cliente_id
        )
        return ClienteService._formatar_telefone(cliente)

    @staticmethod
    def diagnostico_pre_beta(cliente, implantacao=None):
        implantacao = implantacao or {}
        itens = []

        def adicionar(tipo, titulo, detalhe, icone):
            itens.append({
                "tipo": tipo,
                "titulo": titulo,
                "detalhe": detalhe,
                "icone": icone,
                "classe": {
                    "ok": "success",
                    "fluxo": "secondary",
                    "pendencia": "warning",
                    "erro": "danger",
                }.get(tipo, "secondary"),
            })

        if cliente.get("cnpj"):
            adicionar("ok", "CNPJ informado", "Cadastro possui identificador fiscal para conferencia comercial.", "bi-person-vcard")
        else:
            adicionar("pendencia", "CNPJ pendente", "Comercial deve completar o CNPJ antes da validacao Beta assistida.", "bi-person-vcard")

        if cliente.get("razao_social") and cliente.get("nome_fantasia"):
            adicionar("ok", "Dados comerciais basicos", "Razao social e nome fantasia estao preenchidos.", "bi-building-check")
        else:
            adicionar("pendencia", "Dados comerciais incompletos", "Revisar razao social e nome fantasia antes da Beta.", "bi-building-exclamation")

        if cliente.get("email") or cliente.get("telefone"):
            adicionar("ok", "Contato cadastrado", "Cliente possui pelo menos um canal de contato para alinhamentos.", "bi-envelope-check")
        else:
            adicionar("pendencia", "Contato pendente", "Informar email ou telefone para comunicacoes da validacao assistida.", "bi-envelope-exclamation")

        if cliente.get("cidade") and cliente.get("estado"):
            adicionar("ok", "Localizacao cadastrada", "Cidade e UF estao preenchidas para recortes operacionais.", "bi-geo-alt")
        else:
            adicionar("pendencia", "Localizacao incompleta", "Completar cidade e UF quando a informacao estiver homologada.", "bi-geo-alt-fill")

        if implantacao:
            adicionar("ok", "Fluxo operacional vinculado", "Cliente possui implantacao ativa no fluxo operacional atual.", "bi-hdd-network")
        else:
            adicionar("fluxo", "Sem implantacao ativa", "Situacao valida para clientes sem contrato em fase de implantacao; nao gera registro legado automatico.", "bi-signpost-2")

        if cliente.get("origem") == "OMIE":
            adicionar("ok", "Origem OMIE", "Cadastro sincronizado com a base externa e bloqueado para edicoes manuais sensiveis.", "bi-cloud-check")
        else:
            adicionar("fluxo", "Origem manual", "Cadastro manual permitido; revisar dados com Comercial antes da carga oficial da Beta.", "bi-pencil-square")

        if not cliente.get("ativo"):
            adicionar("erro", "Cliente inativo", "Cliente inativo deve ser revisado antes de entrar na validacao operacional.", "bi-slash-circle")

        return itens

    @staticmethod
    def sincronizar_omie(dados):

        return ClienteRepository.upsert_omie(
            ClienteService._normalizar_dados(dados)
        )

    @classmethod
    def listar_todos(cls):

        return ClienteRepository.listar_todos()

    @classmethod
    def listar_para_importacao(cls):

        clientes = ClienteRepository.listar_para_importacao()
        return [cls._formatar_telefone(cliente) for cliente in clientes]

    @staticmethod
    def _normalizar_dados(dados):
        dados = dict(dados)
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        return dados

    @staticmethod
    def _formatar_telefone(cliente):
        if not cliente:
            return cliente

        cliente = dict(cliente)
        cliente["telefone"] = formatar_telefone(cliente.get("telefone"))
        return cliente

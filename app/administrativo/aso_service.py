from datetime import datetime
from pathlib import Path
import re

from app.administrativo.service import AdministrativoService
from app.core.email import EmailService
from app.core.storage import StorageService
from app.repositories.administrativo_aso_repository import AdministrativoAsoRepository


class AdministrativoAsoService:
    repository = AdministrativoAsoRepository
    STATUS = ("ATIVO", "INATIVO")
    ANTECEDENCIAS = (7, 15, 30)

    @classmethod
    def contexto_index(cls, filtros=None, usuario_id=None):
        filtros = filtros or {}
        usuarios = cls.repository.listar_usuarios_agenda()
        return {
            "colaboradores": cls.repository.listar_colaboradores(filtros),
            "clientes": cls.repository.listar_clientes_ativos(),
            "clientes_com_colaboradores": cls.repository.listar_clientes_com_colaboradores(),
            "usuarios": usuarios,
            "dono_agenda_padrao_id": cls._dono_agenda_padrao(usuarios, usuario_id),
            "filtros": filtros,
            "status_options": cls.STATUS,
            "antecedencias": cls.ANTECEDENCIAS,
        }

    @classmethod
    def criar_colaborador(cls, dados, arquivos, usuario_email):
        payload = cls._normalizar_colaborador(dados)
        cls._validar_colaborador(payload)
        cls._validar_cpf_unico(payload["cpf"])
        agendamento = cls._normalizar_agendamento(dados) if cls._flag(dados, "criar_agendamento_aso") else None
        if agendamento:
            cls._validar_usuarios_agenda(agendamento["usuario_ids"])
        payload["criado_por"] = usuario_email
        payload["updated_by"] = usuario_email
        colaborador_id = cls.repository.inserir_colaborador(payload)
        cls._salvar_exames(colaborador_id, arquivos)
        demanda_ids = []
        if agendamento:
            demanda_ids = cls._criar_lembrete_validado(colaborador_id, agendamento, usuario_email)
        return {"colaborador_id": colaborador_id, "demanda_ids": demanda_ids}

    @classmethod
    def atualizar_colaborador(cls, colaborador_id, dados, arquivos, usuario_email):
        if not cls.repository.buscar_colaborador(colaborador_id):
            raise ValueError("Colaborador não encontrado.")
        payload = cls._normalizar_colaborador(dados)
        cls._validar_colaborador(payload)
        cls._validar_cpf_unico(payload["cpf"], colaborador_id)
        payload["updated_by"] = usuario_email
        cls.repository.atualizar_colaborador(colaborador_id, payload)
        cls._salvar_exames(colaborador_id, arquivos)

    @classmethod
    def detalhe_colaborador(cls, colaborador_id):
        colaborador = cls.repository.buscar_colaborador(colaborador_id)
        if colaborador:
            colaborador["exames"] = cls.repository.listar_exames(colaborador_id)
            colaborador["lembretes"] = cls.repository.listar_lembretes(colaborador_id)
        return colaborador

    @classmethod
    def excluir_colaborador(cls, colaborador_id, usuario_email):
        colaborador = cls.repository.buscar_colaborador(colaborador_id)
        if not colaborador:
            raise ValueError("Colaborador não encontrado.")
        for lembrete in cls.repository.listar_lembretes(colaborador_id):
            if lembrete.get("demanda_id"):
                AdministrativoService.cancelar(lembrete.get("demanda_id"), usuario_email)
        exames = cls.repository.listar_exames(colaborador_id)
        cls.repository.excluir_colaborador(colaborador_id)
        for exame in exames:
            cls._remover_arquivo_storage(exame.get("caminho"))

    @classmethod
    def anexar_exames(cls, colaborador_id, arquivos):
        if not cls.repository.buscar_colaborador(colaborador_id):
            raise ValueError("Colaborador não encontrado.")
        cls._salvar_exames(colaborador_id, arquivos)

    @classmethod
    def excluir_exame(cls, colaborador_id, exame_id):
        exame = cls.repository.buscar_exame(exame_id, colaborador_id)
        if not exame:
            raise ValueError("Arquivo de exame não encontrado.")
        cls.repository.excluir_exame(exame_id, colaborador_id)
        cls._remover_arquivo_storage(exame.get("caminho"))

    @classmethod
    def excluir_lembrete(cls, colaborador_id, lembrete_id, usuario_email):
        lembrete = cls.repository.buscar_lembrete(lembrete_id, colaborador_id)
        if not lembrete:
            raise ValueError("Agendamento ASO não encontrado.")
        if lembrete.get("demanda_id"):
            AdministrativoService.cancelar(lembrete.get("demanda_id"), usuario_email)
        cls.repository.excluir_lembrete(lembrete_id, colaborador_id)

    @classmethod
    def criar_lembrete(cls, colaborador_id, dados, usuario_email):
        return cls._criar_lembrete_validado(colaborador_id, cls._normalizar_agendamento(dados), usuario_email)

    @classmethod
    def _criar_lembrete_validado(cls, colaborador_id, agendamento, usuario_email):
        colaborador = cls.repository.buscar_colaborador(colaborador_id)
        if not colaborador:
            raise ValueError("Colaborador não encontrado.")

        cls._validar_usuarios_agenda(agendamento["usuario_ids"])

        demanda_ids = []
        for usuario_id in agendamento["usuario_ids"]:
            participacao = "DONO" if usuario_id == agendamento["dono_id"] else "COMPARTILHADO"
            demanda_id = cls._criar_demanda_aso(colaborador, agendamento["data_aso"], usuario_id, usuario_email, participacao)
            cls.repository.inserir_lembrete({
                "colaborador_id": colaborador_id,
                "demanda_id": demanda_id,
                "usuario_id": usuario_id,
                "data_aso": agendamento["data_aso"],
                "antecedencia_dias": agendamento["antecedencia_dias"],
                "tipo_participacao": participacao,
                "enviar_email": agendamento["enviar_email"],
                "created_by": usuario_email,
            })
            demanda_ids.append(demanda_id)
        return demanda_ids

    @classmethod
    def _validar_usuarios_agenda(cls, usuario_ids):
        usuarios_validos = cls.repository.listar_usuarios_agenda_por_ids(usuario_ids)
        ids_validos = {int(item["id"]) for item in usuarios_validos}
        if set(usuario_ids) != ids_validos:
            raise ValueError("Selecione apenas usuários ativos com agenda habilitada.")

    @classmethod
    def processar_lembretes_email(cls, limite=20):
        pendentes = cls.repository.listar_lembretes_pendentes(limite)
        resultados = []
        for item in pendentes:
            assunto = f"Lembrete ASO - {item.get('nome_completo')}"
            corpo = (
                f"ASO agendado para {cls._data_br(item.get('data_aso'))}.\n\n"
                f"Colaborador: {item.get('nome_completo')}\n"
                f"CPF: {item.get('cpf')}\n"
                f"Cliente: {item.get('cliente_exibicao') or '-'}\n"
                f"Demanda: {item.get('titulo')}\n"
            )
            try:
                resultado = EmailService.enviar(assunto, corpo, [item.get("usuario_email")])
            except Exception as erro:
                cls.repository.marcar_lembrete_erro(item["id"], str(erro))
                resultados.append(f"Erro lembrete #{item['id']}: {erro}")
                continue
            if resultado.get("enviado"):
                cls.repository.marcar_lembrete_enviado(item["id"])
                resultados.append(f"Enviado lembrete #{item['id']} para {item.get('usuario_email')}")
            else:
                motivo = resultado.get("motivo") or "email_nao_enviado"
                cls.repository.marcar_lembrete_erro(item["id"], motivo)
                resultados.append(f"Pendente lembrete #{item['id']}: {motivo}")
        return resultados

    @classmethod
    def _criar_demanda_aso(cls, colaborador, data_aso, usuario_id, usuario_email, participacao):
        cliente = colaborador.get("cliente_exibicao") or "sem cliente vinculado"
        titulo = f"ASO - {colaborador.get('nome_completo')}"
        if participacao == "COMPARTILHADO":
            titulo = f"{titulo} (compartilhado)"
        descricao = (
            f"Agendamento ASO do colaborador {colaborador.get('nome_completo')}.\n"
            f"CPF: {colaborador.get('cpf')}.\n"
            f"Cliente: {cliente}."
        )
        return AdministrativoService.criar({
            "titulo": titulo,
            "descricao": descricao,
            "categoria": "RH",
            "prioridade": "NORMAL",
            "responsavel_id": usuario_id,
            "data_inicial": data_aso.isoformat(),
            "data_limite": data_aso.isoformat(),
            "status": "PENDENTE",
            "observacoes": "Criado pelo Agendamento ASO.",
            "permitir_comentarios": "1",
        }, [], usuario_email)

    @classmethod
    def _salvar_exames(cls, colaborador_id, arquivos):
        for arquivo in arquivos or []:
            if not arquivo or not arquivo.filename:
                continue
            salvo = StorageService.salvar(arquivo, f"exames/{colaborador_id}")
            if salvo:
                cls.repository.inserir_exame(colaborador_id, salvo)

    @classmethod
    def _validar_cpf_unico(cls, cpf, ignorar_id=None):
        existente = cls.repository.buscar_colaborador_por_cpf(cpf, ignorar_id)
        if existente:
            raise ValueError(f"Já existe colaborador cadastrado com este CPF: {existente.get('nome_completo')}.")

    @classmethod
    def _normalizar_colaborador(cls, dados):
        cliente_id = cls._inteiro(dados.get("cliente_id"))
        return {
            "cliente_id": cliente_id,
            "cliente_nome": (dados.get("cliente_nome") or "").strip() or None,
            "nome_completo": (dados.get("nome_completo") or "").strip(),
            "cpf": cls._cpf(dados.get("cpf")),
            "data_nascimento": cls._data(dados.get("data_nascimento"), "Informe uma data de nascimento válida."),
            "data_admissao": cls._data(dados.get("data_admissao"), "Informe uma data de admissão válida."),
            "status": ((dados.get("status") or "ATIVO").strip().upper()),
        }

    @classmethod
    def _validar_colaborador(cls, payload):
        if not payload["cliente_id"] and not payload["cliente_nome"]:
            raise ValueError("Selecione um cliente ou informe o cliente manualmente.")
        if not payload["nome_completo"]:
            raise ValueError("Nome completo é obrigatório.")
        if len(payload["nome_completo"]) > 180:
            raise ValueError("Nome completo deve possuir no máximo 180 caracteres.")
        if not payload["cpf"]:
            raise ValueError("CPF é obrigatório.")
        if len(payload["cpf"]) != 11:
            raise ValueError("CPF deve possuir 11 dígitos.")
        if payload["status"] not in cls.STATUS:
            raise ValueError("Status inválido.")

    @classmethod
    def _normalizar_agendamento(cls, dados):
        data_aso = cls._data(dados.get("data_aso"), "Informe a data do ASO.")
        enviar_email = cls._flag(dados, "enviar_lembrete_email")
        antecedencia = cls._inteiro(dados.get("antecedencia_dias")) or 7
        if enviar_email and antecedencia not in cls.ANTECEDENCIAS:
            raise ValueError("Selecione uma antecedência válida.")

        dono_id = cls._inteiro(dados.get("dono_agenda_id"))
        if not dono_id:
            raise ValueError("Selecione o dono da agenda.")

        compartilhados = dados.getlist("compartilhar_usuario_ids") if hasattr(dados, "getlist") else dados.get("compartilhar_usuario_ids")
        usuarios = [dono_id]
        usuarios.extend(cls._ids_lista(compartilhados))
        usuarios = list(dict.fromkeys(item for item in usuarios if item))
        return {
            "data_aso": data_aso,
            "antecedencia_dias": antecedencia,
            "dono_id": dono_id,
            "usuario_ids": usuarios,
            "enviar_email": enviar_email,
        }

    @staticmethod
    def _remover_arquivo_storage(caminho):
        if not caminho:
            return
        base = StorageService.BASE_STORAGE.resolve()
        arquivo = Path(caminho).resolve()
        if not arquivo.is_relative_to(base):
            return
        if arquivo.exists() and arquivo.is_file():
            arquivo.unlink()

    @staticmethod
    def _cpf(valor):
        return re.sub(r"\D", "", str(valor or ""))

    @staticmethod
    def _data(valor, mensagem):
        if not valor:
            raise ValueError(mensagem)
        if hasattr(valor, "year"):
            return valor
        try:
            return datetime.strptime(str(valor), "%Y-%m-%d").date()
        except ValueError as erro:
            raise ValueError(mensagem) from erro

    @staticmethod
    def _inteiro(valor):
        if valor in (None, ""):
            return None
        return int(valor)

    @staticmethod
    def _dono_agenda_padrao(usuarios, usuario_id=None):
        if usuario_id and any(int(item["id"]) == int(usuario_id) for item in usuarios):
            return int(usuario_id)
        gestor = next((item for item in usuarios if item.get("perfil_codigo") == "ADMINISTRATIVO_GESTOR"), None)
        return int(gestor["id"]) if gestor else (int(usuarios[0]["id"]) if usuarios else None)

    @staticmethod
    def _flag(dados, chave):
        return str(dados.get(chave) or "").lower() in ("1", "true", "on", "sim")

    @staticmethod
    def _ids_lista(valores):
        if not valores:
            return []
        if isinstance(valores, str):
            valores = [valores]
        return [int(item) for item in valores if str(item).isdigit()]

    @staticmethod
    def _data_br(valor):
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
        return str(valor or "-")

from app.repositories.base_repository import BaseRepository


class ContratoAdendoRepository(BaseRepository):

    @classmethod
    def listar_por_contrato(cls, contrato_id):
        adendos = cls.fetch_all(
            """
            SELECT a.*,
                   COALESCE(p.valor_total, 0) AS premiacao_valor_total,
                   p.status_manual AS premiacao_status,
                   p.data_recebimento_omie AS premiacao_data_recebimento_omie,
                   p.id AS premiacao_id,
                   rc.nome AS premiacao_campanha_nome
            FROM contratos_adendos a
            LEFT JOIN financeiro_premiacoes_adendos p ON p.adendo_id = a.id AND p.ativo = 1
            LEFT JOIN regras_campanhas_comissao rc ON rc.id = p.campanha_id
            WHERE a.contrato_id = %s
              AND a.ativo = 1
            ORDER BY COALESCE(a.data_adendo, a.created_at) DESC, a.id DESC
            """,
            (contrato_id,),
        )
        anexos = cls.listar_anexos_por_contrato(contrato_id)
        por_adendo = {}
        for anexo in anexos:
            por_adendo.setdefault(anexo["adendo_id"], []).append(anexo)
        for adendo in adendos:
            adendo["anexos"] = por_adendo.get(adendo["id"], [])
        return adendos

    @classmethod
    def listar_anexos_por_contrato(cls, contrato_id):
        return cls.fetch_all(
            """
            SELECT ax.*
            FROM contratos_adendos_anexos ax
            INNER JOIN contratos_adendos a ON a.id = ax.adendo_id
            WHERE a.contrato_id = %s
              AND a.ativo = 1
            ORDER BY ax.created_at DESC, ax.id DESC
            """,
            (contrato_id,),
        )

    @classmethod
    def buscar_por_id(cls, adendo_id):
        return cls.fetch_one(
            """
            SELECT a.*, c.numero AS contrato_numero, COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_nome
            FROM contratos_adendos a
            INNER JOIN contratos c ON c.id = a.contrato_id
            INNER JOIN clientes cli ON cli.id = a.cliente_id
            WHERE a.id = %s
              AND a.ativo = 1
            """,
            (adendo_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO contratos_adendos (
                uuid, contrato_id, cliente_id, tipo, titulo, numero_adendo, data_adendo,
                valor_recorrente, valor_pontual, quantidade_usuarios, observacoes, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("contrato_id"), dados.get("cliente_id"), dados.get("tipo"),
                dados.get("titulo"), dados.get("numero_adendo"), dados.get("data_adendo"),
                dados.get("valor_recorrente"), dados.get("valor_pontual"), dados.get("quantidade_usuarios"),
                dados.get("observacoes"), dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar(cls, adendo_id, dados):
        return cls.execute(
            """
            UPDATE contratos_adendos
            SET tipo=%s,
                titulo=%s,
                numero_adendo=%s,
                data_adendo=%s,
                valor_recorrente=%s,
                valor_pontual=%s,
                quantidade_usuarios=%s,
                observacoes=%s,
                updated_by=%s
            WHERE id=%s
              AND contrato_id=%s
              AND ativo=1
            """,
            (
                dados.get("tipo"), dados.get("titulo"), dados.get("numero_adendo"), dados.get("data_adendo"),
                dados.get("valor_recorrente"), dados.get("valor_pontual"), dados.get("quantidade_usuarios"),
                dados.get("observacoes"), dados.get("updated_by"), adendo_id, dados.get("contrato_id"),
            ),
        )

    @classmethod
    def inserir_anexo(cls, adendo_id, arquivo, arquivo_original, mime_type, tamanho, usuario_email):
        return cls.execute_insert(
            """
            INSERT INTO contratos_adendos_anexos (uuid, adendo_id, arquivo, arquivo_original, mime_type, tamanho, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(), adendo_id, arquivo, arquivo_original, mime_type, tamanho, usuario_email),
        )

    @classmethod
    def buscar_anexo(cls, anexo_id):
        return cls.fetch_one(
            """
            SELECT ax.*, a.contrato_id
            FROM contratos_adendos_anexos ax
            INNER JOIN contratos_adendos a ON a.id = ax.adendo_id
            WHERE ax.id = %s
              AND a.ativo = 1
            """,
            (anexo_id,),
        )

    @classmethod
    def excluir(cls, adendo_id, usuario_email="sistema"):
        return cls.execute(
            "UPDATE contratos_adendos SET ativo=0, updated_by=%s WHERE id=%s",
            (usuario_email, adendo_id),
        )

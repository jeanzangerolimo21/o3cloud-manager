from app.repositories.base_repository import BaseRepository


class FinanceiroRecebimentoRepository(BaseRepository):

    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        return cls.fetch_one(
            "SELECT * FROM financeiro_recebimentos WHERE codigo_externo=%s",
            (codigo_externo,),
        )

    @classmethod
    def buscar_vinculos(cls, codigo_cliente_omie, numero_contrato):
        return cls.fetch_one(
            """
            SELECT c.id AS contrato_id, c.codigo_externo AS codigo_contrato_omie, cli.id AS cliente_id
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            WHERE cli.codigo_externo=%s
              AND c.numero=%s
              AND c.ativo=1
            ORDER BY c.origem='OMIE' DESC, c.id DESC
            LIMIT 1
            """,
            (codigo_cliente_omie, numero_contrato),
        )

    @classmethod
    def upsert(cls, dados):
        existente = cls.buscar_por_codigo_externo(dados.get("codigo_externo"))
        if existente:
            cls.atualizar(existente["id"], dados)
            return "UPDATE"
        cls.inserir(dados)
        return "INSERT"

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO financeiro_recebimentos (
                uuid, codigo_externo, cliente_id, contrato_id, numero_documento,
                numero_documento_fiscal, numero_parcela, numero_contrato,
                categoria_codigo, categoria_nome, categoria_excluida, motivo_exclusao,
                valor_original, valor_recebido, valor_desconto, valor_juros,
                data_vencimento, data_recebimento, data_emissao, situacao,
                codigo_cliente_omie, codigo_contrato_omie, codigo_vendedor,
                codigo_projeto, origem, synced_at
            ) VALUES (
                UUID(), %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, NOW()
            )
            """,
            cls._params(dados),
        )

    @classmethod
    def atualizar(cls, recebimento_id, dados):
        params = cls._params(dados) + (recebimento_id,)
        cls.execute(
            """
            UPDATE financeiro_recebimentos
            SET codigo_externo=%s,
                cliente_id=%s,
                contrato_id=%s,
                numero_documento=%s,
                numero_documento_fiscal=%s,
                numero_parcela=%s,
                numero_contrato=%s,
                categoria_codigo=%s,
                categoria_nome=%s,
                categoria_excluida=%s,
                motivo_exclusao=%s,
                valor_original=%s,
                valor_recebido=%s,
                valor_desconto=%s,
                valor_juros=%s,
                data_vencimento=%s,
                data_recebimento=%s,
                data_emissao=%s,
                situacao=%s,
                codigo_cliente_omie=%s,
                codigo_contrato_omie=%s,
                codigo_vendedor=%s,
                codigo_projeto=%s,
                origem=%s,
                synced_at=NOW()
            WHERE id=%s
            """,
            params,
        )

    @staticmethod
    def _params(dados):
        return (
            dados.get("codigo_externo"),
            dados.get("cliente_id"),
            dados.get("contrato_id"),
            dados.get("numero_documento"),
            dados.get("numero_documento_fiscal"),
            dados.get("numero_parcela"),
            dados.get("numero_contrato"),
            dados.get("categoria_codigo"),
            dados.get("categoria_nome"),
            1 if dados.get("categoria_excluida") else 0,
            dados.get("motivo_exclusao"),
            dados.get("valor_original"),
            dados.get("valor_recebido"),
            dados.get("valor_desconto"),
            dados.get("valor_juros"),
            dados.get("data_vencimento"),
            dados.get("data_recebimento"),
            dados.get("data_emissao"),
            dados.get("situacao"),
            dados.get("codigo_cliente_omie"),
            dados.get("codigo_contrato_omie"),
            dados.get("codigo_vendedor"),
            dados.get("codigo_projeto"),
            dados.get("origem"),
        )

from app.repositories.base_repository import BaseRepository


class HardwareParceirosRepository(BaseRepository):
    TABLE = "dimensionamento_hardware_parceiros"

    @classmethod
    def listar(cls, parceiro=None, ativo=None):
        sql = f"""
            SELECT *
            FROM {cls.TABLE}
            WHERE 1 = 1
        """
        params = []
        if parceiro:
            sql += " AND parceiro = %s"
            params.append(parceiro)

        if ativo in (0, 1):
            sql += " AND ativo = %s"
            params.append(ativo)
        sql += " ORDER BY parceiro, secao, ordem, id"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_parceiros(cls):
        return cls.fetch_all(
            f"SELECT DISTINCT parceiro FROM {cls.TABLE} ORDER BY parceiro"
        )

    @classmethod
    def buscar(cls, item_id):
        return cls.fetch_one(
            f"SELECT * FROM {cls.TABLE} WHERE id = %s",
            (item_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            f"""
            INSERT INTO {cls.TABLE}
            (uuid, parceiro, secao, faixa_usuarios, memoria, processador, disco, origem, ordem, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados["parceiro"],
                dados["secao"],
                dados["faixa_usuarios"],
                dados.get("memoria"),
                dados.get("processador"),
                dados.get("disco"),
                dados.get("origem", "MANUAL"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, item_id, dados):
        return cls.execute(
            f"""
            UPDATE {cls.TABLE}
            SET parceiro = %s, secao = %s, faixa_usuarios = %s,
                memoria = %s, processador = %s, disco = %s,
                ordem = %s, ativo = %s
            WHERE id = %s
            """,
            (
                dados["parceiro"],
                dados["secao"],
                dados["faixa_usuarios"],
                dados.get("memoria"),
                dados.get("processador"),
                dados.get("disco"),
                dados.get("ordem", 0),
                cls.bool_to_int(dados.get("ativo", True)),
                item_id,
            ),
        )

    @classmethod
    def excluir(cls, item_id):
        return cls.execute(
            f"DELETE FROM {cls.TABLE} WHERE id = %s",
            (item_id,),
        )

    @classmethod
    def limpar_importados(cls):
        return cls.execute(
            f"DELETE FROM {cls.TABLE} WHERE origem = %s",
            ("CSV_TABELA_HARDWARE_PARCEIROS",),
        )

from app.repositories.base_repository import BaseRepository


class ParceiroRepository(BaseRepository):

    @classmethod
    def total(cls, pesquisa=None):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT COUNT(*) AS total
            FROM parceiros
        """

        parametros = []

        if pesquisa:

            sql += """
                WHERE
                    nome LIKE %s
                    OR sigla LIKE %s
            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo])

        cursor.execute(sql, tuple(parametros))

        total = cursor.fetchone()["total"]

        cls.close(conn, cursor)

        return total


    @classmethod
    def listar(cls, pesquisa=None, limit=50, offset=0):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT

                id,

                uuid,

                nome,

                sigla,

                tipo,

                contato,

                email,

                telefone,

                ativo

            FROM parceiros

        """

        parametros = []
            
        condicoes = [
            "ativo = 1"
        ]

        if pesquisa:

            condicoes.append("""

                (

                    nome LIKE %s

                    OR sigla LIKE %s

                )

            """)

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo])

        sql += " WHERE "

        sql += " AND ".join(condicoes)    

        sql += """

            ORDER BY nome

            LIMIT %s OFFSET %s

        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))

        parceiros = cursor.fetchall()

        cls.close(conn, cursor)

        return parceiros


    @classmethod
    def buscar_por_id(cls, parceiro_id):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                id,

                uuid,

                nome,

                sigla,

                tipo,

                contato,

                email,

                telefone,

                site,

                logo,

                descricao,

                ativo,

                created_at,

                updated_at

            FROM parceiros
            
            WHERE id=%s

        """, (parceiro_id,))

        parceiro = cursor.fetchone()

        cls.close(conn, cursor)

        return parceiro
    
    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()

        cursor = conn.cursor()

        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO parceiros (

                uuid,

                nome,

                sigla,

                tipo,

                contato,

                email,

                telefone,

                site,

                logo,

                descricao,

                ativo

            )

            VALUES (

                %s,

                %s,

                %s,

                %s,

                %s,

                %s,

                %s,

                %s,

                %s,

                %s,

                %s

            )

        """, (

            uuid,

            dados["nome"],

            dados["sigla"],

            dados["tipo"],

            dados["contato"],

            dados["email"],

            dados["telefone"],

            dados["site"],

            dados["logo"],

            dados["descricao"],

            dados["ativo"]

        ))

        conn.commit()

        novo_id = cursor.lastrowid

        cls.close(conn, cursor)

        return novo_id

    @classmethod
    def atualizar(cls, parceiro_id, dados):

        conn = cls.connection()

        cursor = conn.cursor()

        cursor.execute("""

            UPDATE parceiros

            SET

                nome=%s,

                sigla=%s,

                tipo=%s,

                contato=%s,

                email=%s,

                telefone=%s,

                site=%s,

                logo=%s,

                descricao=%s,

                ativo=%s

            WHERE id=%s

        """, (

            dados["nome"],

            dados["sigla"],

            dados["tipo"],

            dados["contato"],

            dados["email"],

            dados["telefone"],

            dados["site"],

            dados["logo"],

            dados["descricao"],

            dados["ativo"],

            parceiro_id

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def excluir(cls, parceiro_id):

        conn = cls.connection()

        cursor = conn.cursor()

        cursor.execute("""

            UPDATE parceiros 

            SET

                ativo = 0

            WHERE id=%s

        """, (

            parceiro_id,

        ))

        conn.commit()

        cls.close(conn, cursor)

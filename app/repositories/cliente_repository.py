from app.repositories.base_repository import BaseRepository
from app.core.constants.origens import ( ORIGEM_MANUAL)

class ClienteRepository(BaseRepository):


    SYNC_FIELDS = (
        "codigo_externo",
        "origem",
        "synced_at"
    )

    EDITABLE_FIELDS = (
        "nome_fantasia",
        "razao_social",
        "cnpj",
        "email",
        "telefone",
        "cidade",
        "estado"
    )

    @classmethod
    def listar(cls, pesquisa=None, ativo=None, origem=None, limit=50, offset=0):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                id,
                uuid,
                codigo_externo,
                origem,
                nome_fantasia,
                razao_social,
                cnpj,
                cidade,
                estado,
                ativo
            FROM clientes
        """

        condicoes = []

        parametros = []

        if pesquisa:

            condicoes.append("""

                (

                    nome_fantasia LIKE %s

                    OR razao_social LIKE %s

                    OR cnpj LIKE %s

                )

            """)

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo])


        if ativo is not None and ativo != "":

            condicoes.append("ativo = %s")

            parametros.append(int(ativo))


        if origem:

            condicoes.append("origem = %s")

            parametros.append(origem)


        if condicoes:

            sql += " WHERE "

            sql += " AND ".join(condicoes)  

        sql += """
            ORDER BY nome_fantasia
            LIMIT %s OFFSET %s
        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))

        clientes = cursor.fetchall()

        cls.close(conn, cursor)

        return clientes


    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        
        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes

            WHERE codigo_externo=%s

        """, (codigo_externo,))

        cliente = cursor.fetchone()

        cls.close(conn, cursor)

        return cliente

    @classmethod
    def buscar_por_cnpj(cls, cnpj):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes

            WHERE cnpj = %s

            LIMIT 1

        """, (cnpj,))

        cliente = cursor.fetchone()

        cls.close(conn, cursor)

        return cliente


    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()
        cursor = conn.cursor()
        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO clientes (

                uuid,
                codigo_externo,
                origem,
                nome_fantasia,
                razao_social,
                cnpj,
                email,
                telefone,
                cidade,
                estado,
                ativo,
                synced_at

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
                1,
                NULL 

            )

        """, (
            uuid,
            dados.get("codigo_externo"),
            dados.get("origem"),
            dados.get("nome_fantasia"),
            dados.get("razao_social"),
            dados.get("cnpj"),
            dados.get("email"),
            dados.get("telefone"),
            dados.get("cidade"),
            dados.get("estado")

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def atualizar_sync(cls, cliente_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE clientes

            SET

                codigo_externo=%s,
                origem=%s,
                nome_fantasia=%s,
                razao_social=%s,
                cnpj=%s,
                email=%s,
                telefone=%s,
                cidade=%s,
                estado=%s,
                synced_at=NOW()

            WHERE id=%s

        """, (

            dados.get("codigo_externo"),
            dados.get("origem"),
            dados.get("nome_fantasia"),
            dados.get("razao_social"),
            dados.get("cnpj"),
            dados.get("email"),
            dados.get("telefone"),
            dados.get("cidade"),
            dados.get("estado"),
            cliente_id

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def atualizar(cls, cliente_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE clientes

            SET

                nome_fantasia=%s,
                razao_social=%s,
                cnpj=%s,
                email=%s,
                telefone=%s,
                cidade=%s,
                estado=%s

            WHERE id=%s

        """, (

            dados.get("nome_fantasia"),
            dados.get("razao_social"),
            dados.get("cnpj"),
            dados.get("email"),
            dados.get("telefone"),
            dados.get("cidade"),
            dados.get("estado"),
            cliente_id

        ))

        conn.commit()

        cls.close(conn, cursor)    

    
    @classmethod
    def total(cls, pesquisa=None, ativo=None, origem=None):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT COUNT(*) AS total FROM clientes"

        condicoes = []

        parametros = []

        if pesquisa:

            condicoes.append("""

                (

                    nome_fantasia LIKE %s

                    OR razao_social LIKE %s

                    OR cnpj LIKE %s

                )

            """)

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo])

        if ativo is not None and ativo != "":

            condicoes.append("ativo = %s")

            parametros.append(int(ativo))

        if origem:

            condicoes.append("origem = %s")

            parametros.append(origem)

        if condicoes:

            sql += " WHERE "

            sql += " AND ".join(condicoes)

        cursor.execute(sql, tuple(parametros))

        total = cursor.fetchone()["total"]

        cls.close(conn, cursor)

        return total
 

    @classmethod
    def upsert_omie(cls, dados):

        cliente = cls.buscar_por_codigo_externo(
            dados.get("codigo_externo")
        )

        if not cliente and dados.get("cnpj"):

            cliente = cls.buscar_por_cnpj(
                dados.get("cnpj")
            )

        if cliente:

            cls.atualizar_sync(
                cliente["id"],
                dados
            )

            return "UPDATE"

        cls.inserir(dados)

        return "INSERT"

    @classmethod
    def excluir(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            DELETE FROM clientes

            WHERE id=%s
            AND origem=%s

        """, (cliente_id,ORIGEM_MANUAL))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def buscar_por_id(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM clientes

            WHERE id=%s

        """, (cliente_id,))

        cliente = cursor.fetchone()

        cls.close(conn, cursor)

        return cliente
    

    @classmethod
    def listar_todos(cls):

        conn = cls.connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                id,

                nome_fantasia

            FROM clientes

            WHERE ativo = 1

            ORDER BY nome_fantasia

        """)

        clientes = cursor.fetchall()

        cls.close(conn, cursor)

        return clientes

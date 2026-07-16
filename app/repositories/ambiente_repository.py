from app.repositories.base_repository import BaseRepository


class AmbienteRepository(BaseRepository):

    @classmethod
    def listar(cls, pesquisa=None, limit=50, offset=0):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT

                a.id,
                a.uuid,
                a.cliente_id,
                a.nome,
                a.origem,
                a.parceiro_id,
                a.contrato_id,
                a.ambiente_tipo,
                a.situacao,
                a.prefixo_proxmox,
                a.descricao,
                a.ativo,
                a.synced_at,
                c.nome_fantasia AS cliente_nome,
                p.nome AS parceiro_nome,
                ct.numero AS contrato_numero

            FROM ambientes a
            
            INNER JOIN clientes c
                ON c.id = a.cliente_id

            LEFT JOIN parceiros p
                ON p.id = a.parceiro_id

            LEFT JOIN contratos ct
                ON ct.id = a.contrato_id
            
            WHERE a.ativo = 1

        """

        parametros = []

        if pesquisa:

            sql += """

                WHERE

                    a.nome LIKE %s

                    OR c.nome_fantasia LIKE %s

                    OR a.prefixo_proxmox LIKE %s

                    OR p.nome LIKE %s

                    OR ct.numero LIKE %s

                    OR a.descricao LIKE %s

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo, termo, termo, termo])

        sql += """

            ORDER BY

                c.nome_fantasia ASC,
                a.ambiente_tipo ASC,
                a.nome ASC

            LIMIT %s OFFSET %s

        """

        parametros.extend([limit, offset])

        cursor.execute(sql, tuple(parametros))

        ambientes = cursor.fetchall()

        cls.close(conn, cursor)

        return ambientes

    @classmethod
    def total(cls, pesquisa=None):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        sql = """

            SELECT COUNT(*) AS total

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id

        """

        parametros = []

        if pesquisa:

            sql += """

                WHERE

                    a.nome LIKE %s

                    OR c.nome_fantasia LIKE %s

                    OR a.prefixo_proxmox LIKE %s

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo])

        cursor.execute(sql, tuple(parametros))

        total = cursor.fetchone()["total"]

        cls.close(conn, cursor)

        return total

    @classmethod
    def buscar_por_id(cls, ambiente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT

                a.*,

                c.nome_fantasia AS cliente_nome

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id

            WHERE a.id=%s

        """, (ambiente_id,))

        ambiente = cursor.fetchone()

        cls.close(conn, cursor)

        return ambiente

    @classmethod
    def buscar_por_cliente(cls, cliente_id):

        conn = cls.connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""

            SELECT *

            FROM ambientes

            WHERE cliente_id=%s

            ORDER BY nome

        """, (cliente_id,))

        ambientes = cursor.fetchall()

        cls.close(conn, cursor)

        return ambientes

    @classmethod
    def inserir(cls, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        uuid = cls.generate_uuid()

        cursor.execute("""

            INSERT INTO ambientes (

                uuid,
                cliente_id,
                nome,
                ambiente_tipo,
                prefixo_proxmox,
                origem,
                parceiro_id,
                contrato_id,
                situacao,
                descricao,
                responsavel_implantacao,
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
                %s,
                %s

            )

        """, (

            uuid,
            dados.get("cliente_id"),
            dados.get("nome"),
            dados.get("ambiente_tipo"),
            dados.get("prefixo_proxmox"),
            dados.get("origem"),
            dados.get("parceiro_id"),
            dados.get("contrato_id"),
            dados.get("situacao"),
            dados.get("descricao"),
            dados.get("responsavel_implantacao"),
            dados.get("ativo", 1)

        ))

        conn.commit()

        novo_id = cursor.lastrowid

        cls.close(conn, cursor)

        return novo_id  

    @classmethod
    def atualizar(cls, ambiente_id, dados):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE ambientes

            SET

                cliente_id=%s,
                nome=%s,
                ambiente_tipo=%s,
                prefixo_proxmox=%s,
                origem=%s,
                parceiro_id=%s,
                contrato_id=%s,
                situacao=%s,
                descricao=%s,
                responsavel_implantacao,
                ativo=%s

            WHERE id=%s

        """, (

            dados.get("cliente_id"),
            dados.get("nome"),
            dados.get("ambiente_tipo"),
            dados.get("prefixo_proxmox"),
            dados.get("origem"),
            dados.get("parceiro_id"),
            dados.get("contrato_id"),
            dados.get("situacao"),
            dados.get("descricao"),
            dados.get("responsavel_implantacao"),
            dados.get("ativo"),
            ambiente_id

        ))

        conn.commit()

        cls.close(conn, cursor)

    @classmethod
    def excluir(cls, ambiente_id):

        conn = cls.connection()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE ambientes

            SET ativo=0,

            situacao = 'DESATIVADO'

            WHERE id=%s

        """, (ambiente_id,))

        conn.commit()

        novo_id = cursor.lastrowid

        return novo_id       

        cls.close(conn, cursor)

    @classmethod
    def criar(cls, dados):

        return AmbienteRepository.inserir(dados)

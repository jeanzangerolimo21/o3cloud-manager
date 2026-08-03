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
                a.implantador_id,
                i.nome AS implantador_nome,
                i.email AS implantador_email,
                a.ativo,
                a.synced_at,
                COALESCE(GROUP_CONCAT(DISTINCT cv.nome_fantasia ORDER BY cv.nome_fantasia SEPARATOR ', '), c.nome_fantasia) AS cliente_nome,
                GROUP_CONCAT(DISTINCT cv.nome_fantasia ORDER BY cv.nome_fantasia SEPARATOR ', ') AS clientes_nomes,
                p.nome AS parceiro_nome,
                COALESCE(GROUP_CONCAT(DISTINCT ctv.numero ORDER BY ctv.numero SEPARATOR ', '), ct.numero) AS contrato_numero,
                GROUP_CONCAT(DISTINCT ctv.numero ORDER BY ctv.numero SEPARATOR ', ') AS contratos_numeros,
                COUNT(DISTINCT apr.proxmox_inventory_id) AS recursos_total

            FROM ambientes a
            
            INNER JOIN clientes c
                ON c.id = a.cliente_id

            LEFT JOIN parceiros p
                ON p.id = a.parceiro_id

            LEFT JOIN contratos ct
                ON ct.id = a.contrato_id
            LEFT JOIN ambiente_clientes ac
                ON ac.ambiente_id = a.id
            LEFT JOIN clientes cv
                ON cv.id = ac.cliente_id
            LEFT JOIN ambiente_contratos act
                ON act.ambiente_id = a.id
            LEFT JOIN contratos ctv
                ON ctv.id = act.contrato_id
            LEFT JOIN ambiente_proxmox_recursos apr
                ON apr.ambiente_id = a.id
            LEFT JOIN implantadores i
                ON i.id = a.implantador_id
            
            WHERE a.ativo = 1

        """

        parametros = []

        if pesquisa:

            sql += """

                AND (

                    a.nome LIKE %s

                    OR c.nome_fantasia LIKE %s

                    OR a.prefixo_proxmox LIKE %s

                    OR p.nome LIKE %s

                    OR ct.numero LIKE %s

                    OR a.descricao LIKE %s

                )

            """

            termo = f"%{pesquisa}%"

            parametros.extend([termo, termo, termo, termo, termo, termo])

        sql += """

            GROUP BY
                a.id, a.uuid, a.cliente_id, a.nome, a.origem, a.parceiro_id,
                a.contrato_id, a.ambiente_tipo, a.situacao, a.prefixo_proxmox,
                a.descricao, a.implantador_id, i.nome, i.email, a.ativo, a.synced_at, c.nome_fantasia, p.nome, ct.numero

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

                c.nome_fantasia AS cliente_nome,
                p.nome AS parceiro_nome,
                ct.numero AS contrato_numero,
                i.nome AS implantador_nome,
                i.email AS implantador_email

            FROM ambientes a

            INNER JOIN clientes c
                ON c.id = a.cliente_id
            LEFT JOIN parceiros p
                ON p.id = a.parceiro_id
            LEFT JOIN contratos ct
                ON ct.id = a.contrato_id
            LEFT JOIN implantadores i
                ON i.id = a.implantador_id

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
                implantador_id,
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
            dados.get("implantador_id"),
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
                responsavel_implantacao=%s,
                implantador_id=%s,
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
            dados.get("implantador_id"),
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


    @classmethod
    def buscar_vinculos(cls, ambiente_id):
        return {
            "clientes": cls.fetch_all(
                """
                SELECT ac.cliente_id AS id, c.nome_fantasia, c.razao_social, ac.principal
                FROM ambiente_clientes ac
                JOIN clientes c ON c.id = ac.cliente_id
                WHERE ac.ambiente_id = %s
                ORDER BY ac.principal DESC, c.nome_fantasia
                """,
                (ambiente_id,),
            ),
            "contratos": cls.fetch_all(
                """
                SELECT act.contrato_id AS id, c.numero, c.descricao, c.valor_mensal, act.principal
                FROM ambiente_contratos act
                JOIN contratos c ON c.id = act.contrato_id
                WHERE act.ambiente_id = %s
                ORDER BY act.principal DESC, c.numero
                """,
                (ambiente_id,),
            ),
            "recursos": cls.fetch_all(
                """
                SELECT apr.proxmox_inventory_id AS id, p.vmid, p.tipo, p.nome, p.node, p.status,
                       p.cpu_cores, p.memoria_mb, p.disco_gb
                FROM ambiente_proxmox_recursos apr
                JOIN proxmox_vm_inventory p ON p.id = apr.proxmox_inventory_id
                WHERE apr.ambiente_id = %s
                ORDER BY p.node, p.vmid
                """,
                (ambiente_id,),
            ),
        }

    @classmethod
    def salvar_vinculos(cls, ambiente_id, cliente_ids=None, contrato_ids=None, recurso_ids=None):
        conn = cls.connection()
        cursor = conn.cursor()
        cliente_ids = cls._ids_unicos(cliente_ids)
        contrato_ids = cls._ids_unicos(contrato_ids)
        recurso_ids = cls._ids_unicos(recurso_ids)
        try:
            cursor.execute("DELETE FROM ambiente_clientes WHERE ambiente_id = %s", (ambiente_id,))
            cursor.execute("DELETE FROM ambiente_contratos WHERE ambiente_id = %s", (ambiente_id,))
            cursor.execute("DELETE FROM ambiente_proxmox_recursos WHERE ambiente_id = %s", (ambiente_id,))
            for indice, cliente_id in enumerate(cliente_ids):
                cursor.execute(
                    """
                    INSERT INTO ambiente_clientes (uuid, ambiente_id, cliente_id, principal)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (cls.generate_uuid(), ambiente_id, cliente_id, 1 if indice == 0 else 0),
                )
            for indice, contrato_id in enumerate(contrato_ids):
                cursor.execute(
                    """
                    INSERT INTO ambiente_contratos (uuid, ambiente_id, contrato_id, principal)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (cls.generate_uuid(), ambiente_id, contrato_id, 1 if indice == 0 else 0),
                )
            for recurso_id in recurso_ids:
                cursor.execute(
                    """
                    INSERT INTO ambiente_proxmox_recursos (uuid, ambiente_id, proxmox_inventory_id)
                    VALUES (%s, %s, %s)
                    """,
                    (cls.generate_uuid(), ambiente_id, recurso_id),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @staticmethod
    def _ids_unicos(valores):
        ids = []
        for valor in valores or []:
            try:
                item = int(valor)
            except (TypeError, ValueError):
                continue
            if item and item not in ids:
                ids.append(item)
        return ids

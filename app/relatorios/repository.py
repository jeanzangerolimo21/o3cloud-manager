import json

from app.repositories.base_repository import BaseRepository


class RelatorioRepository(BaseRepository):
    @classmethod
    def listar_modelos(cls, usuario_id=None, perfil_codigo=None, pode_global=True):
        modelos = cls.fetch_all(
            """
            SELECT *
            FROM relatorios_modelos
            WHERE ativo = 1
            ORDER BY updated_at DESC, nome ASC
            """
        )
        visiveis = []
        for modelo in modelos:
            perfis = cls._json(modelo.get("perfis_json"), [])
            privado = modelo.get("visibilidade") == "PRIVADO" and int(modelo.get("criado_por_id") or 0) == int(usuario_id or 0)
            por_perfil = modelo.get("visibilidade") == "PERFIL" and perfil_codigo in perfis
            global_ = modelo.get("visibilidade") == "GLOBAL" and pode_global
            if privado or por_perfil or global_:
                visiveis.append(cls._hidratar(modelo))
        return visiveis

    @classmethod
    def buscar_modelo(cls, modelo_id):
        modelo = cls.fetch_one("SELECT * FROM relatorios_modelos WHERE id=%s AND ativo=1", (modelo_id,))
        return cls._hidratar(modelo) if modelo else None

    @classmethod
    def inserir_modelo(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO relatorios_modelos (
                uuid, nome, descricao, fonte, configuracao_json, visibilidade,
                perfis_json, criado_por_id, criado_por_email, created_by, updated_by, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (
                cls.generate_uuid(),
                dados["nome"],
                dados.get("descricao"),
                dados["fonte"],
                json.dumps(dados["configuracao"], ensure_ascii=False),
                dados.get("visibilidade") or "PRIVADO",
                json.dumps(dados.get("perfis") or [], ensure_ascii=False),
                dados.get("usuario_id"),
                dados.get("usuario_email"),
                dados.get("usuario_email"),
                dados.get("usuario_email"),
            ),
        )

    @classmethod
    def atualizar_modelo(cls, modelo_id, dados):
        return cls.execute(
            """
            UPDATE relatorios_modelos
            SET nome=%s, descricao=%s, fonte=%s, configuracao_json=%s,
                visibilidade=%s, perfis_json=%s, updated_by=%s
            WHERE id=%s AND ativo=1
            """,
            (
                dados["nome"],
                dados.get("descricao"),
                dados["fonte"],
                json.dumps(dados["configuracao"], ensure_ascii=False),
                dados.get("visibilidade") or "PRIVADO",
                json.dumps(dados.get("perfis") or [], ensure_ascii=False),
                dados.get("usuario_email"),
                modelo_id,
            ),
        )

    @classmethod
    def excluir_modelo(cls, modelo_id, usuario_email):
        return cls.execute(
            "UPDATE relatorios_modelos SET ativo=0, updated_by=%s WHERE id=%s",
            (usuario_email, modelo_id),
        )

    @classmethod
    def auditar_execucao(cls, dados):
        return cls.execute(
            """
            INSERT INTO relatorios_execucoes (
                uuid, modelo_id, fonte, formato, total_linhas, usuario_id, usuario_email, filtros_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("modelo_id"),
                dados.get("fonte"),
                dados.get("formato") or "HTML",
                dados.get("total_linhas") or 0,
                dados.get("usuario_id"),
                dados.get("usuario_email"),
                json.dumps(dados.get("filtros") or [], ensure_ascii=False),
            ),
        )


    @classmethod
    def inserir_job(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO relatorios_jobs (
                uuid, modelo_id, fonte, formato, configuracao_json, status,
                solicitado_por_id, solicitado_por_email
            ) VALUES (%s, %s, %s, %s, %s, 'PENDENTE', %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("modelo_id"),
                dados["fonte"],
                dados.get("formato") or "XLSX",
                json.dumps(dados["configuracao"], ensure_ascii=False),
                dados.get("usuario_id"),
                dados.get("usuario_email"),
            ),
        )

    @classmethod
    def listar_jobs_usuario(cls, usuario_id=None, limite=20):
        if not usuario_id:
            return []
        return cls.fetch_all(
            """
            SELECT *
            FROM relatorios_jobs
            WHERE solicitado_por_id=%s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (usuario_id, limite),
        )

    @classmethod
    def proximo_job_pendente(cls):
        return cls.fetch_one(
            """
            SELECT *
            FROM relatorios_jobs
            WHERE status='PENDENTE'
            ORDER BY created_at ASC, id ASC
            LIMIT 1
            """
        )

    @classmethod
    def marcar_job_processando(cls, job_id):
        return cls.execute(
            "UPDATE relatorios_jobs SET status='PROCESSANDO', erro=NULL WHERE id=%s AND status='PENDENTE'",
            (job_id,),
        )

    @classmethod
    def concluir_job(cls, job_id, dados):
        return cls.execute(
            """
            UPDATE relatorios_jobs
            SET status='CONCLUIDO', total_linhas=%s, arquivo_nome=%s, arquivo_url=%s,
                erro=NULL, processado_em=NOW(), email_enviado=%s, email_erro=%s
            WHERE id=%s
            """,
            (
                dados.get("total_linhas"),
                dados.get("arquivo_nome"),
                dados.get("arquivo_url"),
                1 if dados.get("email_enviado") else 0,
                dados.get("email_erro"),
                job_id,
            ),
        )

    @classmethod
    def falhar_job(cls, job_id, erro):
        return cls.execute(
            "UPDATE relatorios_jobs SET status='ERRO', erro=%s, processado_em=NOW() WHERE id=%s",
            (str(erro)[:5000], job_id),
        )

    @classmethod
    def executar_sql(cls, sql, params):
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def _hidratar(cls, modelo):
        modelo["configuracao"] = cls._json(modelo.get("configuracao_json"), {})
        modelo["perfis"] = cls._json(modelo.get("perfis_json"), [])
        return modelo

    @staticmethod
    def _json(valor, padrao):
        if not valor:
            return padrao
        if isinstance(valor, (dict, list)):
            return valor
        try:
            return json.loads(valor)
        except Exception:
            return padrao

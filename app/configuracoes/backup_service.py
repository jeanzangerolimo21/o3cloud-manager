import gzip
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
from pathlib import Path

from app.core.config import Config
from app.repositories.base_repository import BaseRepository


class BackupSistemaService:
    repository = BaseRepository
    TIPOS_BACKUP = {
        "BANCO": "Banco de dados",
        "STORAGE": "Storage",
        "COMPLETO": "Banco + storage",
    }
    DESTINOS = {
        "LOCAL": "Storage local",
        "MOUNT": "Caminho montado/NAS",
    }
    FREQUENCIAS = (
        (6, "6 horas"),
        (12, "12 horas"),
        (24, "24 horas"),
        (48, "48 horas"),
        (168, "7 dias"),
    )
    RETENCOES = (3, 7, 15, 30, 60, 90)
    BACKUP_DIR = Config.STORAGE_PATH / "backups" / "sistema"
    RESTORE_UPLOAD_DIR = Config.STORAGE_PATH / "backups" / "restores"
    PRE_RESTORE_DIR = Config.STORAGE_PATH / "backups" / "pre-restore"

    @classmethod
    def contexto(cls):
        config = cls._config()
        historico = cls.repository.fetch_all(
            """
            SELECT *
            FROM config_backups_execucoes
            ORDER BY created_at DESC, id DESC
            LIMIT 40
            """
        )
        return {
            "config": config,
            "historico": historico,
            "tipos_backup": cls.TIPOS_BACKUP,
            "destinos": cls.DESTINOS,
            "frequencias": cls.FREQUENCIAS,
            "retencoes": cls.RETENCOES,
        }

    @classmethod
    def salvar_config(cls, dados, usuario_email):
        config = cls._config()
        tipo_backup = cls._normalizar_opcao(dados.get("tipo_backup"), cls.TIPOS_BACKUP, "Tipo de backup invalido.")
        destino_tipo = cls._normalizar_opcao(dados.get("destino_tipo"), cls.DESTINOS, "Destino de backup invalido.")
        frequencia = int(dados.get("frequencia_horas") or 24)
        retencao = int(dados.get("retencao_dias") or 7)
        if frequencia not in {item[0] for item in cls.FREQUENCIAS}:
            raise ValueError("Frequencia de backup invalida.")
        if retencao not in cls.RETENCOES:
            raise ValueError("Retencao de backup invalida.")
        destino_path = (dados.get("destino_path") or "").strip() or None
        if destino_tipo == "MOUNT" and not destino_path:
            raise ValueError("Informe o caminho montado/NAS para o destino MOUNT.")
        ativo = 1 if dados.get("ativo") else 0
        cls.repository.execute(
            """
            UPDATE config_backups_agendamentos
               SET ativo=%s,
                   tipo_backup=%s,
                   frequencia_horas=%s,
                   destino_tipo=%s,
                   destino_path=%s,
                   retencao_dias=%s,
                   proxima_execucao_em=CASE
                       WHEN %s = 0 THEN NULL
                       WHEN proxima_execucao_em IS NULL THEN DATE_ADD(NOW(), INTERVAL %s HOUR)
                       ELSE proxima_execucao_em
                   END,
                   updated_by=%s
             WHERE id=%s
            """,
            (ativo, tipo_backup, frequencia, destino_tipo, destino_path, retencao, ativo, frequencia, usuario_email, config["id"]),
        )

    @classmethod
    def executar_manual(cls, usuario_email):
        return cls._executar(cls._config(), usuario_email, manual=True)

    @classmethod
    def processar_pendentes(cls, limite=1):
        limite = max(1, min(int(limite or 1), 5))
        agendamentos = cls.repository.fetch_all(
            f"""
            SELECT *
            FROM config_backups_agendamentos
            WHERE ativo = 1
              AND (proxima_execucao_em IS NULL OR proxima_execucao_em <= NOW())
            ORDER BY COALESCE(proxima_execucao_em, created_at), id
            LIMIT {limite}
            """
        )
        return [cls._executar(item, "sistema-agendador", manual=False) for item in agendamentos]

    @classmethod
    def buscar_execucao(cls, execucao_id):
        return cls.repository.fetch_one("SELECT * FROM config_backups_execucoes WHERE id=%s", (execucao_id,))

    @classmethod
    def restaurar_upload(cls, arquivo, dados, usuario_email):
        if not arquivo or not getattr(arquivo, "filename", None):
            raise ValueError("Selecione o arquivo de backup para restauracao.")
        confirmacao = (dados.get("confirmacao") or "").strip()
        if confirmacao != "RESTAURAR":
            raise ValueError("Digite RESTAURAR para confirmar a operacao.")

        restaurar_banco = bool(dados.get("restaurar_banco"))
        restaurar_storage = bool(dados.get("restaurar_storage"))
        if not restaurar_banco and not restaurar_storage:
            raise ValueError("Selecione pelo menos Banco de dados ou Storage para restaurar.")

        caminho = cls._salvar_upload_restore(arquivo)
        resultados = []
        if restaurar_storage:
            resultados.append(cls._restaurar_storage(caminho))
        if restaurar_banco:
            resultados.append(cls._restaurar_banco(caminho))
        return "RESTORE: OK - " + " | ".join(resultados)

    @classmethod
    def _salvar_upload_restore(cls, arquivo):
        nome = secure_filename(arquivo.filename or "")
        if not cls._arquivo_restore_permitido(nome):
            raise ValueError("Formato invalido. Use .sql, .sql.gz, .tar.gz ou .tgz gerado pelo backup do sistema.")
        cls.RESTORE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        destino = cls.RESTORE_UPLOAD_DIR / (datetime.now().strftime("restore-%Y%m%d-%H%M%S-") + nome)
        arquivo.save(destino)
        return destino

    @staticmethod
    def _arquivo_restore_permitido(nome):
        nome = (nome or "").lower()
        return nome.endswith((".sql", ".sql.gz", ".tar.gz", ".tgz"))

    @classmethod
    def _restaurar_banco(cls, caminho):
        script = Path("deployment/restore-db.sh").resolve()
        if not script.exists():
            raise ValueError("Script deployment/restore-db.sh nao encontrado.")
        db_name = os.getenv("DB_NAME")
        if not db_name:
            raise ValueError("DB_NAME ausente para restauracao do banco.")
        env = {**os.environ, "RESTORE_CONFIRM": db_name}
        comando = [str(script), str(caminho), "--yes", "--skip-service"]
        resultado = subprocess.run(comando, cwd=str(Path.cwd()), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1800)
        if resultado.returncode != 0:
            detalhe = ((resultado.stderr or "") + "\n" + (resultado.stdout or "")).strip()[:800]
            raise ValueError("Falha ao restaurar banco: " + detalhe)
        return "banco restaurado"

    @classmethod
    def _restaurar_storage(cls, caminho):
        with tempfile.TemporaryDirectory(prefix="o3restore-storage-") as tmp:
            tmpdir = Path(tmp)
            storage_tar = cls._extrair_storage_tar(caminho, tmpdir)
            if not storage_tar:
                raise ValueError("Artefato nao contem storage.tar.gz para restaurar storage.")
            cls._backup_storage_pre_restore()
            storage = Config.STORAGE_PATH
            storage.mkdir(parents=True, exist_ok=True)
            for item in storage.iterdir():
                if item.name == "backups":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            cls._extrair_tar_seguro(storage_tar, storage)
        return "storage restaurado"

    @classmethod
    def _extrair_storage_tar(cls, caminho, tmpdir):
        nome = str(caminho).lower()
        if nome.endswith((".tar.gz", ".tgz")):
            with tarfile.open(caminho, "r:gz") as tar:
                membro = next((m for m in tar.getmembers() if m.name == "storage.tar.gz"), None)
                if not membro:
                    return None
                cls._validar_membro_tar(membro)
                tar.extract(membro, path=tmpdir)
                return tmpdir / "storage.tar.gz"
        return None

    @classmethod
    def _backup_storage_pre_restore(cls):
        cls.PRE_RESTORE_DIR.mkdir(parents=True, exist_ok=True)
        destino = cls.PRE_RESTORE_DIR / f"storage-pre-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tar.gz"
        storage = Config.STORAGE_PATH
        with tarfile.open(destino, "w:gz") as tar:
            if storage.exists():
                for item in storage.iterdir():
                    if item.name == "backups":
                        continue
                    tar.add(item, arcname=item.name)
        return destino

    @classmethod
    def _extrair_tar_seguro(cls, caminho_tar, destino):
        with tarfile.open(caminho_tar, "r:gz") as tar:
            for membro in tar.getmembers():
                cls._validar_membro_tar(membro)
            tar.extractall(destino)

    @staticmethod
    def _validar_membro_tar(membro):
        path = Path(membro.name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Backup contem caminho invalido no storage.")

    @classmethod
    def caminho_download(cls, execucao_id):
        item = cls.buscar_execucao(execucao_id)
        if not item or item.get("status") != "OK" or not item.get("arquivo_path"):
            raise ValueError("Backup indisponivel para download.")
        caminho = Path(item["arquivo_path"]).resolve()
        destinos_validos = [cls.BACKUP_DIR.resolve()]
        if item.get("destino_tipo") == "MOUNT" and item.get("destino_path"):
            destinos_validos.append(Path(item["destino_path"]).resolve())
        if not any(caminho == destino or destino in caminho.parents for destino in destinos_validos):
            raise ValueError("Caminho de backup invalido.")
        if not caminho.exists() or not caminho.is_file():
            raise ValueError("Arquivo de backup nao encontrado.")
        return item, caminho

    @classmethod
    def _config(cls):
        config = cls.repository.fetch_one("SELECT * FROM config_backups_agendamentos ORDER BY id LIMIT 1")
        if config:
            return config
        config_id = cls.repository.execute_insert(
            """
            INSERT INTO config_backups_agendamentos (uuid, nome, ativo, tipo_backup, frequencia_horas, destino_tipo, retencao_dias)
            VALUES (%s, 'Backup principal', 0, 'COMPLETO', 24, 'LOCAL', 7)
            """,
            (cls.repository.generate_uuid(),),
        )
        return cls.repository.fetch_one("SELECT * FROM config_backups_agendamentos WHERE id=%s", (config_id,))

    @classmethod
    def _executar(cls, agendamento, usuario_email, manual=False):
        execucao_id = cls.repository.execute_insert(
            """
            INSERT INTO config_backups_execucoes
                (uuid, agendamento_id, tipo_backup, destino_tipo, destino_path, status, executado_por, manual)
            VALUES (%s, %s, %s, %s, %s, 'EXECUTANDO', %s, %s)
            """,
            (
                cls.repository.generate_uuid(),
                agendamento.get("id"),
                agendamento.get("tipo_backup") or "COMPLETO",
                agendamento.get("destino_tipo") or "LOCAL",
                agendamento.get("destino_path"),
                usuario_email,
                1 if manual else 0,
            ),
        )
        try:
            artefato = cls._gerar_backup(agendamento, execucao_id)
            cls._limpar_retencao(agendamento)
            status = "OK"
            mensagem = "Backup gerado com sucesso."
        except Exception as erro:
            artefato = {}
            status = "ERRO"
            mensagem = str(erro)[:500]
        cls.repository.execute(
            """
            UPDATE config_backups_execucoes
               SET status=%s,
                   finalizado_em=NOW(),
                   arquivo_nome=%s,
                   arquivo_path=%s,
                   tamanho_bytes=%s,
                   checksum_sha256=%s,
                   mensagem=%s
             WHERE id=%s
            """,
            (
                status,
                artefato.get("nome"),
                artefato.get("path"),
                artefato.get("tamanho"),
                artefato.get("checksum"),
                mensagem,
                execucao_id,
            ),
        )
        cls.repository.execute(
            """
            UPDATE config_backups_agendamentos
               SET ultima_execucao_em=NOW(),
                   proxima_execucao_em=CASE
                       WHEN ativo = 1 THEN DATE_ADD(NOW(), INTERVAL frequencia_horas HOUR)
                       ELSE NULL
                   END,
                   ultimo_status=%s,
                   ultimo_mensagem=%s,
                   updated_by=%s
             WHERE id=%s
            """,
            (status, mensagem, usuario_email, agendamento.get("id")),
        )
        return f"BACKUP: {status} - {mensagem}"

    @classmethod
    def _gerar_backup(cls, agendamento, execucao_id):
        tipo = cls._normalizar_opcao(agendamento.get("tipo_backup"), cls.TIPOS_BACKUP, "Tipo de backup invalido.")
        destino = cls._destino(agendamento)
        destino.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        nome_base = f"o3cloud-backup-{tipo.lower()}-{timestamp}-{execucao_id}"
        arquivo_final = destino / f"{nome_base}.tar.gz"
        with tempfile.TemporaryDirectory(prefix="o3backup-") as tmp:
            tmpdir = Path(tmp)
            manifest = {"tipo": tipo, "gerado_em": timestamp, "execucao_id": execucao_id, "arquivos": []}
            if tipo in ("BANCO", "COMPLETO"):
                db_file = tmpdir / "database.sql.gz"
                cls._dump_database(db_file)
                manifest["arquivos"].append("database.sql.gz")
            if tipo in ("STORAGE", "COMPLETO"):
                storage_file = tmpdir / "storage.tar.gz"
                cls._tar_storage(storage_file)
                manifest["arquivos"].append("storage.tar.gz")
            (tmpdir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")
            with tarfile.open(arquivo_final, "w:gz") as tar:
                for item in tmpdir.iterdir():
                    tar.add(item, arcname=item.name)
        return {
            "nome": arquivo_final.name,
            "path": str(arquivo_final),
            "tamanho": arquivo_final.stat().st_size,
            "checksum": cls._checksum(arquivo_final),
        }

    @staticmethod
    def _dump_database(destino):
        required = {"DB_HOST": os.getenv("DB_HOST"), "DB_PORT": os.getenv("DB_PORT"), "DB_USER": os.getenv("DB_USER"), "DB_PASSWORD": os.getenv("DB_PASSWORD"), "DB_NAME": os.getenv("DB_NAME")}
        faltando = [key for key, value in required.items() if not value]
        if faltando:
            raise ValueError("Variaveis de banco ausentes para backup: " + ", ".join(faltando))
        mysqldump = BackupSistemaService._localizar_mysqldump()
        comando = [
            mysqldump,
            "--single-transaction",
            "--routines",
            "--triggers",
            "--events",
            "--default-character-set=utf8mb4",
            "--host", required["DB_HOST"],
            "--port", str(required["DB_PORT"]),
            "--user", required["DB_USER"],
            required["DB_NAME"],
        ]
        env = {**os.environ, "MYSQL_PWD": required["DB_PASSWORD"]}
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        raw_tmp = None
        gz_tmp = None
        try:
            with tempfile.NamedTemporaryFile(prefix="database-", suffix=".sql", dir=destino.parent, delete=False) as raw:
                raw_tmp = Path(raw.name)
                resultado = subprocess.run(comando, stdout=raw, stderr=subprocess.PIPE, env=env, timeout=1800)
            if resultado.returncode != 0:
                detalhe = (resultado.stderr or b"").decode("utf-8", errors="ignore")[:300]
                raise ValueError("Falha ao executar mysqldump: " + detalhe)
            if raw_tmp.stat().st_size == 0:
                raise ValueError("mysqldump gerou arquivo vazio.")

            gz_tmp = destino.with_name(destino.name + ".tmp")
            with open(raw_tmp, "rb") as origem, gzip.open(gz_tmp, "wb") as gz:
                shutil.copyfileobj(origem, gz)
            BackupSistemaService._validar_dump_gzip(gz_tmp)
            gz_tmp.replace(destino)
        finally:
            for temporario in (raw_tmp, gz_tmp):
                if temporario and temporario.exists():
                    temporario.unlink()

    @staticmethod
    def _validar_dump_gzip(caminho):
        try:
            with gzip.open(caminho, "rb") as gz:
                amostra = gz.read(4096)
        except OSError as erro:
            raise ValueError("Dump do banco nao foi gerado em gzip valido.") from erro
        if not amostra:
            raise ValueError("Dump do banco gerado esta vazio.")

    @staticmethod
    def _localizar_mysqldump():
        candidatos = [
            os.getenv("MYSQLDUMP_PATH"),
            shutil.which("mysqldump"),
            "/usr/bin/mysqldump",
            "/usr/local/bin/mysqldump",
            "/bin/mysqldump",
        ]
        for candidato in candidatos:
            if candidato and os.path.isfile(candidato) and os.access(candidato, os.X_OK):
                return candidato
        raise ValueError("mysqldump nao encontrado no servidor. Instale o pacote cliente do MariaDB/MySQL ou configure MYSQLDUMP_PATH.")

    @staticmethod
    def _tar_storage(destino):
        storage = Config.STORAGE_PATH
        if not storage.exists():
            raise ValueError("Diretorio storage nao encontrado.")
        with tarfile.open(destino, "w:gz") as tar:
            for item in storage.iterdir():
                if item.name == "backups":
                    continue
                tar.add(item, arcname=item.name)

    @classmethod
    def _destino(cls, agendamento):
        destino_tipo = agendamento.get("destino_tipo") or "LOCAL"
        if destino_tipo == "LOCAL":
            return cls.BACKUP_DIR
        if destino_tipo == "MOUNT":
            destino_path = (agendamento.get("destino_path") or "").strip()
            if not destino_path:
                raise ValueError("Destino MOUNT sem caminho configurado.")
            return Path(destino_path)
        raise ValueError("Destino de backup invalido.")

    @classmethod
    def _limpar_retencao(cls, agendamento):
        retencao = int(agendamento.get("retencao_dias") or 7)
        destino = cls._destino(agendamento)
        if not destino.exists():
            return
        limite = datetime.now().timestamp() - (retencao * 86400)
        for arquivo in destino.glob("o3cloud-backup-*.tar.gz"):
            if arquivo.stat().st_mtime < limite:
                arquivo.unlink()

    @staticmethod
    def _checksum(caminho):
        digest = hashlib.sha256()
        with open(caminho, "rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
        return digest.hexdigest()

    @staticmethod
    def _normalizar_opcao(valor, opcoes, mensagem):
        valor = (valor or "").strip().upper()
        if valor not in opcoes:
            raise ValueError(mensagem)
        return valor

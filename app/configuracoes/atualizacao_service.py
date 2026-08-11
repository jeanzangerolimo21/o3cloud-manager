import json
import re
import subprocess
from pathlib import Path

from app.repositories.base_repository import BaseRepository


class AtualizacaoSistemaService:
    REPO_DIR = Path(__file__).resolve().parents[2]
    repository = BaseRepository

    @classmethod
    def contexto(cls):
        estado = cls.estado_instalado()
        historico = cls.historico_verificacoes()
        return {
            "estado": estado,
            "pre_requisitos": cls._pre_requisitos(estado),
            "plano_atualizacao": cls._plano_atualizacao(),
            "fase_atual": "Consulta e planejamento",
            "historico_verificacoes": historico,
            "ultima_verificacao": historico[0] if historico else None,
        }


    @classmethod
    def verificar_atualizacoes(cls, usuario_email):
        estado = cls.estado_instalado()
        execucao_id = cls.repository.execute_insert(
            """
            INSERT INTO config_atualizacoes_verificacoes
                (uuid, status, branch_atual, commit_atual, tag_atual, remoto, executado_por)
            VALUES (%s, 'EXECUTANDO', %s, %s, %s, %s, %s)
            """,
            (
                cls.repository.generate_uuid(),
                estado.get("branch") or ("detached" if estado.get("detached") else None),
                estado.get("commit"),
                estado.get("tag_atual"),
                estado.get("remoto"),
                usuario_email,
            ),
        )
        try:
            tags_remotas = cls._tags_remotas(estado.get("remoto"))
            release_recomendada = cls._release_recomendada(tags_remotas, estado)
            payload = {
                "tags_remotas": tags_remotas[:30],
                "release_recomendada": release_recomendada,
                "estado": {
                    "branch": estado.get("branch"),
                    "commit_curto": estado.get("commit_curto"),
                    "tag_atual": estado.get("tag_atual"),
                    "worktree_limpa": estado.get("worktree_limpa"),
                    "divergencia": estado.get("divergencia"),
                },
            }
            status = "OK"
            mensagem = "Verificação concluída."
            releases_total = len(tags_remotas)
        except Exception as erro:
            payload = {"erro": str(erro)[:500]}
            status = "ERRO"
            mensagem = str(erro)[:500]
            release_recomendada = None
            releases_total = 0
        cls.repository.execute(
            """
            UPDATE config_atualizacoes_verificacoes
               SET status=%s,
                   mensagem=%s,
                   releases_encontradas=%s,
                   release_recomendada=%s,
                   payload_json=%s,
                   finalizado_em=NOW()
             WHERE id=%s
            """,
            (status, mensagem, releases_total, release_recomendada, json.dumps(payload, ensure_ascii=True), execucao_id),
        )
        if status != "OK":
            raise ValueError(mensagem)
        return f"ATUALIZAÇÕES: OK - {mensagem} {releases_total} tag(s) remota(s) encontrada(s)."

    @classmethod
    def historico_verificacoes(cls):
        itens = cls.repository.fetch_all(
            """
            SELECT *
            FROM config_atualizacoes_verificacoes
            ORDER BY created_at DESC, id DESC
            LIMIT 20
            """
        )
        for item in itens:
            item["payload"] = cls._parse_payload(item.get("payload_json"))
        return itens

    @classmethod
    def estado_instalado(cls):
        branch = cls._git(["rev-parse", "--abbrev-ref", "HEAD"])
        commit = cls._git(["rev-parse", "HEAD"])
        commit_curto = cls._git(["rev-parse", "--short", "HEAD"])
        tag_atual = cls._git(["describe", "--tags", "--exact-match"])
        ultima_tag = cls._git(["describe", "--tags", "--abbrev=0"])
        commit_data = cls._git(["show", "-s", "--format=%cI", "HEAD"])
        commit_mensagem = cls._git(["show", "-s", "--format=%s", "HEAD"])
        remoto = cls._git(["config", "--get", "remote.origin.url"])
        upstream = cls._git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
        divergencia = cls._divergencia_upstream() if upstream else {"ahead": None, "behind": None, "status": "Upstream não configurado"}
        alteracoes = cls._alteracoes_locais()
        tags_recentes = cls._tags_recentes()
        return {
            "branch": None if branch == "HEAD" else branch,
            "detached": branch == "HEAD",
            "commit": commit,
            "commit_curto": commit_curto,
            "tag_atual": tag_atual,
            "ultima_tag": ultima_tag,
            "commit_data": commit_data,
            "commit_mensagem": commit_mensagem,
            "remoto": remoto,
            "upstream": upstream,
            "divergencia": divergencia,
            "alteracoes": alteracoes,
            "worktree_limpa": len(alteracoes) == 0,
            "tags_recentes": tags_recentes,
            "repo_dir": str(cls.REPO_DIR),
        }


    @classmethod
    def _tags_remotas(cls, remoto):
        if not remoto:
            raise ValueError("Remote origin não configurado.")
        try:
            resultado = subprocess.run(
                ["git", "-C", str(cls.REPO_DIR), "ls-remote", "--tags", "--refs", "origin"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=20,
                check=False,
            )
        except subprocess.TimeoutExpired as erro:
            raise ValueError("Timeout ao consultar tags remotas.") from erro
        except OSError as erro:
            raise ValueError("Falha ao executar git ls-remote.") from erro
        if resultado.returncode != 0:
            detalhe = (resultado.stderr or "").strip()[:300]
            raise ValueError("Falha ao consultar tags remotas: " + (detalhe or "git retornou erro."))
        tags = []
        for linha in resultado.stdout.splitlines():
            partes = linha.split()
            if len(partes) != 2 or not partes[1].startswith("refs/tags/"):
                continue
            tags.append(partes[1].replace("refs/tags/", "", 1))
        return sorted(set(tags), key=cls._tag_sort_key, reverse=True)

    @classmethod
    def _release_recomendada(cls, tags, estado):
        atual = estado.get("tag_atual") or estado.get("ultima_tag")
        for tag in tags:
            if tag != atual:
                return tag
        return None

    @staticmethod
    def _tag_sort_key(tag):
        numeros = [int(item) for item in re.findall(r"\d+", tag)]
        versao = (numeros + [0, 0, 0])[:3]
        pre_release = 0 if "beta" in tag.lower() else 1
        pre_release_numero = numeros[3] if len(numeros) > 3 else 0
        return (*versao, pre_release, pre_release_numero, tag)

    @staticmethod
    def _parse_payload(payload_json):
        if not payload_json:
            return {}
        try:
            return json.loads(payload_json)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def _divergencia_upstream(cls):
        saida = cls._git(["rev-list", "--left-right", "--count", "@{upstream}...HEAD"])
        if not saida:
            return {"ahead": None, "behind": None, "status": "Não foi possível comparar com upstream"}
        partes = saida.split()
        if len(partes) != 2:
            return {"ahead": None, "behind": None, "status": saida}
        behind, ahead = int(partes[0]), int(partes[1])
        if ahead == 0 and behind == 0:
            status = "Atualizado com upstream"
        elif ahead and behind:
            status = f"Divergente: {ahead} commit(s) à frente e {behind} atrás"
        elif ahead:
            status = f"{ahead} commit(s) à frente do upstream"
        else:
            status = f"{behind} commit(s) atrás do upstream"
        return {"ahead": ahead, "behind": behind, "status": status}

    @classmethod
    def _alteracoes_locais(cls):
        saida = cls._git(["status", "--short"])
        if not saida:
            return []
        return [linha for linha in saida.splitlines() if linha.strip()]

    @classmethod
    def _tags_recentes(cls):
        saida = cls._git(["tag", "--sort=-creatordate"])
        if not saida:
            return []
        return saida.splitlines()[:8]

    @staticmethod
    def _pre_requisitos(estado):
        return [
            {"nome": "Backup recente válido", "status": "Obrigatório", "detalhe": "A execução de update pela tela ficará bloqueada sem backup OK recente."},
            {"nome": "Worktree limpa", "status": "OK" if estado.get("worktree_limpa") else "Atenção", "detalhe": "Há alterações locais" if not estado.get("worktree_limpa") else "Sem alterações locais."},
            {"nome": "Branch/Tag permitida", "status": "Planejado", "detalhe": "Beta deverá usar branch beta ou tags v0.9.x-beta.x."},
            {"nome": "Healthcheck", "status": "Disponível", "detalhe": "deployment/healthcheck.sh já valida serviço, banco e HTTP."},
        ]

    @staticmethod
    def _plano_atualizacao():
        return [
            "Verificar versão atual e release alvo.",
            "Gerar backup obrigatório do banco e storage.",
            "Validar artefato de backup e checksum.",
            "Buscar tag/release permitida no GitHub.",
            "Instalar dependências, aplicar migrations e reiniciar serviço.",
            "Executar healthcheck e registrar resultado.",
        ]

    @classmethod
    def _git(cls, args):
        try:
            resultado = subprocess.run(
                ["git", "-C", str(cls.REPO_DIR), *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if resultado.returncode != 0:
            return None
        return resultado.stdout.strip() or None

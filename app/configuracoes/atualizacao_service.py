import subprocess
from pathlib import Path


class AtualizacaoSistemaService:
    REPO_DIR = Path(__file__).resolve().parents[2]

    @classmethod
    def contexto(cls):
        estado = cls.estado_instalado()
        return {
            "estado": estado,
            "pre_requisitos": cls._pre_requisitos(estado),
            "plano_atualizacao": cls._plano_atualizacao(),
            "fase_atual": "Consulta e planejamento",
        }

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

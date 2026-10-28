from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_runner_executa_copia_temporaria_do_script_atual():
    instalador = (ROOT / "deployment/install-update-runner.sh").read_text()

    assert 'UPDATE_SCRIPT="$APP_DIR/deployment/update-beta.sh"' in instalador
    assert "mktemp -t o3cloud-update-runner-" in instalador
    assert 'cp "\\$UPDATE_SCRIPT" "\\$TEMP_SCRIPT"' in instalador
    assert 'bash "\\$TEMP_SCRIPT" "\\$@"' in instalador


def test_atualizacao_renova_runner_instalado():
    atualizador = (ROOT / "deployment/update-beta.sh").read_text()

    assert 'log "Atualizando runner do sistema."' in atualizador
    assert 'bash "$APP_DIR/deployment/install-update-runner.sh"' in atualizador


def test_lock_orfao_e_removido_sem_liberar_processo_ativo():
    atualizador = (ROOT / "deployment/update-beta.sh").read_text()

    assert "processo_de_atualizacao_ativo" in atualizador
    assert 'kill -0 "$lock_pid"' in atualizador
    assert 'rmdir "$LOCK_DIR"' in atualizador

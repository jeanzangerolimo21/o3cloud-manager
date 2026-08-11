ALTER TABLE config_atualizacoes_verificacoes
    ADD COLUMN IF NOT EXISTS github_repo VARCHAR(180) NULL AFTER remoto,
    ADD COLUMN IF NOT EXISTS github_releases_encontradas INT NOT NULL DEFAULT 0 AFTER releases_encontradas,
    ADD COLUMN IF NOT EXISTS github_release_recomendada VARCHAR(120) NULL AFTER release_recomendada;

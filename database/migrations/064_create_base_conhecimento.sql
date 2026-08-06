CREATE TABLE IF NOT EXISTS kb_bases (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, uuid CHAR(36) NOT NULL UNIQUE, nome VARCHAR(160) NOT NULL,
 descricao VARCHAR(500) NULL, caminho_relativo VARCHAR(255) NOT NULL, ativo TINYINT(1) NOT NULL DEFAULT 1,
 created_by VARCHAR(120) NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 KEY idx_kb_bases_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS kb_pastas (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, base_id BIGINT NOT NULL, parent_id BIGINT NULL,
 nome VARCHAR(160) NOT NULL, caminho_relativo VARCHAR(500) NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 KEY idx_kb_pastas_base (base_id), KEY idx_kb_pastas_parent (parent_id),
 CONSTRAINT fk_kb_pastas_base FOREIGN KEY (base_id) REFERENCES kb_bases(id) ON DELETE CASCADE,
 CONSTRAINT fk_kb_pastas_parent FOREIGN KEY (parent_id) REFERENCES kb_pastas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS kb_conhecimentos (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, uuid CHAR(36) NOT NULL UNIQUE, base_id BIGINT NOT NULL, pasta_id BIGINT NULL,
 titulo VARCHAR(200) NOT NULL, conteudo_html LONGTEXT NULL, tags VARCHAR(1000) NULL, catalogo VARCHAR(80) NOT NULL DEFAULT 'Todos',
 compartilhado TINYINT(1) NOT NULL DEFAULT 0, created_by VARCHAR(120) NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, KEY idx_kb_conhecimentos_base (base_id),
 KEY idx_kb_conhecimentos_pasta (pasta_id), FULLTEXT KEY idx_kb_conhecimentos_busca (titulo,conteudo_html,tags),
 CONSTRAINT fk_kb_conhecimentos_base FOREIGN KEY (base_id) REFERENCES kb_bases(id) ON DELETE CASCADE,
 CONSTRAINT fk_kb_conhecimentos_pasta FOREIGN KEY (pasta_id) REFERENCES kb_pastas(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS kb_arquivos (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, base_id BIGINT NOT NULL, pasta_id BIGINT NULL, conhecimento_id BIGINT NULL,
 nome_original VARCHAR(255) NOT NULL, nome_armazenado VARCHAR(255) NOT NULL, caminho_relativo VARCHAR(700) NOT NULL,
 mime_type VARCHAR(120) NULL, tamanho BIGINT NOT NULL DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 KEY idx_kb_arquivos_base (base_id), KEY idx_kb_arquivos_pasta (pasta_id), KEY idx_kb_arquivos_conhecimento (conhecimento_id),
 CONSTRAINT fk_kb_arquivos_base FOREIGN KEY (base_id) REFERENCES kb_bases(id) ON DELETE CASCADE,
 CONSTRAINT fk_kb_arquivos_pasta FOREIGN KEY (pasta_id) REFERENCES kb_pastas(id) ON DELETE SET NULL,
 CONSTRAINT fk_kb_arquivos_conhecimento FOREIGN KEY (conhecimento_id) REFERENCES kb_conhecimentos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
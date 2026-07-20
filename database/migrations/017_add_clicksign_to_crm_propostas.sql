ALTER TABLE crm_propostas
    ADD COLUMN clicksign_status VARCHAR(40) NOT NULL DEFAULT 'NAO_ENVIADO' AFTER arquivo,
    ADD COLUMN clicksign_document_key VARCHAR(120) NULL AFTER clicksign_status,
    ADD COLUMN clicksign_document_url VARCHAR(255) NULL AFTER clicksign_document_key,
    ADD COLUMN clicksign_envelope_id VARCHAR(120) NULL AFTER clicksign_document_url,
    ADD COLUMN clicksign_sent_at DATETIME NULL AFTER clicksign_envelope_id,
    ADD COLUMN clicksign_signed_at DATETIME NULL AFTER clicksign_sent_at,
    ADD COLUMN clicksign_completed_at DATETIME NULL AFTER clicksign_signed_at,
    ADD COLUMN clicksign_last_sync_at DATETIME NULL AFTER clicksign_completed_at,
    ADD COLUMN clicksign_eventos MEDIUMTEXT NULL AFTER clicksign_last_sync_at,
    ADD INDEX idx_crm_propostas_clicksign_status (clicksign_status);

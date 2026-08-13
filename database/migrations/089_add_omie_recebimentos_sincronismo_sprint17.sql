INSERT INTO config_sincronismos_agendados (uuid, tipo, nome, ativo, frequencia_minutos)
VALUES (UUID(), 'OMIE_RECEBIMENTOS', 'Omie - Recebimentos', 0, 1440)
ON DUPLICATE KEY UPDATE nome=VALUES(nome);

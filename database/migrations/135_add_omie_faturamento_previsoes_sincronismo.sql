INSERT INTO config_sincronismos_agendados (uuid, tipo, nome, ativo, frequencia_minutos)
VALUES (UUID(), 'OMIE_FATURAMENTO_PREVISOES', 'Omie - Faturamento e Previsoes', 0, 1440)
ON DUPLICATE KEY UPDATE nome=VALUES(nome);

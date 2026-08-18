INSERT INTO config_sincronismos_agendados (uuid, tipo, nome, ativo, frequencia_minutos)
VALUES
    (UUID(), 'TRUENAS_BKP1', 'TrueNAS BKP1', 0, 360),
    (UUID(), 'TRUENAS_BKP2', 'TrueNAS BKP2', 0, 360),
    (UUID(), 'TRUENAS_BKP3', 'TrueNAS BKP3', 0, 360),
    (UUID(), 'TRUENAS_BKP4', 'TrueNAS BKP4', 0, 360),
    (UUID(), 'TRUENAS_BKP5', 'TrueNAS BKP5', 0, 360),
    (UUID(), 'TRUENAS_BKP6', 'TrueNAS BKP6', 0, 360),
    (UUID(), 'TRUENAS_BKP7', 'TrueNAS BKP7', 0, 360)
ON DUPLICATE KEY UPDATE nome=VALUES(nome);

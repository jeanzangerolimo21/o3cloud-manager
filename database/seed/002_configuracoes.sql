INSERT INTO configuracoes
(uuid,categoria,chave,descricao,protegido)

VALUES

(UUID(),'OMIE','APP_KEY','App Key OMIE',TRUE),

(UUID(),'OMIE','APP_SECRET','App Secret OMIE',TRUE),

(UUID(),'PROXMOX','URL','URL API Proxmox',FALSE),

(UUID(),'PROXMOX','TOKEN_ID','Token ID',TRUE),

(UUID(),'PROXMOX','TOKEN_SECRET','Token Secret',TRUE),

(UUID(),'PBS','URL','Servidor PBS',FALSE),

(UUID(),'ZABBIX','URL','Servidor Zabbix',FALSE);

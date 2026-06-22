INSERT INTO produtos (
    uuid,
    codigo,
    nome,
    descricao,
    cor,
    ordem
)
VALUES
(
    UUID(),
    'VPS',
    'VPS',
    'Serviços de VPS em Proxmox',
    '#0d6efd',
    1
),
(
    UUID(),
    'O3SHARE',
    'O3CloudShare',
    'Serviço de compartilhamento O3CloudShare',
    '#198754',
    2
),
(
    UUID(),
    'OUTROS',
    'Outros',
    'Demais produtos comercializados pela O3Cloud',
    '#6c757d',
    99
);

ALTER TABLE implantacoes
    ADD COLUMN IF NOT EXISTS emails_excluidos_interacoes TEXT NULL AFTER emails_adicionais;

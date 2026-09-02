# ClickSign: contrato como entidade assinada no Beta

Data: 2026-09-02

## Contexto

O envio para assinatura pela ClickSign usa o documento contratual gerado a partir da proposta. A proposta permanece como registro comercial aprovado pelo executivo, enquanto o contrato e a sua rastreabilidade devem refletir a assinatura eletronica.

## Ajustes implementados

- A integracao ClickSign passa a priorizar a configuracao ativa do banco (`implantacao_integracoes_config`) e usa `.env` apenas como fallback.
- O teste da integracao ClickSign no painel passou a executar uma validacao real em `/envelopes` com o token criptografado do banco.
- A tela de rastreabilidade deixou de exibir o status ClickSign no card da proposta.
- O card do contrato passou a exibir status ClickSign, envelope e data de assinatura.
- Ao concluir assinatura ClickSign, o contrato recebe `clicksign_status`, `clicksign_document_key`, `clicksign_envelope_id`, `clicksign_enviado_em` e `clicksign_assinado_em`.
- Contratos assinados que ainda estejam em `RASCUNHO`, `ENVIADO_CLICKSIGN` ou `AGUARDANDO_ASSINATURA` passam para `CONCLUIDO`.
- O script `scripts/sync_clicksign_propostas.py` passou a criar contexto Flask para carregar configuracoes do banco.

## Atualizacao do Beta

1. Atualizar o codigo no servidor Beta.
2. Reiniciar ou recarregar o Gunicorn do O3Cloud Manager.
3. Validar no painel de integracoes que existe uma configuracao ativa do tipo `clicksign` com URL base, usuario e token.
4. Usar o botao de teste da integracao ClickSign para confirmar `Conexao Clicksign validada em modo leitura.`
5. Sincronizar a proposta pendente ou testar o envio/conclusao de um novo contrato.

## Correcao pontual de registros ja assinados

Para contratos que foram assinados pela ClickSign antes deste ajuste e ficaram com status operacional incorreto, executar uma atualizacao pontual usando a proposta vinculada como origem dos dados ClickSign:

```sql
UPDATE contratos c
JOIN crm_propostas p ON p.id = c.proposta_id
SET c.clicksign_status = 'ASSINADO',
    c.clicksign_document_key = COALESCE(c.clicksign_document_key, p.clicksign_document_key),
    c.clicksign_envelope_id = COALESCE(c.clicksign_envelope_id, p.clicksign_envelope_id),
    c.clicksign_enviado_em = COALESCE(c.clicksign_enviado_em, p.clicksign_sent_at),
    c.clicksign_assinado_em = COALESCE(c.clicksign_assinado_em, p.clicksign_signed_at, NOW()),
    c.status = CASE
        WHEN c.status IN ('RASCUNHO', 'ENVIADO_CLICKSIGN', 'AGUARDANDO_ASSINATURA') THEN 'CONCLUIDO'
        ELSE c.status
    END
WHERE p.codigo_proposta = 'O3-20260902-1242'
  AND c.numero = 'CTR-20260902124858'
  AND c.ativo = 1;
```

## Validacoes realizadas

- `venv/bin/python -B -m py_compile` nos arquivos Python alterados.
- Carregamento do template `components/rastreabilidade.html` pelo Flask.
- Teste real da integracao ClickSign em modo leitura usando token do banco no ambiente local disponivel.

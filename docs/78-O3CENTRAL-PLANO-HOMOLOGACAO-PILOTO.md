# O3Central - plano de homologacao e cliente piloto

## Pre-condicoes

- backup e restore do Manager testados;
- migrations aplicadas primeiro em clone/homologacao;
- CA e storage com permissoes revisadas;
- permissao O3Central concedida apenas a equipe do piloto;
- artefatos em estado CANDIDATO;
- aceite registrado de que o agente Windows de laboratorio ainda nao possui
  Authenticode, com SHA-256 validado antes de cada instalacao;
- cliente formalmente escolhido, janela e contatos definidos;
- plano de retorno sem dependencia do novo acesso.

## Ambiente de laboratorio

Um pfSense nao produtivo, uma VM de servico, um Windows e um Linux. Redes devem
simular cliente sem permitir alcance lateral ao ambiente corporativo. Capturas e
logs nao podem conter credenciais reais.

Avisos do Windows decorrentes da ausencia temporaria de Authenticode devem ser
registrados como limitacao conhecida, nao como falha funcional. Nao desabilitar
SmartScreen ou antivirus de forma global para contornar o aviso.

## Roteiro funcional

1. Selecionar cliente e ambiente existentes.
2. Cadastrar gateway e redes autorizadas.
3. Selecionar VM Proxmox vinculada e publicar porta de teste.
4. Criar um servico manual adicional.
5. Gerar ticket Windows com uma unica instalacao.
6. Instalar, registrar telemetria e acessar apenas o servico permitido.
7. Repetir no Linux.
8. Alterar concessao e confirmar atualizacao de politica.
9. Revogar terminal e confirmar bloqueio.
10. Rotacionar gateway e confirmar recuperacao controlada.
11. Expirar/revogar ticket e confirmar impossibilidade de novo cadastro.

## Testes negativos

- ticket alterado, expirado, revogado e excedido;
- token de outro gateway/cliente;
- VM de ambiente diferente;
- IP fora das redes autorizadas;
- colisao de porta local;
- usuario LEITURA tentando POST ou URL direta;
- CSRF ausente;
- payload grande, campo desconhecido e JSON invalido;
- replay concorrente de enrollment;
- banco, Nginx ou Manager temporariamente indisponivel;
- politica nova invalida, preservando a anterior.

## Recuperacao

- restaurar banco e PKI em ambiente isolado;
- validar fingerprints e relacoes;
- confirmar que backup antigo nao reativa ticket revogado sem procedimento;
- reverter migration/codigo conforme runbook;
- promover artefato anterior.

## Evidencias

Registrar versoes, data, participantes, IDs opacos, resultados, screenshots sem
segredos, logs sanitizados, checksums, falhas e decisoes. Cada teste recebe
PASSOU, FALHOU ou BLOQUEADO com responsavel.

## Criterios de aprovacao

- nenhum cruzamento entre clientes;
- nenhuma credencial em log/UI apos emissao;
- revogacao efetiva no tempo definido;
- ultimo snapshot valido preservado em falha;
- auditoria completa;
- Zabbix detecta indisponibilidade/falha de job;
- backup restauravel;
- zero regressao critica na suite do Manager;
- aprovacao de Operacoes e Seguranca.

## Liberacao do primeiro cliente

Comecar com poucos terminais e servicos nao criticos. Observar pelo periodo
acordado antes de ampliar. Nao usar o novo tunel como unico acesso administrativo
durante o piloto.

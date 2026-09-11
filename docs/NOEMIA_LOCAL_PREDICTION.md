# Noémia — Previsão Local

A previsão local é uma camada de hipótese sobre o futuro imediato, construída exclusivamente a partir do histórico persistente da Noémia.

## O que pode prever

- continuidade de um estado estável;
- retorno a um estado anterior quando existem reversões repetidas;
- repetição de uma transição já observada.

## O que não pode afirmar

A previsão não é certeza, não implica causalidade e não deve substituir uma observação nova.

Fluxo:

`Histórico → Dinâmica → Padrão → Hipótese de próximo estado → Nova observação → Correção`

A nova observação tem prioridade sobre qualquer previsão anterior.

Esta camada é deliberadamente conservadora para que a Noémia aprenda padrões sem transformar coincidências em factos.

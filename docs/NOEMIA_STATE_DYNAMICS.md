# Noémia — Dinâmica de Estados

A Noémia não deve apenas saber o estado atual de uma informação. Deve reconhecer como esse estado evolui.

## Padrões

- `stable` — valor observado sem mudanças relevantes.
- `reversal` — uma mudança regressou ao estado anterior.
- `oscillation` — duas ou mais mudanças alternam repetidamente entre estados.
- `repeated_change` — a propriedade muda várias vezes, sem assumir uma causa.
- `temporary` — uma alteração foi marcada como temporária e há evidência posterior compatível.

## Regra epistemológica

Uma sequência temporal pode mostrar que A aconteceu antes de B. Isso não prova que A causou B.

A dinâmica de estados mantém:

`valor anterior → valor novo → evidência → tempo → padrão → confiança`

Isto permite à Noémia distinguir uma preferência estável de uma preferência que muda frequentemente, ou uma mudança que parece ter sido apenas temporária.

## Próxima evolução

Esta camada prepara previsão local conservadora: estimar o próximo estado provável a partir de ciclos já observados, sempre como hipótese e nunca como certeza.

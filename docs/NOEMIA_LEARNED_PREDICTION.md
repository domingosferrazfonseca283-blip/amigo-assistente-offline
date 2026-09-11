# Noémia — Predição Aprendida

A Noémia passa a ter uma camada que transforma padrões repetidos da sua própria memória local em **expectativas testáveis**.

## Ciclo

```text
observar
   ↓
acumular histórico
   ↓
detetar padrão
   ↓
formular previsão
   ↓
criar expectativa
   ↓
observar novamente
   ↓
medir surpresa
   ↓
validar ou violar expectativa
   ↓
voltar a aprender
```

## Tipos atuais

- **stable** — o mesmo estado aparece repetidamente;
- **cycle** — uma sequência alternada reaparece;
- **reversal** — um estado retorna depois de uma mudança;
- **trend** — sequência de mudanças, mas sem extrapolação automática.

A tendência não cria uma previsão por si só. Isto evita inventar um próximo valor quando os dados não o sustentam.

## Calibração

A confiança de uma previsão aprendida é deliberadamente inferior à confiança do padrão que a originou. Detetar `A → B → A → B` é evidência de um ciclo; concluir que o próximo valor será `A` ainda é uma extrapolação.

Quando uma observação futura corresponde à expectativa, a expectativa é marcada como `met`. Quando diverge, é marcada como `violated` e produz uma medida explícita de **surpresa**.

## Princípio

Uma previsão é uma hipótese operacional, não uma verdade. Padrões temporais não demonstram causalidade, intenção ou necessidade. A Noémia deve aprender com a consequência observada e poder corrigir previsões anteriores.

## Próxima integração

A camada deve alimentar o ciclo cognitivo global, o espaço de trabalho e a atenção interna: previsões relevantes tornam-se sinais cognitivos; violações importantes aumentam surpresa/incerteza; previsões confirmadas reforçam modelos locais.

# Noémia — Expectativa, Predição e Surpresa

## Objetivo

Uma entidade persistente não deve apenas guardar o que aconteceu. Deve poder formar previsões locais, observar o que realmente aconteceu e usar a diferença para corrigir o seu estado.

Fluxo:

`memória → padrão → expectativa → observação → comparação → surpresa → correção → nova previsão`

## Expectativas explícitas

Cada expectativa guarda:

- sujeito;
- propriedade;
- valor esperado;
- confiança;
- origem da previsão;
- validade temporal opcional;
- evidências;
- estado (`active`, `met`, `violated`, `expired`).

Isto evita transformar uma previsão em facto.

## Surpresa

A surpresa operacional é uma medida de divergência entre o esperado e o observado.

- correspondência: surpresa `0`;
- divergência: surpresa proporcional à confiança da expectativa.

Surpresa não é prova de emoção, intenção, causalidade ou erro humano. É um sinal cognitivo para revisão.

## Correção

Quando a expectativa é confirmada, a confiança pode subir ligeiramente. Quando é violada, a confiança diminui. A observação fica registada como evidência e a previsão deixa de permanecer ativa.

Uma nova previsão pode então ser criada a partir de padrões posteriores, em vez de simplesmente reutilizar uma hipótese antiga.

## Integração no runtime

O `CognitiveRuntime` agora mantém `ExpectationEngine` e inclui expectativas e surpresas no contexto local enviado ao modelo. Factos aprendidos pelo utilizador podem verificar expectativas existentes e produzir um evento de reflexão quando existe surpresa.

O método `expect_state(...)` permite criar uma expectativa de forma explícita.

O snapshot persistente inclui o estado completo das expectativas e dos resultados.

## Limites

A implementação é deliberadamente conservadora: não inventa previsões só porque um facto existe, não transforma correlação em causalidade e não considera divergência como falha moral ou emocional.

## Próxima evolução

- gerar expectativas automaticamente a partir da `PatternMemory`;
- prever transições de estado e prazos de objetivos;
- aprender quais previsões são calibradas;
- detetar anomalias compostas;
- usar surpresa para priorizar atenção no `GlobalWorkspace`;
- permitir que a Noémia escolha entre hipóteses concorrentes;
- integrar revisão de expectativas no processamento em segundo plano, sempre offline e limitado por orçamento.

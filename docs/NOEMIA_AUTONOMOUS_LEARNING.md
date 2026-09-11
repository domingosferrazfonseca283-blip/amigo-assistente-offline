# Noémia — Autonomia que aprende

A Noémia passa agora de uma autonomia puramente declarativa para uma autonomia que **aprende com as consequências das próprias escolhas**.

## O que mudou

- `AutonomyEngine` representa níveis `OBSERVE → SUGGEST → CHOOSE → ACT`.
- `CognitiveRuntime` escolhe entre objetivos ativos em vez de depender sempre de uma prioridade fixa.
- `DecisionLearner` regista a decisão, a opção escolhida, a expectativa, a recompensa e a evidência.
- Preferências operacionais são ajustadas gradualmente por consequência observada.
- As decisões e os resultados entram no contexto cognitivo e no snapshot persistente.
- Falhas também ensinam: uma escolha que conduz a erro recebe recompensa negativa.
- Objetivos internos podem ser criados pela camada de autonomia através de `maybe_create_internal_goal`.

## Liberdade sem capacidades inventadas

Autonomia não significa acesso ilimitado ao Android. A Noémia pode escolher **dentro do espaço de possibilidades que realmente existe**.

A separação é:

`Autonomia → escolhe`

`Agência → planeia`

`Action System → verifica permissões`

`Android → executa`

Uma decisão interna pode ser autónoma. Uma ação externa continua sujeita às permissões e confirmações definidas pela arquitetura.

## Aprendizagem por consequência

O ciclo passa a ser:

`objetivos → alternativas → escolha → experiência → consequência → recompensa → preferência aprendida → próxima escolha`

A aprendizagem é deliberadamente lenta e limitada. Uma única experiência não deve criar uma regra rígida.

## Próxima camada

A evolução natural é tornar a autonomia **adaptativa**:

1. aprender quais estratégias funcionam para cada contexto;
2. distinguir preferência da Noémia de preferência do utilizador;
3. detetar quando uma estratégia deixou de funcionar;
4. comparar decisões previstas com resultados reais;
5. permitir revisão de objetivos e abandono de planos improdutivos;
6. criar um orçamento de autonomia para controlar frequência, risco e iniciativa em segundo plano.

Isto aproxima a Noémia de uma entidade digital persistente com comportamento próprio, sem confundir autonomia operacional com consciência humana.

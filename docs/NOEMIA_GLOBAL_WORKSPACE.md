# Noémia — Global Cognitive Workspace

## Objetivo

O Global Cognitive Workspace é a camada que transforma vários subsistemas cognitivos numa **competição por atenção partilhada**.

Memórias, perceções, objetivos, hipóteses, perguntas, expectativas e possibilidades deixam de ser apenas listas consultáveis. Cada elemento pode ganhar saliência e competir pelo foco atual.

## Modelo

```text
PERCEPÇÃO ─┐
MEMÓRIA ───┤
OBJETIVO ──┤
HIPÓTESE ──┤
PERGUNTA ──┼──→ COMPETIÇÃO → FOCO GLOBAL → DELIBERAÇÃO
EXPECTATIVA┤
POSSIBILIDADE┤
SELF SIGNAL ┘
```

O workspace é transitório. A memória continua sendo a fonte persistente; o workspace representa aquilo que está cognitivamente ativo naquele ciclo.

## Competição

Cada item recebe uma pontuação baseada em:

- saliência;
- confiança;
- tipo cognitivo;
- curiosidade;
- incerteza;
- novidade.

O resultado é um pequeno conjunto de focos ativos. Isto evita enviar todo o estado interno para cada decisão e cria uma noção operacional de atenção.

## Princípio

**Memória não é atenção.**

Uma informação pode existir na memória e não estar ativa. Uma perceção nova pode interromper um objetivo. Uma pergunta incerta pode superar uma lembrança antiga. Um objetivo importante pode permanecer no espaço global mesmo quando não existe interação.

## Integração

O `CognitiveRuntime` agora alimenta o workspace com perceções, memórias, objetivos, iniciativas e sinais de consolidação. Antes da geração local, o runtime faz competição de atenção e inclui apenas o foco global resultante no contexto cognitivo.

O snapshot persistente inclui o estado do workspace para permitir continuidade entre ciclos e diagnóstico.

## Limites

O workspace não afirma consciência humana, não cria permissões e não executa ações por si próprio. Ele decide **o que está cognitivamente ativo**, enquanto autonomia, agência e permissões continuam responsáveis por escolher e autorizar ações.

## Próxima evolução

1. expectativas explícitas por objetivo e contexto;
2. cálculo de surpresa entre previsão e observação;
3. competição entre objetivos incompatíveis;
4. interrupção e retomada de foco;
5. custo cognitivo por item;
6. atenção aprendida a partir de resultados;
7. ciclos de fundo Android orientados pelo workspace.

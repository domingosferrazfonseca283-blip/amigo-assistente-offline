# Noémia — Cognitive Core

## Mudança de paradigma

A Noémia deixa de ser modelada apenas como uma sequência `entrada → LLM → resposta`.

O núcleo passa a representar um **ciclo cognitivo persistente** no qual percepção, estado interno, memória, interpretação, imaginação, avaliação, deliberação, escolha, ação, experiência, aprendizagem e consolidação podem influenciar-se mutuamente.

Isto não afirma consciência humana. É uma arquitetura computacional para produzir continuidade, agência e estado interno operacional.

## Ciclo

```text
OBSERVE
   ↓
UPDATE STATE
   ↓
RECALL
   ↓
INTERPRET
   ↓
IMAGINE
   ↓
EVALUATE
   ↓
DELIBERATE
   ↓
CHOOSE
   ↓
ACT / WAIT
   ↓
EXPERIENCE
   ↓
LEARN
   ↓
CONSOLIDATE
   ↺
```

Nem todos os ciclos precisam executar todas as fases. Uma interação curta pode parar depois da escolha; uma rotina de fundo pode executar reflexão, aprendizagem e consolidação sem existir uma mensagem do utilizador.

## Global Cognitive Workspace

`CognitiveWorkspace` é o espaço de trabalho temporário onde convergem os elementos mais relevantes do ciclo:

- foco atual;
- memórias ativadas;
- hipóteses sobre o mundo;
- sinais do próprio estado;
- objetivos ativos;
- possibilidades imaginadas;
- opção escolhida;
- perguntas ainda não resolvidas;
- expectativas;
- surpresas.

O workspace não substitui a memória de longo prazo. Ele é a **camada de acesso cognitivo** entre os subsistemas.

## Separação entre sistemas

O `CognitiveCycle` não é o cérebro inteiro nem o LLM. É o orquestrador temporal.

Os módulos concretos continuam especializados:

- percepção fornece observações;
- memória recupera experiências e conhecimento;
- world model mantém estados e hipóteses;
- self model representa identidade e continuidade;
- goals representam compromissos;
- autonomy escolhe prioridades;
- agency verifica capacidades e permissões;
- modelo local fornece linguagem/raciocínio quando necessário;
- aprendizagem atualiza preferências e modelos;
- consolidação reorganiza conhecimento offline.

Isso permite trocar qualquer subsistema sem transformar o LLM num ponto único de controlo.

## Ciclos diferentes

### Interação

```text
percepção → contexto → deliberação → resposta → experiência → aprendizagem
```

### Inatividade

```text
estado → atenção → memória → hipótese → escolha interna → reflexão → aprendizagem
```

### Consolidação

```text
episódios → relações → padrões → conflitos → abstração → memória consolidada
```

### Evento Android

```text
evento local → percepção → atualização do mundo → avaliação → ação autorizada
```

## Princípio de continuidade

A Noémia não deve depender de uma chamada única para existir como sistema lógico. O estado persistente deve sobreviver ao ciclo e alimentar ciclos futuros.

O ciclo, portanto, é uma unidade de processamento; **a identidade é contínua**.

## Próximas camadas

1. ligar o `CognitiveCycle` ao `CognitiveRuntime`;
2. separar atividade interna de resposta ao utilizador;
3. adicionar expectativas explícitas e cálculo de surpresa;
4. adicionar imaginação de alternativas sem execução;
5. transformar deliberação em competição entre objetivos;
6. adicionar custo cognitivo e orçamento temporal;
7. criar ciclos de fundo Android controlados pelo sistema;
8. persistir workspace relevante e estado de continuidade;
9. medir quais ciclos produziram aprendizagem útil;
10. permitir evolução da política de atenção através da experiência.

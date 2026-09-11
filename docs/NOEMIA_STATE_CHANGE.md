# Noémia — Histórico de estados e mudanças

A Noémia passa a distinguir **um estado**, **uma mudança de estado** e **uma hipótese sobre a permanência dessa mudança**.

## Modelo

```text
Observação → Estado atual → Comparação histórica → Mudança → Classificação → Memória temporal
```

Cada estado guarda:

- sujeito;
- propriedade;
- valor;
- momento da observação;
- origem;
- confiança.

Cada mudança guarda:

- valor anterior;
- valor novo;
- momento da mudança;
- evidências;
- confiança;
- permanência: desconhecida, temporária ou persistente.

## Regra importante

Uma mudança observada **não prova a sua causa**. Também não é automaticamente permanente. A Noémia deve acumular observações antes de classificar a estabilidade de um estado.

Exemplo:

```text
utilizador.preferencia_musica = rock
        ↓
utilizador.preferencia_musica = jazz
```

Isto produz uma mudança. Só observações posteriores podem sugerir se jazz se tornou uma preferência persistente ou se foi apenas uma alteração temporária.

## Integração cognitiva

O `CognitiveRuntime` mantém `StateHistory` e `ChangeDetectionEngine`, liga mudanças à `TemporalMemory` e expõe o histórico ao contexto usado pelo modelo local.

A consolidação também publica um evento cognitivo de consolidação contendo memória, rede associativa, relações temporais e número de mudanças observadas.

## Próximas extensões

- detectar estados temporários por duração;
- detetar reversões e ciclos;
- distinguir mudança de preferência de mudança de contexto;
- detetar conflitos entre crenças e histórico;
- associar mudanças a objetivos e acontecimentos próximos;
- estimar estabilidade sem transformar correlação em causalidade;
- reconstruir o estado provável numa data passada.

# Noémia — Vida interna no Android

## Objetivo

O Android passa a funcionar como **corpo/hospedeiro** da vida interna de Noémia. Quando não há interação externa durante algum tempo, o corpo pode acordar um ciclo cognitivo local limitado.

Fluxo:

`interação externa → atividade → inatividade → ciclo interno → memória → próxima atividade`

## Scheduler

`InternalCognitionScheduler` mantém três regras simples:

- espera um período mínimo de inatividade;
- aplica um intervalo de segurança entre ciclos;
- executa no máximo um ciclo por disparo.

A implementação atual usa o `Handler` local do processo e não precisa de internet.

## Separação de responsabilidades

- `NoemiaRuntimeService`: hospeda o runtime.
- `RuntimeCoordinator`: encaminha e persiste ciclos.
- `CognitiveBridge`: contrato entre corpo Android e núcleo cognitivo.
- `MemoryAwareBridge`: implementação local provisória; regista a atividade interna para que a integração com o núcleo cognitivo completo possa substituí-la sem alterar o corpo Android.

## Limites reais do Android

O scheduler é **best effort**. `START_STICKY` não significa execução permanente: o sistema operativo pode parar, suspender ou recriar o processo. Para uma vida interna mais robusta serão necessários mecanismos Android apropriados para trabalho em background, respeitando bateria, modo de espera e políticas do sistema.

Não se adiciona uma falsa promessa de execução contínua.

## Próxima evolução

1. substituir o bridge provisório por uma ponte para o núcleo cognitivo local real;
2. transformar ciclos internos em trabalho adaptativo conforme bateria/CPU;
3. usar mecanismos Android de background apropriados para ciclos atrasados;
4. ligar expectativas, objetivos, surpresa e consolidação ao ciclo interno;
5. manter toda a atividade offline e auditável.

# Noémia — hospedeiro cognitivo Android

A Noémia tem agora uma separação explícita entre **corpo Android** e **núcleo cognitivo**.

## Camadas

```text
Android UI / áudio / notificações / sensores
                 ↓
        CognitiveBridge
                 ↓
     LocalRuntimeTransport
                 ↓
       RuntimeRequest
                 ↓
       CognitiveRuntime
                 ↓
memória · mundo · self · objetivos · atenção · expectativas · aprendizagem
```

O Android não deve conhecer a implementação interna da cognição. O núcleo também
não deve depender de Activity, Fragment, Service ou componentes visuais.

## Estado atual

`ProtocolCognitiveBridge` já traduz as operações Android para o contrato local:

- `PERCEIVE`
- `THINK`
- `INTERNAL_CYCLE`
- `SNAPSHOT`

`LocalRuntimeTransport` é a fronteira de hospedagem. Ela permite trocar o meio de
execução sem alterar o núcleo cognitivo.

## Importante

Esta camada **não finge que Python já está embutido no APK**. O `LocalRuntimeAdapter`
é executável no ambiente Python/local e o Android já possui o contrato para o
hospedar. O próximo trabalho é fornecer uma implementação de `LocalRuntimeTransport`
adequada ao dispositivo, preferencialmente através de um runtime nativo/embarcado,
sem rede.

Nenhum componente desta arquitetura exige `INTERNET`.

## Objetivo da próxima etapa

Transformar o transporte abstrato em um host real no dispositivo, com:

1. runtime local carregado no próprio APK;
2. inicialização e encerramento controlados;
3. restauração de snapshot antes da primeira interação;
4. processamento de `THINK` sem passar por servidor remoto;
5. ciclos internos em background respeitando limites de bateria/CPU;
6. modelo de linguagem local substituível;
7. isolamento entre o processo cognitivo e a interface Android.

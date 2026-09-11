# Noémia — Local Runtime Bridge

## Objetivo

Criar uma fronteira estável entre o **corpo Android** e o **núcleo cognitivo local** sem acoplar a arquitetura a um modelo de linguagem, a Python ou a um fornecedor específico.

A comunicação lógica usa quatro comandos:

```text
PERCEIVE
THINK
INTERNAL_CYCLE
SNAPSHOT
```

Cada pedido tem `command`, `payload` e `request_id`. Cada resposta tem `ok`, `payload`, `error` e `request_id`.

## Por que esta camada existe

O Android não deve conhecer a implementação interna de memória, objetivos, expectativas, aprendizagem ou raciocínio. O núcleo também não deve depender da UI ou do ciclo de vida Android.

```text
Android / corpo
      ↓
Local Runtime Protocol
      ↓
Cognitive Runtime
      ↓
memória + estado + objetivos + aprendizagem
      ↓
modelo local, quando necessário
```

Isto permite substituir a implementação do núcleo sem reescrever o corpo.

## Offline

O protocolo é apenas serialização local. Não cria sockets, HTTP, permissões de Internet ou dependência de serviço remoto.

## Estado

`SNAPSHOT` permite persistir/restaurar o estado do runtime. O `request_id` permite correlacionar operações e preparar auditoria de ciclos futuros.

## Próximo passo

Implementar o adaptador executável que transforma estes comandos em chamadas reais ao `CognitiveRuntime`, mantendo o `MemoryAwareBridge` apenas como fallback de desenvolvimento.

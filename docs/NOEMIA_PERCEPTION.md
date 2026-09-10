# Noémia — Percepção local

A percepção é a porta de entrada do mundo para o núcleo cognitivo. O núcleo não deve depender de chamadas Android diretas; recebe acontecimentos normalizados.

## Tipos

- `user_input` — texto ou entrada direta do utilizador
- `device` — estado local do dispositivo
- `notification` — notificações autorizadas
- `audio` — eventos de áudio processados localmente
- `app` — contexto de aplicação
- `time` — passagem do tempo e eventos temporais
- `sensor` — sensores autorizados
- `location` — localização apenas quando explicitamente autorizada
- `system` — eventos do sistema

## Arquitetura

`Android/Kotlin → LocalContextBridge → PerceptionEngine → EventBus → CognitiveRuntime`

O `PerceptionEngine` mantém um histórico limitado e associa confiança, origem e timestamp a cada percepção.

O `LocalContextBridge` é apenas um contrato/adaptador. A implementação Android será responsável por pedir permissões e respeitar o ciclo de vida do sistema.

## Privacidade

A percepção é offline-first. Não existe cliente HTTP ou mecanismo de envio remoto nesta camada. Cada fonte deverá ter permissão independente e poder ser desligada.

## Próximo nível

A camada Android poderá alimentar a percepção através de `BroadcastReceiver`, `NotificationListenerService`, sensores, relógio do sistema, estado da bateria e outros componentes locais. Esses dados serão convertidos em acontecimentos antes de entrarem no cérebro da Noémia.

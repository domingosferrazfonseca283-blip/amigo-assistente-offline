# Noémia Android

Este diretório contém o primeiro corpo Android da Noémia.

## Estrutura

- `app/` — módulo Android.
- `MainActivity` — ponto de entrada.
- `NoemiaRuntimeService` — processo persistente preparado para alojar o runtime.

## Regra arquitetural

O Android é o **corpo**, não o cérebro. O serviço não decide nem executa ações sensíveis por si próprio. O núcleo cognitivo permanece separado e as capacidades do dispositivo serão ligadas através de adaptadores com permissões explícitas.

## Próximas integrações

1. armazenamento persistente local;
2. ponte Kotlin ↔ núcleo cognitivo;
3. percepção de eventos do sistema;
4. áudio local (STT/TTS);
5. notificações e contexto temporal;
6. execução de ações através da política de agência.

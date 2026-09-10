# Noémia Core

O centro do projeto é o `NoemiaCore`. A interface Android, voz e ações do aparelho devem conversar com este núcleo em vez de implementar uma personalidade separada.

```text
                 ┌──────────────────────┐
                 │       Noémia UI      │
                 │ texto / voz / estado │
                 └──────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │   NoemiaCore    │
                    │ conversa +      │
                    │ contexto        │
                    └───┬──────┬──────┘
                        │      │
             ┌──────────▼─┐ ┌─▼────────────┐
             │ LocalMemory │ │ LocalKnowledge│
             └─────────────┘ └──────────────┘
                        │
                  ┌─────▼─────┐
                  │ LocalModel │
                  └─────┬─────┘
                        │
                  ┌─────▼─────┐
                  │ LocalVoice │
                  └───────────┘
```

## Ordem de construção

1. Núcleo conversacional e estado.
2. Memória persistente com memórias importantes separadas do histórico bruto.
3. Modelo local para geração.
4. Base de conhecimento e pesquisa local.
5. Voz offline: fala e reconhecimento.
6. Interface Android.
7. Camada de ações/permissões do Android.
8. Testes de privacidade e comportamento offline.

Nenhuma dessas camadas deve exigir uma API de nuvem para a conversa funcionar.

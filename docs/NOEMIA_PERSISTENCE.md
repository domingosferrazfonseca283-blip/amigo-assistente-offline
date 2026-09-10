# Noémia — Persistência

A continuidade da Noémia é tratada como parte do estado cognitivo, não como um detalhe da interface.

## Fluxo

`Runtime inicia → restaura snapshot → percebe → pensa → age/responde → persiste snapshot`

O Android possui três fronteiras:

- `NoemiaStore` — armazenamento local do snapshot.
- `CognitiveBridge` — contrato entre Kotlin e o núcleo cognitivo.
- `RuntimeCoordinator` — coordena restauração e persistência no ciclo de vida.

## Garantias arquiteturais

- não existe armazenamento remoto;
- o estado pode sobreviver ao encerramento da Activity;
- a memória cognitiva permanece separada da UI;
- o formato de snapshot pode evoluir sem prender o núcleo a Android;
- operações de limpeza devem ser explícitas.

## Segurança

O armazenamento atual é uma fundação local mínima. Dados realmente sensíveis deverão passar por uma camada criptográfica/keystore antes de a aplicação ser considerada pronta para produção.

A persistência não deve transformar uma memória em facto: confiança, origem, contexto e possibilidade de correção continuam a ser responsabilidade do núcleo cognitivo.

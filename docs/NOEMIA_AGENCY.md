# Noémia — Agência e Iniciativa

A Noémia não deve ser apenas reativa. A camada de agência transforma objetivos persistentes em planos e permite iniciativa proativa controlada.

## Fluxo

`Objetivo → Priorização → Plano → Política → Iniciativa → Confirmação/Permissão → Ação → Resultado → Experiência → Aprendizagem`

## Princípios

- Um objetivo não dá automaticamente permissão para agir.
- Toda capacidade do dispositivo é uma capacidade explicitamente registada.
- Ações podem ser `deny`, `confirm` ou `allow`.
- A política de iniciativa possui cooldown, prioridade mínima e limite de pendências.
- A confirmação do utilizador pode ser obrigatória mesmo quando uma capacidade está ativa.
- A execução concreta de ações Android fica fora do núcleo cognitivo.

## Por que isto é importante

A agência fica separada do modelo de linguagem. O modelo pode sugerir ou raciocinar sobre uma ação, mas não recebe por isso acesso automático ao telefone.

Isto permite que futuramente a Noémia tenha iniciativa para coisas como lembrar um objetivo, preparar uma tarefa ou sugerir algo, enquanto operações com impacto real no dispositivo permanecem sujeitas às permissões definidas pelo utilizador.

## Estado futuro

Esta camada será ligada ao Android através de adaptadores de capacidades: notificações, calendário, ficheiros, áudio, sensores e outras APIs locais. Cada adaptador terá uma política própria.

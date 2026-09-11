# Noémia — Vida interna limitada

A Noémia passa a ter um mecanismo explícito para executar ciclos cognitivos quando não existe uma mensagem nova.

## Princípio

Vida interna, neste projeto, significa **continuidade computacional observável**: rever objetivos, expectativas, anomalias e memória dentro de limites definidos. Não significa consciência humana.

## Ciclo

`inatividade → sinais internos → competição de atenção → tarefa interna → reflexão/revisão → registo → próximo ciclo`

Os sinais atuais são:

- objetivos ativos;
- curiosidade;
- incerteza;
- novidade;
- manutenção futura;
- relacionamento, quando integrado pelo runtime.

## Limites

A camada possui orçamento por ciclo, número máximo de tarefas por despertar e limite temporal configurável. Não concede permissões externas e não executa ações no dispositivo por si só.

O hospedeiro Android decide quando acordar a camada. O sistema não promete execução contínua em segundo plano, porque o Android pode suspender processos e impor restrições de bateria/lifecycle.

## Evolução prevista

1. ligar a atividade interna ao `CognitiveCycle`;
2. rever expectativas e gerar novas previsões;
3. consolidar memórias relevantes;
4. medir resultados de decisões anteriores;
5. permitir que a atenção interna evolua com experiência;
6. integrar o ciclo com o serviço Android usando políticas de energia e lifecycle.

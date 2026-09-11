# Noémia — Modelo de relação

O modelo de relação representa persistentemente a pessoa com quem Noémia interage e a evolução da relação, sem afirmar estados humanos que o sistema não pode verificar.

## Camadas

- **UserProfile**: nome, preferências, interesses, padrões de interação e limites conhecidos.
- **RelationshipState**: quantidade de interações, continuidade, familiaridade, tópicos partilhados e momentos importantes.
- **Confidence**: toda aprendizagem sobre o utilizador permanece graduada por confiança.

## Regra fundamental

Uma interação não é automaticamente um facto sobre a pessoa. Uma preferência só deve ser guardada como preferência quando for explicitamente indicada ou suficientemente sustentada por observações repetidas.

## Continuidade

O estado da relação é persistente e deve ser recuperado juntamente com o estado cognitivo. Assim, uma nova sessão pode começar com contexto relacional anterior sem depender da interface ou de uma sessão de chat específica.

## Próximas extensões

1. inferência conservadora de preferências;
2. relações entre pessoas, lugares, atividades e acontecimentos;
3. linha temporal de mudanças de preferências;
4. deteção de contradições e desatualização;
5. explicação de porque uma memória relacional foi recuperada;
6. esquecimento e correção explícitos pelo utilizador.

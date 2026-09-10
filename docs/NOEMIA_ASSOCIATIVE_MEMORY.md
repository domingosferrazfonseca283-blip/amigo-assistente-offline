# Noémia — Memória Associativa

A memória de longo prazo passa a ter duas camadas:

1. **Armazenamento** — episódios e crenças persistidos.
2. **Rede associativa** — entidades, factos, episódios e relações que permitem ativação por significado.

## Modelo

`episódio → entidade → facto/crença → outros episódios`

Cada ligação possui peso e evidência. A ativação começa por correspondência local e propaga-se pela rede, permitindo recuperar memórias relacionadas mesmo quando não repetem exatamente as mesmas palavras.

## Consolidação

`EpisodicMemory + SemanticMemory → MemoryConsolidator → AssociativeMemory`

A consolidação não inventa conhecimento: apenas cria relações a partir de dados já presentes no núcleo.

## Próxima evolução

- identidade persistente de pessoas/entidades;
- relações temporais;
- contexto por sessão/local/atividade;
- importância e recência combinadas;
- esquecimento seletivo;
- deteção de conflitos;
- embeddings locais para recuperação semântica;
- reconstrução da rede após reinício do Android.

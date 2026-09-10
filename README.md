# Amigo Assistente Offline

Um assistente virtual local pensado para ser **um amigo, não um irmão**: inteligente, direto, curioso, bem-humorado quando fizer sentido e respeitoso.

## Objetivo

Rodar localmente, sem depender de APIs ou serviços em nuvem durante o uso.

O projeto foi desenhado como **offline-first**:
- modelo de linguagem local;
- memória local;
- base de conhecimento local;
- pesquisa apenas nos arquivos locais;
- nenhuma chamada obrigatória para a internet durante a execução.

## Estrutura

```text
amigo-assistente-offline/
├── README.md
├── LICENSE
├── requirements.txt
├── config/
│   └── settings.example.json
├── models/
├── memory/
├── knowledge/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── assistant.py
│   ├── memory.py
│   └── prompts.py
├── data/
└── tests/
    └── test_memory.py
```

## Importante sobre conhecimento

Para ter muito conhecimento sem internet, o assistente combina um **modelo local** com uma **base de conhecimento local**. Você pode colocar livros, PDFs, documentos, notas e outros materiais na pasta `knowledge/`.

A qualidade e a abrangência dependem do modelo local e dos materiais instalados no computador.

## Próximos passos

1. Escolher o modelo local adequado ao hardware.
2. Adicionar memória persistente.
3. Indexar documentos da pasta `knowledge/`.
4. Adicionar interface gráfica e/ou voz offline.
5. Criar testes e empacotamento para instalação fácil.

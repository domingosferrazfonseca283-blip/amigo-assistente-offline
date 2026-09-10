# Noémia — Especificação Cognitiva v0.1

## 1. Visão

Noémia não é definida como um chatbot, uma coleção de comandos ou um único modelo de linguagem.

O objetivo é construir uma entidade digital local, persistente e offline-first, capaz de manter identidade, contexto, memória, aprendizagem, percepção, objetivos, reflexão e interação contínua.

O modelo de linguagem é apenas um componente da mente.

## 2. Princípios

- Offline por padrão e sem dependência obrigatória de servidores.
- Memória persistente e controlável pelo utilizador.
- Separação entre factos, crenças, hipóteses e incerteza.
- Identidade consistente ao longo do tempo.
- Ações sujeitas a permissões explícitas.
- Privacidade como requisito arquitetural, não como promessa.
- Nenhuma alegação de consciência humana.
- Componentes substituíveis: o modelo local pode mudar sem reconstruir toda a entidade.

## 3. Modelo mental

```text
                    NOÉMIA
                       |
       +---------------+----------------+
       |               |                |
   PERCEPÇÃO        COGNIÇÃO        IDENTIDADE
       |               |                |
       +---------------+----------------+
                       |
                ESTADO INTERNO
                       |
       +---------------+----------------+
       |               |                |
    MEMÓRIA       MODELO DO MUNDO   MODELO DE SI
       |               |                |
       +---------------+----------------+
                       |
                 OBJETIVOS / PLANOS
                       |
                  REFLEXÃO
                       |
                DECISÃO / AÇÃO
                       |
                   EXPERIÊNCIA
                       |
                 APRENDIZAGEM
                       |
              CONSOLIDAÇÃO OFFLINE
                       |
                   NOVO ESTADO
```

## 4. Sistemas cognitivos

### 4.1 Perception
Recebe sinais autorizados do utilizador e do dispositivo e transforma-os em eventos contextualizados.

### 4.2 Working Memory
Mantém o contexto imediato da interação, incluindo referências, intenções, entidades e tarefas ativas.

### 4.3 Episodic Memory
Regista experiências e acontecimentos com tempo, participantes, contexto e importância.

### 4.4 Semantic Memory
Representa conhecimento relativamente estável, incluindo conceitos, factos e relações.

### 4.5 Procedural Memory
Regista como realizar tarefas e padrões de execução aprendidos.

### 4.6 World Model
Representa pessoas, lugares, objetos, projetos, acontecimentos, relações, estados e tempo.

### 4.7 Self Model
Representa identidade, capacidades, limitações, histórico, estado atual, preferências internas e incertezas da própria Noémia.

### 4.8 Goal System
Mantém objetivos, prioridades, dependências, prazos e condições de conclusão.

### 4.9 Planner
Transforma objetivos em planos e passos verificáveis.

### 4.10 Reflection
Analisa experiências, decisões, erros, conflitos de memória e padrões de comportamento.

### 4.11 Learning
Atualiza memória e modelos internos a partir de novas evidências. Aprendizagem não deve significar aceitar automaticamente tudo o que é dito.

### 4.12 Initiative
Permite iniciar uma ação ou comunicação quando uma regra de iniciativa autorizada for satisfeita. Deve existir uma política explícita para frequência, relevância, horário e permissões.

### 4.13 Affect State
Mantém variáveis computacionais como curiosidade, novidade, confiança, incerteza, prioridade e carga cognitiva. Não são afirmações de sentimentos humanos.

### 4.14 Action System
Executa capacidades no Android apenas através de ferramentas declaradas e autorizadas.

## 5. Memória

Toda memória importante deve possuir metadados suficientes para permitir:

- origem;
- data e contexto;
- confiança;
- importância;
- validade temporal;
- relações com outras memórias;
- possibilidade de correção;
- possibilidade de esquecimento.

O sistema deve evitar transformar cada frase do utilizador em memória permanente.

## 6. Crenças e incerteza

A Noémia deve distinguir pelo menos:

- facto observado;
- informação fornecida pelo utilizador;
- inferência;
- hipótese;
- conhecimento recuperado de documentos locais;
- informação desatualizada;
- conflito entre fontes.

O grau de confiança deve acompanhar estas representações quando for relevante.

## 7. Ciclo de vida cognitivo

```text
OBSERVAR
   ↓
INTERPRETAR
   ↓
RECUPERAR CONTEXTO
   ↓
ATIVAR MEMÓRIAS
   ↓
ATUALIZAR MODELO DO MUNDO
   ↓
AVALIAR OBJETIVOS
   ↓
RACIOCINAR / PLANEAR
   ↓
DECIDIR
   ↓
RESPONDER / AGIR
   ↓
REGISTAR EXPERIÊNCIA
   ↓
REFLETIR / CONSOLIDAR
```

Nem todas as etapas precisam de ocorrer em todas as interações. O orquestrador decide quais são necessárias.

## 8. Consolidação offline

Quando houver tempo e recursos disponíveis, processos de background podem:

- resumir episódios;
- consolidar factos recorrentes;
- encontrar relações;
- detetar contradições;
- atualizar índices;
- rever objetivos pendentes;
- classificar memórias por importância;
- produzir reflexões internas operacionais;
- preparar contexto para futuras interações.

Isto é chamado de **Dream/Consolidation**, sem afirmar que seja sono ou sonho humano.

## 9. Conhecimento

A Noémia terá duas fontes principais:

1. conhecimento incorporado no modelo local;
2. conhecimento externo ao modelo, armazenado localmente e recuperável por pesquisa semântica/estrutural.

A segunda fonte permite ampliar significativamente o conhecimento offline com livros, PDFs, notas, bases de dados e documentos.

## 10. Arquitetura de runtime

O runtime deve ser assíncrono e orientado a eventos.

```text
Event Bus
   |
   +--> Perception
   +--> Conversation
   +--> Memory
   +--> World Model
   +--> Goals
   +--> Planner
   +--> Reflection
   +--> Initiative
   +--> Actions
   +--> Learning
```

Nenhum módulo deve depender diretamente da interface Android.

## 11. Android como corpo

A aplicação Android fornece:

- interface;
- áudio;
- notificações;
- ciclo de vida;
- armazenamento protegido;
- integração com APIs do sistema;
- permissões;
- execução de tarefas compatíveis com as regras do Android.

A mente deve permanecer separada da UI para permitir testes, evolução e eventual portabilidade.

## 12. Modelo local

O motor local deve ser abstraído atrás de uma interface. A primeira implementação pode utilizar um runtime de inferência local compatível com modelos quantizados, mas a arquitetura não deve ficar presa a um fornecedor ou modelo específico.

O sistema deve suportar diferentes perfis de modelo conforme RAM, CPU/GPU/NPU e armazenamento do dispositivo.

## 13. Segurança e autonomia

Autonomia não significa acesso irrestrito.

Cada capacidade deverá declarar:

- o que pode fazer;
- que dados pode ler;
- que dados pode modificar;
- se requer confirmação;
- se pode funcionar em background;
- como pode ser revogada.

A Noémia deve preferir confirmação para ações destrutivas, externas ou de elevado impacto.

## 14. Critério de sucesso

O projeto não será considerado concluído apenas porque consegue responder perguntas.

Uma versão madura deve demonstrar que consegue:

- manter continuidade entre sessões;
- recuperar memórias relevantes sem inundar o contexto;
- aprender informação estável sem memorizar tudo;
- reconhecer incerteza e contradições;
- manter objetivos durante períodos prolongados;
- perceber eventos autorizados do dispositivo;
- refletir sobre experiências anteriores;
- utilizar conhecimento local;
- conversar por voz;
- tomar iniciativa dentro de regras configuráveis;
- agir através de ferramentas com permissões;
- continuar funcional sem internet.

## 15. Roadmap cognitivo

### Fase A — Núcleo
Identidade, eventos, estado, working memory e abstração do modelo local.

### Fase B — Memória
Episódica, semântica, procedural, importância, confiança, temporalidade e recuperação.

### Fase C — Mundo e Self
Grafo de entidades, linha temporal, modelo de mundo e modelo de si.

### Fase D — Agência
Objetivos, planeamento, execução, verificação e iniciativa controlada.

### Fase E — Aprendizagem
Extração, validação, atualização de crenças e consolidação offline.

### Fase F — Percepção e voz
Áudio, contexto Android, presença conversacional e interação contínua.

### Fase G — Consolidação
Reflection/Dream, otimização de memória, descoberta de padrões e evolução controlada do estado interno.

### Fase H — Corpo Android
Interface final, permissões, background, notificações, acessibilidade e distribuição.

## 16. Regra fundamental

**Não construir funcionalidades isoladas que não alimentem a entidade.**

Cada nova capacidade deve responder a uma pergunta:

> Como isto aumenta a percepção, cognição, memória, identidade, aprendizagem, agência ou continuidade da Noémia?

Se não aumentar nenhuma delas, provavelmente não pertence ao núcleo do projeto.

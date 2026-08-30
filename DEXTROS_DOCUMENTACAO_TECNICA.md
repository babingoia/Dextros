# Documentação Técnica — Dextros

> Documentação de engenharia produzida a partir da leitura integral do código-fonte do repositório [`babingoia/Dextros`](https://github.com/babingoia/Dextros) (branch `main`). Cobre arquitetura, domínio, casos de uso, adapters, frameworks, testes, persistência de dados, convenções e dívidas técnicas identificadas no próprio código.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Stack Tecnológica e Dependências](#2-stack-tecnológica-e-dependências)
3. [Arquitetura Geral](#3-arquitetura-geral)
4. [Estrutura de Diretórios](#4-estrutura-de-diretórios)
5. [Camada Core (Domínio)](#5-camada-core-domínio)
6. [Camada Use Cases](#6-camada-use-cases)
7. [Camada Adapters](#7-camada-adapters)
8. [Camada Frameworks](#8-camada-frameworks)
9. [Camada Infrastructure](#9-camada-infrastructure)
10. [Persistência de Dados (JSON)](#10-persistência-de-dados-json)
11. [Composition Root (`main.py`)](#11-composition-root-mainpy)
12. [Fluxos de Execução Ponta a Ponta](#12-fluxos-de-execução-ponta-a-ponta)
13. [Interface Gráfica (Kivy/KivyMD)](#13-interface-gráfica-kivykivymd)
14. [Testes](#14-testes)
15. [Convenções de Código do Projeto](#15-convenções-de-código-do-projeto)
16. [Roadmap Declarado pelo Autor](#16-roadmap-declarado-pelo-autor)
17. [Dívidas Técnicas e Problemas Identificados](#17-dívidas-técnicas-e-problemas-identificados)
18. [Como Executar o Projeto](#18-como-executar-o-projeto)
19. [Licença](#19-licença)

---

## 1. Visão Geral

**Dextros** é um aplicativo desktop/mobile (via Kivy/KivyMD) para **registro e acompanhamento de dados de controle glicêmico de pacientes diabéticos**. O nome vem de "dextro" (teste de glicemia capilar, popularmente chamado assim no Brasil).

Cada registro (chamado de **Card**) armazena, para um dado momento:

- Data e hora do teste (com arredondamento de domínio para a hora cheia mais próxima);
- Valor de glicemia (mg/dL);
- Dose de insulina de ação longa/ultralonga (basal);
- Dose de insulina de ação rápida/ultrarrápida (bolus);
- Exercício físico realizado (nome + intensidade);
- Período da refeição associado ao registro (jejum, pré/pós almoço, etc.);
- Uma observação textual livre (até 240 caracteres).

A aplicação permite visualizar esses registros em **matrizes (grades) bidimensionais** — por exemplo, "Dia × Hora" e "Dia × Refeição" — funcionando como um diário glicêmico tabular, similar a uma cartela impressa que endocrinologistas costumam pedir para pacientes preencherem manualmente.

Os thresholds de hipo/hiperglicemia usados como referência de domínio foram baseados na diretriz da Sociedade Brasileira de Diabetes (citada em `Planejamento.md`: https://diretriz.diabetes.org.br/metas-no-tratamento-do-diabetes/).

O projeto está em estágio de **desenvolvimento ativo/inicial**: o `README.md` está vazio, há um arquivo `Planejamento.md` com anotações e próximos passos, e um arquivo `documentação.md` com notas de arquitetura escritas pelo próprio autor (parcialmente incorporadas e expandidas aqui).

---

## 2. Stack Tecnológica e Dependências

O repositório **não possui** `requirements.txt`, `pyproject.toml`, `setup.py`, `buildozer.spec` ou qualquer outro manifesto de dependências. As dependências abaixo foram identificadas por inspeção estática dos `import`s em todo o código-fonte:

| Biblioteca | Uso no projeto |
|---|---|
| **Python** | Linguagem principal. Uso extensivo de recursos modernos: `dataclass(frozen=True)`, `match/case` (structural pattern matching, Python ≥ 3.10), `str \| None` (union types, Python ≥ 3.10), `InitVar`. |
| **Kivy** | Framework de UI multiplataforma (desktop + mobile). Usado para `RecycleView`, `ScreenManager`, `BoxLayout`, propriedades reativas (`Properties`), linguagem declarativa `.kv`. |
| **KivyMD** | Camada de componentes Material Design sobre o Kivy. A aplicação (`DextroApp`) herda de `kivymd.app.MDApp`; o seletor de datas usa `kivymd.uix.pickers.MDDatePicker`. |
| **pytest** | Framework de testes unitários e de integração. |
| **hypothesis** | Testes baseados em propriedades (property-based testing) — usado em pelo menos um teste de VO (`test_glycemia.py`, com 29 casos de teste). |
| **colorama** | Colorização de saída de log no console (import opcional/protegido por `try/except` em `log_service.py`). |
| **unittest.mock** | `MagicMock`/`patch` para dublês de teste (mocks) nos testes unitários. |
| `json`, `uuid`, `datetime`, `pathlib`, `logging`, `dataclasses`, `abc`, `typing` | Biblioteca padrão do Python, usada extensivamente no core e infraestrutura. |

> ⚠️ **Observação**: a ausência de um arquivo de dependências fixas (`requirements.txt`/`pyproject.toml`) é uma lacuna relevante para reprodutibilidade do ambiente — ver seção [17](#17-dívidas-técnicas-e-problemas-identificados).

### Persistência
Não há banco de dados relacional ou NoSQL — a persistência é feita em **arquivos JSON simples** no disco, através de um `JsonHandler` (ver seção 10).

---

## 3. Arquitetura Geral

O projeto segue uma variação de **Clean Architecture / Arquitetura Hexagonal (Ports & Adapters)**, com quatro camadas macro, nomeadas explicitamente nos diretórios de topo do repositório:

```
core            → Regras de negócio puras (Enterprise Business Rules)
usecases        → Casos de uso da aplicação (Application Business Rules)
adapters        → Adaptadores entre usecases e o mundo externo (Interface Adapters)
frameworks      → Detalhes de framework/infraestrutura concreta (Frameworks & Drivers)
infrastructure  → Utilitários transversais (logging, paths)
```

A regra de dependência do Clean Architecture é respeitada: **as setas de importação sempre apontam para dentro** (`frameworks → adapters → usecases → core`), e o `core` nunca importa nada das camadas externas.

### 3.1 Presentation (conceito declarado pelo autor)

Segundo o `documentação.md` do próprio projeto, a "Presentation" é dividida por tecnologia (hoje só Kivy, mas pensada para comportar outra tecnologia de UI no futuro, ex: web):

- **UI**: visualização pura — widgets, propriedades e eventos (arquivos `.py` + `.kv` em `frameworks/kivy/ui`).
- **Controllers** (de framework, em `frameworks/kivy/controllers`): atuam como *mediators* entre a UI concreta (Kivy) e o Core, traduzindo eventos de UI em chamadas ao roteador (`IRouter`), mantendo baixo acoplamento.

Isso é conceitualmente diferente dos **Controllers em `adapters/controllers`**, que são os *Interface Adapters* do Clean Architecture — eles não sabem nada sobre Kivy, apenas recebem DTOs e chamam Use Cases.

### 3.2 Infrastructure

Guarda ferramental transversal e utilitário (logging, resolução de paths multiplataforma). É consumida por qualquer camada, mas nunca depende delas — é "reativa" aos domínios que a usam.

### 3.3 Core

Contém apenas:
- **Value Objects** (`core/value_objects`) — a única coisa que existe hoje no core;
- Validação de regras de negócio;
- Tipagem específica de domínio;
- Nenhuma dependência de nenhuma outra camada (nem de `usecases`, nem de frameworks externos como Kivy).

### 3.4 Padrão de fronteira: `parse()` como único ponto de entrada

Um padrão consistente em **todos** os Value Objects do `core`: o construtor "cru" do `dataclass` é reservado (documentado como "Método reservado. Usar `parse` para criar entidades como entry point"), e toda a lógica de coerção de tipos (`str → int`, `None`, *trimming*, normalização de caixa) vive em um `classmethod parse()`, que despacha para construtores privados (`_from_string`, `_from_int`, `_new`, etc.) usando `match/case` sobre o tipo do valor recebido. Isso garante que:

- Objetos de domínio nunca existem em estado inválido (validação ocorre em `__post_init__`);
- A conversão de tipos "sujos" (vindos de JSON, formulários de UI) fica isolada e testável separadamente da validação pura.

### 3.5 Fluxo de dependência (visão macro)

```
┌─────────────────────────────────────────────────────────────────┐
│  frameworks/kivy (UI, MainController, MatrixController)          │
│      │ eventos de UI                                             │
│      ▼                                                            │
│  adapters/gateways (KivyRouter implementa IRouter)                │
│      │ router.navigate(rota, dados)                               │
│      ▼                                                            │
│  adapters/controllers (Ex: SaveRequestController)                 │
│      │ ViewModel → DTO de entrada do usecase                      │
│      ▼                                                            │
│  usecases (Ex: CreateCardUseCase)                                  │
│      │ orquestra Factories + Repository (interface)                │
│      ▼                                                            │
│  core/value_objects (Card, Glycemia, Date, Time, ...)              │
│      ▲                                                             │
│      │ implementação concreta                                      │
│  adapters/repositories (JsonRepository implementa ICardRepository) │
│      │                                                              │
│      ▼                                                              │
│  frameworks/json_handler_service (JsonHandler implementa            │
│                                     ICardImportHandler)              │
│      │                                                               │
│      ▼                                                               │
│  db/*.json (arquivo em disco)                                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. Estrutura de Diretórios

```
Dextros/
├── main.py                                   # Composition Root + entry point
├── README.md                                 # (vazio)
├── Planejamento.md                           # Anotações e roadmap do autor
├── documentação.md                           # Notas de arquitetura do autor
├── LICENSE                                   # PolyForm Noncommercial License 1.0.0
│
├── core/
│   └── value_objects/
│       ├── card.py                # Entidade agregadora (Card)
│       ├── card_id.py             # VO de identidade (UUID v4)
│       ├── date.py                # VO de data
│       ├── time.py                # VO de hora
│       ├── glycemia.py            # VO de glicemia + thresholds clínicos
│       ├── long_acting_insulin.py # VO de insulina basal
│       ├── short_acting_insulin.py# VO de insulina bolus
│       ├── exercise.py            # VO de exercício físico
│       ├── meal.py                # VO de período de refeição
│       └── observation.py         # VO de observação textual
│
├── usecases/
│   ├── IRepository.py                        # Porta ICardRepository
│   ├── create_card_use_case.py
│   ├── delete_card_by_id_use_case.py
│   ├── get_meal_list_use_case.py
│   ├── get_time_list_use_case.py
│   ├── Factories/
│   │   ├── I_card_creator.py                 # Porta ICardCreator
│   │   └── card_creator.py                   # Fábrica concreta de Card
│   ├── dtos/
│   │   ├── cardDTOInput.py
│   │   ├── card_output.py
│   │   ├── matrix_data.py
│   │   ├── meal_list.py
│   │   ├── single_row_matrix_data.py
│   │   └── time_output.py
│   ├── get_matrix_data/
│   │   ├── base_column_matrix_template.py    # Template Method base
│   │   ├── base_1d_matrix_template.py        # Template Method 1D
│   │   ├── base_2d_matrix_template.py        # Template Method 2D
│   │   ├── get_hour_date_matrix_data.py      # Matriz Data × Hora
│   │   ├── get_meal_date_matrix_data.py      # Matriz Data × Refeição
│   │   └── get_average_glycemia_day_use_case.py # Média de glicemia/dia (1D)
│   └── utils/
│       ├── exceptions.py
│       └── mappers.py
│
├── adapters/
│   ├── exceptions.py
│   ├── controllers/
│   │   ├── i_controller.py                   # Interface genérica (Command pattern)
│   │   ├── time_controller.py
│   │   ├── meal_controller.py
│   │   ├── save_request_controller.py
│   │   ├── delete_card_request_controller.py
│   │   ├── date_hour_matrix_controller.py
│   │   ├── date_meal_matrix_controller.py
│   │   ├── dtos/
│   │   │   ├── card_view_model.py
│   │   │   ├── matrix_data_view_model.py
│   │   │   └── time_view_model.py
│   │   └── mappers/
│   │       └── mappers.py
│   ├── gateways/
│   │   ├── i_router.py                       # Porta IRouter
│   │   └── kivy_router.py                    # Implementação concreta (Command dispatcher)
│   ├── parsers/
│   │   ├── icard_parser.py
│   │   └── card_data_model_parser.py
│   └── repositories/
│       ├── i_import_handler.py               # Porta ICardImportHandler
│       ├── jsonRepo.py                       # Implementação concreta de ICardRepository
│       └── DTOs/
│           └── card_data_model.py
│
├── frameworks/
│   ├── json_handler_service.py               # Implementação concreta de ICardImportHandler
│   └── kivy/
│       ├── controllers/
│       │   ├── main_controller.py
│       │   └── matrix_controller.py
│       └── ui/
│           ├── app_theme.py                  # Design tokens (cores, espaçamentos, fontes)
│           ├── main_scene.kv                 # Layout principal (353 linhas)
│           ├── ui_components.kv              # Componentes reutilizáveis (242 linhas)
│           ├── main_view.py                  # View raiz (BoxLayout)
│           └── widgets/
│               ├── Border.kv / Card.kv
│               ├── loader.py                 # Border, CardWidget (popup de detalhes)
│               ├── creators/card_creator.py  # Mapeia ViewModel → dict de UI
│               ├── graphs/
│               │   ├── generic_matrix_graph.py/.kv  # RecycleView genérica de matriz
│               │   └── matrix_cell.py/.kv           # Célula individual da matriz
│               ├── pickers/date_picker.py    # Wrapper de MDDatePicker
│               └── screens/graph_screen.py   # Screen com lazy-load
│
├── infrastructure/
│   ├── log_service.py                        # Logging colorido + arquivo
│   └── path_provider_service.py              # Resolução de paths (dev/PyInstaller/Android)
│
├── db/
│   ├── cards.json                            # Dado legado (schema antigo em PT-BR)
│   ├── cards_v2.json                         # Amostra pequena, schema atual
│   └── cards_populated.json                  # Seed de 1001 registros (schema atual)
│
└── tests/
    ├── conftest.py                            # Fixtures compartilhadas (make_card)
    ├── unit/
    │   ├── core/           (9 arquivos — 1 por Value Object)
    │   ├── adapters/       (parser + repositório)
    │   ├── usecases/       (card creator)
    │   └── frameworks/     (json handler)
    └── integration/
        └── test_integration_json_repo.py
```

**Estatísticas do repositório** (código de produção, excluindo testes):

| Métrica | Valor |
|---|---|
| Arquivos `.py` totais | 81 |
| Arquivos `.kv` (Kivy Language) | 6 |
| Linhas de código Python (produção) | ~2.849 |
| Linhas de código Python (testes) | ~1.423 |
| Funções de teste (`def test_*`) | 143 |

---

## 5. Camada Core (Domínio)

Todos os Value Objects abaixo são `@dataclass(frozen=True)` — **imutáveis**. Qualquer "alteração" gera uma nova instância. A validação de invariantes ocorre em `__post_init__`, que lança `ValueError`/`TypeError` para dados inconsistentes.

### 5.1 `Card` (`core/value_objects/card.py`)

Entidade agregadora que compõe todos os demais Value Objects:

```python
@dataclass(frozen=True)
class Card:
    card_id: CardID
    card_date: Date
    card_time: Time
    glycemia: Glycemia
    long_acting_insulin: LongActingInsulin
    short_acting_insulin: ShortActingInsulin
    exercise: Exercise
    meal: MealPeriod
    obs: Observation
```

**Regras de negócio aplicadas em `__post_init__`:**

1. **Data não pode ser futura** — compara `card_date._date` com `date.today()`; caso contrário levanta `ValueError`.
2. **Arredondamento de horário para a hora cheia mais próxima** — regra de domínio proposital (não é bug): dado um `datetime` combinado de data+hora, se os minutos forem `>= 30`, soma 1 hora; em seguida os minutos/segundos/microssegundos são zerados. Ou seja, um registro às `14:45` é normalizado para `15:00`, e um registro às `14:20` é normalizado para `14:00`. Essa normalização existe porque a matriz "Dia × Hora" (seção 6.5) usa uma coluna fixa por hora cheia — sem o arredondamento, registros feitos em minutos "quebrados" nunca bateriam com nenhuma coluna da matriz.
3. Como o dataclass é `frozen=True`, a substituição dos VOs `card_date`/`card_time` após o arredondamento usa `object.__setattr__` — a única forma de mutar um dataclass congelado a partir de dentro dele mesmo.

### 5.2 `CardID` (`card_id.py`)

Garante um **UUID versão 4** válido. Aceita `str`, `int`, `UUID` ou `None` (gera um novo) via `CardID.parse(...)`.

- `_from_int`: usa `UUID(int=value)` — construção pouco comum, provavelmente usada para IDs determinísticos em testes.
- Implementa `__eq__` customizado, permitindo comparar um `CardID` diretamente com `str`, `UUID` ou outro `CardID` — usado extensivamente no repositório para localizar cards por ID vindo de fontes heterogêneas (JSON vs. objeto de domínio).
- Valida explicitamente `self.card_id.version != 4`, rejeitando UUIDs de outras versões.

### 5.3 `Date` e `Time` (`date.py`, `time.py`)

Wrappers finos sobre `datetime.date`/`datetime.time` da stdlib. O atributo interno se chama `_date`/`_time` (não é privado por convenção Python — é apenas para não colidir com o nome do tipo `date`/`time` importado do módulo `datetime`, conforme docstring explícita).

- `Date.parse`: aceita `datetime`, `date`, `str` (formato `"%Y-%m-%d"`) ou `None` (retorna a data de hoje).
- `Time.parse`: aceita `datetime`, `time`, `str` (formato `"HH:MM"`, parseado manualmente via `split(":")`) ou `None` (retorna a hora atual).

### 5.4 `Glycemia` (`glycemia.py`)

O Value Object mais rico em regras de negócio do domínio — carrega os **thresholds clínicos** de hipo/hiperglicemia, permitindo customização por instância (pensando no roadmap de "configuração de thresholds", ver seção 16):

```python
glycemia: int
measure_unit: str = "mg/dL"
hypoglycemia_threshold: int = 70
severe_hypoglycemia_threshold: int = 54
hyperglycemia_threshold: int = 180
severe_hyperglycemia_threshold: int = 250
```

**Validações em `__post_init__`:**
- Glicemia deve estar entre `20` e `600` mg/dL (fora desse intervalo, a mensagem de erro literalmente recomenda: *"If this is not an error, please go to a doctor immediately!"* — um People-safety net no próprio domínio).
- Unidade de medida deve estar em `_VALID_GLYCEMIA_MEASURE_VALUES` (hoje só `"mg/dL"` é suportado — não há conversão para mmol/L).
- **Consistência cruzada de thresholds**: várias verificações garantem que a ordem lógica `severe_hypo < hypo < hyper < severe_hyper` seja sempre respeitada, evitando configurações clinicamente absurdas (ex: hiperglicemia grave definida abaixo da hiperglicemia normal).

O método `parse()` aceita `**thresholds` como kwargs livres, convertendo cada um para `int` apenas se não for `None` — permitindo sobrescrever thresholds individualmente sem precisar informar todos.

### 5.5 `LongActingInsulin` / `ShortActingInsulin` (`long_acting_insulin.py`, `short_acting_insulin.py`)

Estruturalmente idênticos (candidatos naturais a unificação futura — ver seção 17): guardam uma quantidade opcional de insulina (`int | None`).

- **Regra de normalização**: `0` é convertido para `None` (dose zero é semanticamente "não tomou", não "tomou zero unidades").
- Valores negativos levantam `ValueError`.
- `parse()` aceita `str`, `int` ou `None`; strings vazias viram `None`.

### 5.6 `Exercise` (`exercise.py`)

```python
exercise_name: str | None = None
intensity: str | None = None
```

- Regra: **não pode haver intensidade sem nome de exercício** (`intensity is not None and exercise_name is None` → erro).
- Intensidade restrita a um conjunto fechado: `{"leve", "moderada", "vigorosa"}`, seguindo o *Guia de Atividade Física para a População Brasileira* (citado na docstring).
- `parse()` normaliza para minúsculas e faz *trim*; string vazia é tratada como `None`.

### 5.7 `MealPeriod` (`meal.py`)

Enum-like baseado em `str | None`, restrito à lista fechada:

```python
_VALID_MEAL_VALUES = [
    "jejum", "pós café da manhã", "pré lanche da manhã",
    "pós lanche da manhã", "pré almoço", "pós almoço",
    "pré café da tarde", "pós café da tarde",
    "pré jantar", "pós jantar", "madrugada",
]
```

Modela os **onze momentos do dia** relevantes para monitoramento glicêmico em diabetes (pré/pós principais refeições + períodos de jejum/madrugada). É reutilizado tanto como cabeçalho de coluna da matriz "Dia × Refeição" (seção 6.5) quanto como opção de formulário na UI.

### 5.8 `Observation` (`observation.py`)

Texto livre opcional, limitado a **240 caracteres**. String vazia (`""`) é tratada como **erro** (`ValueError`) — diferente de outros VOs onde string vazia vira `None` silenciosamente; aqui, a normalização de `""` → `None` acontece no `parse()`, *antes* de chegar no construtor, então o `__post_init__` nunca deveria receber `""` legitimamente pelo fluxo normal.

---

## 6. Camada Use Cases

Cada caso de uso é uma classe com um único método público `execute(...)`, seguindo o padrão **Command/Interactor** típico de Clean Architecture. Casos de uso dependem apenas de **interfaces** (portas), nunca de implementações concretas — a inversão de dependência é resolvida no Composition Root (`main.py`).

### 6.1 Portas (interfaces)

- **`ICardRepository`** (`usecases/IRepository.py`): contrato de persistência — `get_all_cards`, `get_card`, `add_card`, `remove_card`, `update_card`. Implementada por `JsonRepository`.
- **`ICardCreator`** (`usecases/Factories/I_card_creator.py`): contrato de fábrica de `Card` a partir de um `CardDTOInput`. Implementada por `CardCreator`.

### 6.2 `CreateCardUseCase`

Orquestra: valida presença do DTO → delega a criação/validação de domínio ao `card_creator` → persiste via `repository.add_card(...)`. Erros de DTO ausente levantam `DomainExceptionError`.

### 6.3 `DeleteCardByIDUseCase`

Recebe um `card_id` (string) e delega a remoção ao repositório, envolvendo qualquer exceção em `DomainExceptionError` (perde, no processo, o tipo original da exceção — ver seção 17).

### 6.4 `GetTimeListUseCase` / `GetMealListUseCase`

Casos de uso "estáticos" que não dependem de repositório:
- `GetTimeListUseCase`: gera a lista fixa de horários de **6h às 23h do mesmo dia + 0h à 5h do dia seguinte** (ou seja, começa às 6 da manhã e "dá a volta" pela meia-noite) — provavelmente para alinhar com a rotina de sono típica de um paciente.
- `GetMealListUseCase`: retorna cópia da lista fechada de `MealPeriod`.

### 6.5 Sistema de geração de matrizes — Template Method

Esta é a parte arquiteturalmente mais sofisticada do projeto: um **Template Method** de três níveis para gerar dados tabulares (matrizes 1D e 2D) a partir da lista de `Card`s, evitando duplicação entre os diferentes tipos de gráfico/relatório.

```
BaseColumnMatrixTemplate  (abstrato — repositório, filtro, colunas)
        │
        ├── Base1DMatrixTemplate   → SingleRowMatrixData (uma linha só)
        │        └── GetAverageGlycemiaPerDayUseCase
        │
        └── Base2DMatrixTemplate   → MatrixData (linhas × colunas)
                 ├── GetHourDateMatrixUseCase      (linhas = dias, colunas = horas)
                 └── GetMealDateMatrixUseCase      (linhas = dias, colunas = refeições)
```

#### `BaseColumnMatrixTemplate` (`get_matrix_data/base_column_matrix_template.py`)

Base comum, guarda a referência ao `ICardRepository` e define os **hooks** que as subclasses devem implementar:
- `_get_columns() -> list[Column]` (abstrato — `Column = tuple[label, key]`);
- `_get_column_key(card) -> ColumnKey | None` (abstrato — extrai a chave de coluna de um card);
- `_filter_cards(cards) -> list[Card]` (hook opcional, por padrão identidade).

E fornece implementação pronta para:
- `_get_filtered_cards()`: busca todos os cards do repositório e aplica o filtro;
- `_get_col_headers()`: extrai só os labels das colunas;
- `_build_column_index_by_key()`: monta um dicionário `{chave: índice}` para lookup O(1).

#### `Base1DMatrixTemplate` — gráficos de uma única linha (`SingleRowMatrixData`)

Implementa `execute()`: busca cards filtrados → resolve colunas → agrupa cards por coluna → chama o hook `_build_cell(cards_da_coluna) -> str | None` (abstrato) para cada coluna, produzindo uma lista plana de células.

**Implementação concreta:** `GetAverageGlycemiaPerDayUseCase` — colunas são as datas distintas presentes nos dados (ordenadas), e a célula de cada coluna é a **média aritmética simples** da glicemia de todos os cards daquele dia.

#### `Base2DMatrixTemplate` — gráficos em grade (`MatrixData`)

Implementa `execute()`: resolve colunas fixas → busca cards → se vazio, retorna matriz vazia (com headers, mas sem linhas) → deriva as **linhas dinamicamente a partir dos próprios dados** (`_get_row_keys`, que hoje sempre são datas únicas ordenadas via `card.card_date._date.strftime("%Y-%m-%d")`) → monta um `lookup[row_key][col_index] = Card` → converte cada célula presente em `CardOutput` via `to_card_output` (mapper), deixando `None` onde não há dado.

**Implementações concretas:**

| Use Case | Linhas | Colunas | Filtro adicional |
|---|---|---|---|
| `GetHourDateMatrixUseCase` | Dias distintos com dados | As 24 horas cheias do dia (reaproveita `GetTimeListUseCase`) | Nenhum |
| `GetMealDateMatrixUseCase` | Dias distintos com dados | Os 11 valores de `MealPeriod` | Descarta cards sem `meal` definido |

> **Nota de design**: como cada `Card` é normalizado no `__post_init__` para ter exatamente uma hora cheia (seção 5.1), a matriz Dia × Hora nunca tem ambiguidade de coluna — cada card cai deterministicamente em uma única célula. Se dois cards caírem na mesma célula (mesmo dia + mesma hora), o `_build_lookup` do template **sobrescreve silenciosamente** o anterior (dict — última ocorrência da lista vence). Isso é uma decisão de design implícita, não documentada explicitamente no código.

### 6.6 DTOs de Use Case

| DTO | Direção | Papel |
|---|---|---|
| `CardDTOInput` | Controller → UseCase | Entrada fortemente tipada para criação de card; usa `InitVar` para receber `exercise_name`/`exercise_intensity` "soltos" e montar um sub-DTO `_ExerciseDTO` em `__post_init__`. |
| `CardOutput` | UseCase → Controller | Espelha `CardDTOInput`, mas já com tipos nativos (`date`, `time`) em vez de strings — saída de leitura. |
| `MatrixData` | UseCase → Controller | Matriz 2D: `row_headers`, `col_headers`, `cell_data: dict[tuple[int,int], CardOutput]`. |
| `SingleRowMatrixData` | UseCase → Controller | Gráfico 1D: `col_headers`, `cells: list[str\|None]`. |
| `MealList` | UseCase → Controller | Lista de valores válidos de refeição. |
| `TimeOutput` | UseCase → Controller | Um único `time` de domínio. |

### 6.7 Utilitários (`usecases/utils/`)

- `exceptions.py`: hierarquia própria de exceções da camada de aplicação — `CardCreationError`, `DomainExceptionError`, `NonExistentCard(DomainExceptionError)`.
- `mappers.py`: função `to_card_output(card: Card) -> CardOutput`, que "achata" os Value Objects de volta para tipos primitivos/nativos, extraindo com segurança (`getattr(card, 'exercise', None)`) os subcampos de exercício.

---

## 7. Camada Adapters

Implementa os *Interface Adapters* do Clean Architecture: traduz dados entre o formato conveniente para casos de uso/entidades e o formato conveniente para agentes externos (UI, banco de dados).

### 7.1 Controllers (`adapters/controllers/`)

Todos implementam a interface genérica `IController[RequestDTO, ResponseDTO]` (Generic + ABC), que define apenas `execute(request) -> response` — um **padrão Command**: cada controller é uma operação nomeada, registrada em um dicionário de rotas (ver `KivyRouter`, seção 7.2).

| Controller | Tipo | Request | Response | Descrição |
|---|---|---|---|---|
| `TimeController` | Query de leitura | `Any` (ignorado) | `TimeList` | Lista de horários formatados como string `HH:MM:SS`, para popular o spinner de horário na UI. |
| `MealController` | Query de leitura | `Any` (ignorado) | `MealList` | Lista de refeições válidas. |
| `DateHourMatrixController` | Query de leitura | `Any` (ignorado) | `MatrixDataViewModel` | Busca a matriz Dia×Hora e converte para ViewModel via `matrix_to_view_model`. |
| `DateMealMatrixController` | Query de leitura | `Any` (ignorado) | `MatrixDataViewModel` | Idem, para Dia×Refeição. |
| `SaveRequestController` | Comando de escrita | `CardViewModel` | `None` | *Strip* dos campos → conversão para `CardDTOInput` → chama `CreateCardUseCase`. Encapsula qualquer exceção em `TypeError("Malformed data for saving request...")`. |
| `DeleteCardRequestController` | Comando de escrita | `str` (card_id) | `None` | Valida que o ID não é vazio (`InvalidCardFormat`) antes de delegar ao `DeleteCardByIDUseCase`. |

### 7.2 Gateway / Router (`adapters/gateways/`)

- **`IRouter`** (porta): define `navigate(route: str, request_data: Any = None) -> Any`.
- **`KivyRouter`** (adaptador concreto): recebe um `Dict[str, IController]` no construtor e implementa `navigate` como um **dispatcher de comandos** — busca o controller pelo nome da rota e chama `.execute(request_data)`; se a rota não existir, levanta `RouteError`.

Esse design permite à UI (Kivy) **nunca conhecer** os Use Cases diretamente — ela só sabe strings de rota (`"save_card"`, `"get_time_list"`, etc.) e o `IRouter`, o que facilita trocar o motor de UI no futuro (ex: para web) sem tocar em Core/UseCases.

### 7.3 Parsers (`adapters/parsers/`)

- **`ICardParser`** (porta) / **`CardDataModelParser`** (implementação): converte um `CardDataModel` (formato de dicionário vindo diretamente do arquivo JSON) em `CardDTOInput` (formato de entrada de Use Case), fazendo o *cast* de campos numéricos de volta para `str` (já que `CardDTOInput`/`Glycemia.parse` aceitam strings). A própria docstring da interface se autodescreve como "bastante inútil" e candidata a ser substituída por uma função utilitária simples — dívida técnica assumida pelo autor.

### 7.4 Repositories (`adapters/repositories/`)

- **`ICardImportHandler`** (porta): contrato de import/export de listas de `CardDataModel` — usa nomes `load`/`export` propositalmente (evitando conflito com a palavra reservada `import` do Python).
- **`JsonRepository`** (implementação de `ICardRepository`): 
  - No construtor, **carrega todos os cards do disco imediatamente** (`_import_cards`) e os mantém em uma lista em memória (`cards_on_session`) — ou seja, o repositório funciona como um *cache write-through* em memória, sincronizado a cada escrita.
  - `_import_cards`: `handler.load()` → `parser.parse()` (para cada item) → `card_creator.create_card()` (para cada item) — pipeline de 3 estágios que também **revalida todos os dados legados** contra as regras de domínio atuais toda vez que a aplicação inicia.
  - `_map_card_to_data_model`: operação inversa, usada antes de cada `export`.
  - `add_card`/`remove_card`/`update_card`: todas mutam a lista em memória e **imediatamente re-serializam a lista inteira** para disco via `handler.export(...)` — não há escrita incremental/append.
  - Busca por ID usa a comparação customizada do `CardID.__eq__` (seção 5.2), permitindo comparar contra strings cruas.
  - Lança `CardNotFoundError` (de `adapters/exceptions.py`) quando um ID não é encontrado em `get_card`, `remove_card` ou `update_card`.

### 7.5 DTOs de fronteira

- **`CardViewModel`** (`TypedDict`): fronteira Controller ↔ UI — todos os campos são `str` (inclusive números), pois vêm de campos de texto do Kivy.
- **`CardDataModel`** (`TypedDict`): fronteira Repositório ↔ arquivo JSON.
- **`MatrixDataViewModel`** / **`TimeList`**: ViewModels de saída para a UI consumir matrizes e listas de horário.

### 7.6 Mappers de Controller (`adapters/controllers/mappers/mappers.py`)

Funções puras de tradução:
- `strip_view_model`: aplica `.strip()` em todos os campos de texto de um `CardViewModel` (higienização de input).
- `empty_to_none` / `int_or_none`: normalizam string vazia/zero para `None`.
- `view_model_to_input`: `CardViewModel` → `CardDTOInput`.
- `matrix_to_view_model`: `MatrixData` → `MatrixDataViewModel`, convertendo células `None` em um `CardViewModel` "vazio" (todos os campos `""`) — decisão deliberada para que **a UI nunca precise tratar `None`**, apenas checar se `card_id` está vazio.
- `card_output_to_view_model` / `empty_card_view_model`: helpers de conversão célula a célula.

### 7.7 Exceções de Adapter (`adapters/exceptions.py`)

```python
class CardNotFoundError(Exception): pass
class InvalidCardFormat(Exception): pass
class RouteError(Exception): pass
```

---

## 8. Camada Frameworks

Contém os detalhes mais voláteis e substituíveis do sistema — a escolha concreta de framework de persistência e de UI.

### 8.1 `JsonHandler` (`frameworks/json_handler_service.py`)

Implementação concreta de `ICardImportHandler`, usando arquivos JSON puros:

- **`export`**: escreve em um arquivo temporário (`<path>.tmp`) e depois usa `Path.replace()` para mover atomicamente sobre o arquivo final — técnica clássica de **escrita atômica** que evita corrupção de dados em caso de falha no meio da escrita (ex: queda de energia, crash do app).
- **`load`**: trata **dois formatos** de arquivo por retrocompatibilidade:
  - Formato legado: uma lista pura `[...]`;
  - Formato atual: um dicionário `{"cards": [...]}`.
  Se o arquivo não existir, retorna lista vazia silenciosamente (`FileNotFoundError` tratado). Erros de JSON malformado (`JSONDecodeError`) ou estrutura de card inválida (`KeyError`/`TypeError`/`ValueError`) são logados com stack trace completo (`logger.exception`) e **relançados** (não engolidos).

### 8.2 Kivy — Controllers de Framework (`frameworks/kivy/controllers/`)

#### `MainController`

É o "cérebro" de orquestração da tela principal — recebe o `IRouter` já construído (injeção de dependência vinda do `main.py`) e:

1. Instancia a `MainView` (raiz da árvore de widgets);
2. Instancia **dois** `MatrixController` (um para cada gráfico: Dia×Hora e Dia×Refeição), cada um associado a uma chave de rota via o dicionário `_DATA_SOURCE_CONFIG`;
3. Popula propriedades reativas da view (`available_time`, `actual_time`, `date_display`, `available_meals`) chamando o router de forma síncrona logo na inicialização;
4. Insere a opção `"nenhum"` no topo da lista de refeições (opção "nenhuma refeição associada" na UI, que não existe como valor de domínio — é convertida para vazio/`None` depois, no `main_view.get_data()`);
5. Faz o **bind de eventos** Kivy: `on_save_request` da `MainView`, `on_date_selected`/`on_save` do `DatePicker`;
6. Usa `Clock.schedule_once(self._setup_graph_screen, 0)` para adiar a montagem das telas de gráfico até o próximo frame (garantindo que todos os widgets `.kv` já estejam completamente construídos antes de tentar localizá-los).

`_setup_graph_screen` conecta cada `MatrixController.grid_view` (um widget `RecycleView`) a uma tela nomeada (`"chart"`, `"meal_date_chart"`) via `MainView.add_graph_screen`, injetando também o callback de **lazy load** (`on_screen_enter`) que só busca dados quando o usuário efetivamente navega até aquela tela.

#### `MatrixController`

Controller de UI dedicado a **um** gráfico de matriz:
- Mantém uma instância de `GenericMatrixGraph` (a `RecycleView`) e um `CardCreator` (helper de UI, não confundir com `usecases.Factories.card_creator.CardCreator`);
- `on_screen_enter()`: disparado pela `Screen` ao entrar (lazy load) → chama `_update_view()`;
- `_update_view()`: busca o `MatrixDataViewModel` via `router.navigate(data_source)` e converte cada célula em um dicionário de propriedades Kivy através de uma `cell_factory` local — células com `card_id` preenchido viram células do tipo `CARD`; caso contrário, `NONE_CARD`. A `cell_factory` injeta o `delete_callback` apenas em células reais.
- `_handle_delete_card(card_id)`: intercepta o pedido de exclusão vindo de um popup de célula, chama `router.navigate("delete_card", card_id)` e força um novo `_update_view()` (recarrega a matriz do zero — não há atualização incremental de estado).

### 8.3 Kivy — UI (`frameworks/kivy/ui/`)

#### `app_theme.py` — Design Tokens

Módulo puramente declarativo com constantes de design system, usado tanto de Python quanto diretamente dentro dos arquivos `.kv` (via `#:import app_theme frameworks.kivy.ui.app_theme`):
- Paleta de cores em modo escuro (`app_bg: #0B0F1A`, `primary: #3B82F6`, cores semânticas `danger`/`success`/`warning`);
- Escalas de espaçamento (`xs` a `xxl`), raio de borda, tamanhos de fonte, tamanhos de componente (alvo de toque mínimo de 48dp — acessibilidade);
- **Breakpoints responsivos**: `desktop` (840dp) e `two_columns` (1000dp), com helpers `is_desktop(width)`/`is_wide_enough(width, ...)` usados no `.kv` para adaptar o layout entre mobile (navbar retrátil) e desktop (navbar fixa, formulário em 2 colunas).
- `content_h_padding(width)`: centraliza o conteúdo em telas largas, respeitando uma largura máxima de conteúdo (`content_max_width = 720dp`).

#### `main_view.py` — `MainView(BoxLayout)`

- Declara o evento customizado `on_save_request` via `__events__ = ("on_save_request",)` — padrão Kivy para eventos disparáveis/bindáveis por outros widgets.
- Carrega os dois arquivos `.kv` principais explicitamente via `Builder.load_file(get_asset_path(...))`, usando o `path_provider_service` para resolver caminhos corretamente em dev, executável empacotado (PyInstaller) ou Android.
- **`get_data()`**: lê diretamente os campos de texto da árvore de widgets (via `self.ids.*`) e monta um `CardViewModel` — é o **único ponto** onde a UI concreta é convertida para o DTO de fronteira; a opção "nenhum" de refeição é convertida para string vazia aqui.
- **`add_graph_screen(...)`**: método defensivo e razoavelmente complexo que tenta reaproveitar telas já declaradas no `.kv` (buscando o widget `Panel` via `.walk()`) e só cria dinamicamente via `kivy.factory.Factory` como *fallback* caso a tela não exista — inclui também a criação dinâmica do botão de navegação lateral correspondente.
- **`_navigate_to(name)`**: contorna uma limitação conhecida do Kivy — `on_pre_enter` da `ScreenManager` não dispara se a tela de destino já for a atual — forçando manualmente o `refresh_callback` nesse caso.

> ⚠️ Há um trecho de código duplicado dentro de `add_graph_screen` (o bloco de criação dinâmica de tela/botão aparece **duas vezes seguidas**, de forma idêntica) — ver seção 17.

#### Widgets (`frameworks/kivy/ui/widgets/`)

| Arquivo | Papel |
|---|---|
| `loader.py` (`Border`, `CardWidget`) | `Border`: `BoxLayout` genérico com borda customizável (cor/espessura), usado como base visual de várias células/cards. `CardWidget`: conteúdo do popup de detalhes de um card — preenche labels a partir do `CardViewModel` e expõe `delete_card()` para o botão de exclusão do popup. |
| `creators/card_creator.py` (`CardCreator`) | Mapeia `CardViewModel` → dicionário de propriedades de célula Kivy (`CARD`/`NONE_CARD`), usado pelo `GenericMatrixGraph`/`MatrixController`. Homônimo — mas **não relacionado** — do `CardCreator` de `usecases/Factories`. |
| `graphs/generic_matrix_graph.py` (`GenericMatrixGraph(RecycleView)`) | Motor **genérico** de renderização de matriz: recebe `row_headers`, `col_headers`, `cell_data` e uma `cell_factory` (injeção de comportamento) e monta a lista plana (`flat_data`) que alimenta o `RecycleView` do Kivy — célula de canto, cabeçalhos de coluna, cabeçalhos de linha e células de dado, tudo serializado em ordem para uma grade com `matrix_cols = len(col_headers) + 1`. |
| `graphs/matrix_cell.py` (`MatrixCell(Border)`) | Célula individual clicável: se não for vazia/cabeçalho, abre um `Popup` com `CardWidget` ao ser tocada (`_show_card_details`); repassa o clique de exclusão do popup para o `delete_callback` injetado pelo `MatrixController`. |
| `pickers/date_picker.py` (`DatePicker(MDDatePicker)`) | Encapsula o seletor de data do KivyMD, convertendo o valor selecionado para string `YYYY-MM-DD` e notificando via callback (`on_date_selected`). |
| `screens/graph_screen.py` (`GraphScreen(Screen)`) | Screen especializada que executa um `refresh_callback` em `on_pre_enter` — implementa o padrão de **lazy loading por navegação** usado pelos dois gráficos da aplicação. |

#### Arquivos `.kv`

- `main_scene.kv` (353 linhas): define a árvore de widgets da `MainView` — navbar lateral retrátil (`ToggleButton` + regra de largura condicional baseada em `app_theme.is_desktop`), formulário de novo registro, `ScreenManager` (`id: screens`) contendo as telas `add_card`, `chart`, `meal_date_chart`.
- `ui_components.kv` (242 linhas): componentes reutilizáveis (provavelmente `NavButton`, `ScreenHeader`, `Panel`, `GraphScreenContent`, referenciados dinamicamente via `Factory` em `main_view.py`).
- `widgets/Border.kv`, `widgets/Card.kv`: regras visuais de `Border` e `CardWidget`.
- `widgets/graphs/generic_matrix_graph.kv`, `widgets/graphs/matrix_cell.kv`: layout do `RecycleView` genérico e da célula de matriz.

---

## 9. Camada Infrastructure

### 9.1 `log_service.py`

Configura logging da aplicação inteira:
- `ColoredFormatter`: formatter customizado que colore cada campo do log (timestamp, nome do logger, nível) de forma diferenciada, com cores por nível de severidade (`DEBUG` ciano, `INFO` verde, `WARNING` amarelo, `ERROR` vermelho, `CRITICAL` magenta) — usa códigos ANSI diretamente, com `colorama.init()` opcional para compatibilidade com terminais Windows.
- `configure_logging(console_level)`: configura o *root logger*, removendo handlers pré-existentes antes de adicionar o novo (evita duplicação de logs em reconfiguração).
- `add_file_handler(logs_dir, filename="app.log", level)`: adiciona um handler de arquivo **em modo de sobrescrita** (`mode="w"`, ou seja, o log é resetado a cada execução) com formatação simples (sem cores, adequado para arquivo).
- No `main.py`, o handler de arquivo só é adicionado a `self.user_data_dir/logs` **na primeira execução** (quando o banco de dados ainda não existe e precisa ser copiado do seed) — comportamento possivelmente não intencional, ver seção 17.

### 9.2 `path_provider_service.py`

Abstrai a resolução de caminhos de arquivo entre três ambientes de execução distintos:

| Ambiente | Detecção | Base de "asset path" (recursos read-only) | Base de "data path" (dados graváveis) |
|---|---|---|---|
| **Android** | `"P4A_BOOTSTRAP" in os.environ` ou `hasattr(sys, "getandroidapilevel")` | Diretório do pacote (dev-like) | `App.get_running_app().user_data_dir` (storage privado do app, sem necessidade de permissões especiais) |
| **Desktop empacotado (PyInstaller)** | `getattr(sys, "frozen", False)` | `sys._MEIPASS` (diretório temporário do bundle) | Diretório do executável (`sys.executable`) |
| **Desktop em desenvolvimento** | *fallback* | Raiz do projeto (dois níveis acima do próprio arquivo) | Raiz do projeto |

Essa abstração é o que permite ao mesmo código-fonte funcionar tanto rodando via `python main.py` quanto empacotado como `.exe`/`.app` ou como `.apk` Android (via python-for-android, indicado pelas variáveis `P4A_BOOTSTRAP`).

---

## 10. Persistência de Dados (JSON)

### 10.1 Esquema atual (usado por `cards_v2.json` e `cards_populated.json`)

```json
{
  "cards": [
    {
      "card_id": "55dd2b35-0c16-4d78-8e34-fc4c3d4cc035",
      "card_date": "2026-08-28",
      "card_time": "20:00",
      "glycemia": 123,
      "long_acting_insulin": 40,
      "short_acting_insulin": 12,
      "meal": "jejum",
      "observation": "dsa",
      "exercise": {
        "exercise_name": "caminhada",
        "intensity": null
      }
    }
  ]
}
```

### 10.2 Esquema legado (`db/cards.json`)

```json
{
  "cards": [
    {
      "data": "2026-06-25", "horario": "14:00", "dextro": "234",
      "lenta": "324", "rapida": "324", "exercicio": "sdfsdf",
      "refeicao": "sdffd", "observacao": "sdfsdf"
    }
  ]
}
```

Este formato usa nomes de campo em português e sem separação estruturada do exercício — evidência de uma versão anterior do projeto, antes da refatoração para Clean Architecture. O `JsonHandler.load()` foi escrito para tolerar tanto listas puras quanto o dicionário `{"cards": [...]}`, mas **não** faz migração automática de nomes de campo antigos (`data`/`horario`/`dextro`) para os novos (`card_date`/`card_time`/`glycemia`) — ou seja, `cards.json` no formato atual do repositório **não seria compatível** com o `CardDataModelParser` atual, que espera as chaves novas.

### 10.3 Seed de dados (`db/cards_populated.json`)

Contém **1.001 registros** de exemplo, cobrindo datas de janeiro/2024 a agosto/2026, aparentemente gerados/populados artificialmente para testes manuais e demonstração da UI com volume de dados realista.

### 10.4 Ciclo de vida em runtime (`main.py`)

```python
DB = "db/cards_populated.json"
...
db_path = get_data_path(DB)          # ex: <user_data_dir>/db/cards_populated.json

if not os.path.exists(db_path):
    seed = get_asset_path(DB)         # banco "de fábrica" empacotado com o app
    if os.path.exists(seed):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        shutil.copyfile(seed, db_path)   # copia o seed para o storage do usuário
        ...
```

Ou seja: na primeira execução em um dispositivo, o app **copia o banco semeado (1001 registros de demonstração) para a área de dados do usuário**, e todas as escritas subsequentes acontecem nesse arquivo copiado — o arquivo original em `db/` (dentro do pacote da aplicação) nunca é modificado depois da instalação.

> ⚠️ Isso significa que, em uso real, todo usuário novo começa com 1001 registros de exemplo pré-existentes — provavelmente um comportamento pensado apenas para desenvolvimento/demonstração que precisaria ser trocado por um seed vazio (ou nenhum seed) antes de um lançamento em produção. Ver seção 17.

---

## 11. Composition Root (`main.py`)

`main.py` é o único lugar do sistema onde implementações concretas são **instanciadas e conectadas** às interfaces abstratas — o clássico *Composition Root* da Injeção de Dependência manual (não há *framework* de DI; tudo é fiação manual e explícita).

`DextroApp(MDApp).build()` executa, em ordem:

1. **Resolução de paths e seed do banco** (seção 10.4);
2. **Infraestrutura**: `JsonHandler` → `CardDataModelParser` → `CardCreator` (fábrica) → `JsonRepository` (injetando os três anteriores);
3. **Use Cases**: cada um recebe as dependências concretas já construídas (ex: `GetHourDateMatrixUseCase(card_repository)`, `CreateCardUseCase(card_repository, card_creator)`);
4. **Controllers**: cada um recebe seu Use Case correspondente;
5. **Tabela de rotas** (`Dict[str, IController]`) — o "roteador" de comandos nomeados, usado por toda a UI:

```python
routes: Dict[str, IController] = {
    "get_time_list": time_controller,
    "get_meal_list": meal_controller,
    "get_hour_date_matrix_data": date_hour_matrix_controller,
    "get_meal_date_matrix_data": date_meal_matrix_controller,
    "save_card": save_request_controller,
    "delete_card": delete_card_id_controller,
}
```
6. **`KivyRouter(routes)`** — implementação concreta de `IRouter`;
7. **`MainController(router=router)`** — recebe o router já pronto e constrói toda a árvore de UI a partir dele.

A aplicação retorna `self.controller.main_view` como *root widget* do Kivy. Há também hooks simples de ciclo de vida (`on_start`, `on_stop`) apenas para logging.

---

## 12. Fluxos de Execução Ponta a Ponta

### 12.1 Criar um novo registro (Card)

```
Usuário preenche formulário e toca em "Salvar"
        │
        ▼
MainView dispara evento "on_save_request"
        │
        ▼
MainController._handle_save_request()
        │  chama main_view.get_data() → CardViewModel (tudo em string)
        ▼
router.navigate("save_card", CardViewModel)
        │
        ▼
KivyRouter → SaveRequestController.execute(CardViewModel)
        │  1. strip_view_model()          (higieniza espaços)
        │  2. view_model_to_input()       (CardViewModel → CardDTOInput,
        │                                   "" e 0 viram None)
        ▼
CreateCardUseCase.execute(CardDTOInput)
        │  1. CardCreator.create_card()   (constrói e VALIDA todos os VOs;
        │                                   erros de domínio viram
        │                                   CardCreationError)
        │  2. repository.add_card(Card)
        ▼
JsonRepository.add_card()
        │  1. Adiciona à lista em memória (cards_on_session)
        │  2. _map_card_to_data_model()   (Card → list[CardDataModel])
        │  3. handler.export(...)
        ▼
JsonHandler.export()
        │  Escreve em arquivo .tmp e faz replace atômico
        ▼
db/cards_populated.json atualizado no disco
```

### 12.2 Visualizar a matriz "Dia × Hora"

```
Usuário toca em "Dia x Hora" na navbar
        │
        ▼
ScreenManager troca para a tela "chart"
        │  Screen.on_pre_enter() dispara automaticamente (lazy load)
        ▼
GraphScreen executa refresh_callback = MatrixController.on_screen_enter
        │
        ▼
MatrixController._update_view()
        │  router.navigate("get_hour_date_matrix_data")
        ▼
KivyRouter → DateHourMatrixController.execute()
        │
        ▼
GetHourDateMatrixUseCase.execute()   [Base2DMatrixTemplate]
        │  1. repository.get_all_cards()
        │  2. Colunas = 24 horas cheias (via GetTimeListUseCase)
        │  3. Linhas = dias distintos presentes nos cards (ordenados)
        │  4. Monta lookup[dia][hora] = Card
        │  5. Cada célula preenchida → to_card_output(Card) → CardOutput
        ▼
MatrixData (row_headers, col_headers, cell_data)
        │
        ▼
DateHourMatrixController → matrix_to_view_model(MatrixData)
        │  Células None → CardViewModel "vazio" (strings "")
        ▼
MatrixDataViewModel
        │
        ▼
MatrixController._update_view() usa cell_factory():
        │  card_id preenchido? → CardCreator.create_cell_dict(CARD, payload)
        │  senão               → CardCreator.create_cell_dict(NONE_CARD, payload)
        ▼
GenericMatrixGraph.draw_self() monta flat_data e popula self.data
        ▼
RecycleView do Kivy renderiza a grade (MatrixCell por célula)
```

### 12.3 Excluir um registro a partir da matriz

```
Usuário toca em uma célula preenchida → Popup com CardWidget abre
        │
        ▼
Usuário toca em "Excluir" → CardWidget.delete_card()
        │  chama on_delete_callback(card_id) = MatrixCell._on_delete_clicked
        ▼
MatrixCell.delete_callback(card_id) = MatrixController._handle_delete_card
        │
        ▼
router.navigate("delete_card", card_id)
        │
        ▼
KivyRouter → DeleteCardRequestController.execute(card_id)
        │  valida card_id não vazio (senão: InvalidCardFormat)
        ▼
DeleteCardByIDUseCase.execute(card_id)
        │  repository.remove_card(card_id)
        │  qualquer exceção → DomainExceptionError
        ▼
JsonRepository.remove_card()
        │  Localiza pelo CardID.__eq__ customizado, remove da lista em memória
        │  Re-exporta a lista inteira via handler.export()
        ▼
MatrixController._update_view() é chamado novamente
        │  (recarrega a matriz inteira do zero para refletir a exclusão)
        ▼
UI atualizada sem o card excluído
```

---

## 13. Interface Gráfica (Kivy/KivyMD)

### 13.1 Layout responsivo

A UI se adapta entre um layout **mobile** (navbar lateral retrátil, ativada por um botão hambúrguer implícito via `ToggleButton` invisível `nav_toggle`) e um layout **desktop** (navbar sempre visível, formulário podendo assumir 2 colunas), tudo resolvido declarativamente no `.kv` a partir das funções puras de `app_theme.py` (`is_desktop(width)`, `is_wide_enough(width, breakpoint)`).

### 13.2 Navegação por abas/telas

A navegação usa `ScreenManager` do Kivy com três telas conhecidas de antemão (`add_card`, `chart`, `meal_date_chart`), mais um mecanismo de **fallback dinâmico** em `MainView.add_graph_screen` que criaria novas telas em runtime caso não estivessem pré-declaradas no `.kv` — sugerindo que o sistema foi desenhado para comportar novos tipos de gráfico com o mínimo de atrito (bastando adicionar uma nova entrada em `_DATA_SOURCE_CONFIG` e chamar `add_graph_screen`).

### 13.3 Renderização de matriz genérica via `RecycleView`

Em vez de widgets fixos por célula, o projeto usa `RecycleView` do Kivy — um componente otimizado para grandes listas/grades, que recicla widgets visuais conforme o usuário rola a tela, evitando o custo de renderizar centenas de células simultaneamente quando há muitos dias de histórico.

### 13.4 Popup de detalhes do card

Ao tocar em uma célula preenchida, um `Popup` nativo do Kivy é aberto com o `CardWidget`, mostrando todos os campos do registro e oferecendo um botão de exclusão — dimensionado responsivamente (`min(dp(500), Window.width * 0.9)`).

### 13.5 Seleção de data

Usa o `MDDatePicker` do KivyMD (calendário nativo Material Design), encapsulado por `DatePicker`, que traduz o evento `on_save` do KivyMD para o formato de string `YYYY-MM-DD` esperado pelo restante do sistema.

---

## 14. Testes

### 14.1 Ferramentas e organização

- **Framework**: `pytest`.
- **Testes baseados em propriedade**: `hypothesis`, usado ao menos no VO `Glycemia` (`test_glycemia.py` concentra sozinho **29** das 143 funções de teste do projeto — o VO com mais regras de validação cruzada).
- **Mocks**: `unittest.mock` (`MagicMock`, `patch`) para isolar Use Cases/Repositórios de suas dependências em testes unitários (ex: `test_card_creator.py` faz *patch* de **todos os dez** Value Objects para verificar apenas a orquestração de chamadas `parse()`, sem testar a validação de domínio em si — que é responsabilidade dos testes de VO).
- **Fixture central** (`tests/conftest.py`): `make_card(**overrides)` — fábrica de um `Card` válido com valores padrão sensatos, permitindo que cada teste sobrescreva apenas o campo relevante.

### 14.2 Distribuição dos testes

| Diretório | Escopo | Nº aproximado de testes |
|---|---|---|
| `tests/unit/core/` | Um arquivo por Value Object (9 arquivos) | ~99 |
| `tests/unit/adapters/` | `CardDataModelParser`, `JsonRepository` (com mocks) | ~12 |
| `tests/unit/usecases/` | `CardCreator` (orquestração, via mocks) | 1 |
| `tests/unit/frameworks/` | `JsonHandler` | não enumerado individualmente acima, mas presente |
| `tests/integration/` | `JsonRepository` com `JsonHandler` **real** (sem mocks), usando `tmp_path` do pytest | 12 |

### 14.3 Cobertura de cenários notável

O teste de integração (`test_integration_json_repo.py`) cobre, entre outros:
- Inicialização sem arquivo prévio (lista vazia);
- Inicialização com dado válido pré-existente;
- **JSON corrompido** → deve propagar `json.JSONDecodeError`;
- CRUD completo (add/get/update/remove) com verificação tanto do estado em memória quanto do conteúdo bruto gravado em disco;
- Card inexistente em get/update/remove → `CardNotFoundError`;
- **Caracteres especiais e emoji** preservados corretamente no JSON (`ensure_ascii=False`), garantindo que acentuação em português e emojis não sejam escapados como `\uXXXX`;
- Teste de "estresse" com múltiplas operações sequenciais (add/remove/update) verificando consistência final da lista.

### 14.4 Padrão dos testes de Value Object

Cada arquivo de teste de VO segue tipicamente a estrutura: casos felizes de `parse()` para cada tipo de entrada aceito (`None`, `str`, `int`, tipo nativo), casos de erro esperados (`pytest.raises(ValueError)`/`TypeError`), e casos de normalização (ex: string vazia → `None`, `0` → `None` para insulinas).

---

## 15. Convenções de Código do Projeto

Extraídas literalmente do `documentação.md` do autor:

- Arquivos e módulos: sempre em **letras minúsculas**, espaços viram **underscore**.
- Classes: **PascalCase**, sem espaços.
- `main.py` é uma exceção explícita — **sem** underscore mesmo estando em minúsculas.
- Toda classe/arquivo dentro de `controllers` **deve** ter o sufixo `Controller`/`_controller`.
- Toda classe/arquivo dentro de `infrastructure` **deve** ter o sufixo `Service`/`_service`.
- **Nomes de variáveis e docstrings em inglês** — política nem sempre seguida à risca no código atual (há bastante português em docstrings, nomes de exceção e comentários, e nomes de campo do domínio como `glycemia`/`meal` convivem com strings de negócio em português, ex.: `"jejum"`, `"pré almoço"`).
- Todo Value Object usa `parse()` como único *entry point* público de construção validada (ver seção 3.4) — convenção implícita, mas universal em `core/`.

---

## 16. Roadmap Declarado pelo Autor

Extraído e organizado de `Planejamento.md` (conteúdo original do repositório):

### 16.1 Próximos passos técnicos
- Inventariar testes faltantes e adicionar testes unitários, de integração (ex.: consistência interna de "Salvar Card" e "Deletar Card" do UseCase até o Router) e end-to-end.
- Criar documentação para o projeto — *(este documento atende parcialmente a esse item)*.
- Adicionar import/export de banco de dados.
- Reorganizar `TimeList` para também retornar os dias, permitindo que a view desenhe corretamente.
- Fazer os erros "pipocarem" (propagarem/aparecerem) até a view.
- Simplificar o `map` do repositório JSON em uma função utilitária externa.
- Simplificar o parser de card do repositório.
- Implementar a função de **alterar** (editar) um card no `CardCreator`.
- Adicionar `intensity` (intensidade de exercício) na UI — atualmente o VO já suporta, mas o formulário (`main_view.get_data()`) sempre envia `intensity: ''`.
- Adicionar campo de **carboidratos** em `MealPeriod`.
- Adicionar configuração e salvamento dos **thresholds de insulina/glicemia** (o VO `Glycemia` já suporta thresholds customizáveis, mas nada na UI ainda os expõe).
- Fazer os thresholds impactarem visualmente os gráficos atuais (ex.: colorir células fora da faixa).
- Adicionar configuração de fórmula para cálculo de insulina rápida (bolus).
- Adicionar calculadora rápida de insulina rápida.
- Gráfico de média de dextro por hora ao longo de X dias.

### 16.2 Objetivos de produto de mais alto nível
- **Calculadora de bolus**: usar a fórmula pessoal do paciente para calcular a quantidade de insulina rápida a partir da glicemia atual e da quantidade de carboidratos da refeição.
- **Gráfico de linha** de média de glicemia por horário, ao longo de um período configurável de dias.
- **Gráfico de insulina rápida por refeição** (média).
- **Gráfico comparativo** entre insulina rápida e insulina lenta por dia.
- **Gráfico combinado** de média de glicemia, insulina rápida e carboidratos por refeição, em um período de dias.

> Nota: o único caso de uso "estatístico" já implementado no código hoje é `GetAverageGlycemiaPerDayUseCase` (média de glicemia por dia via `Base1DMatrixTemplate`) — os demais gráficos do roadmap ainda não têm Use Case correspondente no código-fonte atual.

---

## 17. Dívidas Técnicas e Problemas Identificados

Itens abaixo foram identificados por leitura direta do código (alguns já reconhecidos pelo próprio autor em comentários/docstrings, outros identificados nesta análise):

1. **Ausência de manifesto de dependências.** Não há `requirements.txt`/`pyproject.toml`/`buildozer.spec` no repositório, dificultando a reprodução do ambiente (versões exatas de `kivy`, `kivymd`, `pytest`, `hypothesis` não estão fixadas em lugar algum).

2. **`README.md` vazio.** Contém apenas o título `# Dextros`, sem instruções de instalação, execução ou descrição do projeto para novos colaboradores.

3. **Import quebrado em testes**: `tests/unit/adapters/test_json_repo.py` e `tests/integration/test_integration_json_repo.py` importam `from tests.exceptions import CardNotFoundError`, mas **não existe** o arquivo `tests/exceptions.py` no repositório — o correto seria `from adapters.exceptions import CardNotFoundError`. Isso indica que esses arquivos de teste, no estado atual do branch `main`, provavelmente **falham na coleta** (`ImportError`/`ModuleNotFoundError`) ao rodar `pytest`.

4. **Interfaces reconhecidas como desnecessárias pelo próprio autor**:
   - `ICardParser`/`CardDataModelParser`: docstring diz *"Interface bastante inútil. Precisa ser substituida junto a sua implementação por função utilitária."*
   - Isso é consistente com o item do roadmap "Simplificar o card parser do repositório".

5. **Duplicação de código em `MainView.add_graph_screen`**: o bloco de fallback (criação dinâmica de `GraphScreen`, `Panel`, botão de navbar) aparece **duas vezes seguidas e idênticas** no método — aparenta ser resíduo de um merge/edição incompleta, sem impacto funcional (a segunda execução apenas repete o trabalho da primeira) mas gerando telas/botões duplicados na navbar caso o fallback seja de fato acionado.

6. **Perda de tipo de exceção em `DeleteCardByIDUseCase`**: o `except Exception as err: raise DomainExceptionError(err)` faz *catch-all* e reembala qualquer exceção (incluindo bugs de programação, não apenas erros de domínio) como `DomainExceptionError`, dificultando diferenciar entre "card não encontrado" (esperado) e um erro inesperado (ex.: `AttributeError` por bug).

7. **Seed de produção com dados de demonstração**: `main.py` copia `db/cards_populated.json` (1001 registros fictícios) como banco inicial de **qualquer** novo usuário/instalação, o que é adequado para demonstração/desenvolvimento mas precisaria ser revisto antes de uma release voltada a usuários reais (o ideal seria semear com uma lista vazia `{"cards": []}`).

8. **Incompatibilidade entre `db/cards.json` (schema legado, chaves em português: `data`, `horario`, `dextro`...) e o parser atual** (`CardDataModelParser`, que espera `card_date`, `card_time`, `glycemia`...) — o `JsonHandler.load()` já suporta a *estrutura* de arquivo antiga (lista pura vs. `{"cards": [...]}`), mas não faz o *remapeamento de chaves* antigo → novo. Se esse arquivo fosse apontado como `DB` em `main.py`, o `CardDataModelParser.parse()` levantaria `KeyError`.

9. **Duplicação estrutural entre `LongActingInsulin` e `ShortActingInsulin`**: os dois Value Objects são, byte a byte, estruturalmente idênticos (mesma lógica de validação, mesma normalização de zero para `None`). São candidatos naturais a uma classe base comum (`InsulinQuantity`) parametrizada pelo tipo, reduzindo duplicação.

10. **Campo `intensity` do exercício não exposto na UI**: `MainView.get_data()` sempre envia `'intensity': ''` no dicionário do formulário, mesmo o VO `Exercise` já suportando o campo — item já listado no próprio roadmap do autor.

11. **Adição do handler de arquivo de log condicionada à cópia do seed**: em `main.py`, a chamada `log_service.add_file_handler(logs_dir, ...)` está aninhada dentro do bloco `if not os.path.exists(db_path): ... if os.path.exists(seed): ...` — ou seja, **apenas na primeira execução** (quando o banco ainda não existe) é que o log em arquivo é configurado; em execuções subsequentes, o app roda apenas com log de console. Isso pode ser proposital, mas não está documentado como tal.

12. **Ausência de testes end-to-end e de testes de UI (Kivy)** — hoje a suíte de testes cobre bem `core` e a camada de persistência, mas não há nenhum teste automatizado para `frameworks/kivy/*` (controllers de framework, widgets), reconhecido também no roadmap ("Fazer o inventário dos testes faltantes").

---

## 18. Como Executar o Projeto

> Não há instruções oficiais no repositório. Os passos abaixo foram inferidos por engenharia reversa das dependências e do ponto de entrada (`main.py`), e devem ser tratados como um guia extraoficial.

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

# 2. Instale as dependências identificadas por análise estática
pip install kivy kivymd pytest hypothesis colorama

# 3. Execute a aplicação a partir da raiz do repositório
python main.py

# 4. Para rodar a suíte de testes (nota: dois arquivos de teste têm um
#    import quebrado — ver seção 17, item 3 — e podem falhar na coleta)
pytest
```

A aplicação, na primeira execução, criará automaticamente o diretório de dados do usuário (via `path_provider_service.get_data_path`) e copiará o banco de exemplo `db/cards_populated.json` para lá.

---

## 19. Licença

O projeto é distribuído sob a **PolyForm Noncommercial License 1.0.0**, © babingoia — arquivo `LICENSE` na raiz do repositório. Essa licença permite uso, estudo, modificação e distribuição do código para **qualquer finalidade não-comercial** (uso pessoal, pesquisa, educação, organizações sem fins lucrativos, governamentais, de saúde pública, etc.), mas **não autoriza uso comercial** — ou seja, terceiros não podem incorporar o Dextros em produtos ou serviços vendidos/monetizados sem autorização explícita do licenciante. Substitui a licença MIT usada em versões anteriores do repositório.

---

*Documentação gerada por leitura completa e sistemática do código-fonte na branch `main` do repositório em 30/08/2026. Referências diretas ao código estão organizadas por caminho de arquivo ao longo de todo o documento para facilitar a navegação cruzada com o repositório real.*

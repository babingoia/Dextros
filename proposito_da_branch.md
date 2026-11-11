# Objetivo
Essa branch tem como objetivo principal incrementar bastante a classe Meal para que ela abrigue valores nutricionais
importantes para contagem de dextros. Por enquanto esses valores são:

    * Carboidratos.
    * Gorduras.

Ambos afetam diretamente o controle dos dextros.

## Requisitos
Como o aplicativo é offline, as consultas e base de dados também precisam ser. Por isso, estarei utilizando um JSON
contendo a tabela TACO como referência nutricional à partir desse repositório aqui: 

"https://github.com/marcelosanto/tabela_taco"

O que será salvo na base de dados de registro como Card serão os valores consumidos de:

    -> Gorduras
    -> Carboidratos

Consumidos logo após aquele registro.

## Realização
A branch será desenvolvida nas seguintes etapas:

    -> Criação da Branch e base de dados.                          [FEITA]
    -> Desenvolvimento da classe Meal para que ela lide com esses valores.  [FEITA]
    -> Desenvolvimento da aplicação kivy para que ele possa lidar com entradas customizadas de valores. [FEITA]
    -> Desenvolvimento de um mecanismo de consultas dentro da aplicação do kivy. [FEITA]

## Como foi implementado (decisões de design)

### Estrutura de domínio (composição, não substituição)
O `MealPeriod` continua dono do `meal_period` (nada foi descartado) e ganhou um VO novo
aninhado:

```python
Meal  # carboidratos e gorduras CONSUMIDOS em gramas inteiras (round no parse)
MealPeriod(meal_period, meal: Meal | None)  # meal_period preservado: matriz
                                            # Dia x Refeição e mappers intocados
```

Regras de validação do Meal: só o literalmente impossível — negativo, não-numérico
e NaN/infinito são rejeitados; NÃO existe limite superior (1000g+ de CHO é raro mas
real). `Meal.parse` retorna `None` quando não há conteúdo — Meal vazio nunca é
persistido. Nutrição sem período é permitida (`MealPeriod(None, Meal(...))`).

### Banco de dados
Formato canônico espelha o VO 1:1 (estrutura primeiro, compatibilidade a serviço dela):

```json
"meal": { "meal_period": "pós almoço", "meal": { "carbohydrate_g": 45, "fat_g": 12 } }
```

Card sem nutrição grava `"meal": null` dentro do objeto — nunca dict vazio. O
`DatabaseMigrationService` (infrastructure) roda no startup, checa o banco do usuário
e normaliza cards legados (meal como string) para o formato canônico: idempotente
(nada a migrar = nenhuma escrita), escrita atômica, container legado preservado, sem
objetos de quarentena (valor não mapeável vira None + log). O parser lê os dois
formatos como cinto e suspensório durante a transição.

### Consulta TACO (sem porta/interface nova)
`TacoRepository` (adapters, read-only, cacheado) carrega `db/TACO.json` uma vez e o
composition root injeta os `Food` parseados nos use cases — mesmo padrão do
`GetMealListUseCase`, que também recebe os dados de onde estão. Use cases puros,
sem ABC nova:

- `SearchFoodUseCase(foods)`: busca sem acento e sem pontuação ("pao frances" acha
  "Pão, francês"), ranking prefixo > início de palavra > contém, filtro por
  categoria, limite.
- `GetFoodCategoryListUseCase(foods)`: espelho do GetMealListUseCase.
- `CalculateNutritionUseCase`: wrapper de `Meal.from_food(food, grams)` — conversão
  pura no VO (o VO não busca nada), mantida como rota por consistência com o app.

Convenções da fonte tratadas no repositório: "NA" (não aplicável), "Tr" (traço) e
"*" (não medido) viram None — dado indisponível é diferente de zero. A TACO real tem
4 carboidratos levemente negativos (ruído de medição em peixes/carnes): viram 0.0 na
carga; negativo além de 1g/100g é corrupção e falha com erro.

### UI (opt-in)
A seção "Nutrição da refeição" no formulário nasce DESABILITADA: o usuário destrava
com o toggle "Ativar". Com o toggle off, `get_data()` ignora qualquer texto sobrado.
A busca TACO (popup com debounce, categorias e gramas) preenche os campos e destrava
o toggle sozinha. A UI nunca manipula o dict aninhado: ViewModel e DTOInput continuam
planos; a composição acontece no `CardCreator`, na fronteira do domínio. Vírgula
decimal brasileira é normalizada no mapper. Rotas novas: `search_food`,
`get_food_category_list`, `calculate_nutrition`.

### Fora do escopo desta branch
Matrizes continuam mostrando só glicemia (apresentação de nutrição fica para depois,
a `CardOutput` intocada). Edição de registros, calculadora de bolus e alimentos
customizados ficam para as próximas branches.
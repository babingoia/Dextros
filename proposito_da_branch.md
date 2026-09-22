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

    -> Criação da Branch e base de dados.
    -> Desenvolvimento da classe Meal para que ela lide com esses valores.
    -> Desenvolvimento da aplicação kivy para que ele possa lidar com entradas customizadas de valores.
    -> Desenvolvimento de um mecanismo de consultas dentro da aplicação do kivy.
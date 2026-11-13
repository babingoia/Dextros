import pytest

from core.value_objects.food import Food
from usecases.get_food_category_list_use_case import GetFoodCategoryListUseCase


def _food(food_id, description, category):
    return Food.parse(food_id, description, category)


def test_categorias_ordenadas_e_unicas():
    foods = [
        _food(1, "Arroz", "Cereais e derivados"),
        _food(2, "Pão", "Cereais e derivados"),
        _food(3, "Queijo", "Leite e derivados"),
        _food(4, "Banana", "Frutas e derivados"),
    ]
    resultado = GetFoodCategoryListUseCase(foods).execute()
    assert resultado.category_values == [
        "Cereais e derivados",
        "Frutas e derivados",
        "Leite e derivados",
    ]


def test_categorias_voltam_cruas_com_acento_para_exibicao():
    foods = [_food(1, "Feijão", "Leguminosas e derivados")]
    resultado = GetFoodCategoryListUseCase(foods).execute()
    assert resultado.category_values == ["Leguminosas e derivados"]


def test_lista_copiada_mutacao_externa_nao_afeta_o_use_case():
    """Espelho do contrato do GetMealListUseCase: mutação da lista retornada
    não corrói o estado interno do use case."""
    foods = [_food(1, "Arroz", "Cereais e derivados")]
    use_case = GetFoodCategoryListUseCase(foods)

    resultado = use_case.execute()
    resultado.category_values.append(" Categoria injectada")

    assert use_case.execute().category_values == ["Cereais e derivados"]


def test_tabela_vazia_retorna_lista_vazia():
    resultado = GetFoodCategoryListUseCase([]).execute()
    assert resultado.category_values == []

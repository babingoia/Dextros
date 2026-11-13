import pytest

from core.value_objects.food import Food
from core.value_objects.meal import Meal
from usecases.calculate_nutrition_use_case import CalculateNutritionUseCase


@pytest.fixture
def use_case():
    return CalculateNutritionUseCase()


@pytest.fixture
def arroz():
    return Food.parse(1, "Arroz, integral, cozido", "Cereais e derivados", 25.80975, 1.00033333333333)


def test_converte_arroz_150g(use_case, arroz):
    resultado = use_case.execute(arroz, 150)
    assert resultado == Meal(carbohydrate_g=39, fat_g=2)


def test_delega_validacoes_para_o_vo(use_case, arroz):
    """Gramas negativas são literalmente impossíveis — rejeição mora no Meal.from_food."""
    with pytest.raises(ValueError):
        use_case.execute(arroz, -10)


def test_food_invalido_rejeitado(use_case):
    with pytest.raises(TypeError):
        use_case.execute("arroz", 100)


def test_alimento_sem_nutrientes_retorna_none(use_case):
    vazio = Food.parse(999, "Alimento sem dados", "Cereais e derivados", None, None)
    assert use_case.execute(vazio, 100) is None


def test_retorno_e_o_vo_meal_na_entidade_pura(use_case, arroz):
    """O resultado é um Meal de verdade — a UI pode formatar direto para os campos."""
    resultado = use_case.execute(arroz, 100)
    assert isinstance(resultado, Meal)

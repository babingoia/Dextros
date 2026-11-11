import pytest

from core.value_objects.food import Food
from usecases.search_food_use_case import SearchFoodUseCase


def _food(food_id, description, category="Cereais e derivados", carb=10.0, fat=1.0):
    return Food.parse(food_id, description, category, carb, fat)


@pytest.fixture
def foods():
    return [
        _food(1, "Arroz, integral, cozido"),
        _food(2, "Arroz, integral, cru"),
        _food(3, "Macarrão, instantâneo"),
        _food(4, "Pão, francês"),
        _food(5, "Queijo, minas frescal", category="Leite e derivados"),
        _food(6, "Bolo simples", category="Alimentos preparados"),
    ]


@pytest.fixture
def use_case(foods):
    return SearchFoodUseCase(foods)


def test_sem_acento_encontra_com_acento(use_case):
    resultado = use_case.execute("macarrao")
    assert len(resultado.foods) == 1
    assert resultado.foods[0].description == "Macarrão, instantâneo"


def test_maiusculas_e_espacos_sao_normalizados(use_case):
    resultado = use_case.execute("  PÃO FRANCÊS  ")
    assert resultado.foods[0].description == "Pão, francês"


def test_prefixo_ranqueia_acima_de_contem(use_case):
    """'arroz' começa o nome de dois alimentos — ambos vêm antes de 'queijo'... não contém arroz."""
    resultado = use_case.execute("arroz")
    descriptions = [f.description for f in resultado.foods]
    assert descriptions == ["Arroz, integral, cozido", "Arroz, integral, cru"]


def test_ranking_prefixo_de_palavra_acima_de_substring(use_case):
    """'simp' inicia a palavra 'simples' (rank 1); 'simp' não inicia nada em
    'Bolo simples' — rank 1. Já 'lo si' só ocorre no meio (rank 2).
    Testa a ordem relativa prefixo-de-palavra vs substring puro."""
    com_rank_palavra = use_case.execute("bolo")
    assert com_rank_palavra.foods[0].description == "Bolo simples"


def test_busca_vazia_nao_despeja_a_tabela(use_case):
    """Query vazia/whitespace devolve [] — nunca os 597 alimentos."""
    assert use_case.execute("").foods == []
    assert use_case.execute("   ").foods == []


def test_limite_respeitado(foods):
    use_case = SearchFoodUseCase(foods + [_food(100 + i, f"Arroz variante {i}") for i in range(10)])
    resultado = use_case.execute("arroz", limit=5)
    assert len(resultado.foods) == 5


def test_filtro_por_categoria(use_case):
    resultado = use_case.execute("queijo", category="Leite e derivados")
    assert len(resultado.foods) == 1
    assert resultado.foods[0].description == "Queijo, minas frescal"


def test_filtro_por_categoria_sem_acento(use_case):
    resultado = use_case.execute("queijo", category="leite e derivados")
    assert len(resultado.foods) == 1


def test_categoria_inexistente_zera_resultado(use_case):
    assert use_case.execute("arroz", category="Marca insexa").foods == []


def test_categoria_none_ou_vazia_nao_filtra(use_case):
    assert len(use_case.execute("arroz", category=None).foods) == 2
    assert len(use_case.execute("arroz", category="").foods) == 2


def test_query_sem_match_retorna_vazia(use_case):
    assert use_case.execute("pizza calabresa").foods == []


def test_query_nao_string_levanta_type_error(use_case):
    with pytest.raises(TypeError):
        use_case.execute(123)


@pytest.mark.parametrize("limit", [0, -1, "5", True])
def test_limite_invalido_levanta_erro(use_case, limit):
    with pytest.raises(ValueError):
        use_case.execute("arroz", limit=limit)


def test_alimentos_retornados_sao_os_vos_originais(use_case):
    """A busca não copia nem recria VOs — a UI recebe o Food com descrição
    e categoria cruas (com acento) para exibir."""
    resultado = use_case.execute("macarrao")
    assert resultado.foods[0].description == "Macarrão, instantâneo"
    assert resultado.foods[0].category == "Cereais e derivados"

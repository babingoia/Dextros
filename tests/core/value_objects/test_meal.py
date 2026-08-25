import pytest

from core.value_objects.meal import MealPeriod, _VALID_MEAL_VALUES


@pytest.mark.parametrize("valor_valido", _VALID_MEAL_VALUES)
def test_todos_os_valores_validos_da_lista_sao_aceitos(valor_valido):
    resultado = MealPeriod.parse(valor_valido)
    assert resultado.meal_period == valor_valido


def test_normaliza_maiusculas():
    resultado = MealPeriod.parse("JEJUM")
    assert resultado.meal_period == "jejum"


def test_normaliza_espacos_nas_bordas():
    resultado = MealPeriod.parse("   jejum   ")
    assert resultado.meal_period == "jejum"


def test_normaliza_acentuacao_maiuscula():
    resultado = MealPeriod.parse("PÓS CAFÉ DA MANHÃ")
    assert resultado.meal_period == "pós café da manhã"


@pytest.mark.parametrize("valor_invalido", [
    "almoço",           # não está na lista (falta pré/pós)
    "jejum ",            # com espaço mas sem normalizar seria diferente - já normalizado, deve passar
    "café da tarde",     # incompleto
    "",
    "qualquer coisa",
])
def test_valores_fora_da_lista_sao_rejeitados(valor_invalido):
    if valor_invalido.strip().lower() in _VALID_MEAL_VALUES:
        pytest.skip("Este valor na verdade é válido após normalização")
    with pytest.raises(ValueError):
        MealPeriod.parse(valor_invalido)


# --- [DECISÃO MINHA, NÃO CONFIRMADA] ---
# Assumi que você adicionou uma checagem de tipo explícita (TypeError) para
# entradas que não são string, já que o __post_init__ original não tinha
# isso e None quebrava com AttributeError em vez de um erro claro. Se seu
# parse() não tem esse isinstance(), estes dois testes vão falhar - é só
# apagar ou ajustar pra o comportamento real (ex: AttributeError).

@pytest.mark.parametrize("tipo_invalido", [123, 4.5, ["jejum"]])
def test_tipo_nao_string_levanta_type_error(tipo_invalido):
    with pytest.raises(TypeError):
        MealPeriod.parse(tipo_invalido)


def test_e_imutavel():
    resultado = MealPeriod.parse("jejum")
    with pytest.raises(Exception):
        resultado.meal_period = "outro"

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


# ==========================================================
# Meal — VO de nutrição consumida (comida real)
# ==========================================================

from core.value_objects.meal import Meal  # noqa: E402
from core.value_objects.food import Food  # noqa: E402


def _food(carb=25.80975, fat=1.00033333333333):
    """Arroz integral cozido (id 1 da TACO)."""
    return Food.parse(1, "Arroz, integral, cozido", "Cereais e derivados", carb, fat)


class TestMealParse:
    def test_valores_completos_sao_arredondados_para_int(self):
        resultado = Meal.parse(45.2, 12.6)
        assert resultado == Meal(carbohydrate_g=45, fat_g=13)

    def test_strings_numericas_sao_aceitas(self):
        resultado = Meal.parse("45.2", "12")
        assert resultado == Meal(carbohydrate_g=45, fat_g=12)

    def test_apenas_carboidrato_e_caso_comum(self):
        resultado = Meal.parse(45, None)
        assert resultado == Meal(carbohydrate_g=45, fat_g=None)

    @pytest.mark.parametrize("carb,fat", [(None, None), ("", ""), ("", None), (None, "")])
    def test_sem_nenhum_valor_retorna_none(self, carb, fat):
        """Meal sem conteúdo é 'nenhuma nutrição registrada' — parse devolve None."""
        assert Meal.parse(carb, fat) is None

    def test_zero_e_valido_nos_dois_campos(self):
        resultado = Meal.parse(0, 0)
        assert resultado == Meal(carbohydrate_g=0, fat_g=0)

    @pytest.mark.parametrize("valor", [1000, 2000, 999999])
    def test_valores_grandes_sao_permitidos(self, valor):
        """Limite alto não é validação: 1000g de CHO é raro mas real (atletas, recovering severo)."""
        assert Meal.parse(valor, None).carbohydrate_g == valor

    @pytest.mark.parametrize("valor", [-1, -0.5, "-3"])
    def test_valor_negativo_e_literalmente_impossivel(self, valor):
        with pytest.raises(ValueError):
            Meal.parse(valor, None)

    @pytest.mark.parametrize("valor", [float("nan"), float("inf"), "-inf"])
    def test_valor_nao_finito_e_rejeitado(self, valor):
        with pytest.raises(ValueError):
            Meal.parse(valor, None)

    @pytest.mark.parametrize("valor", [object(), [45], {"g": 45}, True])
    def test_tipo_impossivel_e_rejeitado(self, valor):
        with pytest.raises(TypeError):
            Meal.parse(valor, None)

    def test_virgula_decimal_nao_e_responsabilidade_do_vo(self):
        """'45,2' falha no VO — normalizar vírgula é trabalho do mapper da apresentação."""
        with pytest.raises(ValueError):
            Meal.parse("45,2", None)

    def test_e_imutavel(self):
        resultado = Meal.parse(45, 12)
        with pytest.raises(Exception):
            resultado.carbohydrate_g = 99


class TestMealFromFood:
    def test_conversao_pura_arroz_integral_150g(self):
        """150g de arroz integral cozido (25.81g CHO/100g) -> ~38.7g -> 39g."""
        resultado = Meal.from_food(_food(), 150)
        assert resultado == Meal(carbohydrate_g=39, fat_g=2)

    def test_vo_nao_busca_nada_recebe_food_pronto(self):
        """from_food é matemática pura sobre o argumento — zero IO."""
        resultado = Meal.from_food(_food(), 100)
        assert resultado.carbohydrate_g == 26

    def test_grama_zero_produz_meal_zerado(self):
        resultado = Meal.from_food(_food(), 0)
        assert resultado == Meal(carbohydrate_g=0, fat_g=0)

    def test_gramas_negativas_sao_impossiveis(self):
        with pytest.raises(ValueError):
            Meal.from_food(_food(), -50)

    def test_nutriente_ausente_na_tabela_permance_none(self):
        """Desconhecido != zero: alimento sem gordura na tabela não vira 0."""
        resultado = Meal.from_food(_food(carb=10.0, fat=None), 200)
        assert resultado == Meal(carbohydrate_g=20, fat_g=None)

    def test_alimento_sem_nenhum_nutriente_retorna_none(self):
        assert Meal.from_food(_food(carb=None, fat=None), 150) is None

    def test_food_invalido_levanta_type_error(self):
        with pytest.raises(TypeError):
            Meal.from_food("arroz", 150)

    def test_grams_obrigatorio(self):
        with pytest.raises(TypeError):
            Meal.from_food(_food(), None)

    def test_string_de_gramas_e_aceita(self):
        resultado = Meal.from_food(_food(), "200")
        assert resultado.carbohydrate_g == 52


# ==========================================================
# MealPeriod — composição: Meal aninhado, nada descartado
# ==========================================================

class TestMealPeriodComposicao:
    def test_periodo_com_meal(self):
        resultado = MealPeriod.parse("pós almoço", Meal.parse(45, 12))
        assert resultado.meal_period == "pós almoço"
        assert resultado.meal == Meal(carbohydrate_g=45, fat_g=12)

    def test_assinatura_antiga_continua_funcionando(self):
        resultado = MealPeriod.parse("jejum")
        assert resultado.meal_period == "jejum"
        assert resultado.meal is None

    def test_nutricao_sem_periodo_e_permitida(self):
        """Dextro pós-refeição não rotulado: nutrição existe, período não."""
        resultado = MealPeriod.parse(None, Meal.parse(30, None))
        assert resultado.meal_period is None
        assert resultado.meal.carbohydrate_g == 30

    def test_meal_de_tipo_impossivel_e_rejeitado(self):
        with pytest.raises(TypeError):
            MealPeriod.parse("jejum", {"carbohydrate_g": 45})

    def test_construtor_direto_valida_tipo_do_meal(self):
        with pytest.raises(TypeError):
            MealPeriod("jejum", meal="não é um Meal")

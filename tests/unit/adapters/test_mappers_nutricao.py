import pytest

from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.mappers.mappers import (
    strip_view_model,
    normalize_decimal,
    decimal_or_none,
    view_model_to_input,
    card_output_to_view_model,
    empty_card_view_model,
    parse_brazilian_decimal,
    sum_grams_for_input,
)


def _view_model(**overrides) -> CardViewModel:
    data = CardViewModel(
        card_id='',
        card_data='2024-01-03',
        card_time='00:00',
        glycemia='156',
        long_acting_insulin='30',
        short_acting_insulin='5',
        exercise={'exercise_name': 'ciclismo', 'intensity': ''},
        meal='jejum',
        carbohydrate_g='',
        fat_g='',
        observation='Me sentindo bem',
    )
    data.update(overrides)
    return data


class TestNormalizeDecimal:
    @pytest.mark.parametrize("raw,expected", [
        ("45,2", "45.2"),
        ("45.2", "45.2"),
        ("45", "45"),
        ("", ""),
        (None, None),
    ])
    def test_virgula_brasileira_vira_ponto(self, raw, expected):
        assert normalize_decimal(raw) == expected

    def test_espacos_sao_responsabilidade_do_strip_view_model(self):
        """A ordem no SaveRequestController é strip -> normalize: o texto já chega
        limpo aqui. Se um dia chegar com espaço, é bug do pipeline, não do converter."""
        assert normalize_decimal("45,2") == "45.2"


class TestDecimalOrNone:
    def test_decimal_com_virgula(self):
        assert decimal_or_none("45,2") == 45.2

    @pytest.mark.parametrize("raw", ["", None])
    def test_vazio_vira_none(self, raw):
        assert decimal_or_none(raw) is None

    def test_zero_vira_none_convencao_do_app(self):
        """Mesma convenção do int_or_none (insulinas): 0 = campo não preenchido."""
        assert decimal_or_none("0") is None
        assert decimal_or_none("0,0") is None


class TestViewModelToInputNutricao:
    def test_nutricao_chega_no_dto(self):
        dto = view_model_to_input(_view_model(carbohydrate_g='45,2', fat_g='12'))
        assert dto.carbohydrate_g == 45.2
        assert dto.fat_g == 12.0

    def test_toggle_off_manda_string_vazia_e_vira_none(self):
        """get_data() devolve '' com o toggle desligado — o mapper transforma em None."""
        dto = view_model_to_input(_view_model())
        assert dto.carbohydrate_g is None
        assert dto.fat_g is None

    def test_campos_legados_sem_carb_fat_kwargs_seguem_funcionando(self):
        """CardDTOInput com defaults None — chamadas antigas sem nutrição não quebram."""
        dto = view_model_to_input(_view_model())
        assert dto.meal == 'jejum'
        assert dto.observation == 'Me sentindo bem'


class TestStripViewModel:
    def test_strip_nos_novos_campos(self):
        vm = _view_model(carbohydrate_g=' 45,2 ', fat_g=' 12 ')
        stripped = strip_view_model(vm)
        assert stripped['carbohydrate_g'] == '45,2'
        assert stripped['fat_g'] == '12'


class TestViewModelMatrizes:
    def test_card_output_to_view_model_sem_nutricao_vai_vazio(self):
        """Card sem nutrição registrada no MealPeriod: campos vazios, sem 'None' vazando pra UI."""
        from usecases.utils.mappers import to_card_output
        from tests.integration.test_integration_json_repo import make_dummy_card
        card = make_dummy_card()
        vm = card_output_to_view_model(to_card_output(card))
        assert vm['carbohydrate_g'] == ''
        assert vm['fat_g'] == ''

    def test_card_output_carrega_nutricao_do_meal_period(self):
        """A nutrição consumida vive em card.meal.meal (VO Meal) — deve sair no CardOutput."""
        from usecases.utils.mappers import to_card_output
        from tests.integration.test_integration_json_repo import make_dummy_card_com_nutricao
        card = make_dummy_card_com_nutricao(carb=45, fat=12)
        output = to_card_output(card)
        assert output.carbohydrate_g == 45
        assert output.fat_g == 12
        assert output.meal == "pós almoço"

    def test_card_output_sem_nutricao_tem_none(self):
        from usecases.utils.mappers import to_card_output
        from tests.integration.test_integration_json_repo import make_dummy_card
        output = to_card_output(make_dummy_card())
        assert output.carbohydrate_g is None
        assert output.fat_g is None

    def test_view_model_da_matriz_leva_nutricao_formatada(self):
        """O popup de detalhes do card lê o CardViewModel — valores formatados pra exibição."""
        from usecases.utils.mappers import to_card_output
        from tests.integration.test_integration_json_repo import make_dummy_card_com_nutricao
        vm = card_output_to_view_model(to_card_output(make_dummy_card_com_nutricao(carb=45, fat=12)))
        assert vm['carbohydrate_g'] == '45'
        assert vm['fat_g'] == '12'
        assert vm['meal'] == 'pós almoço'

    def test_card_sem_refeicao_exibe_nenhum(self):
        """MealPeriod None (dextro sem refeição próxima) exibe 'nenhum' no popup
        de detalhes — mesma palavra da opção de UI do picker. Célula VAZIA da
        matriz continua com string vazia (empty_card_view_model), pois ali não
        existe card nenhum."""
        from datetime import date, time as dtime
        from usecases.dtos.card_output import CardOutput
        output = CardOutput(
            card_id="x", card_date=date(2024, 1, 3), card_time=dtime(9, 30),
            glycemia=120, long_acting_insulin=None, short_acting_insulin=None,
            meal=None, observation=None,
        )
        vm = card_output_to_view_model(output)
        assert vm['meal'] == 'nenhum'

    def test_empty_card_view_model_tem_campos_de_nutricao(self):
        vm = empty_card_view_model()
        assert vm['carbohydrate_g'] == ''
        assert vm['fat_g'] == ''


class TestFormatGramsForDisplay:
    @pytest.mark.parametrize("raw,expected", [
        (45, "45"),
        (45.0, "45"),
        (45.2, "45,2"),
        (0.5, "0,5"),
        (None, ""),
    ])
    def test_formato_brasileiro_sem_unidade(self, raw, expected):
        """Vírgula decimal e sem 'g' — a unidade fica no rótulo da tela."""
        from adapters.controllers.mappers.mappers import format_grams_for_display
        assert format_grams_for_display(raw) == expected


class TestParseBrazilianDecimal:
    @pytest.mark.parametrize("raw,expected", [
        ("45,2", 45.2),
        ("45.2", 45.2),
        ("45", 45.0),
        ("  12,4  ", 12.4),
        ("", None),
        ("   ", None),
        (None, None),
        ("abc", None),
        ("1,2.3", None),
    ])
    def test_texto_do_campo_vira_float_ou_none(self, raw, expected):
        """Vazio e lixo de digitação viram None — quem decide o que fazer
        com None é o chamador (a soma trata como 0)."""
        assert parse_brazilian_decimal(raw) == expected


class TestSumGramsForInput:
    """O registro de refeição acumula VÁRIOS alimentos da TACO: adicionar
    comida em campo já preenchido soma, não substitui."""

    def test_primeira_comida_campo_vazio(self):
        assert sum_grams_for_input("", 23) == "23"

    def test_soma_com_texto_ja_presente(self):
        assert sum_grams_for_input("45,2", 23) == "68,2"

    def test_soma_com_ponto_tambem_acumula(self):
        assert sum_grams_for_input("45.2", 23) == "68,2"

    def test_resultado_inteiro_nao_tem_virgula(self):
        assert sum_grams_for_input("23", 24) == "47"

    def test_decimal_com_virgula_no_resultado(self):
        assert sum_grams_for_input("12,4", 1) == "13,4"

    @pytest.mark.parametrize("garbage", ["abc", " ", None])
    def test_texto_invalido_conta_como_zero(self, garbage):
        """Lixo de digitação não soma nem estoura: o valor da comida entra limpo."""
        assert sum_grams_for_input(garbage, 23) == "23"

    def test_zero_somado_mantem_convencao_de_exibicao(self):
        """Meal.from_food nunca devolve negativo; 0 somado a campo vazio é '0'."""
        assert sum_grams_for_input("", 0) == "0"

    def test_precisao_flutuante_nao_vaza_no_texto(self):
        """45,2 + 23 em float binário é 68.200000000000003 — %g do formatador
        tem que esconder isso do usuário."""
        assert sum_grams_for_input("45,2", 23) == "68,2"

import pytest

from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.mappers.mappers import (
    strip_view_model,
    normalize_decimal,
    decimal_or_none,
    view_model_to_input,
    card_output_to_view_model,
    empty_card_view_model,
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
    def test_card_output_to_view_model_tem_campos_de_nutricao_vazios(self):
        from usecases.utils.mappers import to_card_output
        from tests.integration.test_integration_json_repo import make_dummy_card
        card = make_dummy_card()
        vm = card_output_to_view_model(to_card_output(card))
        assert vm['carbohydrate_g'] == ''
        assert vm['fat_g'] == ''

    def test_empty_card_view_model_tem_campos_de_nutricao(self):
        vm = empty_card_view_model()
        assert vm['carbohydrate_g'] == ''
        assert vm['fat_g'] == ''

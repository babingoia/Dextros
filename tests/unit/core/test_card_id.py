import pytest
from hypothesis import given, strategies as st

from core.value_objects.card_id import CardID
from core.exceptions import ParseError, InvalidCardId
from tests.config.core.card_id import valid_card_id, invalid_uuid_version, invalid_id_inputs


# Testes do Hypothesis
@given(valid_card_id())
def test_sem_argumento_gera_uuid4_valido(card_id: CardID):
    """
    Checa se a versão do UUID é v4.
    """
    assert card_id.card_id.version == 4


@given(valid_card_id(), valid_card_id())
def test_none_gera_ids_diferentes_a_cada_chamada(first_card_id, second_card_id):
    assert first_card_id.card_id != second_card_id.card_id


@given(card_id=invalid_uuid_version)
def test_invalid_uuid(card_id):
    with pytest.raises(InvalidCardId):
        CardID.parse(card_id)


# Testes do Pytest
@given(card_id=invalid_id_inputs)
def test_invalid_input_value_error(card_id):
    with pytest.raises(ParseError):
        CardID.parse(card_id)

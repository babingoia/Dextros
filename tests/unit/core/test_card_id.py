"""
Arquivo 100% escrito sem IA.
"""

import pytest
from hypothesis import given, strategies as st

from core.value_objects.card_id import CardID
from core.exceptions import ParseError, InvalidCardId
from tests.config.core.card_id import (
    valid_card_id,
    invalid_uuid_version,
    invalid_id_inputs,
    none_valid_card_id,
    invalid_comparisions
    )


# Testes do Hypothesis
@given(valid_card_id())
def test_sem_argumento_gera_uuid4_valido(card_id: CardID):
    """
    Checa se a versão do UUID é v4.
    """
    assert card_id.card_id.version == 4


@given(first_card_id=none_valid_card_id(), second_card_id=none_valid_card_id())
def test_generation_diferent_uuids(first_card_id, second_card_id):
    """
    Testa se dois UUID gerados automaticamente são realmente diferentes.
    """
    assert first_card_id.card_id != second_card_id.card_id


@given(card_id=invalid_uuid_version)
def test_invalid_uuid(card_id):
    """
    Testa se uuid's válidos pelo módulo do python são negados se a versão for diferente de 4 e se o erro 
    levantado é InvalidCardId.
    """
    with pytest.raises(InvalidCardId):
        CardID.parse(card_id)


@given(card_id=invalid_id_inputs)
def test_invalid_input_value_error(card_id):
    """
    Testa se ParseError é levantado para inputs incorretos.
    """
    with pytest.raises(ParseError):
        CardID.parse(card_id)


@given(card_id=valid_card_id())
def test_comparision_to_another_card_id(card_id: CardID):
    """
    Testa se dois CardID com o mesmo ID são iguais de fato.
    """
    second_card_id = CardID.parse(card_id.card_id)
    assert card_id == second_card_id


@given(card_id=valid_card_id())
def test_comparision_to_string(card_id: CardID):
    """
    Comapara um CardID ao mesmo ID em forma de texto.
    """
    text_id = str(card_id.card_id)
    assert text_id == card_id


@given(card_id=valid_card_id())
def test_comparision_to_uuid(card_id: CardID):
    """
    Compara um UUID identico ao CardID.
    """
    uuid_obj = card_id.card_id
    assert uuid_obj == card_id


@given(card_id=valid_card_id(), invalid_comparision=invalid_comparisions)
def test_invalid_comparision(card_id: CardID, invalid_comparision):
    """
    Compara um CardID a valores inválidos para checar false.
    """
    assert (card_id == invalid_comparision) is False


@given(card_id=valid_card_id(), invalid_comparision=invalid_comparisions)
def test_not_implemented_comparision(card_id: CardID, invalid_comparision):
    """
    Compara o __eq__ de um CardID a valores inválidos para checar se há NotImplemented.
    """
    assert card_id.__eq__(invalid_comparision) is NotImplemented
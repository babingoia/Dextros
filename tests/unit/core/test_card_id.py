import pytest
from uuid import UUID, uuid1, uuid5, NAMESPACE_DNS

from core.value_objects.card_id import CardID


def test_sem_argumento_gera_uuid4_valido():
    result = CardID.parse()
    assert result.card_id.version == 4


@pytest.mark.parametrize("invalid_input", [
    "1234",
    "d30601d64-8edf-48bd-a294-98a01e89a375",
    "30601d648edf48bda29498a0s21e89a375",
    12243655510712991259452377859857624405354,
    "30601d64-8edf-48bd-a294-98a01e9a375"
])
def test_invalid_input_value_error(invalid_input):
    with pytest.raises(ValueError):
        CardID.parse(invalid_input)


@pytest.mark.parametrize("invalid_input", [
    CardID.parse(),
    1224365551071299.12594523778598576214405
])
def test_invalid_input_value_error(invalid_input):
    with pytest.raises(TypeError):
        CardID.parse(invalid_input)


@pytest.mark.parametrize("uuid_versao_errada", [
    str(uuid1()),                          # v1 válido, mas não é v4
    str(uuid5(NAMESPACE_DNS, "teste")),    # v5 válido, mas não é v4
])
def test_uuid_de_outra_versao_e_rejeitado(uuid_versao_errada):
    with pytest.raises(ValueError):
        CardID.parse(uuid_versao_errada)


def test_none_gera_ids_diferentes_a_cada_chamada():
    a = CardID.parse()
    b = CardID.parse()
    assert a.card_id != b.card_id
from datetime import date, datetime

import pytest

from core.value_objects.date import Date


def test_sem_argumento_usa_data_atual():
    resultado = Date.parse()
    assert resultado._date == date.today()


def test_string_no_formato_correto():
    resultado = Date.parse("2024-05-20")
    assert resultado._date == date(2024, 5, 20)


def test_aceita_objeto_datetime():
    entrada = datetime(2024, 5, 20, 14, 30)
    resultado = Date.parse(entrada)
    assert resultado._date == date(2024, 5, 20)


def test_aceita_objeto_date():
    entrada = date(2024, 5, 20)
    resultado = Date.parse(entrada)
    assert resultado._date == entrada


@pytest.mark.parametrize("entrada_invalida", [
    "20-05-2024",       # formato errado (dia/mes/ano em vez de ano-mes-dia)
    "data-nenhuma",     # não é data de jeito nenhum
    "2024-13-01",       # mês inexistente
])
def test_string_em_formato_invalido_levanta_value_error(entrada_invalida):
    with pytest.raises(ValueError):
        Date.parse(entrada_invalida)


@pytest.mark.parametrize("tipo_invalido", [123, 45.6, ["2024-05-20"], {"data": "2024-05-20"}])
def test_tipo_nao_suportado_levanta_type_error(tipo_invalido):
    with pytest.raises(TypeError):
        Date.parse(tipo_invalido)


def test_e_imutavel():
    resultado = Date.parse("2024-05-20")
    with pytest.raises(Exception):
        resultado._date = date(2000, 1, 1)

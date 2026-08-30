from datetime import datetime, time

import pytest

from core.value_objects.time import Time


def test_sem_argumento_nao_levanta_erro():
    resultado = Time.parse()
    assert isinstance(resultado._time, time)


def test_string_no_formato_hh_mm():
    resultado = Time.parse("14:30")
    assert resultado._time == time(14, 30)


def test_aceita_objeto_datetime():
    entrada = datetime(2024, 5, 20, 14, 30)
    resultado = Time.parse(entrada)
    assert resultado._time == time(14, 30)


def test_aceita_objeto_time():
    entrada = time(14, 30)
    resultado = Time.parse(entrada)
    assert resultado._time == entrada


@pytest.mark.parametrize("entrada_invalida", [
    "14:30:00",     # segundos não suportados de propósito
    "25:99",        # hora/minuto fora do intervalo válido
    "quatorze:30",  # não numérico
])
def test_string_em_formato_invalido_levanta_value_error(entrada_invalida):
    with pytest.raises(ValueError):
        Time.parse(entrada_invalida)


@pytest.mark.parametrize("tipo_invalido", [123, 45.6, ["14:30"]])
def test_tipo_nao_suportado_levanta_type_error(tipo_invalido):
    with pytest.raises(TypeError):
        Time.parse(tipo_invalido)

import pytest
from hypothesis import given, strategies as st

from core.value_objects.short_acting_insulin import ShortActingInsulin


def test_parse_sem_argumento_usa_none():
    resultado = ShortActingInsulin.parse()
    assert resultado.quantity is None


def test_parse_com_int():
    resultado = ShortActingInsulin.parse(4)
    assert resultado.quantity == 4


def test_parse_com_string_numerica():
    resultado = ShortActingInsulin.parse("4")
    assert resultado.quantity == 4


def test_parse_com_string_com_espacos():
    resultado = ShortActingInsulin.parse("  4  ")
    assert resultado.quantity == 4


def test_zero_e_convertido_para_none():
    resultado = ShortActingInsulin.parse(0)
    assert resultado.quantity is None


def test_zero_via_construtor_direto_tambem_converte():
    resultado = ShortActingInsulin(quantity=0)
    assert resultado.quantity is None


@pytest.mark.parametrize("valor_negativo", [-1, -10, -9999])
def test_quantidade_negativa_e_rejeitada(valor_negativo):
    with pytest.raises(ValueError):
        ShortActingInsulin.parse(valor_negativo)


def test_quantidade_negativa_via_construtor_direto_tambem_e_rejeitada():
    with pytest.raises(ValueError):
        ShortActingInsulin(quantity=-5)


@given(st.integers(min_value=1))
def test_qualquer_inteiro_positivo_e_aceito(valor):
    resultado = ShortActingInsulin.parse(valor)
    assert resultado.quantity == valor


@given(st.integers(max_value=-1))
def test_qualquer_inteiro_negativo_e_sempre_rejeitado(valor):
    with pytest.raises(ValueError):
        ShortActingInsulin.parse(valor)


@pytest.mark.parametrize("tipo_invalido", [4.5, ["4"], {"quantity": 4}])
def test_tipo_nao_coberto_levanta_type_error(tipo_invalido):
    with pytest.raises(TypeError):
        ShortActingInsulin.parse(tipo_invalido)


def test_string_nao_numerica_levanta_erro():
    with pytest.raises(ValueError):
        ShortActingInsulin.parse("quatro")


def test_e_imutavel():
    resultado = ShortActingInsulin.parse(4)
    with pytest.raises(Exception):
        resultado.quantity = 999

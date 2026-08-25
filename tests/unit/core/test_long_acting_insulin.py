import pytest
from hypothesis import given, strategies as st

from core.value_objects.long_acting_insulin import LongActingInsulin


def test_parse_sem_argumento_usa_none():
    resultado = LongActingInsulin.parse()
    assert resultado.quantity is None


def test_parse_com_int():
    resultado = LongActingInsulin.parse(10)
    assert resultado.quantity == 10


def test_parse_com_string_numerica():
    resultado = LongActingInsulin.parse("10")
    assert resultado.quantity == 10


def test_parse_com_string_com_espacos():
    resultado = LongActingInsulin.parse("  10  ")
    assert resultado.quantity == 10


def test_zero_e_convertido_para_none():
    resultado = LongActingInsulin.parse(0)
    assert resultado.quantity is None


def test_zero_via_construtor_direto_tambem_converte():
    # O invariante mora no __post_init__, então vale pra qualquer caminho de
    # construção, não só pelo parse() - mesmo princípio do CardID.
    resultado = LongActingInsulin(quantity=0)
    assert resultado.quantity is None


@pytest.mark.parametrize("valor_negativo", [-1, -10, -9999])
def test_quantidade_negativa_e_rejeitada(valor_negativo):
    with pytest.raises(ValueError):
        LongActingInsulin.parse(valor_negativo)


def test_quantidade_negativa_via_construtor_direto_tambem_e_rejeitada():
    with pytest.raises(ValueError):
        LongActingInsulin(quantity=-5)


@given(st.integers(min_value=1))
def test_qualquer_inteiro_positivo_e_aceito(valor):
    resultado = LongActingInsulin.parse(valor)
    assert resultado.quantity == valor


@given(st.integers(max_value=-1))
def test_qualquer_inteiro_negativo_e_sempre_rejeitado(valor):
    with pytest.raises(ValueError):
        LongActingInsulin.parse(valor)


@pytest.mark.parametrize("tipo_invalido", [4.5, ["10"], {"quantity": 10}])
def test_tipo_nao_coberto_levanta_type_error(tipo_invalido):
    with pytest.raises(TypeError):
        LongActingInsulin.parse(tipo_invalido)


def test_string_nao_numerica_levanta_erro():
    with pytest.raises(ValueError):
        LongActingInsulin.parse("dez")


def test_e_imutavel():
    resultado = LongActingInsulin.parse(10)
    with pytest.raises(Exception):
        resultado.quantity = 999

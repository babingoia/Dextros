import pytest

from core.value_objects.observation import Observation


def test_parse_sem_argumento_usa_none():
    resultado = Observation.parse()
    assert resultado.observation is None


def test_construtor_direto_sem_argumento_tambem_usa_none():
    resultado = Observation()
    assert resultado.observation is None


def test_parse_com_texto_normal():
    resultado = Observation.parse("nada de anormal hoje")
    assert resultado.observation == "nada de anormal hoje"


def test_parse_remove_espacos_nas_bordas():
    resultado = Observation.parse("   texto com espaco   ")
    assert resultado.observation == "texto com espaco"


def test_string_vazia_vira_none():
    resultado = Observation.parse("")
    assert resultado.observation is None


def test_string_so_com_espacos_vira_none():
    resultado = Observation.parse("     ")
    assert resultado.observation is None


def test_texto_no_limite_de_240_caracteres_e_aceito():
    texto = "a" * 240
    resultado = Observation.parse(texto)
    assert resultado.observation == texto


def test_texto_com_241_caracteres_e_rejeitado():
    texto = "a" * 241
    with pytest.raises(ValueError):
        Observation.parse(texto)


def test_texto_muito_longo_e_rejeitado():
    texto = "a" * 1000
    with pytest.raises(ValueError):
        Observation.parse(texto)


def test_none_via_construtor_direto_nao_quebra_o_post_init():
    # Esse é o teste que teria pego o bug de ordem do "and" (len(None) sendo
    # chamado antes da checagem de None) - regressão específica pra isso.
    resultado = Observation(observation=None)
    assert resultado.observation is None


def test_e_imutavel():
    resultado = Observation.parse("texto")
    with pytest.raises(Exception):
        resultado.observation = "outro texto"

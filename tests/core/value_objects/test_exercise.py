import pytest

from core.value_objects.exercise import Exercise


def test_parse_sem_argumentos_representa_nenhum_exercicio():
    resultado = Exercise.parse()
    assert resultado.exercise_name is None
    assert resultado.intensity is None


def test_construtor_direto_sem_argumentos_tambem_funciona():
    resultado = Exercise()
    assert resultado.exercise_name is None
    assert resultado.intensity is None


def test_nome_sem_intensidade_e_permitido():
    resultado = Exercise.parse("caminhada", None)
    assert resultado.exercise_name == "caminhada"
    assert resultado.intensity is None


def test_nome_com_intensidade_valida():
    resultado = Exercise.parse("caminhada", "leve")
    assert resultado.exercise_name == "caminhada"
    assert resultado.intensity == "leve"


@pytest.mark.parametrize("intensidade", ["leve", "moderada", "vigorosa"])
def test_todas_as_intensidades_validas_sao_aceitas(intensidade):
    resultado = Exercise.parse("corrida", intensidade)
    assert resultado.intensity == intensidade


def test_normaliza_maiuscula_e_espacos_no_nome_e_intensidade():
    resultado = Exercise.parse("  CORRIDA  ", "  LEVE  ")
    assert resultado.exercise_name == "corrida"
    assert resultado.intensity == "leve"


def test_intensidade_sem_nome_e_rejeitada():
    with pytest.raises(ValueError):
        Exercise.parse(None, "leve")


def test_intensidade_sem_nome_via_construtor_direto_tambem_e_rejeitada():
    with pytest.raises(ValueError):
        Exercise(exercise_name=None, intensity="leve")


@pytest.mark.parametrize("intensidade_invalida", ["intensa", "extrema", "moderado"])
def test_intensidade_fora_do_conjunto_valido_e_rejeitada(intensidade_invalida):
    with pytest.raises(ValueError):
        Exercise.parse("caminhada", intensidade_invalida)


def test_e_imutavel():
    resultado = Exercise.parse("caminhada", "leve")
    with pytest.raises(Exception):
        resultado.intensity = "vigorosa"

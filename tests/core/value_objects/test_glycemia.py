import pytest
from hypothesis import given, strategies as st

from core.value_objects.glycemia import Glycemia


# ---------------------------------------------------------------------------
# Caso feliz / valores padrão
# ---------------------------------------------------------------------------

def test_parse_com_apenas_glycemia_usa_todos_os_defaults():
    resultado = Glycemia.parse(120)
    assert resultado.glycemia == 120
    assert resultado.measure_unit == "mg/dL"
    assert resultado.hypoglycemia_threshold == 70
    assert resultado.severe_hypoglycemia_threshold == 54
    assert resultado.hyperglycemia_threshold == 180
    assert resultado.severe_hyperglycemia_threshold == 250


def test_construtor_direto_tambem_valida_invariantes():
    # Mesmo bypassando parse(), o __post_init__ tem que aplicar as regras
    with pytest.raises(ValueError):
        Glycemia(glycemia=700)


# ---------------------------------------------------------------------------
# Faixa de medição do aparelho (HI / LO) - a regra que você julgou essencial
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("valor_limite", [20, 21, 599, 600, 300])
def test_glycemia_dentro_da_faixa_medivel_e_aceita(valor_limite):
    resultado = Glycemia.parse(valor_limite)
    assert resultado.glycemia == valor_limite


@pytest.mark.parametrize("valor_fora_da_faixa", [19, 0, -10, 601, 1000])
def test_glycemia_fora_da_faixa_medivel_e_rejeitada(valor_fora_da_faixa):
    with pytest.raises(ValueError):
        Glycemia.parse(valor_fora_da_faixa)


@given(st.integers(min_value=20, max_value=600))
def test_qualquer_inteiro_dentro_da_faixa_e_sempre_aceito(valor):
    resultado = Glycemia.parse(valor)
    assert resultado.glycemia == valor


@given(st.integers(max_value=19))
def test_qualquer_inteiro_abaixo_do_minimo_e_sempre_rejeitado(valor):
    with pytest.raises(ValueError):
        Glycemia.parse(valor)


@given(st.integers(min_value=601))
def test_qualquer_inteiro_acima_do_maximo_e_sempre_rejeitado(valor):
    with pytest.raises(ValueError):
        Glycemia.parse(valor)


# ---------------------------------------------------------------------------
# Unidade de medida
# ---------------------------------------------------------------------------

def test_measure_unit_default_quando_omitido():
    resultado = Glycemia.parse(120)
    assert resultado.measure_unit == "mg/dL"


def test_measure_unit_explicito_valido():
    resultado = Glycemia.parse(120, measure_unit_value="mg/dL")
    assert resultado.measure_unit == "mg/dL"


@pytest.mark.parametrize("unidade_invalida", ["mmol/L", "xyz"])
def test_measure_unit_invalido_e_rejeitado(unidade_invalida):
    with pytest.raises(ValueError):
        Glycemia.parse(120, measure_unit_value=unidade_invalida)


def test_measure_unit_string_vazia_e_rejeitada():
    with pytest.raises(ValueError):
        Glycemia.parse(120, measure_unit_value="")


# ---------------------------------------------------------------------------
# Ordenação dos thresholds - sem empate permitido (regra que você atualizou)
# ---------------------------------------------------------------------------

def test_thresholds_default_sao_ordem_valida():
    # Garante que os próprios defaults da classe não se autoinvalidam.
    resultado = Glycemia.parse(120)
    assert resultado.severe_hypoglycemia_threshold < resultado.hypoglycemia_threshold
    assert resultado.hypoglycemia_threshold < resultado.hyperglycemia_threshold
    assert resultado.hyperglycemia_threshold < resultado.severe_hyperglycemia_threshold


def test_thresholds_customizados_em_ordem_valida_sao_aceitos():
    resultado = Glycemia.parse(
        120,
        severe_hypoglycemia_threshold=50,
        hypoglycemia_threshold=65,
        hyperglycemia_threshold=190,
        severe_hyperglycemia_threshold=260,
    )
    assert resultado.severe_hypoglycemia_threshold == 50
    assert resultado.severe_hyperglycemia_threshold == 260


@pytest.mark.parametrize("severe_hyper,hyper", [
    (180, 180),   
    (170, 180),  
])
def test_severe_hyperglycemia_deve_ser_estritamente_maior_que_hyperglycemia(severe_hyper, hyper):
    with pytest.raises(ValueError):
        Glycemia.parse(120, hyperglycemia_threshold=hyper, severe_hyperglycemia_threshold=severe_hyper)


@pytest.mark.parametrize("severe_hypo,hypo", [
    (70, 70),     
    (80, 70),    
])
def test_severe_hypoglycemia_deve_ser_estritamente_menor_que_hypoglycemia(severe_hypo, hypo):
    with pytest.raises(ValueError):
        Glycemia.parse(120, hypoglycemia_threshold=hypo, severe_hypoglycemia_threshold=severe_hypo)


@pytest.mark.parametrize("hypo,hyper", [
    (100, 100),   # empatados
    (150, 100),   # hyper menor que hypo (invertido)
])
def test_hyperglycemia_deve_ser_estritamente_maior_que_hypoglycemia(hypo, hyper):
    with pytest.raises(ValueError):
        Glycemia.parse(120, hypoglycemia_threshold=hypo, hyperglycemia_threshold=hyper)


def test_hyperglycemia_nao_pode_ser_menor_ou_igual_a_severe_hypoglycemia():
    with pytest.raises(ValueError):
        Glycemia.parse(
            120,
            severe_hypoglycemia_threshold=100,
            hypoglycemia_threshold=101,
            hyperglycemia_threshold=100,  # <= severe_hypo
        )


def test_severe_hyperglycemia_nao_pode_ser_menor_ou_igual_a_severe_hypoglycemia():
    with pytest.raises(ValueError):
        Glycemia.parse(
            120,
            severe_hypoglycemia_threshold=200,
            hypoglycemia_threshold=201,
            hyperglycemia_threshold=202,
            severe_hyperglycemia_threshold=200,  # <= severe_hypo
        )


def test_severe_hyperglycemia_nao_pode_ser_menor_ou_igual_a_hypoglycemia():
    with pytest.raises(ValueError):
        Glycemia.parse(
            120,
            hypoglycemia_threshold=200,
            hyperglycemia_threshold=201,
            severe_hyperglycemia_threshold=200,  # <= hypo
        )


@given(
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100),
)
def test_qualquer_ordem_estritamente_crescente_de_thresholds_e_valida(a, b, c):
    # Constrói 4 valores estritamente crescentes a partir de deltas positivos,
    # cobrindo uma variedade grande de combinações válidas automaticamente.
    severe_hypo = 10
    hypo = severe_hypo + a
    hyper = hypo + b
    severe_hyper = hyper + c
    resultado = Glycemia.parse(
        120,
        severe_hypoglycemia_threshold=severe_hypo,
        hypoglycemia_threshold=hypo,
        hyperglycemia_threshold=hyper,
        severe_hyperglycemia_threshold=severe_hyper,
    )
    assert resultado.severe_hypoglycemia_threshold == severe_hypo
    assert resultado.severe_hyperglycemia_threshold == severe_hyper


# ---------------------------------------------------------------------------
# Coerção de tipo dentro do parse()
# ---------------------------------------------------------------------------

def test_parse_aceita_glycemia_como_string_numerica():
    resultado = Glycemia.parse("120")
    assert resultado.glycemia == 120
    assert isinstance(resultado.glycemia, int)


def test_parse_rejeita_glycemia_string_nao_numerica():
    with pytest.raises(ValueError):
        Glycemia.parse("alta")


def test_parse_trunca_glycemia_float_para_int():
    with pytest.raises(TypeError):
        resultado = Glycemia.parse(120.9)


@pytest.mark.parametrize("valor_invalido", [None, [120], {"glycemia": 120}])
def test_parse_rejeita_tipos_totalmente_incompativeis_para_glycemia(valor_invalido):
    with pytest.raises((ValueError, TypeError)):
        Glycemia.parse(valor_invalido)


# --- [depende do fix do parse()] ---

def test_parse_aceita_threshold_como_string_numerica():
    resultado = Glycemia.parse(120, hyperglycemia_threshold="200")
    assert resultado.hyperglycemia_threshold == 200
    assert isinstance(resultado.hyperglycemia_threshold, int)


def test_parse_rejeita_threshold_string_nao_numerica():
    with pytest.raises(ValueError):
        Glycemia.parse(120, hyperglycemia_threshold="alto")


def test_parse_com_threshold_none_explicito_cai_no_default():
    resultado = Glycemia.parse(120, hypoglycemia_threshold=None)
    assert resultado.hypoglycemia_threshold == 70  # default da classe


# ---------------------------------------------------------------------------
# Imutabilidade
# ---------------------------------------------------------------------------

def test_glycemia_e_imutavel():
    resultado = Glycemia.parse(120)
    with pytest.raises(Exception):
        resultado.glycemia = 999


def test_thresholds_sao_imutaveis():
    resultado = Glycemia.parse(120)
    with pytest.raises(Exception):
        resultado.hyperglycemia_threshold = 999
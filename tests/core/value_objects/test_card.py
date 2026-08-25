from datetime import datetime, timedelta

import pytest

from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.time import Time
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.exercise import Exercise
from core.value_objects.meal import MealPeriod
from core.value_objects.observation import Observation
from core.value_objects.card import Card

from .conftest import make_card


# ---------------------------------------------------------------------------
# Composição básica - Card aceita uma instância de cada VO
# ---------------------------------------------------------------------------

def test_card_valido_e_construido_com_sucesso(valid_card_kwargs):
    resultado = Card(**valid_card_kwargs)
    assert isinstance(resultado.card_id, CardID)
    assert isinstance(resultado.card_date, Date)
    assert isinstance(resultado.card_time, Time)
    assert isinstance(resultado.glycemia, Glycemia)
    assert isinstance(resultado.long_acting_insulin, LongActingInsulin)
    assert isinstance(resultado.short_acting_insulin, ShortActingInsulin)
    assert isinstance(resultado.exercise, Exercise)
    assert isinstance(resultado.meal, MealPeriod)
    assert isinstance(resultado.obs, Observation)


def test_card_preserva_os_valores_passados(valid_card_kwargs):
    resultado = Card(**valid_card_kwargs)
    assert resultado.glycemia.glycemia == 100
    assert resultado.meal.meal_period == "jejum"


def test_card_com_campos_opcionais_todos_vazios_ainda_e_valido(valid_card_kwargs):
    # exercise, obs, e as duas insulinas podem estar "vazias" internamente
    # (None) sem impedir a criação do Card - só o VO em si precisa existir.
    valid_card_kwargs["exercise"] = Exercise.parse()
    valid_card_kwargs["obs"] = Observation.parse()
    valid_card_kwargs["long_acting_insulin"] = LongActingInsulin.parse()
    valid_card_kwargs["short_acting_insulin"] = ShortActingInsulin.parse()
    resultado = Card(**valid_card_kwargs)
    assert resultado.exercise.exercise_name is None
    assert resultado.obs.observation is None
    assert resultado.long_acting_insulin.quantity is None
    assert resultado.short_acting_insulin.quantity is None


# ---------------------------------------------------------------------------
# Card não faz nenhuma validação própria de valor - cada campo já é
# inválido antes de chegar no Card. Estes testes confirmam que o Card NÃO
# tenta revalidar (não duplica a regra) - o erro acontece na CONSTRUÇÃO
# DO VO, não na construção do Card.
# ---------------------------------------------------------------------------

def test_glycemia_invalida_falha_antes_de_chegar_no_card():
    with pytest.raises(ValueError):
        Glycemia.parse(9999)  # já falha aqui, nunca chega a existir


def test_meal_invalido_falha_antes_de_chegar_no_card():
    with pytest.raises(ValueError):
        MealPeriod.parse("refeição inexistente")


# ---------------------------------------------------------------------------
# Imutabilidade
# ---------------------------------------------------------------------------

def test_card_e_imutavel(valid_card_kwargs):
    resultado = Card(**valid_card_kwargs)
    with pytest.raises(Exception):
        resultado.glycemia = Glycemia.parse(150)


def test_card_com_mesmos_valores_sao_iguais(valid_card_kwargs):
    # dataclass frozen gera __eq__ por valor automaticamente - vale conferir
    # que isso não quebrou com a composição de VOs (cada VO também precisa
    # ter __eq__ por valor, o que já vem de graça de ser dataclass também).
    card_id = CardID.parse()
    kwargs_a = dict(valid_card_kwargs)
    kwargs_b = dict(valid_card_kwargs)
    kwargs_a["card_id"] = card_id
    kwargs_b["card_id"] = card_id
    a = Card(**kwargs_a)
    b = Card(**kwargs_b)
    assert a == b


# --------------------------
# REGRA DE DATA/HORA FUTURA
# --------------------------

def test_card_com_data_no_passado_e_aceito(valid_card_kwargs):
    valid_card_kwargs["card_date"] = Date.parse("2020-01-01")
    resultado = Card(**valid_card_kwargs)
    assert resultado.card_date._date.year == 2020


def test_card_com_data_de_hoje_e_aceito_mesmo_com_horario_arredondado_para_futuro(valid_card_kwargs):
    # Este é o caso que a checagem antiga rejeitava incorretamente.
    daqui_a_uma_hora = (datetime.now() + timedelta(hours=1)).time()
    valid_card_kwargs["card_date"] = Date(datetime.now().date())
    valid_card_kwargs["card_time"] = Time(daqui_a_uma_hora)
    resultado = Card(**valid_card_kwargs)
    assert resultado is not None


def test_card_com_data_de_amanha_e_rejeitado(valid_card_kwargs):
    amanha = (datetime.now() + timedelta(days=1)).date()
    valid_card_kwargs["card_date"] = Date(amanha)
    with pytest.raises(ValueError):
        Card(**valid_card_kwargs)


def test_card_com_data_de_uma_semana_no_futuro_e_rejeitado(valid_card_kwargs):
    daqui_a_uma_semana = (datetime.now() + timedelta(days=7)).date()
    valid_card_kwargs["card_date"] = Date(daqui_a_uma_semana)
    with pytest.raises(ValueError):
        Card(**valid_card_kwargs)
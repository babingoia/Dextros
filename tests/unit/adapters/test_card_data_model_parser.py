import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from adapters.parsers.card_data_model_parser import CardDataModelParser
from adapters.DTOs.card_data_model import CardDataModel

# Estratégias do Hypothesis para gerar dados aleatórios válidos
uuid_strategy = st.uuids(version=4).map(str)
date_strategy = st.dates().map(lambda d: d.isoformat())
time_strategy = st.times().map(lambda t: t.strftime("%H:%M"))
int_strategy = st.integers(min_value=20, max_value=600)
optional_str = st.none() | st.text()

# ESCOPO MODULE RESOLVE O HEALTH CHECK DO HYPOTHESIS
@pytest.fixture(scope="module")
def parser():
    return CardDataModelParser()

def test_parse_maps_all_fields_correctly(parser):
    data_model = {
        "card_id": "123", "card_date": "2023-01-01", "card_time": "12:00",
        "glycemia": 100, "long_acting_insulin": 10, "short_acting_insulin": 5,
        "meal": "pré almoço", "observation": "obs",
        "exercise": {"exercise_name": "corrida", "intensity": "moderada"}
    }
    
    result = parser.parse(data_model)
    
    assert result.card_id == "123"
    assert result.glycemia == "100" 
    assert result.long_acting_insulin == "10"
    assert result.short_acting_insulin == "5"
    assert result.exercise.exercise_name == "corrida"

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    card_id=uuid_strategy,
    date=date_strategy,
    time=time_strategy,
    glycemia=int_strategy,
    long_ins=int_strategy,
    short_ins=int_strategy,
    meal=optional_str,
    obs=optional_str,
    ex_name=optional_str,
    ex_int=optional_str
)
def test_parse_handles_random_valid_data(parser, card_id, date, time, glycemia, 
                                         long_ins, short_ins, meal, obs, ex_name, ex_int):
    data_model = {
        "card_id": card_id, "card_date": date, "card_time": time,
        "glycemia": glycemia, "long_acting_insulin": long_ins, "short_acting_insulin": short_ins,
        "meal": meal, "observation": obs,
        "exercise": {"exercise_name": ex_name, "intensity": ex_int}
    }
    
    result = parser.parse(data_model)
    
    assert isinstance(result.glycemia, str)
    assert isinstance(result.long_acting_insulin, str)
    assert isinstance(result.short_acting_insulin, str)
    assert result.card_id == card_id
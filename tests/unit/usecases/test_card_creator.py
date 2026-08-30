# tests/unit/test_card_creator.py
import pytest
from unittest.mock import patch, MagicMock
from usecases.Factories.card_creator import CardCreator
from usecases.dtos.cardDTOInput import CardDTOInput

@pytest.fixture
def creator():
    return CardCreator()

@pytest.fixture
def valid_dto():
    # Cria um DTO válido (o __post_init__ cuida do exercise)
    return CardDTOInput(
        card_id="123e4567-e89b-12d3-a456-426614174000",
        card_date="2023-01-01",
        card_time="12:00",
        glycemia="100",
        long_acting_insulin="10",
        short_acting_insulin="5",
        meal="pré almoço",
        observation="obs",
        exercise_name="corrida",
        exercise_intensity="moderada"
    )

@patch('usecases.Factories.card_creator.Card')
@patch('usecases.Factories.card_creator.Observation')
@patch('usecases.Factories.card_creator.MealPeriod')
@patch('usecases.Factories.card_creator.Exercise')
@patch('usecases.Factories.card_creator.ShortActingInsulin')
@patch('usecases.Factories.card_creator.LongActingInsulin')
@patch('usecases.Factories.card_creator.Glycemia')
@patch('usecases.Factories.card_creator.Time')
@patch('usecases.Factories.card_creator.Date')
@patch('usecases.Factories.card_creator.CardID')
def test_create_card_calls_all_parse_methods(
    mock_id, mock_date, mock_time, mock_glyc, mock_long, mock_short, 
    mock_ex, mock_meal, mock_obs, mock_card, creator, valid_dto
):
    result = creator.create_card(valid_dto)
    
    # Verifica se cada VO teve seu método parse chamado com o argumento certo
    mock_id.parse.assert_called_once_with(valid_dto.card_id)
    mock_date.parse.assert_called_once_with(valid_dto.card_date)
    mock_time.parse.assert_called_once_with(valid_dto.card_time)
    mock_glyc.parse.assert_called_once_with(valid_dto.glycemia)
    mock_long.parse.assert_called_once_with(valid_dto.long_acting_insulin)
    mock_short.parse.assert_called_once_with(valid_dto.short_acting_insulin)
    
    # O Exercise recebe dois argumentos
    mock_ex.parse.assert_called_once_with(valid_dto.exercise.exercise_name, valid_dto.exercise.intensity)
    
    mock_meal.parse.assert_called_once_with(valid_dto.meal)
    mock_obs.parse.assert_called_once_with(valid_dto.observation)
    
    # Verifica se a entidade Card foi instanciada com os VOs retornados
    mock_card.assert_called_once_with(
        mock_id.parse.return_value,
        mock_date.parse.return_value,
        mock_time.parse.return_value,
        mock_glyc.parse.return_value,
        mock_long.parse.return_value,
        mock_short.parse.return_value,
        mock_ex.parse.return_value,
        mock_meal.parse.return_value,
        mock_obs.parse.return_value
    )
    
    assert result == mock_card.return_value
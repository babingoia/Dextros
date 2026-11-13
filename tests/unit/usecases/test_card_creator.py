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
        carbohydrate_g="45",
        fat_g="12",
        exercise_name="corrida",
        exercise_intensity="moderada"
    )

@patch('usecases.Factories.card_creator.Card')
@patch('usecases.Factories.card_creator.Observation')
@patch('usecases.Factories.card_creator.MealPeriod')
@patch('usecases.Factories.card_creator.Meal')
@patch('usecases.Factories.card_creator.Exercise')
@patch('usecases.Factories.card_creator.ShortActingInsulin')
@patch('usecases.Factories.card_creator.LongActingInsulin')
@patch('usecases.Factories.card_creator.Glycemia')
@patch('usecases.Factories.card_creator.Time')
@patch('usecases.Factories.card_creator.Date')
@patch('usecases.Factories.card_creator.CardID')
def test_create_card_calls_all_parse_methods(
    mock_id, mock_date, mock_time, mock_glyc, mock_long, mock_short,
    mock_ex, mock_meal, mock_meal_period, mock_obs, mock_card, creator, valid_dto
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

    # A nutrição (Meal) nasce primeiro e entra composta no MealPeriod
    mock_meal.parse.assert_called_once_with(valid_dto.carbohydrate_g, valid_dto.fat_g)
    mock_meal_period.parse.assert_called_once_with(valid_dto.meal, mock_meal.parse.return_value)
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
        mock_meal_period.parse.return_value,
        mock_obs.parse.return_value
    )
    
    assert result == mock_card.return_value


@patch('usecases.Factories.card_creator.MealPeriod')
def test_card_sem_nutricao_compõe_meal_period_com_meal_none(mock_meal_period, creator, valid_dto):
    """DTO sem carbohydrate_g/fat_g (card antigo): Meal.parse(None, None) -> None
    e o MealPeriod é composto com meal=None, preservando o comportamento de antes."""
    dto_sem_nutricao = CardDTOInput(
        card_id="123e4567-e89b-42d3-a456-426614174000",  # UUID v4 válido (CardID real aqui)
        card_date=valid_dto.card_date,
        card_time=valid_dto.card_time,
        glycemia=valid_dto.glycemia,
        long_acting_insulin=valid_dto.long_acting_insulin,
        short_acting_insulin=valid_dto.short_acting_insulin,
        meal=valid_dto.meal,
        observation=valid_dto.observation,
        exercise_name="corrida",
        exercise_intensity="moderada",
    )
    # carbohydrate_g/fat_g ficam com o default None (card antigo, sem nutrição)

    creator.create_card(dto_sem_nutricao)

    # Meal real: parse(None, None) -> None, e o MealPeriod (mock) recebe None
    mock_meal_period.parse.assert_called_once_with(dto_sem_nutricao.meal, None)

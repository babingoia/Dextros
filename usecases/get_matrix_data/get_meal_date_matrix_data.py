from core.value_objects.card import Card
from usecases.get_matrix_data.base_matrix_template import BaseMatrixTemplate, Column, ColumnKey
from usecases.get_meal_list_use_case import GetMealListUseCase
from usecases.IRepository import ICardRepository

class GetMealDateMatrixUseCase(BaseMatrixTemplate):
    def __init__(
        self,
        repository: ICardRepository,
        get_meal_list: GetMealListUseCase,
    ) -> None:
        super().__init__(repository)
        self._get_meal_list = get_meal_list

    def _get_columns(self) -> list[Column]:
        meal_values: list[str] = self._get_meal_list.execute().meal_values

        return [
            (meal_value, meal_value)
            for meal_value in meal_values
        ]

    def _get_column_key(self, card: Card) -> ColumnKey | None:
        if card.meal is None:
            return None

        return card.meal.meal_period

    def _filter_cards(self, cards: list[Card]) -> list[Card]:
        return [
            card
            for card in cards
            if card.meal is not None
            and card.meal.meal_period is not None
        ]
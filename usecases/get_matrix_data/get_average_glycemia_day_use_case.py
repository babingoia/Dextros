# usecases/get_average_glycemia_per_day_use_case.py

from core.value_objects.card import Card
from usecases.IRepository import ICardRepository
from usecases.get_matrix_data.base_1d_matrix_template import Base1DMatrixTemplate, Column, ColumnKey


class GetAverageGlycemiaPerDayUseCase(Base1DMatrixTemplate):
    def __init__(self, repository: ICardRepository) -> None:
        super().__init__(repository)


    def _get_columns(self) -> list[Column]:
        return self._get_columns_for_cards(self._get_filtered_cards())


    def _get_columns_for_cards(self, cards: list[Card]) -> list[Column]:
        date_keys: list[str] = []

        for card in cards:
            date_key = self._get_column_key(card)

            if date_key is not None:
                date_keys.append(date_key)

        unique_date_keys = sorted(dict.fromkeys(date_keys))

        return [
            (date_key, date_key)
            for date_key in unique_date_keys
        ]


    def _get_column_key(self, card: Card) -> ColumnKey | None:
        return card.card_date._date.strftime("%Y-%m-%d")


    def _build_cell(self, cards: list[Card]) -> str | None:
        if not cards:
            return None

        average = sum(card.glycemia.glycemia for card in cards) / len(cards)

        return str(average)
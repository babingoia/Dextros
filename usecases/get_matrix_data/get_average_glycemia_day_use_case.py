# usecases/get_average_glycemia_per_day_use_case.py

import math

from core.value_objects.card import Card
from usecases.IRepository import ICardRepository
from usecases.dtos.card_average_output import CardAverageOutput
from usecases.get_matrix_data.base_1d_matrix_template import (
    Base1DMatrixTemplate,
    Column,
    ColumnKey,
)


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

    def _build_cell(self, cards: list[Card]) -> CardAverageOutput:
        if not cards:
            raise ValueError(
                "Não é possível construir uma célula de média sem cards."
            )

        glycemia_total: int = 0
        long_acting_total: int = 0
        short_acting_total: int = 0

        glycemia_occurrences: int = len(cards)
        long_acting_insulin_occurrences: int = 0
        short_acting_insulin_occurrences: int = 0

        for card in cards:
            glycemia_total += int(card.glycemia.glycemia)

            long_acting_total += self._get_insulin_quantity(
                card.long_acting_insulin
            )
            short_acting_total += self._get_insulin_quantity(
                card.short_acting_insulin
            )

            if self._has_insulin_occurrence(card.long_acting_insulin):
                long_acting_insulin_occurrences += 1

            if self._has_insulin_occurrence(card.short_acting_insulin):
                short_acting_insulin_occurrences += 1

        glycemia_average = math.trunc(glycemia_total / glycemia_occurrences)

        return CardAverageOutput(
            glycemia=glycemia_average,
            long_acting_insulin=long_acting_total,
            short_acting_insulin=short_acting_total,
            glycemia_occurrences=glycemia_occurrences,
            long_acting_insulin_occurrences=long_acting_insulin_occurrences,
            short_acting_insulin_occurrences=short_acting_insulin_occurrences,
        )

    @staticmethod
    def _get_insulin_quantity(insulin: object | None) -> int:
        """
        Retorna a quantidade de insulina.

        Regras:
        - Se a insulina for None, retorna 0
        - Se quantity não existir, retorna 0
        - Se quantity for None, retorna 0
        - Caso contrário, converte para int
        """

        if insulin is None:
            return 0

        quantity = getattr(insulin, "quantity", 0)

        if quantity is None:
            return 0

        return int(quantity)

    @staticmethod
    def _has_insulin_occurrence(insulin: object | None) -> bool:
        """
        Define se a insulina conta como ocorrência para o dia.

        Regras:
        - Se a insulina for None, não conta
        - Se quantity não existir, não conta
        - Se quantity for None, não conta
        - Se quantity existir, conta, mesmo que seja 0
        """

        if insulin is None:
            return False

        return getattr(insulin, "quantity", None) is not None
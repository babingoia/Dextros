# usecases/templates/base_1d_matrix_template.py

from core.value_objects.card import Card
from usecases.dtos.single_row_matrix_data import SingleRowMatrixData
from usecases.get_matrix_data.base_column_matrix_template import (
    BaseColumnMatrixTemplate,
    Column,
    ColumnKey,
)

ColumnIndex = int


class Base1DMatrixTemplate(BaseColumnMatrixTemplate):
    """
    Base para gráficos unidimensionais.

    O UseCase concreto define:
    - as colunas
    - a chave da coluna para cada card
    - o valor da célula para os cards daquela coluna
    """

    def execute(self) -> SingleRowMatrixData:
        cards: list[Card] = self._get_filtered_cards()
        columns: list[Column] = self._get_columns_for_cards(cards)

        grouped_cards = self._group_cards_by_column(cards, columns)

        cells: list[str | None] = [
            self._build_cell(grouped_cards.get(column_index, []))
            for column_index in range(len(columns))
        ]

        return SingleRowMatrixData(
            col_headers=self._get_col_headers(columns),
            cells=cells,
        )

    # -------------------------------------------------------------------
    # Hooks
    # -------------------------------------------------------------------
    def _get_columns_for_cards(self, cards: list[Card]) -> list[Column]:
        return self._get_columns()

    def _build_cell(self, cards: list[Card]) -> str | None:
        raise NotImplementedError

    # -------------------------------------------------------------------
    # Implementação comum
    # -------------------------------------------------------------------
    def _group_cards_by_column(
        self,
        cards: list[Card],
        columns: list[Column],
    ) -> dict[ColumnIndex, list[Card]]:
        col_index_by_key = self._build_column_index_by_key(columns)

        grouped: dict[ColumnIndex, list[Card]] = {}

        for card in cards:
            column_key = self._get_column_key(card)

            if column_key is None:
                continue

            column_index = col_index_by_key.get(column_key)

            if column_index is None:
                continue

            grouped.setdefault(column_index, []).append(card)

        return grouped
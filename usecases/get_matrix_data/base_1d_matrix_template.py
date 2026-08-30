# usecases/templates/base_1d_matrix_template.py

from core.value_objects.card import Card
from usecases.dtos.card_output import CardOutput
from usecases.dtos.single_row_matrix_data import SingleRowMatrixData
from usecases.get_matrix_data.base_column_matrix_template import (
    BaseColumnMatrixTemplate,
    Column,
    ColumnKey,
)
from usecases.utils.mappers import to_card_output


ColumnIndex = int


class Base1DMatrixTemplate(BaseColumnMatrixTemplate):
    """
    Template para gráficos 1D.

    Este template não possui row headers.
    Ele apenas relaciona colunas com células.
    """

    def execute(self) -> SingleRowMatrixData:
        columns: list[Column] = self._get_columns()
        cards: list[Card] = self._get_filtered_cards()

        lookup = self._build_single_row_lookup(cards, columns)
        cells = self._build_cells(columns, lookup)

        return SingleRowMatrixData(
            col_headers=self._get_col_headers(columns),
            cells=cells,
        )

    # -------------------------------------------------------------------
    # Hooks 1D
    # -------------------------------------------------------------------
    def _build_single_row_lookup(
        self,
        cards: list[Card],
        columns: list[Column],
    ) -> dict[ColumnIndex, Card]:
        """
        Hook principal para customizar o lookup da linha única.
        """

        return self._build_lookup_by_column(cards, columns)

    # -------------------------------------------------------------------
    # Implementação interna
    # -------------------------------------------------------------------
    def _build_lookup_by_column(
        self,
        cards: list[Card],
        columns: list[Column],
    ) -> dict[ColumnIndex, Card]:
        col_index_by_key = self._build_column_index_by_key(columns)

        lookup: dict[ColumnIndex, Card] = {}

        for card in cards:
            column_key = self._get_column_key(card)

            if column_key is None:
                continue

            column_index = col_index_by_key.get(column_key)

            if column_index is None:
                continue

            lookup[column_index] = card

        return lookup

    def _build_cells(
        self,
        columns: list[Column],
        lookup: dict[ColumnIndex, Card],
    ) -> list[CardOutput | None]:
        cells: list[CardOutput | None] = []

        for column_index in range(len(columns)):
            card = lookup.get(column_index)

            cells.append(
                to_card_output(card)
                if card
                else None
            )

        return cells
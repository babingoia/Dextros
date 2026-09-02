from logging import getLogger

from core.value_objects.card import Card
from usecases.dtos.card_output import CardOutput
from usecases.dtos.matrix_data import MatrixData
from usecases.get_matrix_data.base_column_matrix_template import (
    BaseColumnMatrixTemplate,
    Column,
    ColumnKey,
)
from usecases.utils.mappers import to_card_output
from usecases.utils.exceptions import DuplicatedCellError


logger = getLogger(__name__)


RowKey = str


class Base2DMatrixTemplate(BaseColumnMatrixTemplate):
    """
    Template para gráficos 2D.

    A lógica de linhas fica contextual aqui porque, por enquanto,
    não existe um mecanismo radicalmente diferente de montagem de linhas.
    """

    def execute(self) -> MatrixData:
        columns: list[Column] = self._get_columns()
        cards: list[Card] = self._get_filtered_cards()

        if not cards:
            return self._empty_matrix(columns)

        row_keys: list[RowKey] = self._get_row_keys(cards)
        lookup: dict[RowKey, dict[int, Card]] = self._build_lookup(cards, columns)

        cell_data: dict[tuple[int, int], CardOutput | None] = self._build_cell_data(
            row_keys=row_keys,
            columns=columns,
            lookup=lookup,
        )

        return MatrixData(
            row_headers=row_keys,
            col_headers=self._get_col_headers(columns),
            cell_data=cell_data,
        )

    # -------------------------------------------------------------------
    # Row key
    # -------------------------------------------------------------------
    def _get_card_row_key(self, card: Card) -> RowKey | None:
        return card.card_date._date.strftime("%Y-%m-%d")

    # -------------------------------------------------------------------
    # Construção das linhas
    # -------------------------------------------------------------------
    def _get_row_keys(self, cards: list[Card]) -> list[RowKey]:
        raw_row_keys = self._get_raw_row_keys(cards)
        unique_row_keys = self._unique_row_keys(raw_row_keys)
        return self._order_row_keys(unique_row_keys)

    def _get_raw_row_keys(self, cards: list[Card]) -> list[RowKey]:
        row_keys: list[RowKey] = []

        for card in cards:
            row_key = self._get_card_row_key(card)

            if row_key is not None:
                row_keys.append(row_key)

        return row_keys

    def _unique_row_keys(self, row_keys: list[RowKey]) -> list[RowKey]:
        return list(dict.fromkeys(row_keys))

    def _order_row_keys(self, row_keys: list[RowKey]) -> list[RowKey]:
        return sorted(row_keys)

    # -------------------------------------------------------------------
    # Construção da matriz
    # -------------------------------------------------------------------
    def _empty_matrix(self, columns: list[Column]) -> MatrixData:
        return MatrixData(
            row_headers=[],
            col_headers=self._get_col_headers(columns),
            cell_data={},
        )

    def _build_lookup(
        self,
        cards: list[Card],
        columns: list[Column],
    ) -> dict[RowKey, dict[int, Card]]:
        col_index_by_key = self._build_column_index_by_key(columns)

        lookup: dict[RowKey, dict[int, Card]] = {}

        for card in cards:
            row_key = self._get_card_row_key(card)
            column_key = self._get_column_key(card)

            if row_key is None or column_key is None:
                continue

            column_index = col_index_by_key.get(column_key)

            if column_index is None:
                continue

            row_lookup = lookup.setdefault(row_key, {})

            if column_index in row_lookup:
                logger.error(DuplicatedCellError(
                    f"Duplicated cell: row_key={row_key!r}, column_key={column_key!r}"
                ))

            row_lookup[column_index] = card

        return lookup

    def _build_cell_data(
        self,
        row_keys: list[RowKey],
        columns: list[Column],
        lookup: dict[RowKey, dict[int, Card]],
    ) -> dict[tuple[int, int], CardOutput | None]:
        cell_data: dict[tuple[int, int], CardOutput | None] = {}

        for row_index, row_key in enumerate(row_keys):
            row_cards = lookup.get(row_key, {})

            for column_index in range(len(columns)):
                card = row_cards.get(column_index)

                cell_data[(row_index, column_index)] = (
                    to_card_output(card)
                    if card
                    else None
                )

        return cell_data
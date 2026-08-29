from logging import getLogger

from usecases.IRepository import ICardRepository
from usecases.dtos.card_output import CardOutput
from usecases.dtos.matrix_data import MatrixData
from usecases.utils.mappers import to_card_output
from core.value_objects.card import Card

logger = getLogger(__name__)


Column = tuple[str, str]
RowKey = str
ColumnKey = str


class BaseMatrixTemplate:
    def __init__(self, repository: ICardRepository) -> None:
        self._repository = repository

    def execute(self) -> MatrixData:
        columns: list[Column] = self._get_columns()
        cards: list[Card] = self._repository.get_all_cards()
        cards = self._filter_cards(cards)

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
    # Pontos de extensão
    # -------------------------------------------------------------------
    def _get_columns(self) -> list[Column]:
        raise NotImplementedError

    def _get_column_key(self, card: Card) -> ColumnKey | None:
        raise NotImplementedError

    def _filter_cards(self, cards: list[Card]) -> list[Card]:
        return cards

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
    # Implementação comum
    # -------------------------------------------------------------------
    def _get_col_headers(self, columns: list[Column]) -> list[str]:
        return [label for label, _ in columns]

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
        col_index_by_key: dict[ColumnKey, int] = {
            key: index
            for index, (_, key) in enumerate(columns)
        }

        lookup: dict[RowKey, dict[int, Card]] = {}

        for card in cards:
            row_key = self._get_card_row_key(card)
            column_key = self._get_column_key(card)

            if row_key is None or column_key is None:
                continue

            column_index = col_index_by_key.get(column_key)

            if column_index is None:
                continue

            lookup.setdefault(row_key, {})[column_index] = card

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
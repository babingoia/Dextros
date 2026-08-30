# usecases/templates/base_column_matrix_template.py

from core.value_objects.card import Card
from usecases.IRepository import ICardRepository


Column = tuple[str, str]
ColumnKey = str


class BaseColumnMatrixTemplate:
    """
    Base comum para templates de gráficos baseados em colunas.

    Esta classe concentra apenas o que é compartilhado entre templates
    1D e 2D:

    - repositório
    - busca/filtro de cards
    - definição de colunas
    - descoberta da coluna do card
    - headers de coluna
    - índice de coluna por key
    """

    def __init__(self, repository: ICardRepository) -> None:
        self._repository = repository

    # -------------------------------------------------------------------
    # Pontos de extensão
    # -------------------------------------------------------------------
    def _get_columns(self) -> list[Column]:
        raise NotImplementedError

    def _get_column_key(self, card: Card) -> ColumnKey | None:
        raise NotImplementedError

    def _filter_cards(self, cards: list[Card]) -> list[Card]:
        return cards

    # -------------------------------------------------------------------
    # Implementação comum
    # -------------------------------------------------------------------
    def _get_filtered_cards(self) -> list[Card]:
        cards = self._repository.get_all_cards()
        return self._filter_cards(cards)

    def _get_col_headers(self, columns: list[Column]) -> list[str]:
        return [label for label, _ in columns]

    def _build_column_index_by_key(
        self,
        columns: list[Column],
    ) -> dict[ColumnKey, int]:
        return {
            key: index
            for index, (_, key) in enumerate(columns)
        }
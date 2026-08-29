from usecases.get_time_list_use_case import GetTimeListUseCase
from usecases.IRepository import ICardRepository
from usecases.get_matrix_data.base_matrix_template import BaseMatrixTemplate, Column, ColumnKey
from core.value_objects.card import Card

class GetHourDateMatrixUseCase(BaseMatrixTemplate):
    def __init__(self, repository: ICardRepository) -> None:
        super().__init__(repository)
        self._get_time_list = GetTimeListUseCase()

    def _get_columns(self) -> list[Column]:
        return [
            (
                time_output.time_value.strftime("%H:%M"),
                time_output.time_value.strftime("%H:%M:%S"),
            )
            for time_output in self._get_time_list.execute()
        ]

    def _get_column_key(self, card: Card) -> ColumnKey | None:
        if card.card_time is None:
            return None

        return card.card_time._time.strftime("%H:%M:%S")
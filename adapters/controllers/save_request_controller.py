from logging import getLogger
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.mappers.mappers import view_model_to_input, strip_view_model


logger = getLogger(__name__)


class SaveRequestController:
    def __init__(self, save_card_use_case):
        self.save_card_use_case = save_card_use_case


    def save_card(self, data: CardViewModel) -> None:
        logger.debug(f"Save request got: {data}")

        try:
            data = strip_view_model(data)
            input_data = view_model_to_input(data)
            self.save_card_use_case.execute(input_data)

        except Exception:
            raise TypeError(f"Malformed data for saving request: {data}")
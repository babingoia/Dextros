from logging import getLogger
from adapters.controllers.i_controller import IController
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.mappers.mappers import view_model_to_input, strip_view_model

logger = getLogger(__name__)

class SaveRequestController(IController[CardViewModel, None]):
    """Query que processa um comando de adicionar novo card no sistema. Recebe um CardViewModel para isso."""
    def __init__(self, save_card_use_case):
        self.save_card_use_case = save_card_use_case


    def execute(self, request: CardViewModel) -> None:
        logger.debug(f"Save request got: {request}")

        try:
            logger.debug("Striping data")
            stripped_data = strip_view_model(request)
            logger.debug("Converting view model to input")
            input_data = view_model_to_input(stripped_data)
            logger.debug("Calling use case save card")
            self.save_card_use_case.execute(input_data)

        except Exception as e:
            raise TypeError(f"Malformed data for saving request: {request}") from e
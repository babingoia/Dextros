from adapters.exceptions import InvalidCardFormat
from adapters.controllers.i_controller import IController

class DeleteCardRequestController(IController[str, None]):
    def __init__(self, delete_card_use_case):
        self.delete_card_use_case = delete_card_use_case


    def execute(self, request: str) -> None:
        card_id = request

        if not card_id or card_id == '':
            raise InvalidCardFormat(f"Invalid value: {type(card_id)} for card/")
    
        self.delete_card_use_case.execute(card_id)
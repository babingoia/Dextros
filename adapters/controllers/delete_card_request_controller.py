from adapters.exceptions import InvalidCardFormat

class DeleteCardRequestController:
    def __init__(self, delete_card_use_case):
        self.delete_card_use_case = delete_card_use_case


    def delete_card(self, card_id: str) -> None:
        if not card_id or card_id == '':
            raise InvalidCardFormat(f"Invalid value: {type(card_id)} for card/")
    
        self.delete_card_use_case.execute(card_id)
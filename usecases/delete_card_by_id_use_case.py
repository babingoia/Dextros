from usecases.IRepository import ICardRepository
from usecases.utils.exceptions import DomainExceptionError

class DeleteCardByIDUseCase:
    def __init__(self, card_repository: ICardRepository):
        self.repository = card_repository


    def execute(self, card_id: str) -> None:
        try:
            self.repository.remove_card(card_id)
        except Exception as err:
            raise DomainExceptionError(err)
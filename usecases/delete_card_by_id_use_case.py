from usecases.IRepository import ICardRepository
from usecases.utils.exceptions import DomainExceptionError

class DeleteCardByIDUseCase:
    """
    UseCase que deleta um card do sistema. Recebe uma card_id em forma de string e depois chama o repositório
    para remover capturando possíveis erros no caminho.
    """
    def __init__(self, card_repository: ICardRepository):
        self.repository = card_repository


    def execute(self, card_id: str) -> None:
        try:
            self.repository.remove_card(card_id)
        except Exception as err:
            raise DomainExceptionError(err) from err
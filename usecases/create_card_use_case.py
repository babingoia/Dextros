from logging import getLogger


from usecases.utils.exceptions import DomainExceptionError
from usecases.IRepository import ICardRepository
from usecases.dtos.cardDTOInput import CardDTOInput
from core.value_objects.card import Card
from usecases.Factories.I_card_creator import ICardCreator


logger = getLogger(__name__)


class CreateCardUseCase:
    """
    UseCase que recebe um repositório e um card creator para orquestrar o salvamente de um card no sistema.
    Primeiro recebe um CardDTOInput depois o valida com o card_creator e por fim salva com o repositório.
    """
    def __init__(self, repository: ICardRepository, card_creator: ICardCreator):
        self.repository: ICardRepository = repository
        self.card_creator: ICardCreator = card_creator


    def execute(self, cardDTO: CardDTOInput) -> Card:
        if cardDTO is None:
            logger.warning(f"CardDTO missing.")
            raise DomainExceptionError(f"Card creation failed, cardDTO is missing.")
        
        logger.debug(f"Creating Card from dto: {cardDTO}")

        new_card = self.card_creator.create_card(cardDTO)    

        logger.debug(f"Adding card to repository: {new_card}")
        self.repository.add_card(new_card)
        return new_card

from logging import getLogger

from adapters.repositories.DTOs.card_data_model import CardDataModel
from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.parsers.icard_parser import ICardParser


logger = getLogger(__name__)


class CardDataModelParser(ICardParser):

    def parse(self, data_model: CardDataModel) -> CardDTOInput: 
        parsed_data_model = CardDTOInput(
            data_model['card_id'],
            data_model['card_date'],
            data_model['card_time'],
            str(data_model['glycemia']),
            str(data_model['long_acting_insulin']) if data_model['long_acting_insulin'] is not None else None,
            str(data_model['short_acting_insulin']) if data_model['short_acting_insulin'] is not None else None,
            data_model['meal'],
            data_model['observation'],
            data_model['exercise']['exercise_name'],
            data_model['exercise']['intensity']  
        )

        return parsed_data_model

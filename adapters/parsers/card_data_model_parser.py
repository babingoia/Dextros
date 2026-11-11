from logging import getLogger

from adapters.repositories.DTOs.card_data_model import CardDataModel
from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.parsers.icard_parser import ICardParser


logger = getLogger(__name__)


class CardDataModelParser(ICardParser):
    """Classe utilitária que mapeia CardDataModel em outras estruturas de dados. Feita assim para manter
    algum contexto. Deveria ser depreciada em breve por uma função utilitária para simplificação.

    Leitura retrocompatível do campo meal:
    - formato canônico: dict {"meal_period": ..., "meal": {"carbohydrate_g": ..., "fat_g": ...} | None}
    - formato legado:   string simples (ex: "pós almoço") — nutrição vem None
    A normalização do arquivo em disco é responsabilidade do DatabaseMigrationService;
    aqui a tolerância é cinto e suspensório durante a transição.
    """
    def parse(self, data_model: CardDataModel) -> CardDTOInput:
        meal_raw = data_model['meal']

        if isinstance(meal_raw, dict):
            meal_period = meal_raw.get('meal_period')
            nutrition = meal_raw.get('meal') or {}
            carbohydrate_g = nutrition.get('carbohydrate_g')
            fat_g = nutrition.get('fat_g')
        else:
            meal_period = meal_raw
            carbohydrate_g = None
            fat_g = None

        parsed_data_model = CardDTOInput(
            data_model['card_id'],
            data_model['card_date'],
            data_model['card_time'],
            str(data_model['glycemia']),
            str(data_model['long_acting_insulin']) if data_model['long_acting_insulin'] is not None else None,
            str(data_model['short_acting_insulin']) if data_model['short_acting_insulin'] is not None else None,
            meal_period,
            data_model['observation'],
            data_model['exercise']['exercise_name'],
            data_model['exercise']['intensity'],
            carbohydrate_g=carbohydrate_g,
            fat_g=fat_g,
        )

        return parsed_data_model

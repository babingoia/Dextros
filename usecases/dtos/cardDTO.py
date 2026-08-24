from dataclasses import dataclass


@dataclass
class CardDTOInput:
    card_id: str
    date: str
    time: str
    glycemia: str
    long_acting_insulin: str
    short_acting_insulin: str
    exercise: str
    meal: str
    obs: str
# usecases/dtos/card_average_output.py

from dataclasses import dataclass


@dataclass
class CardAverageOutput:
    glycemia: int
    long_acting_insulin: int
    short_acting_insulin: int

    glycemia_occurrences: int
    long_acting_insulin_occurrences: int
    short_acting_insulin_occurrences: int
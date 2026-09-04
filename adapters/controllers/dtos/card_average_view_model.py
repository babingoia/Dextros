from typing import TypedDict

class CardAverageViewModel(TypedDict):
    glycemia: int
    long_acting_insulin: int
    short_acting_insulin: int

    glycemia_occurrences: int
    long_acting_insulin_occurrences: int
    short_acting_insulin_occurrences: int
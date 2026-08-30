from dataclasses import dataclass

@dataclass
class TimeList:
    """Estrutura que guarda uma lista de tempos únicos para a view consumir."""
    not_datetime_time: list[str]
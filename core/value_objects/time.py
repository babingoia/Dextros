from datetime import datetime, time
from logging import getLogger
from dataclasses import dataclass


logger = getLogger(__name__)


@dataclass(frozen=True)
class Time():
    """
    VO de tempo, guarda um objeto time. Aceita None para tempo atual arredondado, time, datetime ou string.
    """

    _time: time

    @classmethod
    def parse(cls, value: None | datetime | time | str = None):
        match value:
            case None:
                return cls._new()
            case datetime():
                return cls._from_datetime(value)
            case time():
                return cls._from_time(value)
            case str():
                return cls._from_string(value)
            case _:
                raise TypeError(f"Invalid type for Time: {type(value)}")


    @classmethod
    def _new(cls):
        return cls(datetime.now().time())

    @classmethod
    def _from_datetime(cls, value: datetime):
        return cls(value.time())

    @classmethod
    def _from_time(cls, value: time):
        return cls(value)

    @classmethod
    def _from_string(cls, value: str):
        try:
            parsed_value = value.strip().lower()
            value_hour, value_minute = map(int, parsed_value.split(":")[:2])

            parsed_time = time(hour=value_hour, minute=value_minute)
            return cls(parsed_time)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid string for Time object: {value}")
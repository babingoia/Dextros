from dataclasses import dataclass
from datetime import date, datetime
from logging import getLogger

logger = getLogger(__name__)


@dataclass(frozen=True)
class Date:
    
    _date: date

    @classmethod
    def parse(cls, value: date | datetime | str | None = None):
        """
        Ponto de entrada de Date.
        :type value: date | datetime | str | None
        """
        match value:
            case datetime():
                return cls._from_datetime(value)
            case date():
                return cls._from_date(value)
            case str():
                return cls._from_string(value)
            case None:
                return cls._new()
            case _:
                raise TypeError(f"Invalid Type for Date: {type(value)}")
    

    @classmethod
    def _new(cls):
        return cls(date.today())

    @classmethod
    def _from_datetime(cls, value: datetime):
        return cls(value.date())

    @classmethod
    def _from_date(cls, value: date):
        return cls(value)

    @classmethod
    def _from_string(cls, value: str):
        try:
            return cls(datetime.strptime(value.strip(), "%Y-%m-%d").date())
        except (ValueError, TypeError) as err:
            raise ValueError(f"Error trying to create date from string value: {value}") from err
from datetime import date, datetime
from logging import getLogger


logger = getLogger(__name__)


class Date():
    def __init__(self, value=None):
        logger.debug(f"Initializing Date with value: {value}")

        if value is None:
            self._date: date = date.today()
        else:
            self._date = self.parse_date(value)


    @property
    def date(self) -> date:
        return self._date


    def to_string(self) -> str:
        return self._date.strftime("%Y-%m-%d")


    def set_date(self, value):
        logger.debug(f"Setting date with value: {value}")

        self._date = self.parse_date(value)


    @staticmethod
    def parse_date(value) -> date:
        """
        Aceita datetime.date, datetime.datetime ou string 'YYYY-MM-DD'.
        Retorna datetime.date ou lança ValueError/TypeError.
        """
        logger.debug(f"Parsing date from value: {value}")

        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Data inválida. Use o formato YYYY-MM-DD.")
        raise TypeError("Valor deve ser datetime.date, datetime.datetime ou string 'YYYY-MM-DD'.")


    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Valida se a string é uma data válida no formato YYYY-MM-DD."""
        logger.debug(f"Validating date string: {date_str}")
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

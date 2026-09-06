from uuid import uuid4, UUID
from dataclasses import dataclass
from logging import getLogger

from core.exceptions import ParseError, InvalidCardId

logger = getLogger(__name__)

@dataclass(frozen=True)
class CardID:
    """VO que garante um UUID versão 4 válido. Aceita string, int, UUID v4 ou None para novo valor."""
 
    card_id: UUID
 
    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.card_id.version != 4:
            raise InvalidCardId(f"CardID can only be v4, but is: {self.card_id}")
 

    @classmethod
    def parse(cls, value: str | int | UUID | None = None) -> "CardID":
        """Ponto de entrada único: decide pra qual constructor rotear.
        Não faz parsing por conta própria — só despacha."""
        match value:
            case None:
                return cls._new()
            case UUID():
                return cls(value)
            case str():
                return cls._from_string(value)
            case int():
                return cls._from_int(value)
            case _:
                raise ParseError(f"Invalid type for CardID: {type(value)}")


    @classmethod
    def _new(cls) -> "CardID":
        return cls(uuid4())
 

    @classmethod
    def _from_string(cls, value: str) -> "CardID":
        try:
            parsed = UUID(value.strip())
        except (ValueError, AttributeError) as err:
            raise ParseError(f"Invalid string for card ID: {value!r}") from err
        return cls(parsed)
 

    @classmethod
    def _from_int(cls, value: int) -> "CardID":
        try:
            parsed = UUID(int=value)
        except (ValueError, TypeError) as err:
            raise ParseError(f"Invalid CardId for integer: {value!r}") from err
        return cls(parsed)
    

    def __eq__(self, other):
        if isinstance(other, CardID):
            return self.card_id == other.card_id
        
        if isinstance(other, str):
            try:
                return self.card_id == UUID(other)
            except ValueError:
                return False 
        
        if isinstance(other, UUID):
            return self.card_id == other
            
        return NotImplemented
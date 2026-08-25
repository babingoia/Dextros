from uuid import uuid4, UUID
from dataclasses import dataclass, InitVar, field
from logging import getLogger

logger = getLogger(__name__)

@dataclass(frozen=True)
class CardID:
    """VO que garante um UUID versão 4 válido. Aceita string, int, UUID v4 ou None para novo valor."""
 
    card_id: UUID
 
    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.card_id.version != 4:
            raise ValueError(f"CardID precisa ser UUID versão 4, recebeu: {self.card_id}")
 

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
                raise TypeError(f"Tipo inválido para CardID: {type(value)}")


    @classmethod
    def _new(cls) -> "CardID":
        return cls(uuid4())
 

    @classmethod
    def _from_string(cls, value: str) -> "CardID":
        try:
            parsed = UUID(value.strip())
        except (ValueError, AttributeError) as err:
            raise ValueError(f"CardID inválido a partir de string: {value!r}") from err
        return cls(parsed)
 

    @classmethod
    def _from_int(cls, value: int) -> "CardID":
        try:
            parsed = UUID(int=value)
        except (ValueError, TypeError) as err:
            raise ValueError(f"CardID inválido a partir de int: {value!r}") from err
        return cls(parsed)
    

    def __eq__(self, other):
        # Se estiver comparando com outro CardID
        if isinstance(other, CardID):
            return self.card_id == other.card_id
        
        # Se estiver comparando com uma string (ex: a que vem do JSON/Repo)
        if isinstance(other, str):
            try:
                return self.card_id == UUID(other)
            except ValueError:
                return False # Se a string não for um UUID válido, não é igual
        
        # Se estiver comparando direto com um objeto UUID
        if isinstance(other, UUID):
            return self.card_id == other
            
        return NotImplemented
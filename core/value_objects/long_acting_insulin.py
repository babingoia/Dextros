from logging import getLogger
from dataclasses import dataclass

logger = getLogger(__name__)

@dataclass(frozen=True)
class LongActingInsulin:
    """
    Quantidade de insulina de ação longa ou ultralonga que o usuário tomou. Pode ser definida como None.\n

    Valores aceitos: None, string, int. (0 é guardado como None)
    """
    quantity: int | None


    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.quantity == None:
            return
        
        if self.quantity == 0:
            object.__setattr__(self, "quantity", None)
            return
        
        if self.quantity < 0:
            raise ValueError(f"Negativa invalid Long-Actin Insulin value: {self.quantity}")


    @classmethod
    def parse(cls, quantity_value: int | str | None = None) -> "LongActingInsulin":
        match quantity_value:
            case None:
                return cls(quantity_value)
            case str():
                return cls._from_string(quantity_value)
            case int():
                return cls(quantity_value)
            case _:
                raise TypeError(f"Inválid value for Long-Actin insulin quantity: {type(quantity_value)}")


    @classmethod
    def _from_string(cls, quantity_value: str) -> "LongActingInsulin":
        quantity_value = quantity_value.strip()
        
        if quantity_value == "":
            quantity_value = None
            return cls()

        return cls(int(quantity_value))
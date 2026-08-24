from dataclasses import dataclass


@dataclass(frozen=True)
class ShortActingInsulin:
    """
    Guarda a quantidade de insulina rápida ou ultrarápida que o usuário tomou naquela medição. Pode assumir
    valores None.

    Tipos aceitos: str, int, None. (0 convertido para None)
    """


    quantity: int | None

    def __post_init__(self):
        if self.quantity == 0:
            object.__setattr__(self, "quantity", None)
        
        if self.quantity < 0:
            raise ValueError(f"Negativa invalid Short-Actin Insulin value: {self.quantity}")


    @classmethod
    def parse(cls, quantity_value: int | str | None = None) -> "ShortActingInsulin":
        match quantity_value:
            case None:
                return cls(quantity_value)
            case int():
                return cls(quantity_value)
            case str():
                return cls._from_string(quantity_value)
            case _:
                raise TypeError(f"Invalid quantity type for Short-Actin insulin: {type(quantity_value)}")


    @classmethod
    def _from_string(cls, quantity_value: str) -> "ShortActingInsulin":
        quantity_value = int(quantity_value.strip())
        return cls(quantity_value)
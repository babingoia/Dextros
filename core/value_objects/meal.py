from dataclasses import dataclass

# Constantes
_VALID_MEAL_VALUES = ["jejum", "pós café da manhã", "pré lanche da manhã",
                      "pós lanche da manhã", "pré almoço", "pós almoço", "pré café da tarde",
                      "pós café da tarde", "pré jantar", "pós jantar", "madrugada"]

@dataclass(frozen=True)
class MealPeriod:
    """
    Guarda um valor de tempo com base nas refeições do usuário. Pode ser None para dextros feitos sem uma
    refeição próxima.
    """
    
    meal_period: str | None = None

    
    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.meal_period is None:
            return
        
        if self.meal_period not in _VALID_MEAL_VALUES:
            raise ValueError(f"Invalid meal value: {self.meal_period}")
    

    @classmethod
    def parse(cls, meal_period_value: str | None = None) -> "MealPeriod":
        if not isinstance(meal_period_value, str | None):
            raise TypeError(f"Invalid time for MealPeriod: {type(meal_period_value)}")
        
        if meal_period_value is None:
            return cls()
        
        meal_period_value = meal_period_value.strip().lower()
        return cls(meal_period_value)
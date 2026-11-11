import math
from dataclasses import dataclass

from core.value_objects.food import Food

# Constantes
_VALID_MEAL_VALUES = ["jejum", "pós café da manhã", "pré lanche da manhã",
                      "pós lanche da manhã", "pré almoço", "pós almoço", "pré café da tarde",
                      "pós café da tarde", "pré jantar", "pós jantar", "madrugada"]


def _normalize_consumed_value(raw_value, field_name: str) -> float | None:
    """Normaliza um valor nutricional consumido para float ou None.

    Regras de domínio (só validações literalmente impossíveis):
    - None ou string vazia -> None (campo não preenchido)
    - valor negativo -> ValueError (massa negativa não existe, análogo a -1 UI de insulina)
    - NaN/infinito -> ValueError (não é um valor de medição real)
    - não numérico -> TypeError/ValueError

    Nota: normalizar vírgula decimal ("45,2" -> "45.2") é responsabilidade da camada
    de apresentação (mapper), não do VO. Aqui a vírgula falha como qualquer char inválido.
    """
    if raw_value is None:
        return None
    if isinstance(raw_value, str) and raw_value.strip() == "":
        return None
    if isinstance(raw_value, bool) or not isinstance(raw_value, float | int | str):
        raise TypeError(f"Invalid type for {field_name}: {type(raw_value)}")

    try:
        value = float(raw_value)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid numeric value for {field_name}: {raw_value!r}") from err

    if not math.isfinite(value):
        raise ValueError(f"Non-finite value for {field_name}: {raw_value!r}")
    if value < 0:
        raise ValueError(f"Negative value for {field_name}: {raw_value!r}")

    return value


@dataclass(frozen=True)
class Meal:
    """Valores nutricionais (comida real) consumidos no registro de um dextro.

    Os valores são os CONSUMIDOS no momento do registro, em gramas inteiras
    (arredondamento feito no parse, pois a precisão de meio grama não muda a
    contagem de dextros). Cada campo é opcional: é comum registrar só carboidrato.
    """

    carbohydrate_g: int | None = None
    fat_g: int | None = None

    def __post_init__(self):
        """Método reservado. Usar parse ou from_food para criar entidades como entry point."""
        for field_name, value in (("carbohydrate_g", self.carbohydrate_g),
                                  ("fat_g", self.fat_g)):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be int or None, got: {type(value)}")
            if value < 0:
                raise ValueError(f"Negative value for {field_name}: {value!r}")

    @classmethod
    def parse(cls, carbohydrate_value=None, fat_value=None) -> "Meal | None":
        """Entry point do VO. Recebe os valores consumidos em gramas.

        Retorna None quando não há nenhum valor informado — um Meal sem conteúdo é
        "nenhuma nutrição registrada" e nunca deve ser persistido como objeto vazio.
        """
        parsed_carb = _normalize_consumed_value(carbohydrate_value, "carbohydrate_g")
        parsed_fat = _normalize_consumed_value(fat_value, "fat_g")

        if parsed_carb is None and parsed_fat is None:
            return None

        return cls(
            carbohydrate_g=None if parsed_carb is None else round(parsed_carb),
            fat_g=None if parsed_fat is None else round(parsed_fat),
        )

    @classmethod
    def from_food(cls, food: Food, grams) -> "Meal | None":
        """Conversão pura de um alimento da tabela TACO em valores consumidos.

        Recebe o Food já resolvido (o VO não busca nada — sem IO, sem consulta) e a
        quantidade consumida em gramas. Retorna None quando o alimento não tem nenhum
        dos dois nutrientes na tabela.

        Regras:
        - gramas negativas -> ValueError (literalmente impossível)
        - grams=0 é válido e produz Meal zerado (a camada de apresentação decide
          como exibir/tratar o zero)
        - nutriente ausente na tabela (None) permanece None no resultado
          (desconhecido != zero)
        """
        if not isinstance(food, Food):
            raise TypeError(f"Invalid type for food: {type(food)}. Expected Food.")

        if grams is None:
            raise TypeError("grams is required and can't be None")

        parsed_grams = _normalize_consumed_value(grams, "grams")
        if parsed_grams is None:
            raise ValueError("grams can't be empty")

        parsed_carb = (round(food.carbohydrate_g * parsed_grams / 100)
                       if food.carbohydrate_g is not None else None)
        parsed_fat = (round(food.fat_g * parsed_grams / 100)
                      if food.fat_g is not None else None)

        if parsed_carb is None and parsed_fat is None:
            return None

        return cls(carbohydrate_g=parsed_carb, fat_g=parsed_fat)


@dataclass(frozen=True)
class MealPeriod:
    """
    Guarda um valor de tempo com base nas refeições do usuário. Pode ser None para dextros feitos sem uma
    refeição próxima. Opcionalmente carrega um Meal com os valores nutricionais consumidos no período.
    """

    meal_period: str | None = None
    meal: Meal | None = None

    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.meal is not None and not isinstance(self.meal, Meal):
            raise TypeError(f"Invalid type for meal: {type(self.meal)}. Use Meal.parse to build one.")

        if self.meal_period is None:
            return

        if self.meal_period not in _VALID_MEAL_VALUES:
            raise ValueError(f"Invalid meal value: {self.meal_period}")

    @classmethod
    def parse(cls, meal_period_value: str | None = None,
              meal: Meal | None = None) -> "MealPeriod":
        if not isinstance(meal_period_value, str | None):
            raise TypeError(f"Invalid time for MealPeriod: {type(meal_period_value)}")

        if meal is not None and not isinstance(meal, Meal):
            raise TypeError(f"Invalid type for meal: {type(meal)}. Use Meal.parse to build one.")

        if meal_period_value is None:
            return cls(None, meal)

        meal_period_value = meal_period_value.strip().lower()
        return cls(meal_period_value, meal)

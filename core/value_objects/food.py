import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Food:
    """Referência nutricional de um alimento da tabela TACO. Todos os valores nutricionais
    são por 100 gramas do alimento, na precisão original da tabela (float).

    Os campos carbohydrate_g e fat_g podem ser None quando a tabela não traz valor
    confiável para o nutriente ("NA", "Tr", "" — a normalização desses casos é
    responsabilidade da fonte de dados, não do VO).
    """

    food_id: int
    description: str
    category: str
    carbohydrate_g: float | None = None
    fat_g: float | None = None

    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if isinstance(self.food_id, bool) or not isinstance(self.food_id, int):
            raise TypeError(f"Invalid type for food_id: {type(self.food_id)}")
        if self.food_id < 0:
            raise ValueError(f"Invalid food_id: {self.food_id}")

        for field_name, value in (("description", self.description),
                                  ("category", self.category)):
            if not isinstance(value, str):
                raise TypeError(f"Invalid type for {field_name}: {type(value)}")
            if not value.strip():
                raise ValueError(f"{field_name} can't be empty")

        for field_name, value in (("carbohydrate_g", self.carbohydrate_g),
                                  ("fat_g", self.fat_g)):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, float | int):
                raise TypeError(f"Invalid type for {field_name}: {type(value)}")
            if not math.isfinite(value):
                raise ValueError(f"Non-finite value for {field_name}: {value!r}")
            if value < 0:
                raise ValueError(f"Negative value for {field_name}: {value!r}")

    @classmethod
    def parse(cls, food_id, description, category,
              carbohydrate_value=None, fat_value=None) -> "Food":
        """Entry point do VO. Valores nutricionais aceitam float, int, string numérica
        (com ponto decimal) ou None. String vazia é tratada como valor indisponível (None).
        """
        if isinstance(food_id, bool) or not isinstance(food_id, int | float | str):
            raise TypeError(f"Invalid type for food_id: {type(food_id)}")

        try:
            parsed_id = int(food_id)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid food_id: {food_id!r}") from err

        if not isinstance(description, str) or not isinstance(category, str):
            raise TypeError(
                f"description and category must be str, got: "
                f"{type(description)}, {type(category)}"
            )

        parsed_description = description.strip()
        parsed_category = category.strip()

        if not parsed_description:
            raise ValueError("description can't be empty")
        if not parsed_category:
            raise ValueError("category can't be empty")

        parsed_carb = _normalize_per_100g_value(carbohydrate_value, "carbohydrate_g")
        parsed_fat = _normalize_per_100g_value(fat_value, "fat_g")

        return cls(
            food_id=parsed_id,
            description=parsed_description,
            category=parsed_category,
            carbohydrate_g=parsed_carb,
            fat_g=parsed_fat,
        )


def _normalize_per_100g_value(raw_value, field_name: str) -> float | None:
    """Normaliza um valor nutricional por 100g para float ou None.

    Regras de domínio:
    - None ou string vazia -> None (dado indisponível na fonte)
    - valor negativo -> ValueError (massa negativa é literalmente impossível)
    - NaN/infinito -> ValueError (não é um valor de tabela real)
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

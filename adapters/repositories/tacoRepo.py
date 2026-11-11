import json
from logging import getLogger
from pathlib import Path

from adapters.exceptions import FoodDataError
from core.value_objects.food import Food

logger = getLogger(__name__)

# Convenções da tabela TACO para valores não aplicáveis / traço / vazio.
# Todos viram None: dado indisponível é diferente de zero.
_UNAVAILABLE_TOKENS = {"NA", "TR", ""}

# Ruído de medição da fonte: a TACO original tem valores de carboidrato
# levemente negativos em peixes/carnes sem CHO (entre -0.045 e -0.007 g/100g),
# produto da média das medições laboratoriais. Analiticamente são zero —
# viram 0.0 na carga. Negativo além desse limiar é corrupção de dados.
_NOISE_THRESHOLD_G = 1.0


def _normalize_taco_value(raw_value) -> float | None:
    """Normaliza um valor nutricional cru da TACO para float ou None.

    A TACO mistura tipos: floats, ints e as strings "NA" (não aplicável),
    "Tr" (traço, desprezível) e "" (não medido). Qualquer valor que não
    represente um número confiável vira None — nunca zero. Ruído negativo
    pequeno vira 0.0; o VO de domínio nunca vê valor negativo.
    """
    if raw_value is None:
        return None

    if isinstance(raw_value, bool):
        return None

    if isinstance(raw_value, int | float):
        value = float(raw_value)
    elif isinstance(raw_value, str):
        stripped = raw_value.strip()
        if stripped.upper() in _UNAVAILABLE_TOKENS:
            return None
        try:
            value = float(stripped)
        except ValueError:
            logger.warning(f"Unparseable TACO value treated as unavailable: {raw_value!r}")
            return None
    else:
        logger.warning(f"Unexpected TACO value type treated as unavailable: {type(raw_value)}")
        return None

    if value < 0:
        if value >= -_NOISE_THRESHOLD_G:
            return 0.0
        raise FoodDataError(f"Corrupted negative value in TACO source: {raw_value!r}")

    return value


class TacoRepository:
    """Fonte de dados concreta e read-only da tabela TACO.

    Não implementa ABC de propósito: tem um único consumidor (o composition
    root, que injeta os Foods parseados nos use cases de busca) e nenhum
    comportamento polimórfico — criar interface aqui seria ceremony. O
    arquivo é um asset somente-leitura: carrega uma vez e cacheia.
    """

    def __init__(self, taco_path: str | Path):
        self._path = Path(taco_path)
        self._foods: list[Food] | None = None

    def get_all(self) -> list[Food]:
        """Retorna todos os alimentos da tabela (cópia defensiva, cacheado)."""
        if self._foods is None:
            self._foods = self._load()
        return list(self._foods)

    def _load(self) -> list[Food]:
        logger.info(f"Loading TACO table from {self._path}")

        try:
            with open(self._path, "r", encoding="utf-8") as f:
                raw_foods = json.load(f)
        except FileNotFoundError as err:
            raise FoodDataError(f"TACO table not found at: {self._path}") from err
        except json.JSONDecodeError as err:
            raise FoodDataError(f"TACO table is not valid JSON: {self._path}") from err

        foods: list[Food] = []
        for entry in raw_foods:
            try:
                foods.append(Food.parse(
                    food_id=entry.get("id"),
                    description=entry.get("description"),
                    category=entry.get("category"),
                    carbohydrate_value=_normalize_taco_value(entry.get("carbohydrate_g")),
                    fat_value=_normalize_taco_value(entry.get("lipid_g")),
                ))
            except (ValueError, TypeError) as err:
                raise FoodDataError(
                    f"Invalid food entry at TACO (id={entry.get('id')!r}): {err}"
                ) from err

        logger.info(f"TACO table loaded: {len(foods)} foods")
        return foods

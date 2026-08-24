from dataclasses import dataclass
from typing import TypedDict


# Constantes para validação interna
_MAX_GLYCEMIA = 600
_MIN_GLYCEMIA = 20
_VALID_GLYCEMIA_MEASURE_VALUES = ["mg/dL"]
_CANONICAL_BY_LOWER = {v.lower(): v for v in _VALID_GLYCEMIA_MEASURE_VALUES}


@dataclass(frozen=True)
class Glycemia:
    """
    Vo que marca a glicemia. Possui diversos campos, mas só um deles precisa ser preenchido que é glycemia
    com valores int ou str. \n
    Os outros podem ser preenchidos com valores int, str e None para valores padrão.
    """
    glycemia: int

    measure_unit: str = "mg/dL"
    hypoglycemia_threshold: int = 70
    severe_hypoglycemia_threshold: int = 54
    hyperglycemia_threshold: int = 180
    severe_hyperglycemia_threshold: int = 250

    def __post_init__(self):
        if self.glycemia > _MAX_GLYCEMIA or self.glycemia <  _MIN_GLYCEMIA:
            raise ValueError(f"Invalid glycemia input: {self.glycemia}\n"
                             f"If this is not an error, please go to a doctor imediatly!")
        
        if self.measure_unit not in _VALID_GLYCEMIA_MEASURE_VALUES:
            raise ValueError(f"Measure Unit not found. {self.measure_unit}")
        
        if self.severe_hyperglycemia_threshold <= self.hyperglycemia_threshold:
            raise ValueError(f"Severe Hyperglycemia ({self.severe_hyperglycemia_threshold}) is lower than Hyperglycemia ({self.hyperglycemia_threshold})!")
        
        if self.severe_hypoglycemia_threshold >= self.hypoglycemia_threshold:
            raise ValueError(f"Severe Hypoglycemia ({self.severe_hypoglycemia_threshold}) is higher than Hipoglycemia({self.hypoglycemia_threshold})!")

        if (self.hyperglycemia_threshold <= self.severe_hypoglycemia_threshold 
            or self.hyperglycemia_threshold <= self.hypoglycemia_threshold):
            raise ValueError(f"Hyperglycemia threshold lower than Hypoglycemia thresholds!")
        
        if (self.severe_hyperglycemia_threshold < self.severe_hypoglycemia_threshold 
            or self.severe_hyperglycemia_threshold < self.hypoglycemia_threshold):
            raise ValueError(f"Severe Hyperglycemia threshold lower than Hypoglycemia thresholds!")


    @classmethod
    def parse(cls, glycemia_value, measure_unit_value=None, **thresholds) -> "Glycemia":
        glycemia_int = int(glycemia_value)

        if measure_unit_value is None:
            unit = "mg/dL"
        else:
            normalized = measure_unit_value.strip().lower()
            unit = _CANONICAL_BY_LOWER.get(normalized, normalized)

        thresholds_int = {k: int(v) for k, v in thresholds.items() if v is not None}
        return cls(glycemia=glycemia_int, measure_unit=unit, **thresholds_int)

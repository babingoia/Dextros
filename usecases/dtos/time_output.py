from dataclasses import dataclass
from datetime import time


@dataclass
class TimeOutput:
    """Representa um único valor time sozinho para saida dos usecases."""
    time_value: time
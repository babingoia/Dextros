from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.value_objects.Card import Card


@dataclass
class DateHourGrid:
    """Estrutura que organiza os cards por data única e os horários dentro dela."""
    date_map: dict[str, dict[str, "Card"]]
    unique_dates: list[str]

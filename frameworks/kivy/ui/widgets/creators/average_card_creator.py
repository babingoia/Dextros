from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.controllers.dtos.card_average_view_model import CardAverageViewModel

class AverageCardCreator:
    """Mapeia CardAverageViewModel para o dicionário de propriedades da BarCell."""

    def create_cell_dict(self, data: CardAverageViewModel) -> dict:
        return {
            "glycemia_value": data["glycemia"],
            "long_value": data["long_acting_insulin"],
            "short_value": data["short_acting_insulin"],
            "glycemia_occurrences": data["glycemia_occurrences"],
            "long_occurrences": data["long_acting_insulin_occurrences"],
            "short_occurrences": data["short_acting_insulin_occurrences"],
            "dialog_metrics": [
                {"label": "Glicemia", "value": data["glycemia"], "occurrences": data["glycemia_occurrences"], "color_name": "primary"},
                {"label": "Ins. lenta", "value": data["long_acting_insulin"], "occurrences": data["long_acting_insulin_occurrences"], "color_name": "success"},
                {"label": "Ins. rápida", "value": data["short_acting_insulin"], "occurrences": data["short_acting_insulin_occurrences"], "color_name": "warning"},
            ],
        }
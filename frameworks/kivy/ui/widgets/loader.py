from logging import getLogger
from typing import Callable, Optional

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from infrastructure.path_provider_service import get_asset_path


logger = getLogger(__name__)
Builder.load_file(get_asset_path('frameworks/kivy/ui/widgets/Border.kv'))
Builder.load_file(get_asset_path('frameworks/kivy/ui/widgets/Card.kv'))


class Border(BoxLayout):
    border_color = ObjectProperty((1, 1, 1, 1))
    border_width = ObjectProperty(1)


class CardWidget(BoxLayout):
    def __init__(self, card_data: dict, on_delete_callback: Optional[Callable] = None, **kwargs):
        logger.debug(f"Initializing CardWidget with card_data: {card_data.get('card_id')}")
        super().__init__(**kwargs)
        
        self.card_data = card_data
        self.on_delete_callback = on_delete_callback
        
        # Preenche os labels usando os dados do CardViewModel
        self.ids.data_value.text = card_data.get("card_data", "")
        self.ids.horario_value.text = card_data.get("card_time", "")
        self.ids.dextro_value.text = card_data.get("glycemia", "")
        self.ids.lenta_value.text = card_data.get("long_acting_insulin", "")
        self.ids.rapida_value.text = card_data.get("short_acting_insulin", "")
        
        # Formata exercício se existir
        exercise = card_data.get("exercise", {})
        exercise_text = exercise.get("exercise_name", "")
        if exercise.get("intensity"):
            exercise_text += f" ({exercise['intensity']})"
        self.ids.exercicio_value.text = exercise_text
        
        self.ids.refeicao_value.text = card_data.get("meal", "")
        self.ids.observacao_value.text = card_data.get("observation", "")
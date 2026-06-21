from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from presentation.kivy.controllers.session_cache import SessionCache
from infrastructure.path_provider import get_asset_path
from logging import getLogger


logger = getLogger(__name__)
Builder.load_file(get_asset_path('presentation/kivy/ui/widgets/Border.kv'))
Builder.load_file(get_asset_path('presentation/kivy/ui/widgets/Card.kv'))


class Border(BoxLayout):
    border_color = ObjectProperty((1, 1, 1, 1))
    border_width = ObjectProperty(1)


class CardWidget(BoxLayout):
    def __init__(self, card_data, **kwargs):
        logger.debug(f"Initializing CardWidget with card_data: {card_data}")
        super().__init__(**kwargs)
        self.cards_on_session = SessionCache()
        self.card_data = card_data
        self.ids.data_value.text = card_data.data
        self.ids.horario_value.text = card_data.horario
        self.ids.dextro_value.text = card_data.dextro
        self.ids.lenta_value.text = card_data.lenta
        self.ids.rapida_value.text = card_data.rapida
        self.ids.exercicio_value.text = card_data.exercicio
        self.ids.refeicao_value.text = card_data.refeicao
        self.ids.observacao_value.text = card_data.observacao
    

    def delete_card(self):
        """Event of card exclusion. Triggered by the delete button in the card."""
        logger.debug(f"Delete card event triggered for card_data: {self.card_data}")
        self.cards_on_session.remove_card(self.card_data)
        self.popup.dismiss()


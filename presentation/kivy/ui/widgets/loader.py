from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from presentation.kivy.controllers.SessionCache import SessionCache
from infrastructure.path_provider import get_asset_path
from logging import getLogger


logger = getLogger(__name__)
Builder.load_file(get_asset_path('presentation/kivy/ui/widgets/Border.kv'))
Builder.load_file(get_asset_path('presentation/kivy/ui/widgets/Card.kv'))


class Border(BoxLayout):
    border_color = ObjectProperty((1, 1, 1, 1))
    border_width = ObjectProperty(1)


class CardWidget(BoxLayout):
    def __init__(self, card_data, cards_on_session = SessionCache(), **kwargs):
        logger.debug(f"Initializing CardWidget with card_data: {card_data}")
        super().__init__(**kwargs)
        self.cards_on_session = cards_on_session
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
        logger.debug(f"Deleting card with data: {self.card_data.data} | horario: {self.card_data.horario}")
        self.cards_on_session.remove_card(self.card_data)

        # Fecha o popup
        self.popup.dismiss()


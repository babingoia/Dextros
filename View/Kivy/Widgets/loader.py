from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from Models.SessionCache import SessionCache
from Handlers.Funcs import get_asset_path

Builder.load_file(get_asset_path('View/Kivy/Widgets/Border.kv'))
Builder.load_file(get_asset_path('View/Kivy/Widgets/Card.kv'))

cards_on_session = SessionCache()


class Border(BoxLayout):
    border_color = ObjectProperty((1, 1, 1, 1))
    border_width = ObjectProperty(1)


class CardWidget(BoxLayout):
    def __init__(self, card_data, **kwargs):
        super().__init__(**kwargs)
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
        # Remove o card da sessão
        cards_on_session.remove_card(self.card_data)

        # Fecha o popup
        self.popup.dismiss()


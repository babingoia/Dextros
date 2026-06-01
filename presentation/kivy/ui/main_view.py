from kivy.uix.accordion import StringProperty
from kivy.uix.accordion import ListProperty
#Libs
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


#My files
from core.value_objects.Time import Time
from presentation.kivy.ui.widgets.pickers.date_picker import DatePicker
from infrastructure.path_provider import get_asset_path
from presentation.kivy.controllers.SessionCache import SessionCache
from core.value_objects.Date import Date


Builder.load_file(get_asset_path('presentation/kivy/ui/main_scene.kv'))


class MainView(BoxLayout):

    __events__ = ("on_save_request",)

    horarios_disponiveis = ListProperty([])
    horario_atual = StringProperty("Horário:")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.date_picker = DatePicker(on_date_selected=self.atualizar_data_input)
        self.ids.data_input.text = self.date_picker.date.to_string()


    def on_save_request(self, *args):
        print("save resquest got")


    def choose_date(self) -> None:
        self.date_picker.show_date_picker()


    def atualizar_data_input(self, date: Date) -> None:
        self.ids.data_input.text = date.to_string()
    

    def show_error(message: str, title: str="ERRO") -> None:
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.55, 0.3))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()


    def get_data(self) -> dict[str, str]:
        data = {
            'data': self.ids.data_input.text,
            'horario': self.ids.horario_spinner.text,
            'dextro': self.ids.dextro_input.text,
            'lenta': self.ids.lenta_input.text,
            'rapida': self.ids.rapida_input.text,
            'exercicio': self.ids.exercicio_input.text,
            'refeicao': self.ids.refeicao_input.text,
            'observacao': self.ids.observacao_input.text,
            'date_hour_matrix': self.ids.graph_layout
        }

        return data
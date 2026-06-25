from kivy.properties import StringProperty
from kivy.properties import ListProperty
from datetime import date
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from logging import getLogger

#My files
from presentation.kivy.ui.widgets.pickers.date_picker import DatePicker
from infrastructure.path_provider_service import get_asset_path


Builder.load_file(get_asset_path('presentation/kivy/ui/main_scene.kv'))
logger = getLogger(__name__)


class MainView(BoxLayout):

    __events__ = ("on_save_request",)

    available_time = ListProperty([])
    actual_time = StringProperty("Horário:")
    date_display = StringProperty()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("MainView initialized")
        self.date_picker = DatePicker(self.date_display, on_date_selected=self._update_data_input)


    def on_save_request(self, *args):
        logger.debug("Save request event triggered with data: %s", args)


    def _choose_date(self) -> None:
        logger.debug("Date picker opened")
        self.date_picker.show_date_picker()


    def _update_data_input(self, date: str) -> None:
        logger.debug("Updating date input with selected date: %s", date)
        self.ids.data_input.text = date
    

    def _show_error(self, message: str, title: str="ERRO") -> None:
        logger.error("Error popup displayed with message: %s", message)
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.55, 0.3))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()


    def get_data(self) -> dict[str, str]:
        logger.debug("Retrieving data from input fields")
        data = {
            'data': self.ids.data_input.text,
            'horario': self.ids.horario_spinner.text,
            'dextro': self.ids.dextro_input.text,
            'lenta': self.ids.lenta_input.text,
            'rapida': self.ids.rapida_input.text,
            'exercicio': self.ids.exercicio_input.text,
            'refeicao': self.ids.refeicao_input.text,
            'observacao': self.ids.observacao_input.text,
            'date_hour_matrix': self.ids.matrix_container
        }

        return data
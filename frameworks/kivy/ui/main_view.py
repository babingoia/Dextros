from kivy.properties import StringProperty
from kivy.properties import ListProperty
from datetime import date
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from logging import getLogger
from kivy.factory import Factory

# My files
from frameworks.kivy.ui.widgets.pickers.date_picker import DatePicker
from frameworks.kivy.ui.widgets.graphs.screens.graph_screen import GraphScreen
from infrastructure.path_provider_service import get_asset_path
from adapters.controllers.dtos.card_view_model import CardViewModel
from frameworks.kivy.ui.widgets.popup.dialog import AppDialog, DialogMessage

Builder.load_file(get_asset_path('frameworks/kivy/ui/main_scene.kv'))
Builder.load_file(get_asset_path('frameworks/kivy/ui/ui_components.kv'))

logger = getLogger(__name__)


class MainView(BoxLayout):
    __events__ = ("on_save_request",)

    available_meals = ListProperty([])
    available_time = ListProperty([])
    actual_meal = StringProperty("Escolha uma Refeição:")
    actual_time = StringProperty("Horário:")
    date_display = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("MainView initialized")
        self.date_picker = DatePicker(
            self.date_display,
            on_date_selected=self._update_data_input
        )

    def on_save_request(self, *args):
        logger.debug("Save request event triggered with data: %s", args)

    def show_save_confirmation(
        self,
        message: str = "Registro Salvo!",
        title: str = "Salvar"
    ) -> None:
        logger.info("Save confirmation popup displayed")

        dialog = AppDialog(title=title, auto_height=True)
        dialog.set_content(DialogMessage(text=message))
        dialog.set_buttons([
            ("OK", "primary", lambda *a: dialog.dismiss())
        ])
        dialog.open()

    def show_error(self, message: str, title: str = "ERRO") -> None:
        logger.error("Error popup displayed with message: %s", message)

        dialog = AppDialog(title=title, auto_height=True)
        dialog.set_content(DialogMessage(text=message))
        dialog.set_buttons([
            ("OK", "danger", lambda *a: dialog.dismiss())
        ])
        dialog.open()

    def _show_error(self, message: str, title: str = "ERRO") -> None:
        self.show_error(message, title)

    def _choose_date(self) -> None:
        logger.debug("Date picker opened")
        self.date_picker.show_date_picker()

    def _update_data_input(self, date: str) -> None:
        logger.debug("Updating date input with selected date: %s", date)
        self.ids.data_input.text = date

    def get_data(self) -> dict[str, str]:
        logger.debug("Retrieving data from input fields")

        data = CardViewModel(
            card_id='',
            card_data=self.ids.data_input.text,
            card_time=self.ids.horario_spinner.text,
            glycemia=self.ids.dextro_input.text,
            long_acting_insulin=self.ids.lenta_input.text,
            short_acting_insulin=self.ids.rapida_input.text,
            exercise={
                'exercise_name': self.ids.exercicio_input.text,
                'intensity': ''
            },
            meal="" if self.ids.meal_value.text.lower() == "nenhum" else self.ids.meal_value.text,
            observation=self.ids.observacao_input.text,
        )

        return data

    def add_graph_screen(self, name, title, graph_widget, refresh_callback=None):
        """
        Na arquitetura nova: a tela já existe no KV, o GraphScreenContent
        já criou o gráfico internamente. Só precisamos configurar o callback
        e (se necessário) atualizar o título.
        """
        sm = self.ids.screens

        if not sm.has_screen(name):
            logger.warning(f"Tela {name} não encontrada no .kv.")
            return

        screen = sm.get_screen(name)

        # Injeta o callback de lazy load
        if hasattr(screen, 'refresh_callback'):
            screen.refresh_callback = refresh_callback

        # Atualiza o título (se o content tiver a property)
        content = screen.children[0] if screen.children else None
        if content and hasattr(content, 'title'):
            content.title = title

        # Navega para a tela
        sm.current = name

    def _navigate_to(self, name):
        sm = self.ids.screens

        # O Kivy NÃO dispara on_pre_enter se a tela atual já for a de destino.
        # Forçamos o refresh manualmente nesse caso específico.
        if sm.current == name:
            screen = sm.get_screen(name)
            if hasattr(screen, 'refresh_callback') and screen.refresh_callback:
                screen.refresh_callback()
        else:
            sm.current = name

        # Em celular, fecha a navbar lateral após navegar
        if hasattr(self.ids, 'nav_toggle'):
            self.ids.nav_toggle.state = "normal"
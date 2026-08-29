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

#My files
from frameworks.kivy.ui.widgets.pickers.date_picker import DatePicker
from frameworks.kivy.ui.widgets.screens.graph_screen import GraphScreen
from infrastructure.path_provider_service import get_asset_path
from adapters.controllers.dtos.card_view_model import CardViewModel

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
        
        data = CardViewModel(
            card_id = '',
            card_data = self.ids.data_input.text,
            card_time =  self.ids.horario_spinner.text,
            glycemia = self.ids.dextro_input.text,
            long_acting_insulin = self.ids.lenta_input.text,
            short_acting_insulin = self.ids.rapida_input.text,
            exercise = {'exercise_name': self.ids.exercicio_input.text,
                          'intensity': ''},
            meal = "" if self.ids.meal_value.text.lower() == "nenhum" else self.ids.meal_value.text,
            observation = self.ids.observacao_input.text,
        )

        return data


    def add_graph_screen(self, name, title, graph_widget, refresh_callback=None):
        """
        Vincula o callback de lazy load e garante que o gráfico esteja na tela,
        sem tentar adicionar duplicadamente se ele já estiver no .kv.
        """
        sm = self.ids.screens

        if sm.has_screen(name):
            screen = sm.get_screen(name)
            
            # 1. Injeta o callback de lazy load (ISSO JÁ ESTÁ FUNCIONANDO)
            if hasattr(screen, 'refresh_callback'):
                screen.refresh_callback = refresh_callback
            
            # 2. SEGURANÇA: Só tenta adicionar o widget se ele NÃO tiver um pai.
            # Se ele já está no .kv (dentro do matrix_container), pulamos essa etapa.
            if graph_widget.parent is None:
                logger.info("Widget do gráfico não tem pai, adicionando dinamicamente...")
                panel_found = False
                for child in screen.walk():
                    if child.__class__.__name__ == 'Panel':
                        child.add_widget(graph_widget)
                        panel_found = True
                        break
                
                # Fallback extremo se não achar o Panel
                if not panel_found:
                    screen.add_widget(graph_widget)
            else:
                logger.info(f"Widget do gráfico já está posicionado no pai: {graph_widget.parent}")

            # Navega para a tela
            sm.current = name
            return

        # 3. Fallback: Se a tela não existir no .kv, cria tudo dinamicamente
        logger.warning(f"Tela {name} não encontrada no .kv. Criando dinamicamente.")
        screen = GraphScreen(name=name, refresh_callback=refresh_callback)
        
        content = Factory.GraphScreenContent()
        content.add_widget(Factory.ScreenHeader(text=title))
        
        panel = Factory.Panel()
        panel.add_widget(graph_widget)
        content.add_widget(panel)
        
        screen.add_widget(content)
        sm.add_widget(screen)
        sm.current = name

        # Cria o botão na navbar lateral
        button = Factory.NavButton(text=title, group="nav")
        button.bind(
            on_release=lambda *args, screen_name=name: self._navigate_to(screen_name)
        )
        self.ids.nav_items.add_widget(button)

        # 2. Se a tela NÃO EXISTE, cria dinamicamente (Fallback seguro)
        screen = GraphScreen(name=name, refresh_callback=refresh_callback)
        
        content = Factory.GraphScreenContent()
        content.add_widget(Factory.ScreenHeader(text=title))
        
        panel = Factory.Panel()
        panel.add_widget(graph_widget)
        content.add_widget(panel)
        
        screen.add_widget(content)
        sm.add_widget(screen)
        sm.current = name

        # Cria o botão na navbar lateral
        button = Factory.NavButton(text=title, group="nav")
        button.bind(
            on_release=lambda *args, screen_name=name: self._navigate_to(screen_name)
        )
        self.ids.nav_items.add_widget(button)

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
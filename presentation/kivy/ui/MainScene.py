#Libs
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

#My files
from presentation.kivy.ui.widgets.error import show_error
from presentation.kivy.ui.widgets.pickers.date_picker import DatePicker
from presentation.kivy.ui.configs import CELL_W, CELL_H, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import Border, CardWidget
from infrastructure.path_provider import get_asset_path
from core.value_objects.Time import Time
from core.value_objects.Card import Card
from core.SessionCache import SessionCache
from core.value_objects.Date import Date
from presentation.kivy.ui.widgets.graphs.DateHourMatrix import DateHourMatrix


# Carrega os arquivos Kivy
Builder.load_file(get_asset_path('presentation/kivy/ui/main_scene.kv'))

#Global variables
cards_on_session = SessionCache()


#MainView
class MainScene(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Usa Time para gerenciar horários
        self.horarios = Time()
        self.horarios_para_colunas = self.horarios.get_horario_colunas()
        self.ids.horario_spinner.values = self.horarios.get_horarios()
        self.ids.horario_spinner.text = self.horarios.get_horario_now()
        
        # DatePicker
        self.date_picker = DatePicker(on_date_selected=self.atualizar_data_input)
        self.ids.data_input.text = self.date_picker.date.to_string()
        
        # Cache 
        cards_on_session.bind("on_add", self.atualizar_grafico)
        cards_on_session.bind("on_remove", self.atualizar_grafico)

        # Gráfico em Matrix de date e horário
        self.date_hour_matrix = DateHourMatrix(self.ids.graph_layout, self.horarios)
        self.ids.graph_layout.add_widget(self.date_hour_matrix)


    def choose_date(self):
        self.date_picker.show_date_picker()


    def atualizar_data_input(self, date: Date):
        self.ids.data_input.text = date.to_string()


    def atualizar_grafico(self):
        self.date_hour_matrix.date = self.date_picker.date
        self.date_hour_matrix.draw_self()


    def save_card(self) -> None:
        # Pega os dados através dos IDs definidos no .kv
        data = self.ids.data_input.text.strip()
        horario = self.ids.horario_spinner.text

        if not Date.is_valid_date(data):
            show_error("Data inválida", "Informe a data no formato YYYY-MM-DD")
            return

        if not self.horarios.is_valid_horario(horario):
            show_error("Horário inválido", "Escolha um horário válido")
            return

        card = Card(
            data=data,
            horario=horario,
            dextro=self.ids.dextro_input.text,
            lenta=self.ids.lenta_input.text,
            rapida=self.ids.rapida_input.text,
            exercicio=self.ids.exercicio_input.text,
            refeicao=self.ids.refeicao_input.text,
            observacao=self.ids.observacao_input.text,
        )

        cards_on_session.add_card(card)
    
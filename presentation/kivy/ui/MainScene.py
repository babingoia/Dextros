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
from presentation.kivy.ui.pickers.date_picker import DatePicker
from presentation.kivy.ui.configs import CELL_W, CELL_H, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import Border, CardWidget
from infrastructure.path_provider import get_asset_path
from core.value_objects.Time import Time
from core.value_objects.Card import Card
from core.SessionCache import SessionCache
from core.value_objects.Date import Date


# Carrega os arquivos Kivy
Builder.load_file(get_asset_path('View/Kivy/main_scene.kv'))

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

        self.date_picker = DatePicker()
        self.ids.data_input.text = self.date_picker.date.to_string()
        self.date_picker = DatePicker(on_date_selected=self.atualizar_data_input)

        cards_on_session.bind("on_add", self.atualizar_grafico)
        cards_on_session.bind("on_remove", self.atualizar_grafico)

        # Desenha o gráfico inicial
        self.draw_graph()


    def choose_date(self):
        self.date_picker.show_date_picker()


    def atualizar_data_input(self, date: Date):
        self.ids.data_input.text = date.to_string()


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


    def draw_graph(self) -> None:
        graph = self.ids.graph_layout
        graph.clear_widgets()

        cards = Card.order_by_date_and_horario(cards_on_session.get_cards())
        if not cards:
            return

        date_map, unique_dates = Card.organize_cards(cards)

        # Linha de cabeçalho (horários)
        graph.add_widget(Label(text="", size_hint=(None, None), size=(CELL_W, CELL_H)))
        for horario in self.horarios.get_horarios():
            border = Border(border_width=BORDER_WIDTH)
            graph.add_widget(border)
            border.add_widget(Label(text=horario, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))

        # Linhas de dados
        for date in unique_dates:
            date_border = Border(border_width=BORDER_WIDTH)
            graph.add_widget(date_border)
            date_border.add_widget(Label(text=date, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))
            for horario in self.horarios.get_horarios():
                if horario in date_map[date]:
                    card_border = Border(border_width=BORDER_WIDTH)
                    graph.add_widget(card_border)
                    card = date_map[date][horario]
                    btn = Button(
                        text=str(card.dextro),
                        size_hint=(None, None),
                        size=(CELL_W, CELL_H),
                    )
                    btn.bind(on_press=lambda _inst, c=card: self.show_card_details(c))
                    card_border.add_widget(btn)
                else:
                    card_border = Border(border_color=(1, 0, 0, 1), border_width=BORDER_WIDTH)
                    graph.add_widget(card_border)
                    card_border.add_widget(Label(text="X", size_hint=(None, None), size=(CELL_W, CELL_H)))


    def show_card_details(self, card: Card) -> None:
        content = CardWidget(card)

        width = min(dp(500), Window.width * 0.9)
        height = min(dp(450), Window.height * 0.9)

        popup = Popup(title="Card Details",
                     content=content, 
                     size_hint=(None, None),
                     size=(width, height)
                     )

        content.popup = popup
        popup.open()
    

    def atualizar_grafico(self):
        self.draw_graph()
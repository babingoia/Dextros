from kivymd.uix.pickers.datepicker.datepicker import date
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

from core.value_objects.Card import Card
from core.SessionCache import SessionCache
from core.value_objects.Date import Date
from core.value_objects.Time import Time
from presentation.kivy.ui.configs import CELL_W, CELL_H, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import Border, CardWidget


cards_on_session = SessionCache()


class DateHourMatrix(Widget):
    def __init__(self, id, horarios: Time, **kwargs):
        super().__init__(**kwargs)
       
        self._id = id
        self._horarios = horarios
        self.draw_self()

        


    def redraw(self):
        pass


    def draw_self(self) -> None:
        print("Drawing DateHourMatrix...")
        self._id.clear_widgets()

        cards = Card.order_by_date_and_horario(cards_on_session.get_cards())
        if not cards:
            return

        date_map, unique_dates = Card.organize_cards(cards)

        # Linha de cabeçalho (horários)
        self._id.add_widget(Label(text="", size_hint=(None, None), size=(CELL_W, CELL_H)))
        for horario in self._horarios.get_horarios():
            border = Border(border_width=BORDER_WIDTH)
            self._id.add_widget(border)
            border.add_widget(Label(text=horario, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))

        # Linhas de dados
        for date in unique_dates:
            date_border = Border(border_width=BORDER_WIDTH)
            self._id.add_widget(date_border)
            date_border.add_widget(Label(text=date, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))
            for horario in self._horarios.get_horarios():
                if horario in date_map[date]:
                    card_border = Border(border_width=BORDER_WIDTH)
                    self._id.add_widget(card_border)
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
                    self._id.add_widget(card_border)
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
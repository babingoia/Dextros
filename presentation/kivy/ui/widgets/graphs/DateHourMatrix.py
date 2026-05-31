from __future__ import annotations

from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from typing import TYPE_CHECKING

from core.value_objects.Card import Card
from presentation.kivy.controllers.SessionCache import SessionCache
from presentation.kivy.ui.configs import CELL_W, CELL_H, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import Border, CardWidget
from presentation.kivy.ui.widgets.creators.card_creator import CardCreator, NONE_CARD, CARD

if TYPE_CHECKING:
    from core.value_objects.Time import Time
    from core.DataClasses import DateHourGrid


class DateHourMatrix(RecycleView):
    def __init__(self, id, card_creator=CardCreator(), **kwargs):
        super().__init__(**kwargs)
        self._container = id
        self.card_creator = card_creator


    def draw_self(self, cards: list[Card], horarios: Time, dates_data: DateHourGrid) -> None:
        print("Drawing DateHourMatrix...", dates_data)
        self._container.clear_widgets()

        if not cards:
            return

        # Linha de cabeçalho (horários)
        self._container.add_widget(Label(text="", size_hint=(None, None), size=(CELL_W, CELL_H)))
        for horario in horarios.get_horarios():
            border = Border(border_width=BORDER_WIDTH)
            self._container.add_widget(border)
            border.add_widget(Label(text=horario, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))

        # Linhas de dados
        for date in dates_data.unique_dates:
            date_border = Border(border_width=BORDER_WIDTH)
            self._container.add_widget(date_border)
            date_border.add_widget(Label(text=date, size_hint=(None, None), size=(CELL_W, CELL_H), bold=True))
            for horario in horarios.get_horarios():
                if horario in dates_data.date_map[date]:
                    new_card = self.card_creator.create_card(CARD, dates_data.date_map[date][horario])
                    self._container.add_widget(new_card)
                else:
                    new_card = self.card_creator.create_card(NONE_CARD, None)
                    self._container.add_widget(new_card)

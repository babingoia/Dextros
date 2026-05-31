from kivy.uix.recyclegridlayout import defaultdict
"""
Classe que controla a matriz de cartas, atualizando a interface gráfica conforme necessário.
"""
from presentation.kivy.ui.widgets.graphs.DateHourMatrix import DateHourMatrix
from presentation.kivy.controllers.SessionCache import SessionCache
from core.DataClasses import DateHourGrid
from core.value_objects.Card import Card
from core.value_objects.Time import Time


class MatrixController:
    def __init__(self, grid_id, time_data=Time(), cards_on_session=SessionCache()):

        self.grid_view = DateHourMatrix(grid_id)
        self.grid_id = grid_id
        grid_id.add_widget(self.grid_view)

        self.cards_on_session = cards_on_session
        self.cards_date: DateHourGrid = self.getDatesCard()
        self.time_data = time_data

        self.atualizar_grafico()


    def _subscribe(self):
        self.cards_on_session.bind("on_add", self.atualizar_grafico())
        self.cards_on_session.bind("on_remove", self.atualizar_grafico())


    def atualizar_grafico(self):
        self.grid_view.draw_self(self.time_data, self.cards_date)    

    
    def getDatesCard(self) -> DateHourGrid:
        cards = self.cards_on_session.get_cards()
        cards = Card.organize_cards(cards)
        return cards
 

from kivy.uix.recyclegridlayout import defaultdict

from logging import getLogger
"""
Classe que controla a matriz de cartas, atualizando a interface gráfica conforme necessário.
"""
from presentation.kivy.ui.widgets.graphs.DateHourMatrix import DateHourMatrix
from presentation.kivy.controllers.SessionCache import SessionCache
from core.DataClasses import DateHourGrid
from core.value_objects.Card import Card
from core.value_objects.Time import Time


logger = getLogger(__name__)


class MatrixController:
    def __init__(self, grid_id, time_data=Time(), cards_on_session=SessionCache()):
        logger.info("Initializing MatrixController...")

        self.grid_view = DateHourMatrix(grid_id)
        self.grid_id = grid_id
        grid_id.add_widget(self.grid_view)

        self.cards_on_session = cards_on_session
        self.cards_date: DateHourGrid = self.getDatesCard()
        self.time_data = time_data

        self._subscribe()
        self.atualizar_grafico()


    def _subscribe(self):
        logger.debug("Subscribing to SessionCache events for card updates...")

        self.cards_on_session.bind("on_add", self.atualizar_grafico)
        self.cards_on_session.bind("on_remove", self.atualizar_grafico)


    def atualizar_grafico(self):
        logger.debug("Updating matrix graph with current session data...")
        
        self.cards_date = self.getDatesCard()
        self.grid_view.draw_self(self.cards_on_session.get_cards(),
                                 self.time_data,
                                 self.cards_date)    

    
    def getDatesCard(self) -> DateHourGrid:
        logger.debug("Extracting date-hour grid from session cards...")
        
        cards = self.cards_on_session.get_cards()
        cards = Card.organize_cards(cards)
        return cards
 

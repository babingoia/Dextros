from __future__ import annotations

from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.lang import Builder
from typing import TYPE_CHECKING
from logging import getLogger


from presentation.kivy.ui.widgets.graphs.matrix_cell import MatrixCell
from core.value_objects.card import Card
from presentation.kivy.ui.configs import CELL_W, CELL_H, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import Border
from presentation.kivy.ui.widgets.creators.card_creator import CardCreator, NONE_CARD, CARD

if TYPE_CHECKING:
    from core.value_objects.time import Time
    from core.data_classes import DateHourGrid


Builder.load_file("presentation/kivy/ui/widgets/graphs/date_hour_matrix.kv")
logger = getLogger(__name__)


class DateHourMatrix(RecycleView):
    def __init__(self, card_creator=CardCreator(), **kwargs):
        logger.info("Initializing DateHourMatrix")
        super().__init__(**kwargs)
        self.card_creator = card_creator


    def draw_self(self, cards: list[Card], horarios: Time, dates_data: DateHourGrid) -> None:
        """Agora ele não desenha, ele apenas constrói a lista de dados para a RecycleView."""
        logger.info(f"Populating DateHourMatrix with {len(cards)} cards...")

        if not cards:
            logger.warning("Card list is empty.")

        flat_data = [] # A lista mestra que o Kivy vai usar

        logger.debug("Building header data...")
        # 1. Célula vazia do canto superior esquerdo
        flat_data.append(self._create_header_dict(""))
        
        # 2. Cabeçalho dos horários
        for horario in horarios.get_horarios():
            flat_data.append(self._create_header_dict(horario))

        logger.debug("Building cells data...")
        # 3. Linhas (Data na primeira coluna + Células de Dextro)
        for date in dates_data.unique_dates:
            # Primeira coluna: A Data
            flat_data.append(self._create_header_dict(date))
            
            # Restante das colunas: Os Cards
            for horario in horarios.get_horarios():
                card_dict = self._get_cell_dict(horario, date, dates_data)
                flat_data.append(card_dict)

        logger.info("Injecting data into RecycleView.")
        # A MÁGICA: Passar a lista pronta pro Kivy. Ele renderiza a tela instantaneamente.
        self.data = flat_data
        logger.debug(f"Data injected: {self.data}")


    def _create_header_dict(self, text: str) -> dict:
        """Cria o dicionário para uma célula de cabeçalho (Data ou Horário)"""
        # Assumindo que a sua MatrixCell tem as propriedades 'dextro_text', 'is_empty' e 'is_header'
        return {
            "dextro_text": text,
            "is_empty": False,
            "is_header": True, 
            "card_ref": None
        }

    def _get_cell_dict(self, horario: str, current_date: str, dates_data: DateHourGrid) -> dict:
        """Busca o card e usa o CardCreator para gerar o dicionário correto"""
        if horario in dates_data.date_map[current_date]:
            card_obj = dates_data.date_map[current_date][horario]
            # O seu card_creator agora retorna um dict, então é só pegar
            return self.card_creator.create_card(CARD, card_obj)
        else:
            # Retorna o dict de célula vazia
            return self.card_creator.create_card(NONE_CARD, None)
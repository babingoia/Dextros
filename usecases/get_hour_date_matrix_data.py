from usecases.IRepository import ICardRepository
from usecases.dtos.card_output import CardOutput
from usecases.dtos.matrix_data import MatrixData
from usecases.get_time_list_use_case import GetTimeListUseCase
from usecases.Factories.card_creator import CardCreator
from core.value_objects.card import Card
from usecases.utils.mappers import to_card_output
from logging import getLogger

logger = getLogger(__name__)

class GetHourDateMatrixUseCase:
    """
    Caso de uso responsável por validar DTOs de entrada, processar a regra de negócio 
    de organização em matriz e devolver um DTO de saída (MatrixData com CardOutput).
    """
    
    def __init__(self, repository: ICardRepository):
        self.get_time_list = GetTimeListUseCase()
        self.expected_times = self.get_time_list.execute()
        self.card_creator = CardCreator()
        self.repository = repository

    def execute(self) -> MatrixData:
        logger.debug(f"Getting and Formatting cards for matrix display")
        
        # 1. Pegar cards
        cards = self.repository.get_all_cards()

        if not cards:
            return MatrixData(
                row_headers=[], 
                col_headers=self.expected_times, 
                cell_data={}
            )

        # 2. Ordenação
        sorted_cards = sorted(
            cards, 
            key=lambda c: (c.card_date._date.strftime("%Y-%m-%d"), c.card_time._time.strftime("%H:%M"))
        )

        # 3. Extrair datas únicas mantendo a ordem cronológica
        unique_dates = list(dict.fromkeys(
            c.card_date._date.strftime("%Y-%m-%d") for c in sorted_cards
        ))

        # 4. Criar um lookup rápido O(1) usando o Domínio
        card_lookup: dict[str, dict[str, Card]] = {}
        for card in sorted_cards:
            date_str = card.card_date._date.strftime("%Y-%m-%d")
            time_str = card.card_time._time.strftime("%H:%M:%S")
            
            if date_str not in card_lookup:
                card_lookup[date_str] = {}
            
            card_lookup[date_str][time_str] = card

        # 5. Mapear para o formato de grade (row_idx, col_idx) -> CardOutput
        cell_data: dict[tuple[int, int], CardOutput | None] = {}
        
        for row_idx, date_str in enumerate(unique_dates):
            date_cards = card_lookup.get(date_str, {})
            
            for col_idx, time_str in enumerate(self.expected_times):
                domain_card = date_cards.get(time_str.time_value.strftime("%H:%M:%S"))
                
                if domain_card:
                    # A MÁGICA DA FRONTEIRA: Converte Domínio -> DTO de Saída
                    cell_data[(row_idx, col_idx)] = to_card_output(domain_card)
                else:
                    cell_data[(row_idx, col_idx)] = None
        
        expected_times: list[str] = []
        for time_output in self.expected_times:
            expected_times.append(time_output.time_value.strftime("%H:%M"))

        matrix_data = MatrixData(
            row_headers=unique_dates,
            col_headers=expected_times,
            cell_data=cell_data
        )
        
        logger.debug(f"Matrix data loaded: {matrix_data.cell_data}")
        logger.debug(f"Matrix data loaded: {matrix_data.col_headers}")
        logger.debug(f"Matrix data loaded: {matrix_data.row_headers}")
        
        return matrix_data
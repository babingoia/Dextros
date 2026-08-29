from __future__ import annotations

from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from typing import Callable, Any, Optional
from logging import getLogger
from adapters.controllers.dtos.card_view_model import CardViewModel

# Se o arquivo KV ainda for o mesmo, mantenha o load. 
# Idealmente, renomeie para generic_matrix_graph.kv no futuro.
Builder.load_file("frameworks/kivy/ui/widgets/graphs/generic_matrix_graph.kv")
logger = getLogger(__name__)


class GenericMatrixGraph(RecycleView):
    def __init__(self, container: Optional[Any] = None, **kwargs):
        logger.info("Initializing GenericMatrixGraph")
        super().__init__(**kwargs)
        self._container = container
        if self._container:
            self._container.add_widget(self)


    def draw_self(
        self, 
        row_headers: list[str], 
        col_headers: list[str], 
        cell_data: dict[tuple[int, int], CardViewModel],
        cell_factory: Callable[[int, int, Any], dict]
    ) -> None:
        """
        Constrói a lista de dados para a RecycleView de forma totalmente genérica.
        
        :param row_headers: Lista de strings para a primeira coluna (cabeçalho de linha).
        :param col_headers: Lista de strings para a primeira linha (cabeçalho de coluna).
        :param cell_data: Dicionário mapeando (row_index, col_index) -> payload dos dados.
                          Ex: {(0, 1): meu_objeto_card, (2, 3): outro_dado}
        :param cell_factory: Função que recebe (row_idx, col_idx, payload) e retorna 
                             o dicionário de propriedades que o widget do Kivy espera.
        """
        logger.info(f"Populating Matrix: {len(row_headers)} rows x {len(col_headers)} cols")

        if not row_headers or not col_headers:
            logger.warning("Matrix headers are empty.")

        flat_data = []

        # 1. Célula vazia do canto superior esquerdo (interseção dos cabeçalhos)
        flat_data.append(self._create_corner_dict())
        
        # 2. Cabeçalho das colunas (primeira linha)
        for col_header in col_headers:
            flat_data.append(self._create_header_dict(col_header))

        # 3. Linhas de dados
        for row_idx, row_header in enumerate(row_headers):
            # Primeira coluna: O cabeçalho da linha
            flat_data.append(self._create_header_dict(row_header))
            
            # Restante das colunas: Os dados (ou células vazias)
            for col_idx in range(len(col_headers)):
                payload = cell_data.get((row_idx, col_idx))
                # Delega a criação do dicionário específico para a função externa
                cell_dict = cell_factory(row_idx, col_idx, payload)
                flat_data.append(cell_dict)

        logger.info("Injecting data into RecycleView.")
        self.data = flat_data


    def _create_corner_dict(self) -> dict:
        """Célula vazia no topo à esquerda"""
        return {
            "dextro_text": "",         
            "is_header": True, 
            "is_empty": True,
            "card_reference": None      
        }


    def _create_header_dict(self, text: str) -> dict:
        """Célula de cabeçalho (seja da linha ou da coluna)"""
        return {
            "dextro_text": text,       
            "is_header": True, 
            "is_empty": False,
            "card_reference": None      
        }

from dataclasses import dataclass
from typing import Optional
from adapters.controllers.dtos.card_view_model import CardViewModel

@dataclass
class MatrixDataViewModel:
    """Estrutura completa da matriz que o Router devolve para a UI."""
    row_headers: list[str]
    col_headers: list[str]
    # O payload aqui É o CardViewModel que você já tem
    cell_data: dict[tuple[int, int], CardViewModel] 
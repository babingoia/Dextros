from dataclasses import dataclass
from usecases.dtos.card_output import CardOutput

@dataclass
class MatrixData:
    """
    Estrutura de dados limpa e previsível para alimentar gráficos de matriz.
    """
    row_headers: list[str]       # Ex: ["01/10/2023", "02/10/2023"]
    col_headers: list[str]       # Ex: ["08:00", "12:00", "18:00"]
    cell_data: dict[tuple[int, int], CardOutput]  # Mapeia (linha, coluna) -> Objeto Card (ou None)
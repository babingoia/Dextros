from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger

# Importação condicional apenas para type hinting, respeitando a fronteira
if TYPE_CHECKING:
    from adapters.controllers.dtos.card_view_model import CardViewModel

logger = getLogger(__name__)

# Constantes para os tipos de célula
CARD = "card"
NONE_CARD = "none_card"


class CardCreator:
    """
    Adaptador de UI. Responsável por mapear CardViewModel (TypedDict) 
    para dicionários de propriedades compatíveis com a RecycleView do Kivy.
    """
    
    def __init__(self):
        logger.debug("CardCreator initialized")

    def create_cell_dict(self, cell_type: str, data: CardViewModel | None = None) -> dict:
        if cell_type == CARD:
            return self._build_card_dict(data)
        elif cell_type == NONE_CARD:
            return self._build_empty_card_dict()
        
        logger.warning(f"Unknown cell type requested: {cell_type}. Returning empty card.")
        return self._build_empty_card_dict()


    def _build_card_dict(self, vm: CardViewModel) -> dict:
        if not vm or not vm.get("card_id"):
            return self._build_empty_card_dict()

        return {
            "is_empty": False,
            "is_header": False,
            "dextro_text": vm["glycemia"],
            # Passa o dict inteiro para o Popup poder ler os dados
            "card_reference": vm, 
        }
    

    def _build_empty_card_dict(self) -> dict:
        return {
            "is_empty": True,
            "is_header": False,
            "dextro_text": "",
            "card_reference": None,
        }
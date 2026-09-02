from logging import getLogger

from frameworks.kivy.ui.widgets.creators.card_creator import CardCreator, CARD, NONE_CARD
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.gateways.i_router import IRouter

logger = getLogger(__name__)


class MatrixController:
    """
    Controller de UI. Só solicita dados ao Router e injeta na view
    que É DONA do gráfico (GraphScreenContent.graph).
    """

    def __init__(self, content, router: IRouter, data_source: str):
        logger.info("Initializing MatrixController...")
        self.content = content
        self.router = router
        self.data_source = data_source
        self.card_creator = CardCreator()

    def on_screen_enter(self):
        """Chamado pela Screen (Lazy Load) quando o usuário navega até ela."""
        logger.debug("Matrix screen entered. Requesting data from Router...")
        self._update_view()

    def _update_view(self):
        logger.debug("Updating GenericMatrixGraph with new data...")
        matrix_vm: MatrixDataViewModel = self.router.navigate(self.data_source)

        def cell_factory(row_idx: int, col_idx: int, payload: CardViewModel):
            if payload["card_id"]:
                cell_dict = self.card_creator.create_cell_dict(CARD, payload)
                cell_dict['delete_callback'] = self._handle_delete_card
                return cell_dict
            return self.card_creator.create_cell_dict(NONE_CARD, payload)

        self.content.graph.draw_self(
            row_headers=matrix_vm.row_headers,
            col_headers=matrix_vm.col_headers,
            cell_data=matrix_vm.cell_data,
            cell_factory=cell_factory,
        )

    def _handle_delete_card(self, card_id: str):
        logger.info(f"Controller intercepting delete for card_id: {card_id}")
        self.router.navigate("delete_card", card_id)
        self._update_view()
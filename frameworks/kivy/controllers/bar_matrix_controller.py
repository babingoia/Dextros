from logging import getLogger

from frameworks.kivy.ui.widgets.creators.average_card_creator import AverageCardCreator
from adapters.controllers.dtos.single_row_matrix_view import SingleRowMatrixView
from adapters.gateways.i_router import IRouter

logger = getLogger(__name__)


class BarMatrixController:
    """
    Controller de UI. Só solicita dados ao Router e injeta na view
    que É DONA do gráfico (GraphScreenContent.graph).
    """

    def __init__(self, content, router: IRouter, data_source: str):
        logger.info("Initializing BarMatrixController...")
        self.content = content
        self.router = router
        self.data_source = data_source
        self.card_creator = AverageCardCreator()

    def on_screen_enter(self):
        """Chamado pela Screen (Lazy Load) quando o usuário navega até ela."""
        logger.debug("Matrix screen entered. Requesting data from Router...")
        self._update_view()

    def _update_view(self):
        logger.debug("Updating GenericBarGraph...")
        graph_vm: SingleRowMatrixView = self.router.navigate(self.data_source)

        def cell_factory(col_idx: int, payload):
            return self.card_creator.create_cell_dict(payload)

        self.content.graph.draw_self(
            data=graph_vm,
            cell_factory=cell_factory,
        )

    def _handle_delete_card(self, card_id: str):
        logger.info(f"Controller intercepting delete for card_id: {card_id}")
        self.router.navigate("delete_card", card_id)
        self._update_view()
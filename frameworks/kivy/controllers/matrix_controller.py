from logging import getLogger
from frameworks.kivy.ui.widgets.graphs.generic_matrix_graph import GenericMatrixGraph
from frameworks.kivy.ui.widgets.creators.card_creator import CardCreator, CARD, NONE_CARD
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.gateways.i_router import IRouter

logger = getLogger(__name__)


class MatrixController:
    """
    Controller de UI. Responsável apenas por gerenciar a View do gráfico 
    e solicitar dados ao KivyRouter quando a tela for exibida (Lazy Load).
    """

    def __init__(self, grid_id, router: IRouter, data_souce: str):
        logger.info("Initializing MatrixController...")

        self.data_source = data_souce
        self.router = router
        self.grid_view = GenericMatrixGraph(grid_id)
        self.card_creator = CardCreator()


    def on_screen_enter(self):
        """
        Chamado pela Screen (Lazy Load) quando o usuário navega para esta tela.
        Solicita os dados ao Router e atualiza a view.
        """
        logger.debug("Matrix screen entered. Requesting data from Router...")

        self._update_view()


    def _update_view(self):
        """Converte o MatrixDataViewModel em dicionários para o RecycleView."""
        logger.debug("Updating GenericMatrixGraph with new data...")
        matrix_vm: MatrixDataViewModel = self.router.navigate(self.data_source)

        def cell_factory(row_idx: int, col_idx: int, payload: CardViewModel):
            # Como o mapper nunca retorna None, basta checar se o card_id está preenchido
            if payload["card_id"]:
                cell_dict = self.card_creator.create_cell_dict(CARD, payload)
                cell_dict['delete_callback'] = self._handle_delete_card
                
                return cell_dict
            else:
                return self.card_creator.create_cell_dict(NONE_CARD, payload)

        self.grid_view.draw_self(
            row_headers=matrix_vm.row_headers,
            col_headers=matrix_vm.col_headers,
            cell_data=matrix_vm.cell_data,
            cell_factory=cell_factory
        )
    

    def _handle_delete_card(self, card_id: str):
        """Captura o evento e deleta o card."""
        logger.info(f"Controller intercepting delete for card_id: {card_id}")
        self.router.navigate("delete_card", card_id)
        self._update_view()
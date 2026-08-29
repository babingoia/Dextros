from logging import getLogger
from frameworks.kivy.ui.widgets.graphs.generic_matrix_graph import GenericMatrixGraph
from frameworks.kivy.ui.widgets.creators.card_creator import CardCreator, CARD, NONE_CARD
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.dtos.card_view_model import CardViewModel

logger = getLogger(__name__)


class MatrixController:
    """
    Controller de UI. Responsável apenas por gerenciar a View do gráfico 
    e solicitar dados ao KivyRouter quando a tela for exibida (Lazy Load).
    """

    def __init__(self, grid_id, router):
        logger.info("Initializing MatrixController...")

        self.router = router
        self.grid_view = GenericMatrixGraph(grid_id)
        self.card_creator = CardCreator()

        self.grid_view.bind(on_delete_request=self._handle_delete_card)


    def on_screen_enter(self):
        """
        Chamado pela Screen (Lazy Load) quando o usuário navega para esta tela.
        Solicita os dados ao Router e atualiza a view.
        """
        logger.debug("Matrix screen entered. Requesting data from Router...")

        # 1. Pede a matriz formatada para o Router
        matrix_vm: MatrixDataViewModel = self.router.get_hour_date_matrix_data()

        # 2. Atualiza a view
        self._update_view(matrix_vm)


    def _update_view(self, matrix_vm: MatrixDataViewModel):
        """Converte o MatrixDataViewModel em dicionários para o RecycleView."""
        logger.debug("Updating GenericMatrixGraph with new data...")

        def cell_factory(row_idx: int, col_idx: int, payload: CardViewModel):
            # Como o mapper nunca retorna None, basta checar se o card_id está preenchido
            if payload["card_id"]:
                return self.card_creator.create_cell_dict(CARD, payload)
            else:
                return self.card_creator.create_cell_dict(NONE_CARD, payload)

        self.grid_view.draw_self(
            row_headers=matrix_vm.row_headers,
            col_headers=matrix_vm.col_headers,
            cell_data=matrix_vm.cell_data,
            cell_factory=cell_factory
        )
    

    def _handle_delete_card(self, instance, card_id: str):
        """Captura o evento vindo do MatrixCell dentro da RecycleView."""
        logger.info(f"Controller intercepting delete for card_id: {card_id}")

        # Precisa implementar